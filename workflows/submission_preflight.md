# Submission-preflight workflow

## Entry and scope

Use when the user asks whether a manuscript is ready to submit or wants references, claims, figures, tables, AI-residue signals, source data, and reporting compliance checked together. It is a readiness gate, not an acceptance guarantee or misconduct verdict.

## Inputs

Require manuscript path/content, target journal, article type, language, and desired report. Source tables/assets, BibTeX/Zotero files, and supplements are optional but needed for their respective branches.

## Route

Controller → 户部 resolves and fingerprints inputs → 中书省 defines gate scope → 门下省 reviews evidence boundaries, external-tool privacy, and risks → `panel` or `council` when publication risk is consequential. Primary: `sci-manuscript-preflight`. When the reference-proofreading branch is requested, mandatory external tickets are `jane` and `ipubmed`; supporting canonical Skills are `paper-audit`, `verify-refs`, `check-reporting`, `scientific-writing`, `academic-expression-polisher`, and `bib-search-citation`. `paperconan` remains conditional on source data.

## Outputs

Blocker/high/moderate/minor issue list, reference/claim/figure/table consistency findings, reporting/ethics/data-availability gaps, target-journal readiness, source-data signals when applicable, and a submission decision with limitations.

## Verification

Check source paths, citations, claim support, numbering, statistics/reporting gaps, target-journal requirements, current policy facts, and whether every automated or external signal has a human-verification boundary. Do not call “no finding” proof of readiness. iPubMed title-level warnings must be reconciled with PubMed/CrossRef/retraction records before they affect the gate.

## Failure/fallback

If a preflight Skill, verifier, or mandatory external adapter is unavailable, report the missing capability and block the affected readiness decision. Do not label the manuscript submission-ready when source files, target-journal requirements, verification evidence, or either mandatory external run record is missing.

## Execution steps

1. Run the preflight owner.
2. Run only the citation, source-data, writing, and reporting branches justified by the input.
3. Send issues to formal review or revision workflow when requested.
4. Package the requested report; formal review uses `nature-review-studio` only when its DOCX/Markdown contract is requested.
