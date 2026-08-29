# SciXZ — Scientific eXpert Zone

[简体中文](README.zh-CN.md)

SciXZ is a portable Codex Skill that coordinates medical-research workflows. It acts as a central controller: it normalizes the request, reviews the proposed route, selects the smallest sufficient set of Skills, and gates the final output with consensus and verification.

The controller uses a three-department gate—中书省 (draft), 门下省 (review), and 尚书省 (execute)—plus six execution ministries. This keeps planning, domain work, critique, consensus, and publication verification separate.

## What is included

- The portable `scixz` controller and its routing contracts.
- Collaboration, role, workflow, consensus, evaluation, and verification contracts.
- A deduplicated public bundle of 260 companion Skills under [`bundled-skills/`](bundled-skills/), including local-only Skills and public-source Skills that would otherwise be hard for another user to reconstruct from this machine.
- Portable runtime-binding examples; machine-specific paths and private state are intentionally excluded.
- A complete dependency and download guide for external services, proprietary readers, and source repositories: [`DOWNLOAD_GUIDE.md`](DOWNLOAD_GUIDE.md).

## Quick start

Install this repository as the `scixz` Skill, then invoke it with a coordinated research request:

```text
/scixz 审稿 manuscript.pdf
/scixz 设计 INSPIRE target-trial emulation
/scixz 分析 GEO 数据并设计验证方案
/scixz 选择适合的 SCI 期刊
/scixz 回复 reviewer comments
```

The entry point is [`SKILL.md`](SKILL.md). For complex requests, SciXZ creates independent evidence passes, a critic pass, a consensus decision, and a verification gate. If native sub-agents are unavailable, the same stages run as explicitly labelled sequential passes.

## Bundled versus external Skills

Companion Skills are placed under [`bundled-skills/`](bundled-skills/) so others can find and install them independently. This release now includes both local-only Skills and public-source Skills that were present in the local catalog. The bundle is deduplicated by Skill name and excludes virtual environments, dependency caches, browser state, credentials, manuscripts, datasets, and other private runtime artifacts.

Bundling does not relicense third-party components under the top-level MIT license. Inspect each component's own license files or source notes before redistributing it on its own. See [`BUNDLED_SKILLS.md`](BUNDLED_SKILLS.md) and the machine-readable [`registry/bundled_skill_manifest.json`](registry/bundled_skill_manifest.json). A readable full list is also available in [`BUNDLED_SKILL_MANIFEST.md`](BUNDLED_SKILL_MANIFEST.md).

Skills with an explicit proprietary license, such as the `anthropics-*` document readers, are not copied into this public repository. Install them from their authorized distribution when a route needs them. JANE, iPubMed, ShowJCR data, JCR MCP servers, Clarivate access, LetPub web pages, and EasyScholar API credentials are external sources/adapters, not secrets or services bundled into this repository.

## Dependency and download guide

### Included in this repository

The repository includes 260 top-level companion Skills under `bundled-skills/`. Install all of them with:

```text
python scripts/install_bundled_skills.py
```

Install or refresh selected Skills with:

```text
python scripts/install_bundled_skills.py find-journal sci-select --overwrite
```

If your runtime does not automatically discover nested packages, install the relevant subdirectory as an independent Skill.

### Verified public Skill repositories

The following public Skill repositories or public Skill directories were verified for this release and are now also bundled when present locally. The links are retained so users can inspect upstream history or install directly from the source:

