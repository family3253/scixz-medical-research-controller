/**
 * `search_google_scholar`. Proxy mode goes through the ai4scholar.net proxy
 * (`/google-scholar/v1/search`, billed, ten results per page). Direct mode
 * queries OpenAlex instead — free, no key — because Google Scholar itself
 * exposes no public API; the tool keeps its name so existing prompts work,
 * and its results are labeled `openalex`.
 * @module litmesh/tools/google-scholar
 */
import type { Context } from '@deepseek-ai/cordis';
import type { Paper, PaperSearchValue } from '../paper.js';
import type { Runtime } from '../runtime.js';
/**
 * Normalize one Google Scholar result from the litmesh proxy.
 * @param record - untyped `results[]` element.
 * @returns the normalized paper, or `undefined` for a record without a title.
 */
export declare function normalizeScholarResult(record: unknown): Paper | undefined;
/** Parameters of one Google Scholar search. */
export interface ScholarSearchParams {
    query: string;
    /** Already bounded number of results wanted (fetched in pages of 10). */
    wanted: number;
    yearFrom?: number | undefined;
    yearTo?: number | undefined;
}
/**
 * Run one Google Scholar search (shared by `search_google_scholar` and `search_papers`).
 * @param runtime - plugin runtime.
 * @param params - query, wanted count, and year range.
 * @param signal - cancellation.
 * @param agent - executing agent for the credit tally.
 * @returns the normalized result set.
 */
export declare function runScholarSearch(runtime: Runtime, params: ScholarSearchParams, signal: AbortSignal | undefined, agent: object | undefined): Promise<PaperSearchValue>;
/**
 * Register the Google Scholar search tool.
 * @param ctx - context whose `tools` registry receives the effect-scoped registration.
 * @param runtime - plugin instance runtime.
 */
export declare function applyGoogleScholarTools(ctx: Context, runtime: Runtime): void;
