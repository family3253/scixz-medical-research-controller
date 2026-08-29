# Manuscript-review workflow

## Entry and scope

Use for external peer review, editorial critique, referee reports, and publication-level assessment. Distinguish it from self-review, language polishing, reviewer response, and direct manuscript rewriting.

## Inputs

Require manuscript path or text, file type, study type if known, target journal if relevant, language, and desired artifact. Reviewer reports and source data are optional. Missing manuscript content is blocking.

## Route

Controller → 中书省 identifies study type, main claim, contribution, and design ceiling → 门下省 checks privacy, ethics, causal framing, and output contract → `council` for publication-level review. Primary: `nature-review-studio` for formal synchronized output or `academic-paper-reviewer` for analysis-only review. Supporting: `sci-manuscript-preflight`, `scientific-critical-thinking`, `check-reporting`, `peer-review`, `paperconan` when source data exist, and conditional statistics/design Skills.

## Outputs

Evidence-anchored overall assessment, major/minor concerns, editorial recommendation, cross-review consensus, uncertainty, and revision tasks. Formal `nature-review-studio` output is exactly one DOCX plus one same-stem Markdown file.

## Verification

Verify manuscript locations, numbers, statistical claims, reporting requirements, severity, output count, and internal consistency. Preserve dissent and do not call a signal proof of misconduct.

## Failure/fallback

If the manuscript is unavailable, stop and request it. If formal rendering is unavailable, return an analysis-only review and state the missing artifact capability. If an optional Skill is unavailable, use an approved fallback with reduced confidence and record the limitation.

## Execution steps

1. Perform deterministic intake and freeze the evidence pack.
2. Run independent methodology, statistics, clinical, reviewer, and editor perspectives as justified.
3. Run Critic, Consensus/政事堂, and Verifier in dependency order.
4. Hand off to the selected formal review owner only after verification.
