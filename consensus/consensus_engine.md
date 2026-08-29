# Consensus engine / 政事堂

Use consensus for important design decisions, causal claims, publication recommendations, safety-sensitive interpretations, or explicit `/scixz` multi-agent requests. Consensus is a barrier stage after independent reports and the critic pass; it is not a majority vote taken before evidence is compared.

## Round 0 — quorum and evidence gate

Confirm that the selected mode's quorum is met, every worker has a status, and the evidence pack is immutable. A failed or timed-out worker is not agreement. If quorum is not met for a safety-critical or estimand-defining role, stop and request the missing input.

## Round 1 — independent analyses

Give each role a separate question and the same evidence boundary. Preserve assumptions, evidence anchors, confidence, and recommended action.

## Round 2 — critic and disagreement map

Run the critic first, then compare only the outputs. Classify each point as agreement, complementary, unresolved disagreement, or unsupported assertion. Do not average incompatible estimands or silently erase minority concerns.

## Round 3 — arbitration

Prefer the recommendation with the stronger evidence, clearer assumptions, lower risk of overclaim, and better reproducibility. If the conflict cannot be resolved, report both views and the information that would resolve it.

Consensus hands a structured decision record to the verifier. It must not publish the final artifact itself.
The decision record must list dissenting roles explicitly, including an empty list when no dissent remains.

In the three-department analogy, this barrier is the `政事堂`: the approved mandate, ministry reports, critic challenges, and unresolved dissent are jointly reconciled before verification. It cannot reopen scope or authorize a new Skill without returning the change to 中书省 and 门下省.

## Required final fields

- `Consensus findings`
- `Strong agreement`
- `Remaining uncertainty`
- `Final recommendation`
- `Why this recommendation is limited`
