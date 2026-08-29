# SciXZ dependency and installation guide

## Principle

SciXZ owns routing, governance, collaboration, consensus, and verification contracts. Domain Skills remain separate packages so that each can be versioned, licensed, updated, or replaced independently. This repository includes only four local-only companion Skills under `bundled-skills/`; Skills that already have discoverable public sources are referenced rather than duplicated.

Do not vendor every dependency into this repository by default. Vendoring creates duplicate copies, version drift, license ambiguity, and a larger risk of publishing private configuration. If a deployment needs a frozen bundle, create a separately reviewed release bundle with each dependency's license and source commit recorded.

## Required by route

| Route | Built into this repository | Download separately | External adapters / notes |
|---|---|---|---|
| Core controller | `scixz` | — | Codex-compatible Skill runtime |
| Known-journal lookup | — | [`sci-select`](https://github.com/keros68/sci-select) | Add [`ShowJCR`](https://github.com/hitfyd/ShowJCR) as the JCR/CAS/XinRui data source, optionally use the EasyScholar adapter with `EASY_SCHOLAR_SECRET_KEY`, or expose ShowJCR through [`jcr_mcp`](https://github.com/yosh3289/jcr_mcp); LetPub review speed is a live/browser field |
| Local file intake | `deterministic-local-file-reading` | — | Add the reader matching the file: `anthropics-docx`, `anthropics-pdf`, `anthropics-xlsx`, or `anthropics-pptx` |
| Manuscript review | — | [`nature-review-studio`](https://github.com/mumdark/nature-review-studio/tree/main/skill) **or** [`academic-paper-reviewer`](https://github.com/bystander563/academic-paper-reviewer-portable); [`check-reporting`](https://github.com/Aperivue/check-reporting/tree/main/skills/check-reporting) for guideline audit; `scientific-critical-thinking` or `peer-review` for an independent perspective | Use the public source/catalog version |
| Revision after review | `revise` | [`academic-paper`](https://github.com/Imbad0202/academic-research-skills/tree/main/academic-paper); add `analyze-stats`/`make-figures` only when a new analysis/figure is required; add [`verify-refs`](https://github.com/Aperivue/verify-refs/tree/main/skills/verify-refs) after citation edits | — |
| Journal selection | `find-journal` | — | JANE **and** iPubMed are mandatory evidence branches; verify current journal policy at the journal site |
| Citation management | `manage-refs` | [`verify-refs`](https://github.com/Aperivue/verify-refs/tree/main/skills/verify-refs) if preferred | JANE **and** iPubMed are mandatory discovery/triage branches; canonical verification remains local/authoritative |
| Literature synthesis | — | [`research-lit`](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/tree/main/skills/research-lit) or [`deep-research`](https://github.com/Imbad0202/academic-research-skills/tree/main/deep-research); add `pubmed-database` or `search-lit` when direct retrieval is needed | — |
| Statistical analysis | — | `analyze-stats` | Use the relevant R/Python runtime and preserve analysis scripts plus outputs |
| Data preparation | — | `clean-data`, `deidentify`, `generate-codebook`; add `version-dataset` for deterministic manifests | — |
| Sample-size planning | — | `calc-sample-size` | Record assumptions and reproducible calculations |
| Submission preflight | — | [`sci-manuscript-preflight`](https://github.com/VivalavidaLu/sci-manuscript-preflight/tree/master); optional `paper-audit`, [`verify-refs`](https://github.com/Aperivue/verify-refs/tree/main/skills/verify-refs), [`check-reporting`](https://github.com/Aperivue/check-reporting/tree/main/skills/check-reporting), `sync-submission`, `venue-templates` | — |

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
2. Install the one route owner Skill required by the task; use `bundled-skills/` for the local-only companions in this repository.
3. Install only the supporting Skills named by the approved route; use the public source or local catalog for public companions.
4. Check optional runtimes (Word/PDF/XLSX/R/Python) before execution.
5. Run a read-only health check and record versions in a local, non-public run manifest.

Never copy absolute machine paths from a local registry into a public repository. Resolve them at runtime or keep them in a private machine-local file.
