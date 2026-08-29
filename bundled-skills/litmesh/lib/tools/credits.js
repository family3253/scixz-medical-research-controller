/**
 * Credit balance: the `get_litmesh_credits` tool (free `GET /api/credits`)
 * and the human `/litmesh` command, which reports key status, balance, and
 * the credits this session has spent.
 * @module litmesh/tools/credits
 */
import { defineTool } from '@deepseek-ai/dsh-tools';
import { compact, isRecord, str } from '../paper.js';
import { BALANCE_ROUTE } from '../shared/balance-route.js';
const OUTPUT_SCHEMA = {
    type: 'object',
    additionalProperties: false,
    properties: {
        totalAvailable: { type: 'number', required: true, description: 'Credits available right now (permanent + member monthly remaining).' },
        permanent: { type: 'number', required: true, description: 'Permanent credits (purchased or redeemed; never expire).' },
        memberMonthlyRemaining: { type: 'number', required: true, description: 'Membership monthly credits left in the current period; 0 for non-members.' },
        keyCreditLimit: { type: 'number', description: 'Spending cap of this API key, when one is set.' },
        keyCreditsUsed: { type: 'number', description: 'Credits this API key has spent.' },
        keyCreditsRemaining: { type: 'number', description: 'Cap minus used, when a cap is set.' },
        membership: {
            type: 'object',
            additionalProperties: false,
            properties: {
                plan: { type: 'string', required: true },
                status: { type: 'string', required: true },
                periodEnd: { type: 'string' },
            },
        },
        sessionTotal: { type: 'number', required: true, description: 'Credits charged by this plugin during the current session (process-local tally).' },
    },
};
/**
 * Fetch the balance for one key.
 * @param runtime - plugin runtime (client + key).
 * @param signal - cancellation.
 * @param agent - the calling agent, for the session tally.
 * @returns the normalized balance, or throws with the API's explanation.
 */
export async function fetchBalance(runtime, signal, agent) {
    const apiKey = await runtime.requireApiKey();
    const res = await runtime.client.get('/api/credits', { apiKey, signal });
    if (!res.ok)
        throw new Error(`could not read the AI4Scholar balance: ${res.error}`);
    const credits = isRecord(res.data.credits) ? res.data.credits : {};
    const key = isRecord(res.data.api_key) ? res.data.api_key : {};
    const membershipRecord = isRecord(res.data.membership) ? res.data.membership : undefined;
    const num = (v) => (typeof v === 'number' && Number.isFinite(v) ? v : undefined);
    const permanent = num(credits.permanent) ?? 0;
    const memberMonthlyRemaining = num(credits.member_monthly_remaining) ?? 0;
    const membership = membershipRecord !== undefined && str(membershipRecord, 'plan') !== undefined
        ? compact({ plan: str(membershipRecord, 'plan'), status: str(membershipRecord, 'status') ?? 'unknown', periodEnd: str(membershipRecord, 'period_end') })
        : undefined;
    return compact({
        totalAvailable: num(credits.total_available) ?? permanent + memberMonthlyRemaining,
        permanent,
        memberMonthlyRemaining,
        keyCreditLimit: num(key.credit_limit),
        keyCreditsUsed: num(key.credits_used),
        keyCreditsRemaining: num(key.credits_remaining),
        membership,
        sessionTotal: runtime.ledger.total(agent),
    });
}
/**
 * Balance summary as `Label: value` lines. Readable as plain text (the generic
 * command card and the model see it verbatim) and parseable by this plugin's
 * browser card, which upgrades the `/litmesh` row into a balance card.
 * Labels are stable identifiers; the browser half localizes them.
 */
export function formatBalance(value) {
    const n = (v) => v.toLocaleString('en-US');
    const lines = [];
    lines.push(`Credits available: ${n(value.totalAvailable)}`);
    lines.push(`Permanent: ${n(value.permanent)}`);
    lines.push(`Member monthly remaining: ${n(value.memberMonthlyRemaining)}`);
    if (value.membership !== undefined)
        lines.push(`Membership: ${value.membership.plan} (${value.membership.status})${value.membership.periodEnd !== undefined ? `, period ends ${value.membership.periodEnd.slice(0, 10)}` : ''}`);
    if (value.keyCreditsUsed !== undefined)
        lines.push(`API key spent in total: ${n(value.keyCreditsUsed)}`);
    if (value.keyCreditLimit !== undefined)
        lines.push(`API key cap: ${n(value.keyCreditLimit)}${value.keyCreditsRemaining !== undefined ? ` (${n(value.keyCreditsRemaining)} left)` : ''}`);
    lines.push(`Session spent: ${n(value.sessionTotal)}`);
    return lines.join('\n');
}
/**
 * Answer one balance-route request. Exported for tests; the route wires it to
 * the web server. Always HTTP 200 JSON with an `ok` discriminant so the
 * browser card can show the API's own explanation for a bad key.
 * @param runtime - plugin runtime.
 * @param signal - request cancellation.
 * @returns the JSON body.
 */
