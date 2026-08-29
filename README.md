# SciXZ — Scientific eXpert Zone

[简体中文](README.zh-CN.md)

SciXZ is a portable Codex Skill that coordinates medical-research workflows. It acts as a central controller: it normalizes the request, reviews the proposed route, selects the smallest sufficient set of Skills, and gates the final output with consensus and verification.

The controller uses a three-department gate—中书省 (draft), 门下省 (review), and 尚书省 (execute)—plus six execution ministries. This keeps planning, domain work, critique, consensus, and publication verification separate.

## What is included

- The portable `scixz` controller and its routing contracts.
- Collaboration, role, workflow, consensus, evaluation, and verification contracts.
- The local-only companion Skills that are otherwise difficult to discover: `revise`, `find-journal`, `deterministic-local-file-reading`, and `manage-refs`. See [`BUNDLED_SKILLS.md`](BUNDLED_SKILLS.md).
- Portable runtime-binding examples; machine-specific paths and private state are intentionally excluded.
- A complete download matrix for Skills that users must obtain separately: [`DOWNLOAD_GUIDE.md`](DOWNLOAD_GUIDE.md).

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

The local-only companion Skills are placed under [`bundled-skills/`](bundled-skills/) so others can find and install them independently. They are not silently relicensed by the top-level MIT license; see the per-component notes in [`BUNDLED_SKILLS.md`](BUNDLED_SKILLS.md).

Skills that already have public GitHub sources are referenced but not duplicated. Skills with an explicit proprietary license, such as the `anthropics-*` document readers, are not copied into this public repository. Install them from their authoritative distribution when a route needs them. JANE and iPubMed are external evidence adapters, not bundled Skills.

## Dependency and download guide

### Included in this repository

These local-only companion Skills are already included under `bundled-skills/`:

- `revise`
- `find-journal`
- `deterministic-local-file-reading`
- `manage-refs`

No additional download is needed for these four. If your runtime does not automatically discover nested packages, install each subdirectory as an independent Skill.

### Public Skills to download separately

These Skills already have discoverable public sources and are intentionally not duplicated here:

| Use case | Download separately |
|---|---|
| Manuscript peer review | `nature-review-studio` or `academic-paper-reviewer` |
| Reporting-guideline audit | `check-reporting` |
| Reference authenticity audit | `verify-refs` |
| Submission-readiness preflight | `sci-manuscript-preflight` |
| Manuscript drafting or broad revision | `academic-paper` |
| Literature retrieval/synthesis | `research-lit`, `deep-research`, `search-lit`, or `pubmed-database` |
| Statistical analysis | `analyze-stats` |
| Figures and tables | `make-figures`, `academic-python-plotting`, or the plotting Skill required by the analysis |
| Data cleaning and provenance | `clean-data`, `deidentify`, `generate-codebook`, and optionally `version-dataset` |
| Sample-size planning | `calc-sample-size` |
| Submission packaging | `sync-submission`, `venue-templates`, and optionally `paper-audit` |

Public repositories and versions may change. Use the Skill catalog or the source repository's release instructions rather than copying an unpinned local cache.

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

For a Skill bundled in this repository:

```text
npx skills add ./bundled-skills/revise --skill revise -g
npx skills add ./bundled-skills/find-journal --skill find-journal -g
npx skills add ./bundled-skills/deterministic-local-file-reading --skill deterministic-local-file-reading -g
npx skills add ./bundled-skills/manage-refs --skill manage-refs -g
```

If the installer does not recognize a nested package, copy that package directory into the runtime's configured Skills directory and keep the directory name equal to the Skill name. Resolve the destination from your runtime configuration; do not hard-code another machine's absolute path.

### Minimal download sets by task

**Review and revise a DOCX manuscript**

`scixz` + bundled `deterministic-local-file-reading` + proprietary `anthropics-docx` + public `nature-review-studio` or `academic-paper-reviewer` + public `check-reporting` + bundled `revise` + bundled `manage-refs` or public `verify-refs`.

**Select a journal**

`scixz` + bundled `find-journal` + one manuscript-review/preflight Skill + the mandatory external JANE and iPubMed evidence branches.

**Perform a new statistical analysis**

`scixz` + public `analyze-stats` + the relevant data-preparation and plotting Skills. Preserve analysis scripts, inputs, versions, and outputs in a private run directory.

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

The SciXZ controller and repository-authored documentation are released under the MIT License. Bundled companion Skills retain the provenance and licensing notes recorded in [`BUNDLED_SKILLS.md`](BUNDLED_SKILLS.md); inspect those notes before redistributing a component on its own.
