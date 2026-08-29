---
name: stata-academic-graphing
description: Use when the user wants Stata graph code for academic papers, especially in economics, political science, sociology, public policy, management, or other social-science workflows that rely on Stata. Make sure to use this whenever the request involves twoway graphs, coefplot, marginsplot, event-study figures, panel-data visualization, regression result plotting, scheme optimization, or turning ugly default Stata output into journal-ready figures. Prefer `academic-write-all-skill` as the first academic intake when the request is broad or mixed; use this skill as the dedicated downstream Stata plotting owner after AWAS has already fixed the plotting route.
---

# Stata Academic Graphing

## Purpose

Produce clean, publication-oriented Stata plotting commands for empirical research, with an emphasis on interpretability, reproducibility, and better styling than Stata defaults.

## When to Use

Use this skill whenever the user:
- asks for `stata` graph code or `.do` snippets
- wants to visualize regression results, coefficients, marginal effects, panel trends, event studies, heterogeneity, or fitted relationships
- mentions `twoway`, `marginsplot`, `coefplot`, `binscatter`, `kdensity`, `histogram`, or `graph export`
- says the Stata chart is ugly, default-looking, crowded, or not submission-ready
- needs a full graph command instead of generic plotting advice

## Default Deliverable

Provide **complete Stata commands** that the user can paste into a do-file.

Whenever possible include:
1. any required estimation command context
2. graph command
3. title/axis/legend options
4. scheme or style suggestions
5. export command
6. brief note on any user-side package dependency

## Academic Style Rules

### General Look
- Prefer minimal, flat, publication-safe styling.
- Remove unnecessary background clutter.
- Keep legends compact or suppress them if the mapping is obvious.
- Use monochrome-safe differentiation when the figure may be printed in grayscale.

### Text and Labels
- Use concise `xtitle()`, `ytitle()`, `legend()` and `note()` settings.
- Avoid long titles inside the figure unless journal style requires them.
- Prefer informative axis labels over decorative titles.

### Lines and Markers
- Use moderate line widths and readable marker sizes.
- Distinguish groups with line pattern + marker shape, not only color.
- Avoid overloaded overlays if a faceted or split display is clearer.

## Common Figure Patterns

### 1. Scatter + fit
Use for relationship between core explanatory and outcome variables.

Typical structure:
```stata
twoway ///
    (scatter y x, mcolor(navy%55) msymbol(o)) ///
    (lfit y x, lcolor(maroon) lwidth(medthick)), ///
    xtitle("X") ytitle("Y") legend(off)
```

### 2. Marginal effects / adjusted predictions
Use `margins` + `marginsplot` when interpretation after a fitted model is the point.

### 3. Coefficient plots
Prefer `coefplot` for regression summaries.
If external package is needed, say so explicitly.

### 4. Event-study / dynamic effects
Center the reference period clearly and emphasize confidence intervals.

### 5. Group trends over time
Use `line` or `connected` carefully; if uncertainty matters, add confidence bands or error bars.

## External Package Rule

If the best solution depends on a user-contributed package, state it clearly.

Examples:
- `ssc install coefplot`
- `ssc install blindschemes`
- `ssc install palettes`
- `ssc install binscatter`

Do not assume these are already installed.

## Workflow

1. Infer the estimand or relationship the user wants to show.
2. Determine whether raw data, adjusted predictions, or model coefficients are the right visual object.
3. Choose the cleanest Stata graph family.
4. Write a full command block.
5. Add export instructions, usually EPS/PDF/PNG as appropriate.
6. Mention needed user-written commands if relevant.

## Output Expectations

Prefer this response structure:
- one short sentence naming the recommended graph type
- a complete Stata code block
- 2-4 short bullets explaining what to tweak if the user changes labels, colors, or sample restrictions

## Graph Hygiene

Check for:
- clear reference category or omitted period
- readable confidence intervals
- non-overlapping labels
- sensible axis range
- exportability for manuscript use

## What to Avoid

Avoid unless explicitly requested:
- default `s2color` look without refinement
- unnecessary in-figure titles
- excessive decimal noise in labels
- too many series in one panel
- visually ambiguous color-only encoding

## Response Style

Be practical and code-first. When the request is under-specified, infer the most likely econometric use case and provide a solid baseline command that the user can adapt quickly.
