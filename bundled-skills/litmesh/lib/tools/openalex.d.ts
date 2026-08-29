/**
 * OpenAlex (api.openalex.org, free, no key) — the key-free stand-in for
 * Google Scholar: the broadest open scholarly index, with cited-by counts.
 * Google Scholar itself exposes no public API, so direct mode routes
 * `search_google_scholar` here and labels the results `openalex`.
 * @module litmesh/tools/openalex
 */
import type { Paper, PaperSearchValue } from '../paper.js';
import type { Runtime } from '../runtime.js';
/**
 * Normalize one OpenAlex `results[]` record.
 * @param record - untyped work record.
 * @returns the normalized paper, or `undefined` for a record without a title.
 */
export declare function normalizeOpenalexWork(record: unknown): Paper | undefined;
/** Parameters of one OpenAlex search. */
export interface OpenalexSearchParams {
    query: string;
    /** Already bounded number of results wanted. */
    wanted: number;
    yearFrom?: number | undefined;
    yearTo?: number | undefined;
}
/**
 * Run one OpenAlex search (the direct-mode backend of `search_google_scholar`).
 * @param runtime - plugin runtime (client only).
 * @param params - query, wanted count, and year range.
 * @param signal - cancellation.
 * @returns the normalized result set.
 */
export declare function runOpenalexSearch(runtime: Runtime, params: OpenalexSearchParams, signal: AbortSignal | undefined): Promise<PaperSearchValue>;
