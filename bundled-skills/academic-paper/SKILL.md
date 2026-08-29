---
name: academic-paper
description: "Use when the user wants academic manuscript production work such as planning a paper outline, generating paper figures or tables, drafting sections, revising a manuscript, converting a manuscript to LaTeX, compiling LaTeX to PDF, or producing a paper or thesis chapter end to end. Also use when requests mention paper plan, paper figures, write paper, draft LaTeX, compile paper, or build manuscript PDF."
metadata:
  version: "2.6"
  last_updated: "2026-04-04"
---

# Academic Paper

## Canonical Role

`academic-paper` is the canonical academic-series skill for manuscript production work.

It absorbs the legacy responsibilities that were previously split across:

- `paper-plan`
- `paper-figure`
- `paper-write`
- `paper-compile`

If the user asks for paper outlining, figure generation, section drafting, LaTeX conversion, or LaTeX-to-PDF compilation for an academic manuscript, prefer this skill instead of the legacy `paper-*` wrappers.

## When To Use

Use this skill whenever the user wants to do any of the following for an academic manuscript, thesis chapter, review article, or conference/journal submission:

- create a paper outline
- turn a narrative report into a manuscript structure
- generate paper figures or tables from results
- draft sections or a full manuscript
- convert a manuscript to LaTeX
- compile LaTeX into PDF
- revise a paper after feedback
- package a submission-ready manuscript

## Core Coverage

This skill should own the full manuscript-production layer inside the academic series:

1. Outline planning and section architecture
2. Figure and table planning from available evidence
3. Drafting and rewriting manuscript sections
4. Citation and formatting normalization
5. LaTeX manuscript assembly
6. PDF compilation and compile-error repair

## Routing Rules

- If the request is only about peer review, reviewer simulation, or editorial critique, prefer `academic-paper-reviewer`.
- If the request is for a complete research-to-paper pipeline across multiple stages, prefer `academic-pipeline`.
- If the request is specifically about isolated plotting outside manuscript production, a plotting-focused skill may still be appropriate.

## Migration Note

The legacy `paper-plan`, `paper-figure`, `paper-write`, and `paper-compile` skills are now compatibility wrappers. Maintain manuscript-production logic here, not in those wrappers.
