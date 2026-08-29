/**
 * PubMed over the free public NCBI E-utilities (no key, no credits): esearch
 * finds PMIDs, efetch returns the abstract XML, elink walks the citation and
 * similar-article links. The XML is parsed into the same record shape the
 * ai4scholar.net PubMed proxy uses, so `normalizePubmedPaper` is shared.
 * @module litmesh/tools/pubmed-eutils
 */
import type { Paper } from '../paper.js';
import type { Ai4ScholarClient } from '../api-client.js';
/** Result of one esearch: the total hit count and a page of PMIDs. */
export interface EsearchResult {
    total: number;
    ids: string[];
}
/**
 * Search PubMed through esearch.
 * @param client - host-agnostic fetch helpers.
 * @param term - PubMed query (field tags and booleans supported).
 * @param options - paging, sort, and a publication-date window (`YYYY`, `YYYY/MM`, `YYYY/MM/DD`).
 * @param signal - cancellation.
 */
export declare function eutilsSearch(client: Ai4ScholarClient, term: string, options: {
    retmax: number;
    retstart: number;
    sort?: 'relevance' | 'date' | undefined;
    minDate?: string | undefined;
    maxDate?: string | undefined;
    signal?: AbortSignal | undefined;
}): Promise<EsearchResult>;
/**
 * Fetch full records for PMIDs through efetch (XML) and normalize them.
 * @param client - host-agnostic fetch helpers.
 * @param ids - PMIDs (at most 200; the caller bounds them).
 * @param signal - cancellation.
 * @returns normalized papers, in id order; unparseable records drop out.
 */
export declare function eutilsFetchPapers(client: Ai4ScholarClient, ids: readonly string[], signal: AbortSignal | undefined): Promise<Paper[]>;
/**
 * Linked PMIDs for one article through elink.
 * @param client - host-agnostic fetch helpers.
 * @param pmid - the seed PMID.
 * @param linkname - `pubmed_pubmed` (similar) or `pubmed_pubmed_citedin` (citing).
 * @param limit - stop after this many link ids.
 * @param signal - cancellation.
 * @returns linked PMIDs excluding the seed itself, link order preserved.
 */
export declare function eutilsLinks(client: Ai4ScholarClient, pmid: string, linkname: 'pubmed_pubmed' | 'pubmed_pubmed_citedin', limit: number, signal: AbortSignal | undefined): Promise<string[]>;
