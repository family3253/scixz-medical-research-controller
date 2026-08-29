/**
 * litmesh: free, key-less academic literature search and citation tools for AI agents. Registers
 * Semantic Scholar, PubMed, Google Scholar, arXiv, bioRxiv/medRxiv, DOI,
 * full-text, auto-cite, figure-drawing, and credit-balance tools on
 * `ctx.tools`, a system-prompt guidance section, and the `/litmesh`
 * command. Two modes: `direct` (default) runs every search tool on the free
 * public APIs — api.semanticscholar.org, NCBI E-utilities, OpenAlex — with no
 * API key; `proxy` restores the billed ai4scholar.net behavior, where the
 * API key resolves per call through `ctx.credentials`.
 * @module litmesh
 */
import type { Context } from '@deepseek-ai/cordis';
import Schema from '@deepseek-ai/schemastery';
export { Ai4ScholarClient } from './api-client.js';
export type { ApiClientOptions, ApiResult, RequestOptions, CreditsInfo } from './api-client.js';
export { PAPER_SCHEMA, PAPER_SEARCH_OUTPUT_SCHEMA, CREDITS_SCHEMA, formatPaper, formatPaperSearch, formatCredits } from './paper.js';
export type { Paper, PaperSearchValue, PaperSource, CreditsValue } from './paper.js';
export { normalizeS2Paper, normalizeS2Author, AUTHOR_SCHEMA } from './tools/semantic-scholar.js';
export { normalizePubmedPaper } from './tools/pubmed.js';
export { normalizeScholarResult } from './tools/google-scholar.js';
export { parseArxivFeed, normalizeArxivId } from './tools/arxiv.js';
export { normalizeRxivPaper, normalizeRxivDoi } from './tools/rxiv.js';
export { normalizeDoi } from './tools/doi.js';
export { mergePaperLists, identityKeys, titleKey, UNIFIED_SOURCES } from './tools/unified.js';
export { runOpenalexSearch, normalizeOpenalexWork } from './tools/openalex.js';
export { eutilsSearch, eutilsFetchPapers, eutilsLinks } from './tools/pubmed-eutils.js';
export { runLocalAutoCite, splitSentences, sentenceKeywords, matchScore, pickAutoPoints, pickManualPoints, formatReference, bibtexEntry, DIRECT_AUTOCITE_CAP } from './tools/auto-cite-local.js';
export type { CitationStyle, LocalAutoCiteArgs, LocalAutoCiteResult } from './tools/auto-cite-local.js';
export { READ_OUTPUT_SCHEMA, sliceText, pdfCandidatesFor } from './pdf.js';
export { CreditLedger } from './runtime.js';
export { buildGuidance } from './prompt.js';
/** Cordis plugin name used by loader diagnostics. */
export declare const name = "litmesh";
/** Services required before `apply` runs; `credentials` and `commands` are read lazily and stay optional. */
export declare const inject: string[];
/** Version string sent as `User-Agent`; kept in sync with package.json by the release script. */
export declare const VERSION = "0.3.0";
/** Plugin configuration; every deployment-varying value is a field with a schema default. */
export interface Config {
    /**
     * How the tools reach the platforms. `direct` (default) calls the free
     * public APIs — api.semanticscholar.org, NCBI E-utilities, OpenAlex — and
     * needs no key anywhere. `proxy` restores the ai4scholar.net behavior
     * (billed, needs the AI4Scholar API key). Validated to those two values in
     * `apply`; typed as string because schemastery has no union default here.
     */
    mode?: string;
    /** ai4scholar.net API origin (proxy mode). */
    baseUrl?: string;
    /** Credential reference (environment-variable name) that holds the AI4Scholar API key. */
    apiKeyEnv?: string;
    /** Optional Semantic Scholar API key reference (direct mode): unauthenticated works, a key raises the rate limits. */
    s2ApiKeyEnv?: string;
    /** Register the Semantic Scholar tools. */
    semanticScholar?: boolean;
    /** Register the PubMed tools. */
    pubmed?: boolean;
    /** Register the Google Scholar tool. */
    googleScholar?: boolean;
    /** Register the arXiv tools. */
    arxiv?: boolean;
    /** Register the bioRxiv and medRxiv tools. */
    biorxiv?: boolean;
    /** Register the DOI download/read tools. */
    doi?: boolean;
    /** Register the full-text `read_*` tools (PDF download + text extraction). */
    fullText?: boolean;
    /** Register `auto_cite`. */
    autoCite?: boolean;
    /** Register `sci_draw`. */
    sciDraw?: boolean;
    /** Register `search_papers` (unified cross-platform search over the enabled families). */
    unifiedSearch?: boolean;
    /** Register `get_litmesh_credits`. */
    creditsTool?: boolean;
    /** Register the `/litmesh` command (needs the commands service). */
    command?: boolean;
    /** Register `GET /litmesh/balance` on the web server for the settings card's key test. */
    balanceRoute?: boolean;
    /** Attach credits charged/remaining and the session tally to billed results. */
    showCredits?: boolean;
    /** Register the system-prompt guidance section. */
    promptGuidance?: boolean;
    /** Order of the guidance section within the assembled prompt (tool guidance uses 100–199). */
    promptOrder?: number;
    /** Results returned when the model omits `max_results`. */
    defaultMaxResults?: number;
    /** Upper bound the model may request per call. */
    maxResultsCap?: number;
    /** Cap on abstract characters per paper in model-facing text; 0 omits abstracts. */
    abstractMaxChars?: number;
    /** Characters returned per full-text read call when the model omits `max_chars`. */
    readMaxChars?: number;
    /** Per-attempt HTTP timeout in milliseconds. */
    requestTimeoutMs?: number;
    /** Per-download timeout for PDFs in milliseconds. */
    pdfTimeoutMs?: number;
    /** Timeout for generation/streaming endpoints (auto_cite, sci_draw) in milliseconds. */
    generationTimeoutMs?: number;
    /** Attempts for retryable failures (HTTP 429 and network errors). */
    maxRetries?: number;
    /** Base delay before the second attempt in milliseconds; doubles per attempt. */
    retryBackoffMs?: number;
    /** Cooperative per-tool-call budget in milliseconds enforced by dsh-tool-call-timeout-policy. */
    toolTimeoutMs?: number;
}
export declare const Config: Schema<Config>;
/**
 * Validate the config and register the enabled tools, command, and guidance.
 * Every registration is an effect on `ctx`, so disposing the plugin fiber
 * removes the tools, the command, and the prompt section together.
 * @param ctx - plugin context with `tools` and `systemPrompt` ready.
 * @param config - schemastery-validated config with defaults applied.
 */
export declare function apply(ctx: Context, config: Config): void;
