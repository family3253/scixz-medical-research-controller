/**
 * bioRxiv and medRxiv tools over the public api.biorxiv.org (no key, no
 * credits) plus PDF reading.
 * @module litmesh/tools/rxiv
 */
import type { Context } from '@deepseek-ai/cordis';
import type { Paper } from '../paper.js';
import type { Runtime } from '../runtime.js';
type Server = 'biorxiv' | 'medrxiv';
/** Accept a bare DOI (10.1101/…), with or without a version suffix, or a content URL. */
export declare function normalizeRxivDoi(input: string): {
    doi: string;
    version: string | undefined;
};
/**
 * Normalize one `collection[]` record from api.biorxiv.org.
 * @param record - untyped item.
 * @param server - which server it came from.
 * @returns the normalized paper, or `undefined` for a record without DOI or title.
 */
export declare function normalizeRxivPaper(record: unknown, server: Server): Paper | undefined;
/**
 * Register the bioRxiv and medRxiv tools.
 * @param ctx - context whose `tools` registry receives the effect-scoped registrations.
 * @param runtime - plugin instance runtime.
 * @param fullText - whether to register the PDF-reading tools.
 */
export declare function applyRxivTools(ctx: Context, runtime: Runtime, fullText: boolean): void;
export {};
