/**
 * Semantic Scholar tools over the Graph API (`/graph/v1/...` and
 * `/recommendations/v1/...`). Proxy mode goes through ai4scholar.net (billed,
 * results carry credits); direct mode calls api.semanticscholar.org itself —
 * free, no key required (an optional `SEMANTIC_SCHOLAR_API_KEY` raises the
 * rate limits and is sent as `x-api-key`).
 * @module litmesh/tools/semantic-scholar
 */
import type { Context } from '@deepseek-ai/cordis';
import type { InferValue, JsonValue } from '@deepseek-ai/dsh-tools';
import { formatPaper } from '../paper.js';
import type { Paper, PaperSearchValue } from '../paper.js';
import type { Runtime } from '../runtime.js';
/**
 * Normalize one Graph API paper record.
 * @param record - untyped `data[]` element or `/paper/{id}` body.
 * @param extra - platform-specific extras to attach (citation contexts).
 * @returns the normalized paper, or `undefined` for a record without a title or id.
 */
export declare function normalizeS2Paper(record: unknown, extra?: Record<string, JsonValue | undefined>): Paper | undefined;
/** Output schema of one author record. */
export declare const AUTHOR_SCHEMA: {
    readonly type: "object";
    readonly additionalProperties: false;
    readonly properties: {
        readonly authorId: {
            readonly type: "string";
            readonly required: true;
            readonly description: "Semantic Scholar author id.";
        };
        readonly name: {
            readonly type: "string";
            readonly required: true;
        };
        readonly affiliations: {
            readonly type: "array";
            readonly required: true;
            readonly items: {
                readonly type: "string";
            };
        };
        readonly homepage: {
            readonly type: "string";
        };
        readonly paperCount: {
            readonly type: "integer";
        };
        readonly citationCount: {
            readonly type: "integer";
        };
        readonly hIndex: {
            readonly type: "integer";
        };
        readonly url: {
            readonly type: "string";
        };
        readonly externalIds: {
            readonly type: "object";
            readonly additionalProperties: true;
            readonly description: "Other identifiers keyed by scheme, e.g. ORCID, DBLP.";
        };
    };
};
/** One normalized author. */
export type Author = InferValue<typeof AUTHOR_SCHEMA>;
/**
 * Normalize one Graph API author record.
 * @param record - untyped record.
 * @returns the author, or `undefined` without id or name.
 */
export declare function normalizeS2Author(record: unknown): Author | undefined;
/** Output schema of single-paper detail tools. */
export declare const PAPER_DETAIL_SCHEMA: {
    readonly type: "object";
    readonly additionalProperties: false;
    readonly properties: {
        readonly paper: {
            readonly required: true;
            readonly type: "object";
            readonly additionalProperties: false;
            readonly properties: {
                readonly source: {
                    readonly type: "string";
                    readonly required: true;
                    readonly enum: readonly ["semantic-scholar", "pubmed", "google-scholar", "openalex", "arxiv", "biorxiv", "medrxiv"];
                };
                readonly id: {
                    readonly type: "string";
                    readonly required: true;
                    readonly description: "Platform-native identifier: Semantic Scholar paperId, PubMed PMID, arXiv id, bioRxiv/medRxiv DOI, or a Google Scholar result URL.";
                };
                readonly title: {
                    readonly type: "string";
                    readonly required: true;
                };
                readonly authors: {
                    readonly type: "array";
                    readonly required: true;
                    readonly items: {
                        readonly type: "string";
                    };
                };
                readonly year: {
                    readonly type: "integer";
                };
                readonly date: {
                    readonly type: "string";
                    readonly description: "Publication date as returned by the platform (ISO date when available).";
                };
                readonly venue: {
                    readonly type: "string";
                    readonly description: "Journal or venue name.";
                };
                readonly abstract: {
                    readonly type: "string";
                    readonly description: "Abstract, or the platform snippet when no abstract is available.";
                };
                readonly citationCount: {
                    readonly type: "integer";
                };
                readonly doi: {
                    readonly type: "string";
                };
                readonly url: {
                    readonly type: "string";
                    readonly required: true;
                };
                readonly pdfUrl: {
                    readonly type: "string";
                    readonly description: "Open-access PDF URL when the platform reports one.";
                };
                readonly externalIds: {
                    readonly type: "object";
                    readonly additionalProperties: true;
                    readonly description: "Other identifiers keyed by scheme, e.g. DOI, ArXiv, PubMed, CorpusId.";
                };
                readonly categories: {
                    readonly type: "array";
                    readonly items: {
                        readonly type: "string";
                    };
                    readonly description: "Subject categories (arXiv) or the preprint category (bioRxiv/medRxiv).";
                };
                readonly extra: {
                    readonly type: "object";
                    readonly additionalProperties: true;
                    readonly description: "Platform-specific fields that have no normalized slot, e.g. citation contexts and intents on citation-graph results.";
                };
            };
        };
        readonly credits: {
            readonly type: "object";
            readonly additionalProperties: false;
            readonly description: "AI4Scholar credit accounting for this call, when the API reported it.";
            readonly properties: {
                readonly charged: {
                    readonly type: "number";
                    readonly description: "Credits this call cost.";
                };
                readonly remaining: {
                    readonly type: "number";
                    readonly description: "Account balance after this call.";
                };
                readonly sessionTotal: {
                    readonly type: "number";
                    readonly description: "Credits charged by this plugin during the current session (process-local tally).";
                };
            };
        };
    };
};
/** Parameters of one Semantic Scholar paper search. */
export interface SemanticSearchParams {
    query: string;
    /** Already bounded page size. */
    limit: number;
    offset?: number | undefined;
    /** Graph API year filter: `2019`, `2016-2020`, `2010-`, `-2015`. */
    year?: string | undefined;
}
/**
 * Run one Semantic Scholar paper search (shared by `search_semantic` and `search_papers`).
 * @param runtime - plugin runtime.
 * @param params - query and paging.
 * @param signal - cancellation.
 * @param agent - executing agent for the credit tally.
 * @returns the normalized page.
 */
export declare function runSemanticSearch(runtime: Runtime, params: SemanticSearchParams, signal: AbortSignal | undefined, agent: object | undefined): Promise<PaperSearchValue>;
/**
 * Register the Semantic Scholar tools.
 * @param ctx - context whose `tools` registry receives the effect-scoped registrations.
 * @param runtime - plugin instance runtime.
 * @param fullText - whether to register the PDF-reading tool.
 */
export declare function applySemanticScholarTools(ctx: Context, runtime: Runtime, fullText: boolean): void;
export { formatPaper };
