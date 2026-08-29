# Table and Source-Data Integrity Release Gate

Use this protocol when a manuscript includes quantitative tables, spreadsheet source data, or figure-level source-data exports. It is a pre-submission quality-control gate, not a misconduct adjudication workflow.

## Gate boundary

- A numerical anomaly is a signal requiring verification, not proof of error or intent.
- A clean numerical scan is not proof that the data, analysis, or manuscript is correct.
- Do not issue final `PASS` when expected files failed to parse, source data are missing, or high-impact findings remain unresolved.
- Keep deterministic scanner output separate from contextual scientific judgment.

## Required inputs

Request, where applicable:

- Source-data tables: `.xlsx`, `.xls`, `.xlsm`, `.xlsb`, `.csv`, or `.tsv`.
- The manuscript tables and figure source-data exports.
- Raw or minimally processed values used for each quantitative panel.
- Statistical scripts or analysis notebooks.
- Figure legends, Methods, exclusion rules, and data dictionary.
- A mapping from sample IDs to groups, time points, batches, and replicates.

If any expected input is unavailable, record it as a coverage limitation. Missing material that prevents verification of a central result is a `BLOCKER` or `MANUAL` item, not `PASS`.

## Stage 1: Freeze and inventory

1. Inventory every expected source-data file.
2. Record relative path, file type, byte size, and SHA-256 hash.
3. Identify files that are generated outputs versus manually edited tables.
4. Preserve the scanner name, version, profile, parameters, timestamp, and output paths.

Use `scripts/table_integrity_gate.py` to create `source_manifest.tsv` when scanning a directory.

## Stage 2: Parse-coverage gate

Before interpreting findings, verify:

- Every expected file was discovered.
- Every expected sheet or table was parsed.
- No unsupported legacy workbook or oversized file was silently skipped.
- `scan_errors` is empty.
- Extracted PDF/DOCX tables can be traced to their source pages or sections.

Any parse failure blocks final clearance until the file is successfully assessed or a named author documents why it is outside scope.

## Stage 3: Deterministic numerical scan

When available, run the external [paperconan](https://github.com/zixixr/paperconan) CLI rather than inferring patterns by visual inspection:

```bash
python -m pip install "paperconan[all]>=0.8,<0.9"
python scripts/table_integrity_gate.py --input-dir path/to/source_data --out preflight/table_gate --profile review
```

If paperconan is already run:

```bash
python scripts/table_integrity_gate.py --scan-json path/to/scan.json --out preflight/table_gate
```

The wrapper accepts the documented paperconan `0.8.x` schema, validates required fields, and reconciles the frozen manifest with scanner-reported files and Sheets. A version/schema mismatch or incomplete reconciliation is a blocker.

Do not install packages into a shared or production environment without user approval. If the deterministic scanner is unavailable, mark this gate `NOT_ASSESSED`; do not fabricate findings or claim a pass.

Review at least these signal classes:

- Cross-sheet or cross-file reuse, including identical positions or value overlap.
- Constant offset, constant ratio, exact linear relation, or complementary sums.
- Copy-then-tweak patterns and unusual long decimal-tail reuse.
- Repeated high-precision values or unusually restricted difference sets.
- Arithmetic/geometric progressions and fixed rounding grids.
- GRIM/GRIMMER inconsistency when the underlying observations are integer-granular.
- Last-digit distribution only with appropriate multiple-testing correction.

For every surfaced finding, record:

```text
file -> sheet -> row/column range -> detector/rule -> n -> value sample -> scanner action
```

## Stage 4: False-positive control

Preserve the scanner's raw context:

- `kept`: retained at the active profile's visible severity.
- `demoted`: visible but downgraded by a deterministic false-positive rule.
- `hidden`: suppressed from normal triage but retained in the machine-readable audit.

For each finding, test plausible benign mechanisms:

- Shared control, common baseline, or repeated reference sample.
- Re-plotting or combined-versus-individual display of the same data.
- Unit conversion, normalization, background subtraction, log/fold transform, or formula-derived values.
- Fixed-denominator percentages or ratios.
- Time, dose, rank, identifier, plate/well, or coordinate axes.
- Technical replicates, repeated instrument reads, pooled samples, or repeated exports.
- Detection floors, saturation ceilings, missing-value fills, bounded scores, or coarse rounding.
- Model outputs, p/q values, correlation matrices, or other pipeline-generated tables.

Do not discard a finding merely because a benign explanation is conceivable. Record whether that explanation is supported, contradicted, or unresolved.

## Stage 5: Separate signal strength from scientific impact

Use two independent dimensions.

### Signal review state

- `REVIEW_REQUIRED`: a kept high/medium signal requires source-table and manuscript-context review.
- `MANUAL_REVIEW`: a low/demoted/hidden signal needs confirmation of its benign explanation.
- `RESOLVED_BENIGN`: the original table and Methods support a documented benign explanation.
- `RESOLVED_ERROR`: a verified data, label, formula, or export error was corrected and rechecked.
- `NOT_ASSESSED`: required material or tooling was unavailable.

### Scientific impact scope

- `CORE`: affects a main figure, primary endpoint, headline result, or central mechanism.
- `SUPPORTING`: affects supporting evidence but is not the only basis for the conclusion.
- `PERIPHERAL`: affects a secondary or supplementary analysis with limited influence on conclusions.

Never collapse these dimensions into one misconduct or fraud probability.

## Stage 6: Recompute and reconcile

Numerical-pattern scanning does not replace statistical validation. For each quantitative output:

1. Recompute key summaries and statistical tests from the frozen source data where feasible.
2. Confirm `n`, exclusions, missing-data handling, units, transformations, and biological versus technical replicates.
3. Reconcile raw/source data with plotted values, table cells, exact p values, captions, Results, and Methods.
4. Confirm multiple-testing correction for omics-scale or repeated comparisons.
5. Regenerate corrected tables or figures from scripts whenever possible; avoid manual copy-paste repair.

## Stage 7: Adversarial review

Require a separate reverse-check for unresolved `CORE` findings and any finding initially considered high priority. The reviewer must assume the concern is a false positive and actively test shared-control, re-plot, transformation, formula, technical-replicate, boundary-value, and provenance explanations.

Record:

- Initial finding and evidence.
- Benign explanations tested.
- Materials reviewed.
- Outcome: `CONFIRMED`, `DOWNGRADED`, `RESOLVED_BENIGN`, or `NEEDS_MORE_MATERIAL`.
- Reviewer and date.

## Final release criteria

Final submission clearance requires all of the following:

- No expected file or sheet remains unparsed without documented scope justification.
- Every quantitative figure and table maps to frozen source data and an analysis path.
- Key statistics are independently reproducible where feasible.
- Manuscript, figures, tables, legends, and source data agree on `n`, groups, units, tests, and p values.
- All `BLOCKER`, `REVIEW_REQUIRED`, and unresolved `CORE` items are closed.
- Corrected artifacts are rescanned after changes.
- A named author signs off on remaining `MANUAL` limitations.

Even after these conditions are met, describe the result as "no unresolved issue detected within the assessed scope," not as a guarantee that no error exists.
