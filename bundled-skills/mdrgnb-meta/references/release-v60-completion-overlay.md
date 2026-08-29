# v6.0 completion overlay and release gate

## Scope

Use this overlay when completing previously extracted studies, recovering a legacy workbook,
or exporting a v6.0 compact workbook. It applies to the current diagnostic-only MDR-GNB review
and does not change the frozen screening or adjudication branches.

## Fact precedence

Resolve a displayed field only at the complete key:

`report_id × study_id × entity_type × entity_id × field_code`

Use this order:

1. latest v6.0 adjudicated completion overlay;
2. same-entity frozen canonical fact;
3. same-entity legacy increment;
4. explicit non-observed status.

Never borrow from another model, dataset, outcome, analysis population, predictor, threshold,
calibration context, or performance record merely because it belongs to the same study. A
cross-entity match requires an explicit SEMKEY or adjudicated crosswalk and must remain auditable.

## Legacy missingness repair

At ingestion, treat `NR`, `NA`, `N/A`, `UNKNOWN`, `NR_SOURCE`, `NOT_CAPTURED`,
`SOURCE_NOT_ACCESSIBLE`, and blank legacy cells as missing tokens, not observed values. Preserve
the original cell in the migration/audit ledger. Write an empty typed value with the appropriate
status and rationale:

- `NR_SOURCE`: complete accessible source package searched and field not reported;
- `NA_STRUCTURAL`: deterministic structural rule applies;
- `NOT_CAPTURED`: not yet systematically extracted;
- `UNCLEAR` or `PENDING_REVIEW`: accessible but unresolved.

A historical `NR_SOURCE`, evidence ID, workbook note, or generic "source searched" statement is
still legacy missingness and migrates to `NOT_CAPTURED`. Promotion to current `NR_SOURCE` requires
a renewed v6.0 field-level review:

1. rebuild a source manifest containing the main article, supplements, appendices, corrections,
   registrations, and other relevant attachments with source ID, real local path, role, access
   status, and SHA-256 recomputed from the file bytes; declare one frozen source-package root and
   inventory every file beneath it, including explicitly excluded files;
2. open and search the main article plus every accessible relevant supplement/attachment;
3. link one evidence row per searched source file and record its exact page/table/figure/section
   locator and evidence span; a main-text evidence row cannot stand in for a supplement;
4. store a machine-readable search scope whose searched-file list covers every accessible source
   marked for complete search, with locations searched, exact entity/field key, reviewer, v6.0
   review round, and renewed-review rationale;
5. link that new evidence record to the final fact.

If a source is inaccessible, record it in the manifest/access log and use
`SOURCE_NOT_ACCESSIBLE` when it blocks the field. If the renewed search has not occurred, use
`NOT_CAPTURED`. Do not use `NA_STRUCTURAL` without a versioned deterministic `status_rule_id`.
The release gate must fail a current `NR_SOURCE` justified only by legacy facts or old-table text.
It must normalize and validate both compact (`field_code`, `value_status`) and canonical
(`field_name`, `value_status_code`) fact schemas; missing required headers are blocking errors.
Canonical facts must populate `status_rationale` itself. Evidence, fact, and source-manifest report
IDs must agree. The release gate scans the declared package root and fails any unregistered file.
For `NA_STRUCTURAL`, it must load the structural-rule table, match the entity/field, and evaluate
the active rule against `context_json`.
Reject duplicate source IDs, paths, and hashes. Accessible main reports, supplements, appendices,
attachments, corrections, and registrations cannot be excluded from complete search. Accept only
the frozen approved structural-rule table bundled with v6.0. Release mode rejects uncontrolled
status codes and blocks unresolved states; audit mode is never a release substitute.
Effective fact identity includes `report_id`; same-key duplicates require exactly one explicit
current fact. Row order is never an overlay precedence rule. Every accessible file under the
declared source-package root must be included in complete search, regardless of free-text role.

Do not replace a bad cell only at display time. The fact lineage must be repaired first. The
`NA` response in a TRIPOD+AI or PROBAST+AI item is a controlled appraisal answer and must not be
removed as a legacy placeholder.

## Minimal model and view rules

- Keep one row per minimal model unit. Separate original, penalized, updated, recalibrated,
  score/nomogram, comparator, and external-evaluation branches.
- Preserve mother-model lineage for fitted regression-derived scores and nomograms.
- Keep `03_模型` and `03_预测因子` as separate views. Link predictors through `模型实体ID` and
  `模型家族ID`; do not collapse model method fields into predictor rows.
- Materialize `02_队列数据集` at `dataset × analysis population`, preserving training, tuning,
  internal test, apparent, temporal external, geographic external, and time-geographic external
  roles separately.
- Keep `04_性能`, `05_阈值四格`, and `06_校准临床价值` linked to model, dataset, outcome,
  analysis-population, and evaluation-context IDs.

## Current-study sentinels

The following checks are mandatory because they previously exposed migration defects:

- `STU-005 / MOD-STU005-LR01`: candidate parameter count is source-not-reported, not literal `NR`.
- `STU-011`: the later infection branch is a future-event prognosis branch and stays outside the
  diagnostic synthesis pool.
- `STU-013`: external performance must remain linked to the correct LASSO model and evaluation
  context; do not attach it to the score or an unpenalized mother model.
- `STU-016`: machine-learning models do not inherit the logistic model's predictor count unless
  the source explicitly reports the same feature set.

## Release checks

Before releasing a generated workbook:

1. required-field gaps for eligible studies are zero, with excluded-study gaps reported separately;
2. every observed performance, threshold, and calibration value has closed model/dataset/outcome/
   analysis-population/context links;
3. every predictor has a valid model entity link;
4. no substantive view contains literal legacy `NR`/`NA`/`N/A` placeholders;
5. model algorithm taxonomy passes in freeze mode;
6. no formula or workbook error is present;
7. workbook is reopened after export and checked against the fact/companion tables;
8. regression tests pass.
9. every `NR_SOURCE` passes the renewed-review evidence and complete source-manifest coverage gate;
10. every `NA_STRUCTURAL` has a valid deterministic structural-rule identifier.

`NR_SOURCE` counts may remain when the complete source package truly does not report a field.
They are not data loss when the status, search scope, and rationale are present.
