# Figure and presentation workflow

## Entry and scope

Use for publication figures, tables, visual abstracts, schematics, and research presentations. It does not alter underlying data to improve appearance.

## Inputs

Require source data or an existing figure, claim/purpose, target medium, dimensions/resolution, accessibility requirements, and requested output format.

## Route

Controller → 户部 checks source data → 礼部 checks journal/format requirements → 尚书省 ticket. Primary: `make-figures` or `scientific-visualization`. Supporting: `academic-python-plotting`, `journal-figure-polisher`, `scientific-schematics`, `present-paper`, or `scientific-slides`.

## Outputs

Figure/table or presentation artifact, source code when applicable, caption/alt text, data-to-panel mapping, and reproducibility notes.

## Verification

Check that values, labels, units, denominators, uncertainty, color accessibility, panel references, and export resolution match the source and manuscript.

## Failure/fallback

If source data are missing, provide a layout/specification only. If a requested format cannot be rendered, preserve the source and report the exact limitation.
