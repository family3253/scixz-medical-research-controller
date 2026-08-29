# SCI Manuscript Preflight Skill

[简体中文](README.zh-CN.md)

A portable agent skill / instruction pack for pre-submission and revision-stage quality control of SCI, biomedical, and bioinformatics manuscripts.

Current release: `v0.2.2`.

It is modeled after the idea of an arXiv-style preflight check, but adapted for journal manuscripts: AI residue scanning, reference authenticity checks, claim-to-citation review, figure/table consistency, figure/source-data/statistical integrity, deterministic table-source-data gating, reporting-guideline readiness, and submission-risk review.

## What it checks

- AI drafting residue, retained agent instructions, placeholders, Markdown/LaTeX remnants, and unresolved notes.
- Hallucinated, fabricated, unresolved, duplicated, or mismatched references, including DOI/PMID/title/author/year inconsistencies.
- Overstated claims, unsupported claims, and clinical or mechanistic claims that exceed the cited evidence.
- Figure, table, supplementary-material, caption, abbreviation, statistical-annotation, and numbering consistency.
- Figure, source-data, and statistical integrity risks, including duplicated-looking panels, source-data gaps, quantification mismatches, and methods-results-figure contradictions.
- Deterministic table signals, parse coverage, source-file hashes, false-positive explanations, independent recalculation, and submission release gating.
- Methods, statistics, ethics, data availability, code availability, reporting-guideline gaps, and target-journal readiness.

## Design Inspiration

