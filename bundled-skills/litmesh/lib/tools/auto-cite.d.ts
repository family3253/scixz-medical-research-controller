/**
 * `auto_cite`: annotate academic text with real citations through the
 * ai4scholar.net Auto-Cite service (a server-sent-events endpoint; billed).
 * @module litmesh/tools/auto-cite
 */
import type { Context } from '@deepseek-ai/cordis';
import type { Runtime } from '../runtime.js';
/**
 * Register `auto_cite`.
 * @param ctx - context whose `tools` registry receives the effect-scoped registration.
 * @param runtime - plugin instance runtime.
 */
export declare function applyAutoCiteTool(ctx: Context, runtime: Runtime): void;