export async function answerBalanceRoute(runtime, signal) {
    if (runtime.direct) {
        // Key-free mode: there is no account, so there is nothing to check — the
        // card shows the friendly note instead of a key tester.
        return { ok: false, code: 'DIRECT_MODE', error: 'Key-free mode: this build calls the public APIs directly; no AI4Scholar key or credits are involved.' };
    }
    const key = await runtime.apiKey();
    if (key === undefined)
        return { ok: false, code: 'MISSING_KEY', error: 'AI4Scholar API key is not configured' };
    const res = await runtime.client.get('/api/credits', { apiKey: key, signal });
    if (!res.ok)
        return { ok: false, code: res.code ?? 'REQUEST_FAILED', error: res.error };
    const credits = isRecord(res.data.credits) ? res.data.credits : {};
    const apiKey = isRecord(res.data.api_key) ? res.data.api_key : {};
    const membershipRecord = isRecord(res.data.membership) ? res.data.membership : undefined;
    const num = (v) => (typeof v === 'number' && Number.isFinite(v) ? v : undefined);
    const permanent = num(credits.permanent) ?? 0;
    const memberMonthlyRemaining = num(credits.member_monthly_remaining) ?? 0;
    const plan = membershipRecord !== undefined ? str(membershipRecord, 'plan') : undefined;
    return compact({
        ok: true,
        totalAvailable: num(credits.total_available) ?? permanent + memberMonthlyRemaining,
        permanent,
        memberMonthlyRemaining,
        keyCreditsUsed: num(apiKey.credits_used),
        keyCreditLimit: num(apiKey.credit_limit),
        keyCreditsRemaining: num(apiKey.credits_remaining),
        membership: plan !== undefined ? compact({ plan, status: str(membershipRecord, 'status') ?? 'unknown', periodEnd: str(membershipRecord, 'period_end') }) : undefined,
    });
}
/**
 * Register the balance tool, the `/litmesh` command, and the balance route
 * the settings card calls.
 * @param ctx - plugin context.
 * @param runtime - plugin runtime.
 * @param command - whether to register the slash command (needs `ctx.commands`).
 * @param tool - whether to register the model-facing balance tool.
 * @param route - whether to register `GET /litmesh/balance` (needs `ctx.webServer`).
 */
export function applyCreditsTools(ctx, runtime, command, tool, route) {
    if (route) {
        // `webServer` exists only in the web composition; headless never activates this child.
        ctx.inject(['webServer'], (webCtx) => {
            webCtx.webServer.register({
                kind: 'exact',
                path: BALANCE_ROUTE,
                handler: async (req, res) => {
                    if (req.method !== 'GET') {
                        res.writeHead(405, { 'Content-Type': 'application/json', 'Allow': 'GET' });
                        res.end(JSON.stringify({ ok: false, code: 'METHOD_NOT_ALLOWED', error: 'GET only' }));
                        return;
                    }
                    const controller = new AbortController();
                    req.once('close', () => { controller.abort(); });
                    let body;
                    try {
                        body = await answerBalanceRoute(runtime, controller.signal);
                    }
                    catch (error) {
                        body = { ok: false, code: 'REQUEST_FAILED', error: error instanceof Error ? error.message : String(error) };
                    }
                    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' });
                    res.end(JSON.stringify(body));
                },
            });
        });
    }
    if (tool)
        ctx.tools.register(defineTool({
            name: 'get_litmesh_credits',
            description: 'Check the AI4Scholar credit balance of the configured API key (free) and how many credits this session has spent. Use it when the user asks about remaining credits/积分 or before an expensive batch of calls.',
            parameters: {},
            output: {
                schema: OUTPUT_SCHEMA,
                render: (_args, value) => [{ type: 'text', text: formatBalance(value) }],
            },
            timeoutMs: runtime.timeouts.tool,
            isConcurrencySafe: () => true,
            presentCall: () => ({ card: 'generic', title: 'AI4Scholar credit balance', kind: 'read' }),
            async execute(_args, exec) {
                return fetchBalance(runtime, exec.signal, exec.agent);
            },
        }));
    if (!command)
        return;
    // `commands` is optional: the child fiber activates when the service exists.
    ctx.inject(['commands'], (commandCtx) => {
        commandCtx.commands.register({
            name: 'litmesh',
            description: 'AI4Scholar: show API key status, credit balance, and credits spent in this session',
            handler: async (invocation) => {
                if (runtime.direct) {
                    return {
                        kind: 'success',
                        text: 'AI4Scholar runs in key-free mode: Semantic Scholar, PubMed, OpenAlex (in place of Google Scholar), arXiv, bioRxiv/medRxiv, DOI resolution, full text, and auto_cite all use free public APIs — no key, no credits.'
                            + '\nNot available without a key: sci_draw (AI figure generation) and the paid Auto-Cite ranking. Set mode: proxy plus an AI4Scholar API key in the plugin config to use those.',
                    };
                }
                const key = await runtime.apiKey();
                if (key === undefined) {
                    return { kind: 'error', text: 'AI4Scholar API key is not configured. Open Settings → Plugins → AI4Scholar to store one (or set LITMESH_API_KEY). Get a key at https://ai4scholar.net' };
                }
                try {
                    const balance = await fetchBalance(runtime, invocation.signal, invocation.agent);
                    return { kind: 'success', text: `${formatBalance(balance)}\nAPI key: configured (…${key.slice(-4)})` };
                }
                catch (error) {
                    return { kind: 'error', text: error instanceof Error ? error.message : String(error) };
                }
            },
        });
    });
}
