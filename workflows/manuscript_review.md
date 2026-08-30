# Manuscript-review workflow

## Entry and scope

Use for external peer review, editorial critique, referee reports, and publication-level assessment. Distinguish it from self-review, language polishing, reviewer response, and direct manuscript rewriting.

## Inputs

Require manuscript path or text, file type, study type if known, target journal if relevant, language, and desired artifact. Reviewer reports and source data are optional. Missing manuscript content is blocking. An optional PaperReview.ai branch additionally requires an English PDF and explicit current authorization for that exact external upload.

## Route

Controller → 中书省 identifies study type, main claim, contribution, and design ceiling → 门下省 checks privacy, ethics, causal framing, and output contract → `council` for publication-level review. After one deterministic intake freezes the manuscript fingerprint, start two independent branches in the same parallel wave. Branch A is the local primary chain: `nature-review-studio` for formal synchronized output or `academic-paper-reviewer` for analysis-only review, supported by `sci-manuscript-preflight`, `scientific-critical-thinking`, `check-reporting`, `peer-review`, `paperconan` when source data exist, and conditional statistics/design Skills. Branch B is the optional, explicitly authorized PaperReview upload/poll chain using `scripts/paperreview_automation.py` and `scripts/build_paperreview_synthesis_bundle.py`. Branch B may be slower and must never delay the start or alter the independent reasoning of Branch A.

Final synthesis is a barrier stage, not part of either branch. When both artifacts are complete and reference the same fingerprint, run `scripts/build_parallel_review_fusion_bundle.py` and dispatch a fresh synthesis sub-agent that did not participate in Branch A or B. Give it only the frozen manuscript and two completed branch artifacts. It must independently verify evidence, build an agreement/disagreement matrix, preserve dissent, disposition each external issue, and produce the final bilingual review contract.

## Outputs

Evidence-anchored overall assessment, major/minor concerns, editorial recommendation, cross-review consensus, uncertainty, and revision tasks. Any PaperReview.ai result is retained as an `external-signal` and converted into a separately labelled, evidence-anchored issue ledger with stable `PR-xx` identifiers. The final synthesis must record exactly one disposition for every external issue and include a cross-branch agreement/disagreement matrix. When bilingual Word output is requested, render the verified final-review JSON through `scripts/render_final_review_docx.py --fusion-bundle ...` as one Chinese and one English DOCX; strict mode blocks omitted, duplicated, or unknown external issue IDs. Formal `nature-review-studio` output is exactly one DOCX plus one same-stem Markdown file.

## Verification

Verify manuscript locations, numbers, statistical claims, reporting requirements, severity, output count, and internal consistency. For PaperReview.ai, check the frozen input fingerprint, submission date, result path, English-language boundary, 1–15 reviewed-page boundary, and substantive review-content fingerprint; independently verify every issue against the manuscript. Repeated results with the same content fingerprint count as one external signal. Preserve dissent and do not call a signal proof of misconduct.

## Failure/fallback

If the manuscript is unavailable, stop and request it. If formal rendering is unavailable, return an analysis-only review and state the missing artifact capability. If PaperReview.ai is unavailable or not authorized, skip it without blocking the primary review and do not claim two-branch fusion. If PaperReview was requested but remains pending, finish and freeze Branch A, wait only until the declared external-review deadline, and report the pending state. After timeout or provider failure, publish a clearly labelled local-primary review only if the user accepts that degraded mode; otherwise leave final synthesis blocked. A failed synthesis sub-agent is retried once; after a second failure, mark fusion failed and preserve both branch artifacts rather than silently merging them in the coordinator.

## Execution steps

1. Perform deterministic intake once and freeze an evidence manifest: the exact uploaded PDF fingerprint shared by both branches plus fingerprints for any companion tables, supplements, or data files. Record branch visibility for every item.
2. In parallel, run Branch A's independent methodology, statistics, clinical, reporting, reviewer, and editor perspectives and, when explicitly authorized, start Branch B's PaperReview upload/poll run in private local state.
3. Complete and freeze the local primary-review artifact without reading the PaperReview result. Polling continues independently within its bounded deadline.
4. Validate both branch artifacts and their identical uploaded-PDF fingerprints. If local review used companion evidence unavailable to PaperReview, mark branch scopes as non-identical and carry the frozen companion files into fresh synthesis; do not describe the evidence scopes as identical.
5. Build the strict fusion bundle and dispatch a fresh synthesis sub-agent with no hidden branch history. It compares both issue ledgers, independently checks the manuscript, resolves or preserves disagreements, and records every canonical `PR-xx` disposition exactly once.
6. Run Critic, Consensus/政事堂, and Verifier on the fused output, then write the bilingual final-review JSON and render the Chinese/English DOCX reports in strict fusion mode.
