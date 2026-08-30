# Figure and presentation workflow

## Entry and scope

Use for publication figures, tables, visual abstracts, schematics, and research presentations. It does not alter underlying data to improve appearance.

## Inputs

Require source data or an existing figure, claim/purpose, target medium, dimensions/resolution, accessibility requirements, and requested output format.

## Route

Controller → 户部 checks source data → 礼部 checks journal/format requirements → 尚书省 ticket. Primary: `make-figures` or `scientific-visualization`. Supporting: `academic-python-plotting`, `journal-figure-polisher`, `scientific-schematics`, `present-paper`, or `scientific-slides`.

Choose the visual from the estimand, data type, comparison, uncertainty, and manuscript claim before selecting a template or aesthetic. A gallery image or R package is an implementation example, not a reason to use the wrong geometry. Preserve the upstream license and prefer official example data/code over unverified copied datasets.

For technical routes, mechanisms, and graphical abstracts, separate two passes:

1. **evidence extraction/specification** — create nodes, edges, groups, labels, and source locators; use `[TO CONFIRM]` for missing scientific steps and preserve original technical terms;
2. **rendering** — apply layout, font, accessibility, dimensions, and export rules only after the scientific graph is approved.

Do not let rendering tools add steps, mechanisms, causal arrows, or outcomes absent from the approved specification. Plan graphical abstracts before image generation and keep labels concise, spell-checked, and claim-calibrated.

## Outputs

Figure/table or presentation artifact, source code when applicable, caption/alt text, data-to-panel mapping, reproducibility notes, and a provenance-bearing diagram specification for routes/schematics/graphical abstracts.

## Verification

Check that values, labels, units, denominators, uncertainty, color accessibility, panel references, and export resolution match the source and manuscript. For diagrams, verify every node and edge against the approved source-located specification; for plots, verify the geometry matches the estimand and no template/example data remain.

## Failure/fallback

If source data are missing, provide a layout/specification only. If a requested format cannot be rendered, preserve the source and report the exact limitation.
