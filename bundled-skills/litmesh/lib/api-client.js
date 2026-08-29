/**
 * HTTP client for the ai4scholar.net API plus the plain fetch helpers the
 * free upstream platforms (arXiv, bioRxiv, doi.org) need. Owns base URL,
 * timeout, retry, bearer authorization, and credit-header capture; tool
 * modules own paths, payloads, and result shapes.
 * @module litmesh/api-client
 */
/** Maximum characters of a non-2xx response body kept in the error message. */
const ERROR_BODY_MAX_CHARS = 240;
/** Browser-like headers publishers and preprint servers accept for PDF downloads. */
export const BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/pdf,application/x-pdf,*/*',
};
/**
 * Sleep that rejects when `signal` aborts, so a retry backoff never outlives
 * the tool call that scheduled it.
 */
function sleep(ms, signal) {
    return new Promise((resolve, reject) => {
        if (signal?.aborted) {
            reject(abortError(signal));
            return;
        }
        const timer = setTimeout(() => {
            signal?.removeEventListener('abort', onAbort);
            resolve();
        }, ms);
        function onAbort() {
            clearTimeout(timer);
            reject(abortError(signal));
        }
        signal?.addEventListener('abort', onAbort, { once: true });
    });
}
function abortError(signal) {
    const reason = signal?.reason;
    return reason instanceof Error ? reason : new Error('The operation was aborted');
}
/** Whether `error` is an abort raised by the caller's own signal (never retried). */
function isCallerAbort(error, signal) {
    return signal?.aborted === true && error instanceof Error && error.name === 'AbortError';
}
/** Whether `error` is the per-attempt timeout (retryable). */
function isTimeout(error) {
    return error instanceof Error && error.name === 'TimeoutError';
}
/** Combine the caller signal with a fresh timeout. */
export function requestSignal(signal, timeoutMs) {
    const signals = [AbortSignal.timeout(timeoutMs)];
    if (signal !== undefined)
        signals.push(signal);
    return AbortSignal.any(signals);
}
/** Parse the `X-Credits-*` headers when present. */
export function creditsFromHeaders(headers) {
    const charged = numberHeader(headers.get('x-credits-charged'));
    const remaining = numberHeader(headers.get('x-credits-remaining'));
    if (charged === undefined && remaining === undefined)
        return undefined;
    return {
        ...(charged !== undefined ? { charged } : {}),
        ...(remaining !== undefined ? { remaining } : {}),
    };
}
function numberHeader(value) {
    if (value === null)
        return undefined;
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : undefined;
}
/**
 * Turn a non-2xx response into a message the model can act on: the status,
 * plus the server's own explanation when the body carries one.
 */
