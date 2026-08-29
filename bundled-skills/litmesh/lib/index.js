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
import Schema from '@deepseek-ai/schemastery';
import { Ai4ScholarClient } from './api-client.js';
import { buildGuidance } from './prompt.js';
import { CreditLedger, makeCreditsFolder, makeCredentialResolvers, makeOptionalKeyResolver } from './runtime.js';
import { applySemanticScholarTools } from './tools/semantic-scholar.js';
import { applyPubmedTools } from './tools/pubmed.js';
import { applyGoogleScholarTools } from './tools/google-scholar.js';
import { applyArxivTools } from './tools/arxiv.js';
import { applyRxivTools } from './tools/rxiv.js';
import { applyDoiTools } from './tools/doi.js';
import { applyAutoCiteTool } from './tools/auto-cite.js';
import { applySciDrawTool } from './tools/sci-draw.js';
import { applyCreditsTools } from './tools/credits.js';
import { applyUnifiedSearchTool } from './tools/unified.js';
export { Ai4ScholarClient } from './api-client.js';
export { PAPER_SCHEMA, PAPER_SEARCH_OUTPUT_SCHEMA, CREDITS_SCHEMA, formatPaper, formatPaperSearch, formatCredits } from './paper.js';
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
export { READ_OUTPUT_SCHEMA, sliceText, pdfCandidatesFor } from './pdf.js';
export { CreditLedger } from './runtime.js';
export { buildGuidance } from './prompt.js';
/** Cordis plugin name used by loader diagnostics. */
export const name = 'litmesh';
/** Services required before `apply` runs; `credentials` and `commands` are read lazily and stay optional. */
export const inject = ['tools', 'systemPrompt'];
/** Version string sent as `User-Agent`; kept in sync with package.json by the release script. */
export const VERSION = '0.3.0';
export const Config = Schema.object({
    mode: Schema.string().default('direct').description('direct: free public APIs, no key needed (default). proxy: ai4scholar.net, needs the AI4Scholar API key.'),
    baseUrl: Schema.string().default('https://ai4scholar.net').description('ai4scholar.net API origin (proxy mode).'),
    apiKeyEnv: Schema.string().default('LITMESH_API_KEY').description('Credential reference holding the AI4Scholar API key (proxy mode).'),
    s2ApiKeyEnv: Schema.string().default('SEMANTIC_SCHOLAR_API_KEY').description('Optional Semantic Scholar API key reference (direct mode); raises the rate limits.'),
    semanticScholar: Schema.boolean().default(true).description('Register the Semantic Scholar tools.'),
    pubmed: Schema.boolean().default(true).description('Register the PubMed tools.'),
    googleScholar: Schema.boolean().default(true).description('Register the Google Scholar tool.'),
    arxiv: Schema.boolean().default(true).description('Register the arXiv tools.'),
    biorxiv: Schema.boolean().default(true).description('Register the bioRxiv/medRxiv tools.'),
    doi: Schema.boolean().default(true).description('Register the DOI tools.'),
    fullText: Schema.boolean().default(true).description('Register the full-text read_* tools.'),
    autoCite: Schema.boolean().default(true).description('Register auto_cite.'),
    sciDraw: Schema.boolean().default(true).description('Register sci_draw.'),
    unifiedSearch: Schema.boolean().default(true).description('Register search_papers (unified cross-platform search).'),
    creditsTool: Schema.boolean().default(true).description('Register get_litmesh_credits.'),
    command: Schema.boolean().default(true).description('Register the /litmesh command.'),
    balanceRoute: Schema.boolean().default(true).description('Register GET /litmesh/balance for the settings card.'),
    showCredits: Schema.boolean().default(true).description('Attach credit accounting to billed results.'),
    promptGuidance: Schema.boolean().default(true).description('Register the system-prompt guidance section.'),
    promptOrder: Schema.number().default(150).description('Order of the guidance section within the assembled prompt.'),
    defaultMaxResults: Schema.number().default(10).description('Results returned when the model omits max_results.'),
    maxResultsCap: Schema.number().default(50).description('Upper bound the model may request per call.'),
    abstractMaxChars: Schema.number().default(600).description('Abstract characters per paper in model-facing text; 0 omits abstracts.'),
    readMaxChars: Schema.number().default(60_000).description('Characters per full-text read call by default.'),
    requestTimeoutMs: Schema.number().default(30_000).description('Per-attempt HTTP timeout (ms).'),
    pdfTimeoutMs: Schema.number().default(120_000).description('Per-download PDF timeout (ms).'),
    generationTimeoutMs: Schema.number().default(300_000).description('auto_cite / sci_draw timeout (ms).'),
    maxRetries: Schema.number().default(3).description('Attempts for retryable failures.'),
    retryBackoffMs: Schema.number().default(2_000).description('Base retry delay (ms); doubles per attempt.'),
    toolTimeoutMs: Schema.number().default(180_000).description('Cooperative per-call budget (ms) for ordinary tools.'),
});
function assertPositiveInteger(field, value) {
    if (!Number.isInteger(value) || value < 1)
        throw new Error(`litmesh: ${field} must be a positive integer`);
}
function assertNonNegativeInteger(field, value) {
    if (!Number.isInteger(value) || value < 0)
        throw new Error(`litmesh: ${field} must be a non-negative integer`);
}
/**
 * Validate the config and register the enabled tools, command, and guidance.
 * Every registration is an effect on `ctx`, so disposing the plugin fiber
 * removes the tools, the command, and the prompt section together.
 * @param ctx - plugin context with `tools` and `systemPrompt` ready.
 * @param config - schemastery-validated config with defaults applied.
 */
