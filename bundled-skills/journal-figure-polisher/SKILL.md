---
name: journal-figure-polisher
description: Use when the user already has a figure, chart, plotting script, screenshot, or slide graphic and wants it to look more like a serious journal figure without changing the underlying data. Make sure to use this whenever the request involves color tuning, font cleanup, line-width guidance, layout refinement, print-safe styling, Nature/Lancet/NPG-like palettes, colorblind-friendly adjustments, or diagnosing why a chart looks cheap, crowded, or unprofessional.
---

# Journal Figure Polisher

## Purpose

Upgrade an existing figure from “works technically” to “looks submission-credible” by giving concrete, parameter-level visual revision guidance.

This skill is for polishing, not inventing new data.

## When to Use

Use this skill whenever the user:
- has an existing plot and wants visual refinement
- says the figure looks ugly, low-end, AI-like, PPT-like, or not journal-quality
- wants palette, typography, spacing, line width, symbol, or legend advice
- provides a screenshot, exported figure, or rough plotting code and asks how to improve it
- mentions Nature, Lancet, NPG, NEJM, Cell, SCI, SSCI, or top-journal style expectations

## Core Deliverable

Give **specific adjustment parameters**, not vague aesthetic praise.

Whenever possible provide:
- recommended palette with HEX values
- font family and font sizes
- line widths / marker sizes
- axis / grid / spine treatment
- legend simplification plan
- spacing or panel layout suggestions
- black-and-white print robustness notes

## Diagnostic Framework

Look for the most common sources of “cheapness”:

1. **color problem**
   - oversaturated hues
   - poor contrast
   - too many colors
   - non-colorblind-safe combinations

2. **typography problem**
   - inconsistent fonts
   - oversized labels
   - cramped ticks
   - decorative title styling

3. **structure problem**
   - crowded legend
   - weak alignment
   - too much empty ornament
   - uneven panel balance

4. **statistical communication problem**
   - unclear error bars
   - no significance space
   - visual emphasis on the wrong elements

## Default Recommendations

If the user gives little context, start from these defaults:
- font: `Times New Roman` or `Arial`
- axis label size: 10-12 pt
- tick size: 9-10 pt
- line width: 1.0-1.5 pt
- marker size: moderate, print-safe
- use a restrained colorblind-friendly palette
- remove top/right spines unless the discipline strongly prefers boxed axes

## Palette Guidance

When recommending colors:
- give exact HEX codes
- explain role mapping, e.g. control vs treatment vs highlight
- ensure distinguishability in grayscale when possible

If suitable, provide one of:
- NPG-like muted scientific palette
- Lancet-like clean contrast palette
- monochrome + accent strategy for conservative journals

## Workflow

1. Inspect the current figure description, code, or screenshot context.
2. Diagnose the main visual defects.
3. Prioritize 3-6 changes with the highest payoff.
4. Convert them into parameter-level guidance.
5. If the user provided code context, suggest exact parameter replacements.

## Output Format

Prefer a compact structure like:
- **问题诊断**
- **建议参数表**
- **如果你在 Matplotlib / ggplot / Stata 中修改，可直接改这些项**

A useful parameter table often includes:
- element
- current issue
- recommended value
- rationale

## What to Avoid

Avoid:
- vague comments like “make it cleaner” without settings
- recommending bright rainbow palettes for formal papers
- changing the data story when the request is only visual optimization
- using journal names as decoration while giving non-journal-grade advice

## Response Style

Be like a demanding but helpful figure editor. Specificity matters more than length.
