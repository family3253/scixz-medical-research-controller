# Revision-after-review workflow

## Entry and scope

Use when reviewer/editor comments require actual manuscript changes, new analyses, new figures, revised references, or a resubmission package. It is the executable change workflow behind a response letter.

## Inputs

Require editor decision and comments, current manuscript, revision round, target journal, language, and optional data/code/figures/supplements. Missing manuscript or comments is blocking; missing source data blocks only the affected ticket.

## Route

Controller → 中书省 creates the comment ledger and revision plan → 门下省 checks scientific justification, scope, privacy, argument depth, citation allocation, and external-tool authorization → `recursive-review` with bounded tickets. Primary: `academic-paper` or `revise`. Supporting: `reviewer-response-assistant`, `scientific-writing`, `research-lit`/`deep-research` when the revision needs new evidence, optional external adapters `jane`/`ipubmed` for candidate discovery or citation triage, optional authorized `paperreview-ai` for a post-revision supplementary critique, `bib-search-citation`/`manage-refs`, `analyze-stats`, `make-figures`, `verify-refs`, and `check-reporting`. If the introduction or discussion is rewritten, require a section brief and an introduction/discussion citation-overlap report.

## Outputs

Revised manuscript or tracked revision, point-by-point response, revision ledger mapping comments to changes and locations, section-depth briefs, citation allocation/overlap report when relevant, external-tool run records when used, validation summary, and unresolved issues. If `nature-review-studio.respond` is primary, preserve its locked DOCX + same-stem Markdown contract.

## Verification

Freeze the original, fingerprint the input, confirm every accepted comment has a real change, verify defended comments, rerun new analyses/figures/references, verify any JANE/iPubMed candidate through canonical sources before adding it, check cross-section consistency, confirm the introduction ends in a precise gap/objective, confirm the discussion adds evidence-based interpretation rather than repetition, audit introduction/discussion citation overlap and reuse reasons, and fill exact locations only from the final artifact. Re-review unresolved major issues.

## Failure/fallback

If the current manuscript, comments, or required data are missing, stop before claiming a revision. If an analysis Skill is unavailable, record a blocked ticket and offer a verified fallback with reduced confidence. If a location cannot be verified, leave it unresolved. A PaperReview.ai re-review is optional and requires separate current authorization; never auto-upload the revised manuscript or represent its external signal as confirmation that revisions are sufficient.

## Execution steps

1. Parse comments into `E-1`, `R1-1`, `R2-1` atomic IDs.
2. Assign stance, severity, action, evidence, owner, and acceptance criteria.
3. Execute revision tickets in a separate workspace while preserving the original.
4. Verify, generate the response package, and run recursive re-review.
