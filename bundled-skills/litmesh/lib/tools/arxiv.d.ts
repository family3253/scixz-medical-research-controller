/**
 * arXiv tools over the public arXiv API (no key, no credits) plus PDF reading.
 * @module litmesh/tools/arxiv
 */
import type { Context } from '@deepseek-ai/cordis';
import type { Paper, PaperSearchValue } from '../paper.js';
import type { Runtime } from '../runtime.js';
declare const SORT_BY: {
    readonly relevance: "relevance";
    readonly lastUpdatedDate: "lastUpdatedDate";
    readonly submittedDate: "submittedDate";
};
/** Normalize an arXiv id from an `<id>` URL: strip the abs prefix and version. */
export declare function arxivIdFromUrl(idUrl: string): string;
/** Accept `2106.12345`, `2106.12345v2`, `hep-th/9901001`, or a full arXiv URL; return the bare id. */
export declare function normalizeArxivId(input: string): string;
/**
 * Parse an arXiv Atom feed into normalized papers.
 * @param xml - the feed body.
 * @returns papers in feed order plus the reported total.
 */
export declare function parseArxivFeed(xml: string): {
    papers: Paper[];
    total: number;
};
/** Parameters of one arXiv search. */
export interface ArxivSearchParams {
    query: string;
    /** Already bounded page size. */
    limit: number;
    offset?: number | undefined;
    sortBy?: keyof typeof SORT_BY | undefined;
    /** `YYYY-MM-DD` lower bound on submission date. */
    dateFrom?: string | undefined;
}
/**
 * Run one arXiv search (shared by `search_arxiv` and `search_papers`). Free; no key.
 * @param runtime - plugin runtime (client only).
 * @param params - query, paging, sort, and date bound.
 * @param signal - cancellation.
 * @returns the normalized page.
 */
export declare function runArxivSearch(runtime: Runtime, params: ArxivSearchParams, signal: AbortSignal | undefined): Promise<PaperSearchValue>;
/**
 * Register the arXiv tools.
 * @param ctx - context whose `tools` registry receives the effect-scoped registrations.
 * @param runtime - plugin instance runtime.
 * @param fullText - whether to register the PDF-reading tool.
 */
export declare function applyArxivTools(ctx: Context, runtime: Runtime, fullText: boolean): void;
export {};
