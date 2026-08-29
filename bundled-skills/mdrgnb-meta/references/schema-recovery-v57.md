# Schema recovery and writeback protocol v5.7

Use this protocol whenever legacy extraction batches, independently reviewed branches, a wide
fact store, or an exported workbook contains literal `NR`/`NA`, duplicated old/new field groups,
or separate entity/value tables.

## Why this gate exists

The source can contain a valid value while the displayed workbook contains `NR` when:

1. a narrow final/third-review table replaces a richer A/B table;
2. old and new schemas are concatenated by ordered header union without semantic mapping;
3. schema-created blanks are converted to literal `NR`;
4. `performance_values`, `dataset_values`, `threshold_values`, `calibration_values`, or scoring
   companions are not joined or exported.

These are migration defects, not source non-reporting. They must be repaired before targeted
full-text re-extraction begins.

## Field-level adjudication overlay

Adjudication operates on the complete key:

`report_id × study_id × entity_type × entity_id × field_name`.

Start from the union of complete A and B field facts. Apply only fields explicitly listed in the
adjudication scope. A narrow final row cannot delete or blank a field that is outside that scope.
Within scope, a final blank, legacy missing token, or `NOT_CAPTURED` cannot replace an observed
base fact without a source-supported adjudication record. Entity additions, removals, splits, and
merges require the SEMKEY crosswalk.

Resolution order for legacy recovery is:

1. observed final or adjudicated companion value;
2. exact A/B field consensus;
3. unresolved single-branch value -> `PENDING_REVIEW`;
4. incompatible A/B or final values -> `CONFLICT`;
5. no mapped value -> `NOT_CAPTURED`.

Never use majority vote, row order, the first nonmissing branch, or a whole-row overwrite.

## Semantic migration

Canonical entity identity is the compound key `report_id × study_id × entity_id`, scoped by
entity type. An entity ID alone is never sufficient for a cross-report merge. When a companion
omits report/study, recover context from its exact parent key or a unique SEMKEY crosswalk only.
Ambiguous loose matches block recovery. A branch entity adjudicated as removed is retained in the
source-value audit but cannot create a canonical row. An unmapped branch entity likewise cannot
inflate a recovered view. A one-to-many SEMKEY split requires field-level adjudication; never
broadcast one coarse source value to every final child.

Every active source field belongs to one of three classes:

- mapped once to a canonical field fact;
- explicit provenance/operational metadata;
- `UNMAPPED_NONMISSING_SOURCE_FIELD`, which blocks migration closure.

An ordered union of headers is an archival operation only. It is never a canonical migration.
Legacy blanks/`NR`/`NA` remain preserved in the migration ledger and map to `NOT_CAPTURED`, not
`NR_SOURCE`. `NR_SOURCE` still requires a complete field-specific source search under the v5.6
data contract.

## Table-family contract

Entity and value companions form one table family and are materialized by exact entity key:

| Entity table | Companion tables |
|---|---|
| `dataset.tsv` | `dataset_values.tsv` |
| `performance.tsv`/`discrimination.tsv` | `performance_values.tsv` |
| `threshold.tsv` | `threshold_values.tsv`, conditional `threshold_2x2_values.tsv` |
| `calibration.tsv` | `calibration_values.tsv` |
| `predictor.tsv` | `predictor_values.tsv` when present |
| `TRIPOD.tsv`/`tripod_ai_long.tsv` | final item response and scoring-adjudication view |
| `PROBAST_dev.tsv`, `PROBAST_eval.tsv`, `probast_ai_long.tsv` | record-type and scoring-adjudication views |

Use keyed joins only. A missing companion, orphan key, duplicate `entity key × target field`, or
unexported companion value blocks release. One-to-many child rows are valid when their child IDs
or target fields differ.

