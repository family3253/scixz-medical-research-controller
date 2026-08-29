# Reviewer-response workflow

## Entry and scope

Use when editor/reviewer comments must become a response letter, rebuttal, or revision plan. Actual manuscript revision is handled by `revision_after_review.md`, but this workflow can be called as its response-package stage.

## Inputs

Require editor decision, reviewer comments, current manuscript or intended revision scope, revision round, target journal, language, and desired output. Missing comments is blocking; missing final page/line locations is allowed until verification.

## Route

Controller → 中书省 decomposes comments → 门下省 checks stance, evidence, scope, and tone → `panel` or `recursive-review` when a revised manuscript is available. Primary: `reviewer-response-assistant`; formal output: `nature-review-studio.respond`. Supporting: `academic-paper`, `scientific-writing`, `verify-refs`, `check-reporting`, `analyze-stats`, and `make-figures` for linked revision tickets.

## Outputs

Atomic comment ledger, accept/partial-accept/defend stance, point-by-point response, evidence-linked revision plan, exact locations after verification, and remaining unresolved items. Formal Nature output is one DOCX plus one same-stem Markdown file.

## Verification

Every response maps to a real manuscript change or an evidence-based defense. Verify page/line/figure/table locations against the final revised artifact. Never claim a revision that was not made.

## Failure/fallback

If the revised manuscript is not yet available, preserve explicit location placeholders and mark the response as draft. If a requested new analysis cannot run, state the blocked ticket and do not write “as requested” language.

## Execution steps

1. Parse and number editor/reviewer comments.
2. Classify severity, stance, required action, owner, and evidence.
3. Build the revision ledger or hand off to `revision_after_review`.
4. Draft the response only after action status is known.