| Use case | Skill | Repository |
|---|---|---|
| Manuscript peer review | `nature-review-studio` | [mumdark/nature-review-studio/skill](https://github.com/mumdark/nature-review-studio/tree/main/skill) |
| Manuscript peer review | `academic-paper-reviewer` | [bystander563/academic-paper-reviewer-portable](https://github.com/bystander563/academic-paper-reviewer-portable) (Codex-portable) or [fbdeme/academic-paper-reviewer](https://github.com/fbdeme/academic-paper-reviewer) |
| Reporting-guideline audit | `check-reporting` | [Aperivue/check-reporting/skills/check-reporting](https://github.com/Aperivue/check-reporting/tree/main/skills/check-reporting) |
| Reference authenticity audit | `verify-refs` | [Aperivue/verify-refs/skills/verify-refs](https://github.com/Aperivue/verify-refs/tree/main/skills/verify-refs) |
| Submission-readiness preflight | `sci-manuscript-preflight` | [VivalavidaLu/sci-manuscript-preflight](https://github.com/VivalavidaLu/sci-manuscript-preflight/tree/master) |
| Manuscript drafting or broad revision | `academic-paper` | [Imbad0202/academic-research-skills/academic-paper](https://github.com/Imbad0202/academic-research-skills/tree/main/academic-paper) |
| Literature retrieval/synthesis | `research-lit` | [wanshuiyin/Auto-claude-code-research-in-sleep/skills/research-lit](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/tree/main/skills/research-lit) |
| Literature retrieval/synthesis | `deep-research` | [Imbad0202/academic-research-skills/deep-research](https://github.com/Imbad0202/academic-research-skills/tree/main/deep-research) |
| Known-journal lookup | `sci-select` | [keros68/sci-select](https://github.com/keros68/sci-select) |

Public repositories and versions may change. For strict reproducibility, use the bundled copy from this repository; for updates, compare with the linked upstream before replacing a local Skill.

### Catalog-dependent route Skills

The following route names are available in the local Skill catalog, but this release does not assert an exact public GitHub Skill repository for them. Obtain the current version from the active catalog or your authorized distribution: `search-lit`, `pubmed-database`, `analyze-stats`, `make-figures`, `academic-python-plotting`, `clean-data`, `deidentify`, `generate-codebook`, `version-dataset`, `calc-sample-size`, `sync-submission`, `venue-templates`, `paper-audit`, `bulk-rnaseq`, and `scanpy`.

### Proprietary readers to obtain from an authorized source

For local Office files, install the reader matching the file type:

- `anthropics-docx` for DOCX/Word
- `anthropics-pdf` for PDF
- `anthropics-xlsx` for XLSX/CSV/tabular files
- `anthropics-pptx` for PowerPoint

These packages are not included because their source metadata marks them Proprietary. Do not mirror or redistribute them from this repository.

### External services, not downloadable Skills

The journal-selection and citation-management routes require auditable JANE and iPubMed evidence branches. They are external services/adapters, not files to copy into this repository. Configure them at runtime and do not send unpublished manuscripts, PHI, restricted data, credentials, or API keys by default.

### Installation patterns

For a public Skill repository, the generic `skills` installer supports:

```text
npx skills add <owner>/<repo> --list
npx skills add <owner>/<repo> --skill <skill-name> -g
```

For all bundled Skills:

```text
python scripts/install_bundled_skills.py
```

For one bundled Skill:

```text
npx skills add ./bundled-skills/find-journal --skill find-journal -g
```

For the recommended known-journal lookup stack:

```text
npx skills add keros68/sci-select --skill sci-select -g
git clone https://github.com/hitfyd/ShowJCR.git
git clone https://github.com/yosh3289/jcr_mcp.git
```

`ShowJCR` is a data/application repository rather than a Skill; `jcr_mcp` is an optional MCP server rather than a replacement for `sci-select`.

If the installer does not recognize a nested package, copy that package directory into the runtime's configured Skills directory and keep the directory name equal to the Skill name. Resolve the destination from your runtime configuration; do not hard-code another machine's absolute path.

### Minimal download sets by task

**Known-journal lookup (journal name → metrics card)**

Use [`sci-select`](https://github.com/keros68/sci-select) as the primary lookup Skill. Add the [`ShowJCR` data repository](https://github.com/hitfyd/ShowJCR) as the local/static source for JCR 2025, 2025 CAS, 2026 Emerging/New Journal data, and warning flags. Optionally enable the EasyScholar API adapter in `bundled-skills/find-journal/scripts/easyscholar_lookup.py` with the local `EASY_SCHOLAR_SECRET_KEY` environment variable to supplement `sciif`, JCR/CAS-upgraded, XinRui, and warning fields. If you want Codex to call the ShowJCR-style database as an MCP tool, use [`jcr_mcp`](https://github.com/yosh3289/jcr_mcp). LetPub review-speed text is obtained live by `sci-select`; use [`agent-browser`](https://github.com/vercel-labs/agent-browser) or `chrome:control-chrome` only as a browser fallback. Verify current JIF/JCR/coverage at Clarivate or institutional sources. Use bundled `find-journal` only when you also want scope fit and a ranked submission cascade; do not run [`journal-recommender`](https://github.com/zero565656/journal-recommender) and `sci-select` redundantly for an exact-name lookup.

Expected fields: canonical title/ISSN, IF/JIF and edition/year, JCR Q by category, 2025 CAS major/minor quartiles, 2026 Emerging/New Journal classification, LetPub review-speed text with URL/date, indexing, OA/APC, warning status, and `_source_status`. Missing or conflicting values must remain visible.

Run the repository smoke workflow with:

```text
python scripts/journal_lookup.py "Journal of Global Antimicrobial Resistance" --pretty
```

The runner loads the installed `sci-select`, uses the local index plus LetPub, and optionally merges EasyScholar when `EASY_SCHOLAR_SECRET_KEY` is configured. Without that variable it skips EasyScholar without sending a request and keeps the field status explicit.

Implementation note: `jcr_mcp` currently exposes a general journal-search/partition interface and does not replace the field-level provenance contract by itself. For separate JCR/CAS/XinRui columns, use `sci-select` with ShowJCR/CSV/SQLite data or extend the MCP response schema; LetPub review speed still requires a live page/browser check.

**Review and revise a DOCX manuscript**

`scixz` + bundled `deterministic-local-file-reading` + proprietary `anthropics-docx` + public `nature-review-studio` or `academic-paper-reviewer` + public `check-reporting` + bundled `revise` + bundled `manage-refs` or public `verify-refs`.

**Select a journal**

`scixz` + bundled `find-journal` + one manuscript-review/preflight Skill + the mandatory external JANE and iPubMed evidence branches.

**Perform a new statistical analysis**

`scixz` + catalog-provided `analyze-stats` + the relevant data-preparation and plotting Skills. Preserve analysis scripts, inputs, versions, and outputs in a private run directory.

**Work with GEO/RNA-seq or single-cell data**

Add the domain Skill for the requested analysis, such as `bulk-rnaseq` or `scanpy`, together with `clean-data`, `deidentify`, and `version-dataset` when the data-governance route requires them.

## Typical manuscript route

For review, revision, journal selection, and citation QC, the usual route is:

1. `deterministic-local-file-reading` plus the reader for the file type.
2. A public review Skill such as `nature-review-studio` or `academic-paper-reviewer`.
3. A public reporting/preflight Skill such as `check-reporting` or `sci-manuscript-preflight`.
4. The bundled local-only `revise` Skill for point-by-point responses.
5. The bundled local-only `manage-refs` Skill or public `verify-refs` after citation edits.
6. The bundled local-only `find-journal` Skill, with auditable JANE and iPubMed evidence branches.

See [`DEPENDENCIES.md`](DEPENDENCIES.md) for the compact route matrix. [`DOWNLOAD_GUIDE.md`](DOWNLOAD_GUIDE.md) is provided as a standalone copy of the same setup guidance for people who want an installation-only reference.

## Safety and public-release boundary

SciXZ supports research planning and evaluation, not autonomous patient care, diagnosis, prescribing, or ethics approval. Keep clinical outputs research-only unless a separate governance artifact is explicitly requested.

This release contains no manuscripts, patient-level data, extraction workbooks, private journal profiles, local audit logs, API keys, tokens, browser state, or machine-specific binding registries. Do not send unpublished manuscripts, PHI, restricted data, credentials, or API keys to external adapters by default.

## Design principles

- Reuse an existing Skill before adding an overlapping one.
- Keep independent evidence passes separate until consensus.
- Distinguish association, prediction, and causation.
- Make uncertainty, missing evidence, and route limitations visible.
- Archive rather than permanently delete during maintenance.

## License

The SciXZ controller and repository-authored documentation are released under the MIT License. Bundled companion Skills retain their own provenance and licensing notes recorded in [`BUNDLED_SKILLS.md`](BUNDLED_SKILLS.md) and [`BUNDLED_SKILL_MANIFEST.md`](BUNDLED_SKILL_MANIFEST.md); inspect those notes before redistributing a component on its own.
