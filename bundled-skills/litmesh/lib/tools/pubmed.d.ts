/**
 * PubMed tools. Proxy mode goes through the ai4scholar.net PubMed API
 * (`/pubmed/v1/...`, billed); direct mode runs on the free public NCBI
 * E-utilities (esearch + efetch + elink, no key, no credits) with the same
 * normalized record shape.
 * @module litmesh/tools/pubmed
 */
import type { Context } from '@deepseek-ai/cordis';
import type { Paper, PaperSearchValue } from '../paper.js';
import type { Runtime } from '../runtime.js';
/**
 * Normalize one PubMed record from the litmesh API.
 * @param record - untyped `papers[]` element or `/paper/{pmid}` body.
 * @returns the normalized paper, or `undefined` for a record without a title or PMID.
 */
export declare function normalizePubmedPaper(record: unknown): Paper | undefined;
/** Parameters of one PubMed search. */
export interface PubmedSearchParams {
    query: string;
    /** Already bounded page size. */
    limit: number;
    offset?: number | undefined;
    sort?: 'relevance' | 'date' | undefined;
    /** `YYYY`, `YYYY/MM`, or `YYYY/MM/DD`. */
    minDate?: string | undefined;
    maxDate?: string | undefined;
}
/**
 * Run one PubMed search (shared by `search_pubmed` and `search_papers`).
 * @param runtime - plugin runtime.
 * @param params - query, paging, sort, and date range.
 * @param signal - cancellation.
 * @param agent - executing agent for the credit tally.
 * @returns the normalized page.
 */
export declare function runPubmedSearch(runtime: Runtime, params: PubmedSearchParams, signal: AbortSignal | undefined, agent: object | undefined): Promise<PaperSearchValue>;
/**
 * Register the PubMed tools.
 * @param ctx - context whose `tools` registry receives the effect-scoped registrations.
 * @param runtime - plugin instance runtime.
 */
export declare function applyPubmedTools(ctx: Context, runtime: Runtime): void;