Declare every companion required by the package manifest. For the current full40 package, invoke
recovery with `--require-companion performance_values.tsv`,
`--require-companion threshold_values.tsv`, and
`--require-companion calibration_values.tsv`. When recovering appraisal tables, additionally
require `tripod_scoring_adjudication.tsv`, `probast_record_type.tsv`, and
`probast_scoring_adjudication.tsv`. The PROBAST record-type table may populate only
`record_type`; its branch `response` must never overwrite the final scoring response. A package may instead provide
`table_family_manifest.json` with a `required_companions` array. Branch-only companions are read
for A/B/third recovery but are not presented as adjudicated final companions.

Threshold proportions from normalized value tables and source-reported rounded percentages from
2×2 companions are separate typed facts. Normalize deterministic 0–100 versus 0–1 scales without
discarding the raw cell. Project calibration metric/value companions to typed fields such as
calibration intercept, slope, Brier score, and Hosmer-Lemeshow p while retaining their generic
metric/value facts.

## Recovery command

Preserve every input and write to a new directory:

```text
python scripts/recover_schema_drift_v57.py \
  --canonical <facts_canonical> \
  --branch A=<frozen_A_dir> --branch B=<frozen_B_dir> \
  --branch THIRD=<frozen_third_dir> --branch FINAL=<frozen_final_dir> \
  --output <new_recovery_dir>
```

If a `FINAL` branch may change any preserved A/B or canonical field, pass
`--adjudication-scope <scope.tsv>`. Each scope row must contain the complete fact key, an approved
adjudication status, and evidence. An unscoped final value can confirm an existing consensus but
cannot override it or become authoritative by itself.

Use repeated `--branch` options for multiple batches. Use repeated `--table` options for a staged
recovery. The command writes:

- `recovered_field_facts.tsv`;
- entity-specific recovered views;
- `recovery_audit.tsv`;
- `unresolved_fields.tsv`;
- `unlinked_source_values.tsv` for removed, ambiguous, and unmapped source entities;
- `companion_coverage.tsv` proving each final companion cell is visible in facts and views;
- `recovery_manifest.json`.

The manifest reports `unmapped_source_fields` separately from `blocking_audit_issues` and also
records `blocking_audit_issues_by_code`. An unresolved final override is a real adjudication
conflict, not an unmapped source field; these counts must never be aliased.

Migration QA recomputes the complete `SPECS x canonical entity` fact inventory, status totals,
view headers, companion source hashes, and compound-key coverage. Deleted facts, injected
`NR_SOURCE`, cross-file duplicate business values, and unscoped final overrides are blocking.

Then run:

```text
python scripts/qa_schema_recovery_v57.py --recovery-root <new_recovery_dir> --mode migration
```

For this project, also run:

```text
python scripts/qa_real_recovery_smoke_v57.py --recovery-root <new_recovery_dir>
```

The smoke gate locks canonical entity counts and sentinel facts for STU-018, STU-031, and STU-039.
It prevents a later schema change from silently losing AUC, threshold, calibration, or multi-model
values that are already present.

`--mode freeze` additionally blocks `NOT_CAPTURED`, `PENDING_REVIEW`, and `CONFLICT`.

## Workbook export gate

Excel sheets are generated views, not the fact store. Before release, verify that every observed
companion fact is visible either in its parent entity view or in an explicitly exported normalized
companion sheet. A workbook must not show a missing code in a target cell when a keyed companion
contains an observed value. Re-running recovery and export must be idempotent.

Generate and round-trip test the actual workbook with:

```text
python scripts/export_recovered_workbook_v57.py \
  --recovery-root <new_recovery_dir> --output <new_workbook.xlsx>
```

The exporter reopens the written XLSX and checks every companion value against its entity sheet.
If a workbook cell displays a missing token while the recovered fact is observed, export fails and
the `.xlsx.qa.json` audit records the exact location.

Do not use display-only token replacement or header-based guesses such as converting `NR` to
"source not reported". Repair the keyed fact lineage first.
