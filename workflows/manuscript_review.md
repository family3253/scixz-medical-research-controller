# Manuscript-review workflow

## Entry and scope

Use for external peer review, editorial critique, referee reports, and publication-level assessment. Distinguish it from self-review, language polishing, reviewer response, and direct manuscript rewriting.

## Inputs

Require manuscript path or text, file type, study type if known, target journal if relevant, language, and desired artifact. Reviewer reports and source data are optional. Missing manuscript content is blocking. An optional PaperReview.ai branch additionally requires an English PDF and explicit current authorization for that exact external upload.

## Route

Controller → 中书省 identifies study type, main claim, contribution, and design ceiling → 门下省 checks privacy, ethics, causal framing, and output contract → `council` for publication-level review. Primary: `nature-review-studio` for formal synchronized output or `academic-paper-reviewer` for analysis-only review. Supporting: `sci-manuscript-preflight`, `scientific-critical-thinking`, `check-reporting`, `peer-review`, `paperconan` when source data exist, and conditional statistics/design Skills. If explicitly authorized, add `paperreview-ai` as a non-automated browser-upload supplementary critique branch after local intake; use `scripts/paperreview_adapter.py` to prepare and validate its local run record.

## Outputs

Evidence-anchored overall assessment, major/minor concerns, editorial recommendation, cross-review consensus, uncertainty, and revision tasks. Any PaperReview.ai result is retained as an `external-signal` and converted into a separately labelled, evidence-anchored issue ledger. Formal `nature-review-studio` output is exactly one DOCX plus one same-stem Markdown file.

## Verification

Verify manuscript locations, numbers, statistical claims, reporting requirements, severity, output count, and internal consistency. For PaperReview.ai, check the frozen input fingerprint, submission date, result path, English-language boundary, and 1–15 reviewed-page boundary; independently verify every issue against the manuscript. Preserve dissent and do not call a signal proof of misconduct.

## Failure/fallback

If the manuscript is unavailable, stop and request it. If formal rendering is unavailable, return an analysis-only review and state the missing artifact capability. If PaperReview.ai is unavailable or not authorized, skip it without blocking the primary review. If an optional Skill is unavailable, use an approved fallback with reduced confidence and record the limitation.

## Execution steps

1. Perform deterministic intake and freeze the evidence pack.
2. Run independent methodology, statistics, clinical, reviewer, and editor perspectives as justified.
3. Run Critic, Consensus/政事堂, and Verifier in dependency order.
4. Hand off to the selected formal review owner only after verification.
5. Only after explicit authorization, prepare the optional PaperReview.ai browser-upload manifest. Do not auto-upload, collect an email, or let the resulting signal replace the primary review.
