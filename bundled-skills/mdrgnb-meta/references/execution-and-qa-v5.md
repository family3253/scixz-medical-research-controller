# Execution and QA Protocol v5.6

## Stage gates

1. Pool lock: verify 41 source records map to 40 unique reports using the frozen v4.5
   `01_Source_Report_Index`; never infer IDs from row/file order.
2. Unit lock: enumerate candidate outcome × model × dataset units before full extraction.
3. Cross-report grain lock: create reviewer-specific `granularity_alignment.tsv`, validate semantic
   keys against the v5.3 contract, and re-audit earlier batches whenever the contract changes.
4. Dual extraction: freeze A and B artifacts before comparison.
5. Extraction adjudication: resolve all material field and granularity conflicts.
6. Dual TRIPOD+AI and PROBAST+AI scoring: freeze independent branches.
7. Scoring adjudication: resolve item/domain conflicts.
8. Workbook writeback: write adjudicated long-form facts and derived views.
9. Pool/synthesis lock: validate fixed audit and dynamic branch/performance pools, assign
   cohort/dependency/model-family/synthesis groups, and freeze versioned analysis sets.
10. Statistical execution: code reads the locked analysis table; no hand-typed study values.
11. Manuscript reconciliation: tables, figures, prose, PRISMA counts, and supplements derive from
    the same locked sources.
12. Analysis-set reconciliation: distinguish the 40-report audit pool, 39-report primary diagnostic
   set, and 38-report strict-adult sensitivity set in every table, figure, and prose count.

Before stage 8, run the v5.7 schema-recovery gate whenever legacy or mixed-schema artifacts exist.
The gate must prove field-level overlay preservation, exactly-one semantic mapping of every
nonmissing source field, keyed companion materialization, and export visibility. Row-count
preservation or ordered header union alone cannot pass this gate.

## Material conflicts requiring third adjudication

- eligibility or diagnostic/prognostic status;
- duplicate/report/cohort identity;
- adult status;
- outcome/phenotype/reference standard;
- N/events/non-events or prevalence;
- dataset role/external-validation axis/investigator relation;
- model identity/family/final-model status;
- algorithm family/superclass, score-to-mother-model lineage, final-model status, or
  traditional-versus-ML assignment;
- performance estimate/CI/2×2/calibration;
- TRIPOD+AI item status;
- PROBAST+AI item/domain/overall judgment;
- synthesis eligibility or dependency grouping.
- entity split/link/merge decisions or duplicate semantic keys.
- known-current-organism model input versus organism-restricted cohort classification;
- model-branch eligibility/report aggregation/pool membership.

## Workbook rules

- The v4.3 workbook is the fact store; do not resurrect the legacy isolated-paper/merged-workbook
  pipeline.
- Long evidence and item-level scoring tables are authoritative. Wide scoring matrices, summaries,
  and meta-ready tables are generated views.
- Maintain referential integrity between report, study, cohort, outcome, model, dataset, performance,
  and evidence keys.
- Maintain `tripod_component_id`, PROBAST development scope, and PROBAST evaluation scope keys;
  each A/B/final judgment must retain its own evidence ID.
- No fact row may be silently overwritten. Corrections require a change-log row with old/new value,
  source, reason, reviewer/adjudicator, and timestamp.
- No blank final values in tracked fields; use explicit missingness codes.
- Apply `extraction-data-contract-v56.md`: legacy blank/`NR`/`NA` means `NOT_CAPTURED` until a
  targeted source search or deterministic structural rule justifies another status.
- Reject universal wide-schema default filling, fixed-character whole-report truncation, row-order
  comparison, and arbitration fallback to one extractor.
- Require one granularity-ledger row for every study, cohort, dataset, outcome, model, performance,
  threshold, calibration, and predictor entity; validate each semantic key and split/link reason.
- Run a 40-report alignment audit before synthesis: duplicate semantic keys, unexplained splits,
  inconsistent role-instance handling, and different missingness treatment are blocking errors.
- Validate every eligibility scope at model-branch level. Included branches require current target,
  unknown current organism, no current-organism input, no organism-restricted cohort, fixed model,
  and final adjudication.
- Validate exactly 40 audit reports separately from the dynamic synthesis membership count.
- Validate exactly 39 reports in `PRIMARY_DIAGNOSTIC_39` and 38 in `STRICT_ADULT_38`; require
  `STU-005` to remain audit-only and `STU-016` to be excluded only from the strict-adult set.