async function describeFailure(res, hintCredentials = true) {
    let detail = '';
    let code;
    try {
        const text = await res.text();
        if (text.length > 0) {
            try {
                const parsed = JSON.parse(text);
                if (typeof parsed === 'object' && parsed !== null) {
                    const record = parsed;
                    const candidate = record.message ?? record.error ?? record.detail;
                    detail = typeof candidate === 'string' ? candidate : text;
                    if (typeof record.error === 'string' && /^[A-Z0-9_]+$/.test(record.error))
                        code = record.error;
                }
                else {
                    detail = text;
                }
            }
            catch {
                // Not JSON: keep the raw text as the detail.
                detail = text;
            }
        }
    }
    catch {
        // Body unreadable: the status alone still explains the failure.
    }
    detail = detail.replace(/\s+/g, ' ').trim();
    if (detail.length > ERROR_BODY_MAX_CHARS)
        detail = `${detail.slice(0, ERROR_BODY_MAX_CHARS)}…`;
    const hint = hintCredentials && (res.status === 401 || res.status === 403)
        ? ' (check the AI4Scholar API key)'
        : hintCredentials && res.status === 402
            ? ' (insufficient AI4Scholar credits; top up at https://ai4scholar.net)'
            : res.status === 403
                ? ' (the site refused the download; it may block automated clients)'
                : '';
    const error = detail.length > 0
        ? `HTTP ${res.status}${hint}: ${detail}`
        : `HTTP ${res.status} ${res.statusText}${hint}`.trim();
    return code !== undefined ? { error, code } : { error };
}
/** Thin JSON client over `fetch` with bounded retry and credit-header capture. */
export class Ai4ScholarClient {
    options;
    constructor(options) {
        this.options = options;
    }
    /**
     * GET a JSON endpoint.
     * @param path - path relative to `baseUrl`.
     * @param options - authorization, cancellation, and query parameters.
     * @returns the parsed body or a described failure; never throws for HTTP or
     *   transport errors, only for caller-initiated aborts.
     */
    get(path, options = {}) {
        return this.request('GET', path, undefined, options);
    }
    /**
     * POST a JSON body.
     * @param path - path relative to `baseUrl`.
     * @param body - JSON payload.
     * @param options - authorization, cancellation, and query parameters.
     * @returns the parsed body or a described failure; never throws for HTTP or
     *   transport errors, only for caller-initiated aborts.
     */
    post(path, body, options = {}) {
        return this.request('POST', path, body, options);
    }
    /**
     * POST a JSON body to a server-sent-events endpoint and collect the final
     * `result` event. Not retried: the server bills as it streams.
     * @param path - path relative to `baseUrl`.
     * @param body - JSON payload.
     * @param options - authorization, cancellation, and the stream timeout.
     * @returns the `result` event payload, or the last `error` event / transport failure.
     */
    async postSse(path, body, options = {}) {
        const url = this.buildUrl(path, options.query);
        const timeoutMs = options.timeoutMs ?? this.options.timeoutMs;
        let res;
        try {
            res = await fetch(url, {
                method: 'POST',
                headers: { ...this.headers(options.apiKey), Accept: 'text/event-stream' },
                body: JSON.stringify(body),
                signal: requestSignal(options.signal, timeoutMs),
            });
        }
        catch (error) {
            if (isCallerAbort(error, options.signal))
                throw error;
            return { ok: false, error: isTimeout(error) ? `request timed out after ${timeoutMs} ms` : String(error instanceof Error ? error.message : error), status: 0 };
        }
        if (!res.ok)
            return { ok: false, ...(await describeFailure(res)), status: res.status };
        const credits = creditsFromHeaders(res.headers);
        if (res.body === null)
            return { ok: false, error: 'empty response body', status: res.status };
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let event = '';
        let result;
        let lastError;
        const consume = (line) => {
            if (line.startsWith('event:')) {
                event = line.slice(6).trim();
            }
            else if (line.startsWith('data:')) {
                const raw = line.slice(5).trim();
                if (raw.length === 0)
                    return;
                try {
                    const data = JSON.parse(raw);
                    if (event === 'result')
                        result = data;
                    else if (event === 'error') {
                        lastError = typeof data === 'object' && data !== null && typeof data.message === 'string'
                            ? data.message
                            : raw;
                    }
                }
                catch {
                    // Malformed frame: ignore, the final result frame is what matters.
                }
            }
            else if (line.length === 0) {
                event = '';
            }
        };
        try {
            for (;;) {
                const { done, value } = await reader.read();
                if (done)
                    break;
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() ?? '';
                for (const line of lines)
                    consume(line.replace(/\r$/, ''));
            }
            if (buffer.length > 0)
                consume(buffer);
        }
        catch (error) {
            if (isCallerAbort(error, options.signal))
                throw error;
            return { ok: false, error: isTimeout(error) ? `stream timed out after ${timeoutMs} ms` : String(error instanceof Error ? error.message : error), status: 0 };
        }
        if (result === undefined)
            return { ok: false, error: lastError ?? 'stream ended without a result', status: res.status };
        return { ok: true, data: result, ...(credits !== undefined ? { credits } : {}) };
    }
    /**
     * GET a URL outside ai4scholar.net (arXiv, bioRxiv APIs) as text. No auth,
     * no retry, one timeout.
     * @param url - absolute URL.
     * @param options - cancellation and timeout.
     * @returns the body text or a described failure.
     */
    async fetchText(url, options = {}) {
        const timeoutMs = options.timeoutMs ?? this.options.timeoutMs;
        try {
            const res = await fetch(url, {
                headers: { 'User-Agent': this.options.userAgent, 'Accept': 'application/atom+xml, application/json, text/plain, */*' },
                signal: requestSignal(options.signal, timeoutMs),
            });
            if (!res.ok)
                return { ok: false, ...(await describeFailure(res, false)), status: res.status };
            return { ok: true, data: await res.text() };
        }
        catch (error) {
            if (isCallerAbort(error, options.signal))
                throw error;
            return { ok: false, error: isTimeout(error) ? `request timed out after ${timeoutMs} ms` : String(error instanceof Error ? error.message : error), status: 0 };
        }
    }
    /**
     * GET a URL outside ai4scholar.net as JSON. No auth, no retry, one timeout.
     * @param url - absolute URL.
     * @param options - cancellation and timeout.
     * @returns the parsed body or a described failure.
     */
    async fetchJson(url, options = {}) {
        const text = await this.fetchText(url, options);
        if (!text.ok)
            return text;
        try {
            return { ok: true, data: JSON.parse(text.data) };
        }
        catch {
            return { ok: false, error: 'response is not valid JSON', status: 0 };
        }
    }
    /**
     * Download a binary resource (a PDF) following redirects with browser-like
     * headers.
     * @param url - absolute URL.
     * @param options - cancellation and timeout.
     * @returns the bytes with the final URL and content type, or a described failure.
     */
    async fetchBinary(url, options = {}) {
        const timeoutMs = options.timeoutMs ?? this.options.timeoutMs;
        try {
            const res = await fetch(url, {
                headers: BROWSER_HEADERS,
                redirect: 'follow',
                signal: requestSignal(options.signal, timeoutMs),
            });
            if (!res.ok)
                return { ok: false, ...(await describeFailure(res, false)), status: res.status };
            return {
                ok: true,
                data: new Uint8Array(await res.arrayBuffer()),
                finalUrl: res.url.length > 0 ? res.url : url,
                contentType: res.headers.get('content-type') ?? '',
            };
        }
        catch (error) {
            if (isCallerAbort(error, options.signal))
                throw error;
            return { ok: false, error: isTimeout(error) ? `download timed out after ${timeoutMs} ms` : String(error instanceof Error ? error.message : error), status: 0 };
        }
    }
    buildUrl(path, query) {
        const url = new URL(path, this.options.baseUrl);
        if (query !== undefined) {
            for (const [key, value] of Object.entries(query)) {
                if (value !== undefined)
                    url.searchParams.set(key, String(value));
            }
        }
        return url.toString();
    }
    headers(apiKey) {
        const headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': this.options.userAgent,
        };
        if (apiKey !== undefined && apiKey.length > 0) {
            if (this.options.authHeader === 'x-api-key')
                headers['x-api-key'] = apiKey;
            else
                headers.Authorization = `Bearer ${apiKey}`;
        }
        return headers;
    }
    async request(method, path, body, options) {
        const url = this.buildUrl(path, options.query);
        const attempts = Math.max(1, this.options.maxRetries);
        const timeoutMs = options.timeoutMs ?? this.options.timeoutMs;
        let lastError = { ok: false, error: 'request not attempted', status: 0 };
        for (let attempt = 0; attempt < attempts; attempt++) {
            if (attempt > 0) {
                await sleep(this.options.retryBackoffMs * 2 ** (attempt - 1), options.signal);
            }
            try {
                const res = await fetch(url, {
                    method,
                    headers: this.headers(options.apiKey),
                    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
                    signal: requestSignal(options.signal, timeoutMs),
                });
                if (res.status === 429) {
                    lastError = { ok: false, ...(await describeFailure(res)), status: 429 };
                    continue;
                }
                if (!res.ok)
                    return { ok: false, ...(await describeFailure(res)), status: res.status };
                const credits = creditsFromHeaders(res.headers);
                return { ok: true, data: (await res.json()), ...(credits !== undefined ? { credits } : {}) };
            }
            catch (error) {
                if (isCallerAbort(error, options.signal))
                    throw error;
                const message = error instanceof Error ? error.message : String(error);
                lastError = {
                    ok: false,
                    error: isTimeout(error) ? `request timed out after ${timeoutMs} ms` : message,
                    status: 0,
                };
            }
        }
        return { ok: false, error: `${lastError.error} (after ${attempts} attempt${attempts === 1 ? '' : 's'})`, status: lastError.status, ...(lastError.code !== undefined ? { code: lastError.code } : {}) };
    }
}
