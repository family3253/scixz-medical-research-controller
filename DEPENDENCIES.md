# SciXZ dependency and installation guide

## Principle

SciXZ owns routing, governance, collaboration, consensus, and verification contracts. Domain Skills remain separate packages so that each can be versioned, licensed, updated, or replaced independently.

Do not vendor every dependency into this repository by default. Vendoring creates duplicate copies, version drift, license ambiguity, and a larger risk of publishing private configuration. If a deployment needs a frozen bundle, create a separately reviewed release bundle with each dependency's license and source commit recorded.

## Required by route

| Route | Required local Skills | External adapters / notes |
|---|---|---|
| Core controller | `scixz` | Codex-compatible Skill runtime |
| Local file intake | `deterministic-local-file-reading` | Add the reader matching the file: `anthropics-docx`, `anthropics-pdf`, `anthropics-xlsx`, or `anthropics-pptx` |
| Manuscript review | `nature-review-studio` **or** `academic-paper-reviewer` | `check-reporting` for reporting-guideline audit; `scientific-critical-thinking` or `peer-review` as an independent perspective |
| Revision after review | `revise` **or** `academic-paper` | Add `analyze-stats`/`make-figures` only when a new analysis/figure is required; add `verify-refs` after citation edits |
| Journal selection | `find-journal` | JANE **and** iPubMed are mandatory evidence branches; verify current journal policy at the journal site |
| Citation management | `verify-refs` or `manage-refs` | JANE **and** iPubMed are mandatory discovery/triage branches; canonical verification remains local/authoritative |
| Literature synthesis | `research-lit` or `deep-research` | Add `pubmed-database` or `search-lit` when direct bibliographic retrieval is needed |
| Statistical analysis | `analyze-stats` | Use the relevant R/Python runtime and preserve analysis scripts plus outputs |
| Data preparation | `clean-data`, `deidentify`, `generate-codebook` | Add `version-dataset` for deterministic dataset manifests |
| Sample-size planning | `calc-sample-size` | Record assumptions and reproducible calculations |
| Submission preflight | `sci-manuscript-preflight` | Optional `paper-audit`, `verify-refs`, `check-reporting`, `sync-submission`, `venue-templates` |

## Common document runtimes

- DOCX: Pandoc or a compatible Word-processing runtime; use `anthropics-docx`.
- PDF: `pypdf`/`pdfplumber`/Poppler as appropriate; use `anthropics-pdf`.
- XLSX: `openpyxl`/`pandas` plus LibreOffice for formula recalculation; use `anthropics-xlsx`.
- Figures: the route-specific plotting/figure Skill and its declared Python/R packages.

Runtime availability is separate from Skill availability. A Skill may be installed while its optional executable or package runtime still needs setup.

## External adapter policy

For journal-selection and citation-management routes, SciXZ requires auditable JANE and iPubMed run records before publishing a final ranking or citation-proofreading conclusion. Treat their output as an external signal only. Do not send full unpublished manuscripts, peer-review files, PHI, restricted data, credentials, or API keys by default.

## What is intentionally not included

- User-specific `memory/` and project notes
- Local audit logs and run manifests containing machine paths
- Private journal profiles and confidential editorial overlays
- Absolute-path binding registries generated on one machine
- Manuscripts, patient-level data, extraction workbooks, API keys, tokens, and browser state

## Suggested setup order

1. Install SciXZ and confirm that `SKILL.md` is discoverable.
2. Install the one route owner Skill required by the task.
3. Install only the supporting Skills named by the approved route.
4. Check optional runtimes (Word/PDF/XLSX/R/Python) before execution.
5. Run a read-only health check and record versions in a local, non-public run manifest.

Never copy absolute machine paths from a local registry into a public repository. Resolve them at runtime or keep them in a private machine-local file.
