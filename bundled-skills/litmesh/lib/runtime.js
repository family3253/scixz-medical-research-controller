/**
 * Per-plugin-instance runtime handed to every tool module: the configured API
 * client, rendering and paging limits, per-call credential resolution, and
 * the session credit ledger.
 * @module litmesh/runtime
 */
import { credentialRef } from '@deepseek-ai/dsh-credentials';
/**
 * Process-local tally of credits charged per agent (session). Keyed by the
 * agent object identity, so a resumed session starts a fresh tally.
 */
export class CreditLedger {
    totals = new WeakMap();
    /**
     * Add one call's charge to its agent's tally.
     * @param agent - the executing agent (`exec.agent`); `undefined` skips the tally.
     * @param charged - credits the API reported for the call.
     * @returns the agent's running total, or `undefined` without an agent.
     */
    record(agent, charged) {
        if (agent === undefined)
            return undefined;
        const total = (this.totals.get(agent) ?? 0) + charged;
        this.totals.set(agent, total);
        return total;
    }
    /**
     * Read one agent's running total.
     * @param agent - the agent object.
     * @returns the total charged so far, or `0`.
     */
    total(agent) {
        return agent === undefined ? 0 : (this.totals.get(agent) ?? 0);
    }
}
/** Bound the model's requested count to `[1, cap]`, defaulting when omitted. */
export function boundResults(requested, limits, cap = limits.maxResultsCap) {
    const upper = Math.min(limits.maxResultsCap, cap);
    if (requested === undefined)
        return Math.min(limits.defaultMaxResults, upper);
    if (!Number.isFinite(requested) || requested < 1)
        return 1;
    return Math.min(Math.trunc(requested), upper);
}
/** Reject blank or whitespace-only strings the schema DSL cannot express. */
export function requireQuery(query, name = 'query') {
    const trimmed = query.trim();
    if (trimmed.length === 0)
        throw new Error(`${name} must be a non-empty string`);
    return trimmed;
}
/** Reject an empty id list and normalize whitespace. */
export function requireIds(ids, name, max) {
    const cleaned = ids.map((id) => id.trim()).filter((id) => id.length > 0);
    if (cleaned.length === 0)
        throw new Error(`${name} must contain at least one identifier`);
    if (cleaned.length > max)
        throw new Error(`${name} accepts at most ${max} identifiers per call`);
    return cleaned;
}
/**
 * Build the credential resolvers for one plugin instance.
 * @param ctx - plugin context; `credentials` is read lazily so the plugin
 *   also runs in compositions without the seam.
 * @param apiKeyEnv - credential reference (a POSIX identifier) named by config.
 * @returns the two resolver methods of {@link Runtime}.
 */
export function makeCredentialResolvers(ctx, apiKeyEnv) {
    const ref = credentialRef(apiKeyEnv);
    const apiKey = async () => {
        const credentials = ctx.get('credentials');
        if (credentials !== undefined) {
            const hit = await credentials.resolve(ref);
            return hit?.value;
        }
        const ambient = process.env[ref];
        return ambient !== undefined && ambient.length > 0 ? ambient : undefined;
    };
    const requireApiKey = async () => {
        const key = await apiKey();
        if (key === undefined) {
            throw new Error(`AI4Scholar API key is not configured. Store it as ${ref} in the environment, `
                + `or get a key at https://ai4scholar.net`);
        }
        return key;
    };
    return { apiKey, requireApiKey };
}
/**
 * Build a resolver that never throws: the reference it names is optional, so a
 * missing value means "call unauthenticated" rather than failure. Direct mode
 * uses it for the optional Semantic Scholar key.
 * @param ctx - plugin context; `credentials` is read lazily.
 * @param env - credential reference (a POSIX identifier) named by config.
 * @returns an {@link Runtime.apiKey}-shaped resolver that yields `undefined` when unset.
 */
export function makeOptionalKeyResolver(ctx, env) {
    const ref = credentialRef(env);
    return async () => {
        const credentials = ctx.get('credentials');
        if (credentials !== undefined) {
            const hit = await credentials.resolve(ref);
            if (hit !== undefined && hit.value.length > 0)
                return hit.value;
        }
        const ambient = process.env[ref];
        return ambient !== undefined && ambient.length > 0 ? ambient : undefined;
    };
}
/**
 * Build the credits folder for one plugin instance.
 * @param ledger - the session tally.
 * @param enabled - the `showCredits` config.
 * @returns the {@link Runtime.creditsOf} method.
 */
export function makeCreditsFolder(ledger, enabled) {
    return (response, agent) => {
        if (!enabled)
            return undefined;
        const info = response.credits;
        if (info === undefined)
            return undefined;
        const sessionTotal = info.charged !== undefined ? ledger.record(agent, info.charged) : undefined;
        const out = {};
        if (info.charged !== undefined)
            out.charged = info.charged;
        if (info.remaining !== undefined)
            out.remaining = info.remaining;
        if (sessionTotal !== undefined)
            out.sessionTotal = sessionTotal;
        return out;
    };
}
