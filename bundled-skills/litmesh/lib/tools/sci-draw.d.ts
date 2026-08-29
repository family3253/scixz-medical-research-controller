/**
 * `sci_draw`: AI scientific figure generation and processing through the
 * ai4scholar.net Nano Draw service (billed).
 * @module litmesh/tools/sci-draw
 */
import type { Context } from '@deepseek-ai/cordis';
import type { Runtime } from '../runtime.js';
/**
 * Register `sci_draw`.
 * @param ctx - context whose `tools` registry receives the effect-scoped registration.
 * @param runtime - plugin instance runtime.
 */
export declare function applySciDrawTool(ctx: Context, runtime: Runtime): void;
