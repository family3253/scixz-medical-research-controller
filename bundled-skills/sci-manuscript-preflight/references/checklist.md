# SCI Manuscript Preflight Checklist

## Critical

- [ ] No explicit AI or prompt residue remains.
- [ ] No unresolved placeholders remain.
- [ ] All references resolve to real bibliographic records.
- [ ] All DOI/PMID/title/year/author metadata are consistent.
- [ ] All high-risk claims have direct citation support.
- [ ] All figures, tables, and supplementary files are cited and numbered consistently.
- [ ] Every figure panel has traceable source data or a documented reason if source files are unavailable.
- [ ] No duplicated-looking image panels are used for different conditions without explanation.
- [ ] No unexplained Western blot, gel, microscopy, flow cytometry, or IHC assembly artifacts remain.
- [ ] All quantitative panels match raw/source values, group sizes, statistical tests, and figure legends.
- [ ] Methods, Results, figure legends, and supplementary/source data agree on groups, doses, time points, sample sizes, and tests.
- [ ] Every expected source-data file and sheet was discovered and successfully parsed; all `scan_errors` are resolved.
- [ ] A frozen source-data manifest records relative paths, byte sizes, SHA-256 hashes, scanner version, profile, and run time.
- [ ] Cross-sheet/file duplication, constant offsets/ratios, exact linear relations, copy-then-tweak patterns, decimal-tail reuse, rounding grids, and applicable GRIM/GRIMMER signals were assessed.
- [ ] Every retained numerical signal is located by file, sheet, row/column range, rule, `n`, and value sample.
- [ ] Benign explanations for `kept`, `demoted`, and `hidden` findings were checked against the original table, figure legend, and Methods.
- [ ] Signal review state and scientific impact scope were assessed separately.
- [ ] All `BLOCKER`, `REVIEW_REQUIRED`, and unresolved `CORE` items are closed before submission.

## Table and source-data release gate

- [ ] Every quantitative table and figure maps to frozen source data and an analysis path.
- [ ] Key descriptive statistics, effect estimates, confidence intervals, and p values were independently recomputed where feasible.
- [ ] Sample IDs, groups, units, exclusions, missing values, transformations, and biological versus technical replicates are consistent.
- [ ] Corrected data, tables, and figures were regenerated from scripts where feasible and rescanned.
- [ ] An independent reverse-check actively tested shared controls, re-plots, formulas, normalization, unit conversion, technical replicates, fixed denominators, and boundary values for high-impact findings.
- [ ] The final wording is "no unresolved issue detected within the assessed scope," not a guarantee that no error exists.

## Biomedical compliance

- [ ] Ethics approval is stated when required.
- [ ] Consent statement is included when required.
- [ ] Data availability statement is complete.
- [ ] Code availability statement is complete for computational work.
- [ ] Reporting guideline is identified and followed.

## Final author check

- [ ] Every flagged reference is manually verified in Zotero/EndNote/PubMed.
- [ ] Every figure panel has source data and a clear caption.
- [ ] Every representative image is linked to the correct experimental group and raw image.
- [ ] Every statistical annotation is reproducible from the source data or analysis script.
- [ ] Every table-integrity gate limitation and `MANUAL` item has a named author sign-off.
- [ ] Any possible image reuse, crop, rotation, flip, or relabeling has been manually checked against original files.
- [ ] The conclusion does not overstate the evidence.
