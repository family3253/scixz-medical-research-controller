/**
 * The normalized paper record every search tool returns, its output schema,
 * and the pure model-facing / UI-facing projections. Normalizing here keeps
 * one programmatic shape across Semantic Scholar, PubMed, and Google Scholar
 * for Code Mode callers and one renderer for the model.
 * @module litmesh/paper
 */
import type { ContentBlock } from '@deepseek-ai/dsh-llm';
import type { GenericCallView, GenericResultView, InferValue, JsonValue, ToolResult, WebSearchResultView } from '@deepseek-ai/dsh-tools';
/** Which platform produced a record. */
export type PaperSource = 'semantic-scholar' | 'pubmed' | 'google-scholar' | 'openalex' | 'arxiv' | 'biorxiv' | 'medrxiv';
/** Every platform value, for schema enums. */
export declare const PAPER_SOURCES: readonly ["semantic-scholar", "pubmed", "google-scholar", "openalex", "arxiv", "biorxiv", "medrxiv"];
/** Human-readable platform label for headings and card titles. */
export declare const SOURCE_LABEL: Record<PaperSource, string>;
/** Credit accounting attached to billed results (absent on free platforms). */
export declare const CREDITS_SCHEMA: {
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
/** The {@link CREDITS_SCHEMA} value type. */
export type CreditsValue = InferValue<typeof CREDITS_SCHEMA>;
/** One-line credit note for model-facing text, or `undefined` when nothing is known. */
export declare function formatCredits(credits: CreditsValue | undefined): string | undefined;
/** Output schema of one normalized paper. Every optional field is omitted when unknown, never `null`. */
export declare const PAPER_SCHEMA: {
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
/** One normalized paper (the {@link PAPER_SCHEMA} value type). */
export type Paper = InferValue<typeof PAPER_SCHEMA>;
/** Output schema shared by every paper-list search tool. */
export declare const PAPER_SEARCH_OUTPUT_SCHEMA: {
    readonly type: "object";
    readonly additionalProperties: false;
    readonly properties: {
        readonly source: {
            readonly type: "string";
            readonly required: true;
            readonly enum: readonly ["semantic-scholar", "pubmed", "google-scholar", "openalex", "arxiv", "biorxiv", "medrxiv"];
        };
        readonly query: {
            readonly type: "string";
            readonly required: true;
        };
        readonly total: {
            readonly type: "integer";
            readonly required: true;
            readonly description: "Total matches reported by the platform, or the returned count when unknown.";
        };
        readonly papers: {
            readonly type: "array";
            readonly required: true;
            readonly items: {
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
        };
        readonly truncated: {
            readonly type: "boolean";
            readonly required: true;
            readonly description: "True when more results exist beyond the returned page.";
        };
        readonly nextOffset: {
            readonly type: "integer";
            readonly description: "Offset to request the next page, when the platform paginates by offset.";
        };
        readonly warning: {
            readonly type: "string";
            readonly description: "Set when the platform answered partially, e.g. a later page failed; the returned papers are still valid.";
        };
        readonly nextToken: {
            readonly type: "string";
            readonly description: "Continuation token for the next page, when the platform paginates by token (Semantic Scholar bulk search).";
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
/** The paper-list search tools' canonical value. */
export type PaperSearchValue = InferValue<typeof PAPER_SEARCH_OUTPUT_SCHEMA>;
/** Rendering knobs owned by the plugin config. */
export interface RenderOptions {
    /** Cap on abstract characters per paper in model-facing text; `0` omits abstracts. */
    abstractMaxChars: number;
}
/** Remove `undefined` members so a value satisfies its schema and `exactOptionalPropertyTypes`. */
export declare function compact<T extends Record<string, unknown>>(record: T): {
    [K in keyof T]: Exclude<T[K], undefined>;
};
/** Decode the HTML entities some platform payloads (PubMed) leave in titles and abstracts. */
export declare function decodeEntities(text: string): string;
/** Read a string field from an untyped platform record; blank strings count as absent. */
export declare function str(record: Record<string, unknown>, key: string): string | undefined;
/** Read an integer field from an untyped platform record. */
export declare function int(record: Record<string, unknown>, key: string): number | undefined;
/** Narrow an unknown JSON value to a plain object record. */
export declare function isRecord(value: unknown): value is Record<string, unknown>;
/** Truncate at a word boundary and mark the cut. */
export declare function clip(text: string, maxChars: number): string;
/** `A, B, C et al.` style author line. */
export declare function formatAuthors(authors: readonly string[], max?: number): string;
/** One paper as a markdown list entry: title link, byline, identifiers, and a clipped abstract. */
export declare function formatPaper(paper: Paper, index: number, options: RenderOptions): string;
/**
 * Model-facing text for a paper-list result: a heading with counts, the
 * numbered list, and a pagination note when more results exist.
 */
export declare function formatPaperSearch(value: PaperSearchValue, options: RenderOptions): string;
/** Model-facing content blocks for a paper-list result. */
export declare function renderPaperSearch(value: PaperSearchValue, options: RenderOptions): ContentBlock[];
/** Model-facing content for a single-paper result (details, full abstract). */
export declare function renderPaperDetail(paper: Paper, credits?: CreditsValue): ContentBlock[];
/** Pending-call card: a search card titled with the platform and query. */
export declare function presentPaperSearchCall(source: PaperSource, query: string): GenericCallView;
/** Project a paper into the `web` card's source shape (as plain JSON for the persisted meta). */
export declare function paperToSource(paper: Paper): Record<string, string>;
/** Replayable presentation meta for a paper-list result: the structured sources, the truncation flag, and the credits. */
export declare function paperSearchMeta(value: PaperSearchValue): JsonValue;
/** Replayable presentation meta for any paper list (shared by platform searches and the unified search). */
export declare function paperListMeta(papers: readonly Paper[], truncated: boolean, credits: CreditsValue | undefined): JsonValue;
/** The `credits` member of a presentation meta object (empty when the value carries none). */
export declare function creditsMeta(value: {
    credits?: CreditsValue | undefined;
}): {
    credits?: JsonValue;
};
/**
 * Card-title suffix from persisted meta, e.g. ` · 10 credits · 89,409 left`.
 * Empty when the meta carries no credits (free platforms, older logs).
 */
export declare function creditsTitleSuffix(meta: unknown): string;
/**
 * Completed generic card whose title carries the credit suffix; `undefined`
 * (framework generic card) on failure so the error stays visible unchanged.
 */
export declare function presentGenericWithCredits(title: string, result: ToolResult): GenericResultView | undefined;
/**
 * Completed-call card: the `web` search card carrying the structured sources
 * from `result.meta`. Returns `undefined` (generic card) on failure or when the
 * meta is malformed, e.g. a log written by a different plugin version.
 */
export declare function presentPaperSearchResult(source: PaperSource, query: string, result: ToolResult): WebSearchResultView | undefined;
/**
 * Completed-call `web` search card for any paper list, titled by the caller.
 * @param title - card title without the credit suffix.
 * @param result - the final tool result whose meta carries the sources.
 * @returns the card, or `undefined` (generic card) on failure or malformed meta.
 */
export declare function presentPaperListResult(title: string, result: ToolResult): WebSearchResultView | undefined;
