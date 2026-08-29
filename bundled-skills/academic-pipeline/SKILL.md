---
name: academic-pipeline
description: "Use when the user wants a complete academic workflow from idea, narrative report, or existing draft through planning, figure generation, drafting, compilation, integrity checks, review, revision, and final PDF delivery. Also use when requests mention full paper workflow, report to PDF, end-to-end paper writing, paper pipeline, or research-to-manuscript workflow."
metadata:
  version: "2.8"
  last_updated: "2026-04-04"
  depends_on: "deep-research, academic-paper, academic-paper-reviewer"
---

# Academic Pipeline

## Canonical Role

`academic-pipeline` is the canonical end-to-end orchestrator for the academic series.

It absorbs the legacy responsibility previously carried by `paper-writing`.

If the user wants a full workflow such as "from report to PDF", "paper writing pipeline", or a start-to-finish manuscript production process, prefer this skill instead of the legacy `paper-writing` wrapper.

## When To Use

Use this skill when the user wants a multi-stage academic workflow, including any combination of:

- research scoping or evidence synthesis
- manuscript planning
- figure generation
- manuscript drafting
- compilation and PDF generation
- integrity checks
- peer review and revision loops
- final delivery packaging

## Delegation Model

This orchestrator should route work to the academic-series specialists:

- `deep-research` for upstream research and evidence gathering
- `academic-paper` for manuscript production work
- `academic-paper-reviewer` for review, critique, and re-review

## Migration Note

The legacy `paper-writing` skill is now a compatibility wrapper. Maintain end-to-end paper-pipeline logic here, not in that wrapper.
