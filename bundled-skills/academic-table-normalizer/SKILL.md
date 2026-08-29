---
name: academic-table-normalizer
description: Use when the user wants raw data, rough table content, or a badly formatted chart/table description turned into an academic-style table, especially Markdown tables that follow three-line-table logic. Make sure to use this whenever the request involves table captions, table notes, decimal alignment, descriptive-statistics tables, bilingual table titles, or preparing a manuscript-ready table skeleton for Word or journal formatting.
---

# Academic Table Normalizer

## Purpose

Turn rough tabular content into a structured academic table with proper caption, note, and layout logic.

## When to Use

Use this skill whenever the user:
- asks to convert raw data or pasted text into a table
- wants a Markdown table for a paper, thesis, report, or appendix
- needs a three-line-table style logical structure
- wants table caption and note generation
- needs descriptive-statistics tables, comparison tables, coding matrices, or summary tables cleaned up
- mentions decimal alignment, bilingual table titles, or Word-ready academic table formatting

## Core Rule

The table should communicate structure clearly before it tries to look pretty.

Do not guess values. If the user’s raw data are incomplete or ambiguous, preserve the uncertainty instead of filling gaps creatively.

## Table Rules

- Put the table title above the table.
- Put notes below the table.
- Keep headers short but informative.
- Align numeric content consistently, ideally around decimal logic when possible.
- Distinguish clearly between body rows, totals, subtotals, and notes.

## Default Deliverable

Unless the user requests another format, provide:
1. a Markdown table
2. a standard caption
3. a table note
4. a short Word follow-up note if the user wants a true three-line table in Word

## Workflow

1. Read the raw table material.
2. Infer column meaning and row structure.
3. Normalize headers and row labels.
4. Build a Markdown table.
5. Add caption and note.
6. Mention any manual Word adjustments if relevant.

## Response Style

Be structured and practical. If bilingual output helps, provide concise Chinese-English table titles.
