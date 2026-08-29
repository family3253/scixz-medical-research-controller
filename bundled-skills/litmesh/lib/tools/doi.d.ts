/**
 * DOI tools: resolve any DOI to a PDF (open access, or publisher access from
 * the host network) and read its full text. No credits.
 * @module litmesh/tools/doi
 */
import type { Context } from '@deepseek-ai/cordis';
import type { Runtime } from '../runtime.js';
/** Accept a bare DOI or a doi.org URL; return the bare DOI. */
export declare function normalizeDoi(input: string): string;
/**
 * Register the DOI tools.
 * @param ctx - context whose `tools` registry receives the effect-scoped registrations.
 * @param runtime - plugin instance runtime.
 * @param fullText - whether to register the PDF-reading tool.
 */
export declare function applyDoiTools(ctx: Context, runtime: Runtime, fullText: boolean): void;