## Numerical QA

- reproduce event percentages from event/denominator;
- validate CI order and bounds; AUC and proportions must remain in [0,1];
- distinguish reported from derived values and original from transformed scales;
- require all four TP/FP/FN/TN cells before validating 2×2 arithmetic;
- do not convert all-empty cells to zero;
- verify sensitivity/specificity against 2×2 within rounding tolerance;
- do not reconstruct specificity or 2×2 cells from sensitivity plus test-positivity rate in weighted
  case-control, multiply-imputed, or otherwise non-integer analysis populations;
- detect duplicate performance IDs and multiple primary selections per independent cohort/group;
- flag nested pooled/site-specific estimates and probable cohort overlap;
- verify each event/denominator reproduces the reported percentage within a prespecified tolerance;
- distinguish patient, episode, specimen, and analysis-population denominators;
- require third review for every 2×2 mismatch, denominator change, or unit-of-analysis conflict;
- run influence/leave-one-cluster-out checks from locked data, not manual matrices.

Validate every controlled field against the active workbook vocabulary, including dataset role,
external axis, investigator relation, TRIPOD component type, PROBAST record type, and missingness
codes. Validate every TRIPOD/PROBAST item foreign key and item-specific response options before a
branch may be frozen.

## Branch artifacts

Use immutable, role-specific TSV/JSON files with report/batch IDs and source hashes. Require
`unit_inventory.tsv` and `granularity_alignment.tsv` in addition to the fact/scoring tables. Required fields
include reviewer, agent mode, protocol version/hash, source package hash, timestamp, and branch
status. An empty or schema-incompatible branch is invalid and must be rerun.

## Mandatory executable QA

Run these against branch/adjudication artifacts, not hand-built summaries:

1. `qa_source_identity_v1.py` against the frozen v4.5 source index and relevant tables;
2. `qa_semantic_key_v1.py` against alignment plus crosswalk;
3. `qa_eligibility_consistency_v1.py --mode branch|final`;
4. `qa_pool_consistency_v1.py` against audit, synthesis, eligibility, and source mapping;
5. `qa_full40_coverage_v1.py` against the migrated cumulative tables;
6. `regression_check.py` and skill validation.

7. `qa_schema_recovery_v57.py` against the recovery manifest, field facts, audit ledger,
   unresolved fields, and materialized views.
8. `qa_real_recovery_smoke_v57.py` against the current full40 recovery output to lock canonical
   entity cardinality and the STU-018/STU-031/STU-039 sentinel values.
9. `export_recovered_workbook_v57.py` for every released XLSX; its round-trip audit must prove
   every observed companion value is visible in the actual workbook, not only in a TSV view.
10. `qa_algorithm_taxonomy_v58.py --facts <facts.tsv> --mode freeze` before synthesis; migration
    mode may inventory legacy gaps, but freeze mode requires complete model-level algorithm fields
    and consistent family/superclass/binary mappings.

Each QA emits JSON and nonzero exit status on blocking error. Run SEMKEY, eligibility coverage,
and pool QA cumulatively over the current batch plus all previously adjudicated batches. A batch-
only pass is insufficient for cross-report closure. Compatibility mode may warn about frozen v5.3
formatting, but cannot suppress duplicate identities, orphan mappings, or ineligible synthesis
memberships.

When importing v5.3 packages with different headers, first run `migrate_v53_to_v54.py` into a new
directory under the rules in `schema-migration-v54.md`. Never concatenate source tables directly
and never resolve drift by retaining the smaller header.

For v5.6 field-fact packages, additionally run `qa_extraction_package_v56.py`. In freeze mode,
`NOT_CAPTURED`, `PENDING_REVIEW`, and `CONFLICT` are blocking. An inaccessible required source
routes the report to `BLOCKED_SOURCE_UNAVAILABLE`.

## Completion states

- `OPEN_UNIT_INVENTORY`
- `OPEN_DUAL_EXTRACTION`
- `OPEN_GRANULARITY_ALIGNMENT`
- `OPEN_EXTRACTION_ADJUDICATION`
- `OPEN_DUAL_SCORING`
- `OPEN_SCORING_ADJUDICATION`
- `OPEN_WRITEBACK_QA`
- `CLOSED_FIELD_COMPLETE`
- `BLOCKED_SOURCE_UNAVAILABLE`

Do not call a report complete while any material conflict, unmapped unit, or unscored applicable
component remains.
