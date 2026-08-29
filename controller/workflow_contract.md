# Workflow completeness contract

Every task-class workflow must contain all six sections below. A workflow is not complete because it names Skills; it is complete only when another Codex instance can determine when to enter, what to read, what to produce, how to verify it, and what to do when a dependency is missing.

Required sections:

1. **Entry and scope** — when this workflow applies and what it does not do.
2. **Inputs** — required, optional, and blocking inputs.
3. **Route** — controller gate, primary Skill, supporting Skills, and collaboration mode.
4. **Outputs** — user-facing artifacts and internal handoff fields.
5. **Verification** — factual, numerical, reference, path, and output-contract checks.
6. **Failure/fallback** — missing Skill, missing data, tool failure, uncertainty, and stop condition.

Use one canonical owner per output contract. A fallback may continue only when it preserves the same contract and its limitations are reported. Do not silently turn an analysis into a draft, a review into a revision, or an association into a causal conclusion.
