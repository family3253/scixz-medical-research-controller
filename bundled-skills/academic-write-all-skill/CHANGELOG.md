# Changelog

All notable changes to this repository are documented in this file.

## 2026-03-18

### Added
- published `academic-write-all-skill` to GitHub as a standalone repository
- added `evals/evals.json` with live routing and adversarial fallback regression prompts
- added prediction-model review/appraisal support and dedicated evidence-matrix and appraisal-checklist templates
- added a detailed `README.md` covering:
  - repository purpose
  - capability areas
  - repository layout
  - installation paths
  - CLI usage
  - testing guidance
  - known limitations
- added `scripts/smoke_test.py` for repeatable repository-level smoke checks
- added guarded self-update / capability-gap handling to the core skill design

### Changed
- renamed the public skill identity to `academic-write-all-skill`
- expanded `SKILL.md` routing to include stronger paper-production and review-project distinctions
- absorbed selected research-lifecycle patterns from the legacy `family3253/academic-write` repository
- added research-lifecycle routing for idea discovery, novelty checks, literature-to-gap narrowing, and experiment-to-writing handoff
- made prediction-model appraisal more native with TRIPOD-like / PROBAST-like / CHARMS-like built-in working structure while syncing TRIPOD+AI and PROBAST+AI as explicit external standards
- documented one-command installation for OpenCode and OpenClaw
- added self-update routing that prefers local skills first and external GitHub learning second
- added `paper-production family` routing language
- added local course-library absorption routing so paired teaching PDFs and reusable code folders can be treated as a method library during writing, workflow migration, and statistics-to-prose tasks
- simplified that routing so relevant statistics/modeling knowledge points now trigger proactive local-course lookup without requiring the user to explicitly name the folder paths
- added paper submodes including:
  - `outline-only`
  - `abstract-only`
  - `citation-check`
  - `format-convert`
  - `revision-coach`
- added review-project output-level gating to distinguish:
  - `submission-grade review draft`
  - `review-grade evidence synthesis`
  - `evidence map / scoping output`
  - `framework memo / review outline`

### Updated references
- `references/literature-search-and-screening.md`
- `references/section-workflows.md`
- `references/review-routing-and-gates.md`
- `references/review-and-submission.md`
- `references/prediction-model-review.md`
- `references/local-course-asset-bridge.md`

### Verification
- repository-level smoke checks were rerun successfully for:
  - Python script compilation
  - CLI help output
  - project scaffold initialization
  - project status inspection
  - gate report generation

### Notes
- harness-level live skill-routing regression was retried separately through an alternate agent path and produced successful route-specific outputs for:
  - outline-only behavior
  - revision-coach behavior
  - review-output downgrading behavior
