/**
 * Per-plugin-instance runtime handed to every tool module: the configured API
 * client, rendering and paging limits, per-call credential resolution, and
 * the session credit ledger.
 * @module litmesh/runtime
 */
import type { Context } from '@deepseek-ai/cordis';
import type { ApiOk, Ai4ScholarClient } from './api-client.js';
import type { CreditsValue, RenderOptions } from './paper.js';
/** Result-count limits shared by the search tools. */
export interface SearchLimits {
    /** Results returned when the model omits `max_results`. */
    defaultMaxResults: number;
    /** Upper bound the model may request per call. */
    maxResultsCap: number;
}
/** Timeouts for the slow tool families. */
export interface Timeouts {
    /** Cooperative per-call budget attached to ordinary tools as `timeoutMs`. */
    tool: number;
    /** Per-download timeout for PDF fetches. */
    pdf: number;
    /** Timeout for generation and streaming endpoints (auto_cite, sci_draw). */
    generation: number;
}
/** Full-text tool limits. */
export interface ReadLimits {
    /** Characters returned per read call when the model omits `max_chars`. */
    maxChars: number;
}
/**
 * Process-local tally of credits charged per agent (session). Keyed by the
 * agent object identity, so a resumed session starts a fresh tally.
 */
export declare class CreditLedger {
    private readonly totals;
    /**
     * Add one call's charge to its agent's tally.
     * @param agent - the executing agent (`exec.agent`); `undefined` skips the tally.
     * @param charged - credits the API reported for the call.
     * @returns the agent's running total, or `undefined` without an agent.
     */
    record(agent: object | undefined, charged: number): number | undefined;
    /**
     * Read one agent's running total.
     * @param agent - the agent object.
     * @returns the total charged so far, or `0`.
     */
    total(agent: object | undefined): number;
}
/** Everything a tool module needs from the plugin instance. */
export interface Runtime {
    /** How the plugin talks to the platforms: `direct` hits the free public APIs, `proxy` goes through ai4scholar.net (billed). */
    mode: 'direct' | 'proxy';
    /** Convenience for `mode === 'direct'`. */
    direct: boolean;
    /** Configured ai4scholar.net client (proxy mode); in direct mode only its host-agnostic fetch helpers are used. */
    client: Ai4ScholarClient;
    /**
     * Client the Semantic Scholar tools call. Proxy mode: the ai4scholar.net
     * proxy (same Graph API paths). Direct mode: `https://api.semanticscholar.org`
     * itself, optionally authenticated with `x-api-key`.
     */
    graph: Ai4ScholarClient;
    /** Model-facing rendering knobs. */
    render: RenderOptions;
    /** Result-count limits. */
    limits: SearchLimits;
    /** Full-text limits. */
    read: ReadLimits;
    /** Timeouts. */
    timeouts: Timeouts;
    /** Whether results carry credit accounting. */
    showCredits: boolean;
    /** Session credit tally. */
    ledger: CreditLedger;
    /**
     * Resolve the API key for one call. Reads the credentials service when the
     * composition provides one, else the process environment. Resolved per call
     * so a key stored or rotated while the process runs applies to the next call.
     * @returns the key, or `undefined` when nothing is configured.
     */
    apiKey(): Promise<string | undefined>;
    /**
     * Resolve the API key or throw a model-readable error naming the reference
     * and where to store it.
     * @returns the non-empty key.
     */
    requireApiKey(): Promise<string>;
    /**
     * Resolve the key the Semantic Scholar Graph calls authenticate with.
     * Proxy mode: the ai4scholar.net key (required). Direct mode: the optional
     * `SEMANTIC_SCHOLAR_API_KEY` reference — the public endpoint works without
     * one, a key only raises the rate limits.
     * @returns the key, or `undefined` to call unauthenticated.
     */
    s2ApiKey(): Promise<string | undefined>;
    /**
     * Fold one billed response's credit headers into the canonical value shape,
     * recording the charge on the agent's tally.
     * @param response - the successful API response.
     * @param agent - the executing agent (`exec.agent`).
     * @returns the credits object, or `undefined` when disabled or unreported.
     */
    creditsOf(response: Pick<ApiOk<unknown>, 'credits'>, agent: object | undefined): CreditsValue | undefined;
}
/** Bound the model's requested count to `[1, cap]`, defaulting when omitted. */
export declare function boundResults(requested: number | undefined, limits: SearchLimits, cap?: number): number;
/** Reject blank or whitespace-only strings the schema DSL cannot express. */
export declare function requireQuery(query: string, name?: string): string;
/** Reject an empty id list and normalize whitespace. */
export declare function requireIds(ids: readonly string[], name: string, max: number): string[];
/**
 * Build the credential resolvers for one plugin instance.
 * @param ctx - plugin context; `credentials` is read lazily so the plugin
 *   also runs in compositions without the seam.
 * @param apiKeyEnv - credential reference (a POSIX identifier) named by config.
 * @returns the two resolver methods of {@link Runtime}.
 */
export declare function makeCredentialResolvers(ctx: Context, apiKeyEnv: string): Pick<Runtime, 'apiKey' | 'requireApiKey'>;
/**
 * Build a resolver that never throws: the reference it names is optional, so a
 * missing value means "call unauthenticated" rather than failure. Direct mode
 * uses it for the optional Semantic Scholar key.
 * @param ctx - plugin context; `credentials` is read lazily.
 * @param env - credential reference (a POSIX identifier) named by config.
 * @returns an {@link Runtime.apiKey}-shaped resolver that yields `undefined` when unset.
 */
export declare function makeOptionalKeyResolver(ctx: Context, env: string): () => Promise<string | undefined>;
/**
 * Build the credits folder for one plugin instance.
 * @param ledger - the session tally.
 * @param enabled - the `showCredits` config.
 * @returns the {@link Runtime.creditsOf} method.
 */
export declare function makeCreditsFolder(ledger: CreditLedger, enabled: boolean): Runtime['creditsOf'];
