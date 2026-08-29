/**
 * HTTP client for the ai4scholar.net API plus the plain fetch helpers the
 * free upstream platforms (arXiv, bioRxiv, doi.org) need. Owns base URL,
 * timeout, retry, bearer authorization, and credit-header capture; tool
 * modules own paths, payloads, and result shapes.
 * @module litmesh/api-client
 */
/** Client construction options; every value comes from the plugin config. */
export interface ApiClientOptions {
    /** API origin, e.g. `https://ai4scholar.net`. */
    baseUrl: string;
    /** Per-attempt request timeout in milliseconds. */
    timeoutMs: number;
    /** Total attempts for retryable failures (429 and network errors); `1` disables retry. */
    maxRetries: number;
    /** Base delay before the second attempt; doubles per attempt. */
    retryBackoffMs: number;
    /** `User-Agent` header value. */
    userAgent: string;
    /** How an API key is presented: `Authorization: Bearer` (ai4scholar.net) or `x-api-key` (api.semanticscholar.org). */
    authHeader?: 'bearer' | 'x-api-key';
}
/** Credit accounting the API reports on billed responses (`X-Credits-*` headers). */
export interface CreditsInfo {
    /** Credits this call cost. */
    charged?: number;
    /** Account balance after this call. */
    remaining?: number;
}
/** Successful response with the parsed JSON body. */
export interface ApiOk<T> {
    ok: true;
    data: T;
    /** Present when the response carried credit headers. */
    credits?: CreditsInfo;
}
/** Failed response: a human-readable message and the HTTP status (`0` for transport errors). */
export interface ApiErr {
    ok: false;
    error: string;
    status: number;
    /** Machine code from the body (`MISSING_API_KEY`, `INSUFFICIENT_CREDITS`, …) when the server sent one. */
    code?: string;
}
/** Discriminated result of one API call. */
export type ApiResult<T> = ApiOk<T> | ApiErr;
/** Per-request options. */
export interface RequestOptions {
    /** Bearer token; omitted requests go out unauthenticated. */
    apiKey?: string | undefined;
    /** Caller cancellation; combined with the per-attempt timeout. */
    signal?: AbortSignal | undefined;
    /** Query-string parameters; `undefined` values are skipped. */
    query?: Record<string, string | number | boolean | undefined> | undefined;
    /** Override the per-attempt timeout for slow endpoints (image generation, streaming). */
    timeoutMs?: number | undefined;
}
/** Result of one plain binary download. */
export interface BinaryResult {
    ok: true;
    data: Uint8Array;
    /** URL after redirects. */
    finalUrl: string;
    contentType: string;
}
/** Browser-like headers publishers and preprint servers accept for PDF downloads. */
export declare const BROWSER_HEADERS: Record<string, string>;
/** Combine the caller signal with a fresh timeout. */
export declare function requestSignal(signal: AbortSignal | undefined, timeoutMs: number): AbortSignal;
/** Parse the `X-Credits-*` headers when present. */
export declare function creditsFromHeaders(headers: Headers): CreditsInfo | undefined;
/** Thin JSON client over `fetch` with bounded retry and credit-header capture. */
export declare class Ai4ScholarClient {
    private readonly options;
    constructor(options: ApiClientOptions);
    /**
     * GET a JSON endpoint.
     * @param path - path relative to `baseUrl`.
     * @param options - authorization, cancellation, and query parameters.
     * @returns the parsed body or a described failure; never throws for HTTP or
     *   transport errors, only for caller-initiated aborts.
     */
    get<T>(path: string, options?: RequestOptions): Promise<ApiResult<T>>;
    /**
     * POST a JSON body.
     * @param path - path relative to `baseUrl`.
     * @param body - JSON payload.
     * @param options - authorization, cancellation, and query parameters.
     * @returns the parsed body or a described failure; never throws for HTTP or
     *   transport errors, only for caller-initiated aborts.
     */
    post<T>(path: string, body: Record<string, unknown>, options?: RequestOptions): Promise<ApiResult<T>>;
    /**
     * POST a JSON body to a server-sent-events endpoint and collect the final
     * `result` event. Not retried: the server bills as it streams.
     * @param path - path relative to `baseUrl`.
     * @param body - JSON payload.
     * @param options - authorization, cancellation, and the stream timeout.
     * @returns the `result` event payload, or the last `error` event / transport failure.
     */
    postSse<T>(path: string, body: Record<string, unknown>, options?: RequestOptions): Promise<ApiResult<T>>;
    /**
     * GET a URL outside ai4scholar.net (arXiv, bioRxiv APIs) as text. No auth,
     * no retry, one timeout.
     * @param url - absolute URL.
     * @param options - cancellation and timeout.
     * @returns the body text or a described failure.
     */
    fetchText(url: string, options?: Pick<RequestOptions, 'signal' | 'timeoutMs'>): Promise<ApiResult<string>>;
    /**
     * GET a URL outside ai4scholar.net as JSON. No auth, no retry, one timeout.
     * @param url - absolute URL.
     * @param options - cancellation and timeout.
     * @returns the parsed body or a described failure.
     */
    fetchJson<T>(url: string, options?: Pick<RequestOptions, 'signal' | 'timeoutMs'>): Promise<ApiResult<T>>;
    /**
     * Download a binary resource (a PDF) following redirects with browser-like
     * headers.
     * @param url - absolute URL.
     * @param options - cancellation and timeout.
     * @returns the bytes with the final URL and content type, or a described failure.
     */
    fetchBinary(url: string, options?: Pick<RequestOptions, 'signal' | 'timeoutMs'>): Promise<BinaryResult | ApiErr>;
    private buildUrl;
    private headers;
    private request;
}