Version `v0.2.0` adapted figure-provenance, image-assembly, statistical-consistency, and methods-contradiction checks from [wooly99/geng-academic-fraud-detector](https://github.com/wooly99/geng-academic-fraud-detector) into non-accusatory author-side quality control.

Version `v0.2.2` learned from [zixixr/paperconan](https://github.com/zixixr/paperconan): deterministic numerical signals, explicit parse failures, localized evidence, false-positive profiles, separate review/impact dimensions, and adversarial review. The local wrapper validates compatible `0.8.x` output and reconciles expected files with scanner-reported files and Sheets. No paperconan source code is copied; it remains an external dependency under its own license and release cycle.

## Repository Contents

- `SKILL.md` - main skill instructions
- `scripts/preflight_static_scan.py` - static scan for AI residue, placeholders, Markdown/LaTeX remnants, and high-risk submission wording
- `scripts/reference_audit.py` - DOI resolution plus title/first-author/year/journal metadata comparison
- `scripts/table_integrity_gate.py` - source manifest, paperconan invocation/interpretation, and conservative release-gate outputs
- `references/checklist.md` - manual pre-submission checklist
- `references/table_source_data_gate.md` - detailed table/source-data gate, false-positive review, reconciliation, and release criteria
- `templates/preflight_report.md` - structured preflight report template
- `examples/example-preflight-report.md` - example submission-QC report
- `tests/` - offline regression tests for the static scanner, reference audit, and table gate

## Download

Clone the repository:

```bash
git clone https://github.com/VivalavidaLu/sci-manuscript-preflight.git
cd sci-manuscript-preflight
```

Or download the ZIP from GitHub:

1. Open <https://github.com/VivalavidaLu/sci-manuscript-preflight>
2. Click **Code**
3. Click **Download ZIP**
4. Extract the folder

Keep the full folder. This skill is not only `SKILL.md`; it also depends on `scripts/`, `references/`, `templates/`, and `examples/`.

## Installation

This repository is a portable agent skill. It can be used in Claude Code, Codex, Antigravity, Cursor, GitHub Copilot, Trae, or any agent that can read local instruction files.

### Claude Code

Global install:

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/VivalavidaLu/sci-manuscript-preflight.git ~/.claude/skills/sci-manuscript-preflight
```

Project install:

```bash
mkdir -p .claude/skills
git clone https://github.com/VivalavidaLu/sci-manuscript-preflight.git .claude/skills/sci-manuscript-preflight
```

Then ask Claude Code:

```text
Use the sci-manuscript-preflight skill to check this manuscript folder before submission.
```

### Codex

Global install:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/VivalavidaLu/sci-manuscript-preflight.git ~/.codex/skills/sci-manuscript-preflight
```

Then ask Codex:

```text
Use the sci-manuscript-preflight skill to check this manuscript folder for AI residue, reference problems, claim-citation mismatch, figure/data/statistical integrity issues, and submission risks.
```

### Antigravity

Use this repository as a local instruction/skill folder. Clone it into a stable workspace path and reference `SKILL.md` in the agent instructions.

```bash
git clone https://github.com/VivalavidaLu/sci-manuscript-preflight.git tools/sci-manuscript-preflight
```

Recommended instruction:

```text
When I ask for manuscript preflight, follow tools/sci-manuscript-preflight/SKILL.md and use its scripts, references, templates, and examples when relevant.
```

### Cursor

Clone the repository into a project:

```bash
git clone https://github.com/VivalavidaLu/sci-manuscript-preflight.git .cursor/skills/sci-manuscript-preflight
```

Then add a project rule or instruction:

```text
For manuscript pre-submission checks, follow .cursor/skills/sci-manuscript-preflight/SKILL.md. Treat the whole folder as the skill package.
```

### GitHub Copilot

Clone the repository into a project or shared local tools folder:

```bash
git clone https://github.com/VivalavidaLu/sci-manuscript-preflight.git .github/copilot/skills/sci-manuscript-preflight
```

Then reference it in Copilot instructions:

```text
For SCI/biomedical manuscript preflight tasks, follow .github/copilot/skills/sci-manuscript-preflight/SKILL.md and use the included scripts and templates when applicable.
```

### Trae

Clone the repository into a project:

```bash
git clone https://github.com/VivalavidaLu/sci-manuscript-preflight.git .trae/skills/sci-manuscript-preflight
```

Then add a Trae project rule or agent instruction:

```text
When reviewing a manuscript for submission readiness, follow .trae/skills/sci-manuscript-preflight/SKILL.md and keep the report structured by severity.
```

## Basic Use

Ask your agent:

```text
Use the sci-manuscript-preflight skill to check this manuscript folder for AI residue, hallucinated references, claim-citation mismatch, figure/table numbering issues, figure/data/statistical integrity issues, and SCI submission risks.
```

Recommended inputs:

- Main manuscript: `.docx`, `.pdf`, `.tex`, or `.md`
- Reference file: `.bib`, `.ris`, `.nbib`, `.xml`, `.enl`, or `.txt`
- Figure, source-data, and supplementary-material folders
- Cover letter
- Target journal instructions
- Reviewer checklist or response-to-reviewers draft

If only one file is provided, the agent should perform the feasible partial preflight and explicitly list missing inputs.

## Compatibility and Dependencies

- Python `3.10`–`3.12` is tested in CI.
- The static scanner uses only the Python standard library. `.docx` extraction optionally uses `python-docx>=1.1`; PDF extraction optionally uses `PyMuPDF>=1.24`.
- The reference audit requires network access to Crossref for live DOI metadata; offline unit tests use fixed synthetic metadata.
- The table gate supports `paperconan[all]>=0.8,<0.9`. A schema or version mismatch blocks interpretation until compatibility is reviewed.

The repository does not install dependencies automatically. Obtain approval before modifying a shared Python environment.

## Helper Scripts

Static residue scan:

```bash
python scripts/preflight_static_scan.py path/to/manuscript_folder --out static_scan.tsv
```

DOI/Crossref reference audit:

```bash
python scripts/reference_audit.py path/to/references.bib --out reference_audit.tsv
```

Table and source-data integrity gate:

```bash
python -m pip install "paperconan[all]>=0.8,<0.9"
python scripts/table_integrity_gate.py --input-dir path/to/source_data --out preflight/table_gate --profile review
```

Or interpret an existing scan:

```bash
python scripts/table_integrity_gate.py --scan-json path/to/scan.json --out preflight/table_gate
```

The wrapper writes a source manifest, `gate.json`, `findings.tsv`, and `gate_report.md`. Ask before installing paperconan into a shared environment. If the scanner is unavailable, report `NOT_ASSESSED`; do not claim a pass.

Script outputs are supporting evidence, not final judgment. Database failures, DOI metadata gaps, style-risk signals, image similarity, and statistical anomalies all require manual verification before drawing conclusions.

## Important Notes

This is not an AI detector and not a misconduct-adjudication tool. It is a pre-submission quality-control workflow for detecting high-risk residue, fabricated or mismatched references, unsupported claims, figure/source-data/statistical consistency problems, formatting issues, and compliance gaps before journal submission.

The skill distinguishes verified errors from suspicious items requiring manual confirmation. It should not silently rewrite scientific conclusions, and it should not present hypotheses as validated conclusions.

No skill or scanner can guarantee that published data contain no error. Final clearance means only that no unresolved issue was detected within the explicitly assessed scope after complete parsing, reconciliation, reverse-checking, rescanning, and author sign-off.

## License

This repository is released under the [MIT License](LICENSE).
