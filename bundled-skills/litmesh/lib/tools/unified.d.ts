/**
 * `search_papers`: one query across several platforms, merged and
 * de-duplicated (DOI, arXiv id, PMID, then normalized title), papers found
 * on more than one platform first. Free platforms cost nothing; billed ones
 * report their credits summed.
 * @module litmesh/tools/unified
 */
import type { Context } from '@deepseek-ai/cordis';
import type { Paper } from '../paper.js';
import type { Runtime } from '../runtime.js';
/** Platforms the unified search can fan out to, in merge priority order (richest metadata first). */
export declare const UNIFIED_SOURCES: readonly ["semantic-scholar", "pubmed", "arxiv", "google-scholar"];
export type UnifiedSource = (typeof UNIFIED_SOURCES)[number];
/** Lower-cased alphanumeric title for near-duplicate matching. */
export declare function titleKey(title: string): string;
/** Every identity key of one paper: DOI, arXiv id, PMID, and the normalized title. */
export declare function identityKeys(paper: Paper): string[];
/**
 * Merge platform result lists into one de-duplicated, ranked list.
 * @param lists - per-platform results in merge priority order.
 * @returns unique papers: multi-platform hits first, then by citations, then by year.
 */
export declare function mergePaperLists(lists: readonly (readonly Paper[])[]): Paper[];
/**
 * Register `search_papers`.
 * @param ctx - context whose `tools` registry receives the effect-scoped registration.
 * @param runtime - plugin instance runtime.
 * @param enabled - which platforms this composition mounted; the tool offers only those.
 */
export declare function applyUnifiedSearchTool(ctx: Context, runtime: Runtime, enabled: Record<UnifiedSource, boolean>): void;