export function apply(ctx, config) {
    const resolved = config;
    if (resolved.mode !== 'direct' && resolved.mode !== 'proxy') {
        throw new Error(`litmesh: mode must be "direct" or "proxy" (got "${resolved.mode}")`);
    }
    const mode = resolved.mode;
    const direct = mode === 'direct';
    for (const field of ['defaultMaxResults', 'maxResultsCap', 'readMaxChars', 'requestTimeoutMs', 'pdfTimeoutMs', 'generationTimeoutMs', 'maxRetries', 'toolTimeoutMs']) {
        assertPositiveInteger(field, resolved[field]);
    }
    assertNonNegativeInteger('abstractMaxChars', resolved.abstractMaxChars);
    assertNonNegativeInteger('retryBackoffMs', resolved.retryBackoffMs);
    if (!Number.isFinite(resolved.promptOrder))
        throw new Error('litmesh: promptOrder must be a finite number');
    let baseUrl;
    try {
        baseUrl = new URL(resolved.baseUrl).toString();
    }
    catch {
        throw new Error(`litmesh: baseUrl "${resolved.baseUrl}" is not a valid URL`);
    }
    if (resolved.defaultMaxResults > resolved.maxResultsCap) {
        throw new Error('litmesh: defaultMaxResults must not exceed maxResultsCap');
    }
    const client = new Ai4ScholarClient({
        baseUrl,
        timeoutMs: resolved.requestTimeoutMs,
        maxRetries: resolved.maxRetries,
        retryBackoffMs: resolved.retryBackoffMs,
        userAgent: `litmesh/${VERSION}`,
    });
    // Direct mode points the Graph API calls at api.semanticscholar.org itself
    // (same paths as the proxy, `x-api-key` when the optional key resolves).
    // The unauthenticated pool is shared and often congested, so 429 backoff
    // starts at 5 s there instead of the configured default.
    const graph = direct
        ? new Ai4ScholarClient({
            baseUrl: 'https://api.semanticscholar.org',
            timeoutMs: resolved.requestTimeoutMs,
            maxRetries: resolved.maxRetries,
            retryBackoffMs: Math.max(resolved.retryBackoffMs, 5_000),
            userAgent: `litmesh/${VERSION}`,
            authHeader: 'x-api-key',
        })
        : client;
    const ledger = new CreditLedger();
    const resolvers = makeCredentialResolvers(ctx, resolved.apiKeyEnv);
    const runtime = {
        mode,
        direct,
        client,
        graph,
        render: { abstractMaxChars: resolved.abstractMaxChars },
        limits: { defaultMaxResults: resolved.defaultMaxResults, maxResultsCap: resolved.maxResultsCap },
        read: { maxChars: resolved.readMaxChars },
        timeouts: { tool: resolved.toolTimeoutMs, pdf: resolved.pdfTimeoutMs, generation: resolved.generationTimeoutMs },
        showCredits: resolved.showCredits,
        ledger,
        ...resolvers,
        s2ApiKey: direct ? makeOptionalKeyResolver(ctx, resolved.s2ApiKeyEnv) : resolvers.requireApiKey,
        creditsOf: makeCreditsFolder(ledger, resolved.showCredits),
    };
    if (resolved.semanticScholar)
        applySemanticScholarTools(ctx, runtime, resolved.fullText);
    if (resolved.pubmed)
        applyPubmedTools(ctx, runtime);
    if (resolved.googleScholar)
        applyGoogleScholarTools(ctx, runtime);
    if (resolved.arxiv)
        applyArxivTools(ctx, runtime, resolved.fullText);
    if (resolved.biorxiv)
        applyRxivTools(ctx, runtime, resolved.fullText);
    if (resolved.doi)
        applyDoiTools(ctx, runtime, resolved.fullText);
    if (resolved.unifiedSearch) {
        applyUnifiedSearchTool(ctx, runtime, {
            'semantic-scholar': resolved.semanticScholar,
            'pubmed': resolved.pubmed,
            'arxiv': resolved.arxiv,
            'google-scholar': resolved.googleScholar,
        });
    }
    if (resolved.autoCite)
        applyAutoCiteTool(ctx, runtime);
    // sci_draw is the AI image service at ai4scholar.net; it has no free
    // counterpart, so direct mode registers nothing rather than a tool that
    // always fails.
    if (resolved.sciDraw && !direct)
        applySciDrawTool(ctx, runtime);
    if (resolved.creditsTool || resolved.command || resolved.balanceRoute)
        applyCreditsTools(ctx, runtime, resolved.command, resolved.creditsTool && !direct, resolved.balanceRoute);
    if (resolved.promptGuidance) {
        const text = buildGuidance({
            direct,
            semanticScholar: resolved.semanticScholar,
            pubmed: resolved.pubmed,
            googleScholar: resolved.googleScholar,
            arxiv: resolved.arxiv,
            biorxiv: resolved.biorxiv,
            doi: resolved.doi,
            fullText: resolved.fullText,
            autoCite: resolved.autoCite,
            sciDraw: resolved.sciDraw && !direct,
            credits: resolved.creditsTool && !direct,
            unified: resolved.unifiedSearch,
        });
        if (text !== undefined)
            ctx.systemPrompt.section({ name: 'tool:litmesh', order: resolved.promptOrder, text });
    }
}
