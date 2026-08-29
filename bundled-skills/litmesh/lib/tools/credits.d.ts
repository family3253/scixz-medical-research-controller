/**
 * Credit balance: the `get_litmesh_credits` tool (free `GET /api/credits`)
 * and the human `/litmesh` command, which reports key status, balance, and
 * the credits this session has spent.
 * @module litmesh/tools/credits
 */
import type { Context } from '@deepseek-ai/cordis';
import type { InferValue } from '@deepseek-ai/dsh-tools';
import type { Runtime } from '../runtime.js';
import type { BalanceRouteResponse } from '../shared/balance-route.js';
declare const OUTPUT_SCHEMA: {
    readonly type: "object";
    readonly additionalProperties: false;
    readonly properties: {
        readonly totalAvailable: {
            readonly type: "number";
            readonly required: true;
            readonly description: "Credits available right now (permanent + member monthly remaining).";
        };
        readonly permanent: {
            readonly type: "number";
            readonly required: true;
            readonly description: "Permanent credits (purchased or redeemed; never expire).";
        };
        readonly memberMonthlyRemaining: {
            readonly type: "number";
            readonly required: true;
            readonly description: "Membership monthly credits left in the current period; 0 for non-members.";
        };
        readonly keyCreditLimit: {
            readonly type: "number";
            readonly description: "Spending cap of this API key, when one is set.";
        };
        readonly keyCreditsUsed: {
            readonly type: "number";
            readonly description: "Credits this API key has spent.";
        };
        readonly keyCreditsRemaining: {
            readonly type: "number";
            readonly description: "Cap minus used, when a cap is set.";
        };
        readonly membership: {
            readonly type: "object";
            readonly additionalProperties: false;
            readonly properties: {
                readonly plan: {
                    readonly type: "string";
                    readonly required: true;
                };
                readonly status: {
                    readonly type: "string";
                    readonly required: true;
                };
                readonly periodEnd: {
                    readonly type: "string";
                };
            };
        };
        readonly sessionTotal: {
            readonly type: "number";
            readonly required: true;
            readonly description: "Credits charged by this plugin during the current session (process-local tally).";
        };
    };
};
type CreditsBalance = InferValue<typeof OUTPUT_SCHEMA>;
/**
 * Fetch the balance for one key.
 * @param runtime - plugin runtime (client + key).
 * @param signal - cancellation.
 * @param agent - the calling agent, for the session tally.
 * @returns the normalized balance, or throws with the API's explanation.
 */
export declare function fetchBalance(runtime: Runtime, signal: AbortSignal | undefined, agent: object | undefined): Promise<CreditsBalance>;
/**
 * Balance summary as `Label: value` lines. Readable as plain text (the generic
 * command card and the model see it verbatim) and parseable by this plugin's
 * browser card, which upgrades the `/litmesh` row into a balance card.
 * Labels are stable identifiers; the browser half localizes them.
 */
export declare function formatBalance(value: CreditsBalance): string;
/**
 * Answer one balance-route request. Exported for tests; the route wires it to
 * the web server. Always HTTP 200 JSON with an `ok` discriminant so the
 * browser card can show the API's own explanation for a bad key.
 * @param runtime - plugin runtime.
 * @param signal - request cancellation.
 * @returns the JSON body.
 */
export declare function answerBalanceRoute(runtime: Runtime, signal: AbortSignal | undefined): Promise<BalanceRouteResponse>;
/**
 * Register the balance tool, the `/litmesh` command, and the balance route
 * the settings card calls.
 * @param ctx - plugin context.
 * @param runtime - plugin runtime.
 * @param command - whether to register the slash command (needs `ctx.commands`).
 * @param tool - whether to register the model-facing balance tool.
 * @param route - whether to register `GET /litmesh/balance` (needs `ctx.webServer`).
 */
export declare function applyCreditsTools(ctx: Context, runtime: Runtime, command: boolean, tool: boolean, route: boolean): void;
export {};
