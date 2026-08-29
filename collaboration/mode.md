# Multi-agent collaboration mode

SciXZ uses a coordinator-led, evidence-bounded collaboration protocol. The collaboration layer runs under the central controller: no worker is dispatched until 中书省 has drafted the mandate and 门下省 has approved the route. The goal is not to produce many opinions; it is to make independent reasoning visible, expose disagreement, and reduce unsupported conclusions.

## Mode selection

| Mode | Use when | Typical roles | Stop condition |
|---|---|---|---|
| `single` | One-step task with low ambiguity and low consequence | coordinator or one domain owner | deliverable verified |
| `panel` | Two or more independent perspectives materially improve the answer | coordinator + 2–4 experts + verifier | all critical claims have an owner and evidence status |
| `council` | Causal claims, clinical design, publication decisions, safety issues, or explicit multi-agent request | coordinator + domain experts + critic + consensus + verifier | unresolved issues are either resolved or explicitly reported |
| `recursive-review` | Draft → review → revise → re-review is requested | coordinator + reviewer panel + reviser + verifier | critical issue count reaches zero or max rounds is reached |

Use `panel` by default for `/scixz` tasks that combine two domains. Use `council` for medical decisions where an overclaim could change study design, patient interpretation, or publication strategy. Do not start a council for a simple file conversion or a one-variable calculation.

## Collaboration lifecycle

### Phase 0 — controller-approved coordinator brief

After the controller has approved execution, create a short `collaboration_brief` containing the user goal, input paths, language, deliverable, study type, decision to be made, evidence boundary, exclusions, and deadline/round budget. Resolve local files once before dispatch.

### Phase 1 — independent work

Dispatch each worker a non-overlapping question. Workers receive the same evidence pack and do not see other workers' conclusions. Each worker returns claims, evidence anchors, assumptions, confidence, risks, and a recommendation.

### Phase 2 — critic pass

Give the critic only the brief and worker reports. Ask it to find contradictions, duplicated reasoning, unsupported claims, causal overreach, missing analyses, and hidden dependency failures. The critic must cite the report or evidence item it is challenging.

### Phase 3 — consensus

The consensus agent builds an agreement/disagreement matrix, resolves compatible differences, preserves incompatible estimands, and decides what remains uncertain. It may not manufacture a majority vote from correlated workers.

### Phase 4 — verification and finalization

The verifier checks paths, numbers, citations, reporting guidelines, output counts, and whether each final claim is supported by the evidence pack. The finalizer packages the primary Skill's deliverable and the SciXZ synthesis.

## Execution backends

- **Native multi-agent backend available:** dispatch independent workers in parallel, then invoke critic, consensus, and verifier in dependency order. Pass only the collaboration brief and artifacts required by each worker; do not pass hidden conversation history.
- **No native backend:** run the same roles as clearly separated sequential passes in one context. Label the output `simulated multi-agent mode`; never claim that independent agents ran in parallel.
- **External API worker:** use only when the user requests it or a configured Skill explicitly requires it. Never expose credentials in prompts or artifacts.

## Shared-state rules

- Workers read the immutable evidence pack and write only their assigned report.
- The coordinator owns the run manifest and task status.
- Consensus reads reports but does not edit worker reports.
- Verifier may append verification findings but cannot silently alter scientific results.
- User-facing output is written only after verification.
- Project memory is updated only with explicit user approval.

## Failure and retry

Retry a worker once when it fails because of a transient tool error, malformed output, or missing required field. On the second failure, mark the role `failed`, reduce the confidence of affected findings, and continue only if the remaining quorum is adequate. If a missing role is safety-critical or changes the estimand, stop and ask for the missing input.

A timed-out worker is not agreement and must remain visible in the run manifest and final uncertainty section.

## Quorum

- `panel`: coordinator + at least two completed independent roles + verifier.
- `council`: coordinator + at least three independent roles, including the domain owner and one methods/statistics or safety role, plus critic, consensus, and verifier.
- `recursive-review`: every round requires a reviewer report and verifier check; never report approval solely because the maximum round count was reached.
