# SciXZ dependency and installation guide

## Principle

SciXZ owns routing, governance, collaboration, consensus, and verification contracts. Domain Skills remain separate packages so that each can be versioned, licensed, updated, or replaced independently. This repository now includes 264 deduplicated top-level companion Skills under `bundled-skills/`, including local-only components and public-source Skills present in the local catalog.

The bundle is a portability snapshot. It excludes explicit Proprietary packages, system/plugin-cache copies, virtual environments, dependency caches, credentials, manuscripts, datasets, browser state, and machine-local runtime records. Bundled third-party Skills keep their own license status; the top-level MIT license does not automatically relicense them.

## Required by route

| Route | Built into this repository | Download separately | External adapters / notes |
|---|---|---|---|
| Core controller | `scixz` | — | Codex-compatible Skill runtime |
| Known-journal lookup | `sci-select` when installed from the bundle; run `python scripts/refresh_journal_index.py` once for automatic JCR Q | [`sci-select`](https://github.com/keros68/sci-select) for upstream updates | The refresh script downloads [`ShowJCR`](https://github.com/hitfyd/ShowJCR) public CSV snapshots (2026 JCR release / 2025 JIF-JCR / 2025 CAS / 2026 XinRui) into a user cache and builds a local index; optionally use the EasyScholar adapter with `EASY_SCHOLAR_SECRET_KEY`, or expose ShowJCR through [`jcr_mcp`](https://github.com/yosh3289/jcr_mcp); LetPub review speed is a live/browser field |
| Local file intake | `deterministic-local-file-reading` | — | Add the reader matching the file: `anthropics-docx`, `anthropics-pdf`, `anthropics-xlsx`, or `anthropics-pptx` |
| Prompt/repository/n8n capability absorption | `skill-creator`, `n8n-to-skill` | — | Static inspection by default; preserve provenance/license, never copy credentials or execute workflow nodes during conversion |
| Image/report OCR to auditable table | `image-to-table-qa` after a verified OCR reader | OCR runtime/Skill appropriate to the source | Keep source ID, units, flags, confidence/review state, schema QA, and privacy authorization |
| Manuscript review | Bundled public/local review Skills when available | [`nature-review-studio`](https://github.com/mumdark/nature-review-studio/tree/main/skill) **or** [`academic-paper-reviewer`](https://github.com/bystander563/academic-paper-reviewer-portable); [`check-reporting`](https://github.com/Aperivue/check-reporting/tree/main/skills/check-reporting) for upstream updates | Use the bundled snapshot for reproducibility; compare upstream before upgrading |
| Revision after review | `revise`, `academic-paper`, `verify-refs`, and many supporting writing Skills when installed from the bundle | Upstream public repositories for updates | Add `analyze-stats`/`make-figures` only when a new analysis/figure is required |
| Journal selection | `find-journal` | — | JANE **and** iPubMed are mandatory evidence branches; verify current journal policy at the journal site |
| Citation management | `manage-refs` and `verify-refs` when installed from the bundle | [`verify-refs`](https://github.com/Aperivue/verify-refs/tree/main/skills/verify-refs) for upstream updates | JANE **and** iPubMed are mandatory discovery/triage branches; canonical verification remains local/authoritative |
| Literature synthesis | Bundled literature Skills when available | [`research-lit`](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/tree/main/skills/research-lit) or [`deep-research`](https://github.com/Imbad0202/academic-research-skills/tree/main/deep-research) for upstream updates | Add `pubmed-database` or `search-lit` when direct retrieval is needed |
| Statistical analysis | Bundled analysis Skills when available | Catalog/upstream versions for updates | Use the relevant R/Python runtime and preserve analysis scripts plus outputs |
| Data preparation | Bundled data-governance Skills when available | Catalog/upstream versions for updates | Add `version-dataset` for deterministic manifests |
| Sample-size planning | `calc-sample-size` when installed from the bundle | Catalog/upstream versions for updates | Record assumptions and reproducible calculations |
| Submission preflight | Bundled preflight/reporting Skills when available | [`sci-manuscript-preflight`](https://github.com/VivalavidaLu/sci-manuscript-preflight/tree/master), [`verify-refs`](https://github.com/Aperivue/verify-refs/tree/main/skills/verify-refs), and [`check-reporting`](https://github.com/Aperivue/check-reporting/tree/main/skills/check-reporting) for upstream updates | — |

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
2. Install bundled companion Skills with `python scripts/install_bundled_skills.py`, or install only the route owner Skill required by the task.
3. Install external services, proprietary readers, data repositories, or upstream updates only when the approved route needs them.
4. Check optional runtimes (Word/PDF/XLSX/R/Python) before execution.
5. Run a read-only health check and record versions in a local, non-public run manifest.

Never copy absolute machine paths from a local registry into a public repository. Resolve them at runtime or keep them in a private machine-local file.
