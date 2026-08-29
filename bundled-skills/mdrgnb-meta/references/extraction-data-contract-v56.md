# Extraction Data Contract v5.6

This contract governs new extraction, legacy migration, adjudication, and workbook export. It
supersedes any earlier instruction that treats a blank, missing key, `NR`, or `NA` as one meaning.

## 1. Source package and staged reading

Create a source manifest before extraction. Inventory the main report, supplements, appendices,
registrations, corrections, and linked validation reports with file ID, SHA-256, format, page
count, text-layer status, OCR status, table/image presence, and access status.

The machine-checkable source manifest must contain at least:

`source_file_id, report_id, source_sha256, source_role, access_status, text_layer_status,
ocr_status, page_count, included_in_complete_search_01`.

Use this sequence for every report:

1. verify report identity and source completeness;
2. extract or OCR every relevant page, preserving page boundaries and tables;
3. enumerate candidate study, cohort, outcome, model, dataset, and metric units;
4. search targeted sections/tables/supplements for each unit and field block;
5. extract row-shaped facts with evidence anchors;
6. run arithmetic, denominator, range, and foreign-key checks;
7. freeze independent A and B branches, compare them, then adjudicate;
8. write adjudicated facts and generated views only after QA.

Never treat a fixed leading-character slice as the full report. When model methods, results,
tables, or supplements fall outside extracted text, use `SOURCE_NOT_ACCESSIBLE` or
`NOT_CAPTURED`, not `NR_SOURCE`. Figure/table-only values require targeted table extraction,
OCR, or an explicit manual-review flag; do not estimate pixels by eye.

## 2. Relational extraction architecture

Use the entity hierarchy and atomic unit in `extraction-and-units-v5.md`. Keep separate tables for
report/study, cohort, outcome, model, dataset, performance, threshold/2x2, calibration/utility,
predictor, appraisal, evidence, reviewer branch, adjudication, and review questions.

Do not force unlike entities into one universal wide row. A report with several models or datasets
must have separate linked rows. A dataset may exist without a performance row. AUC, calibration,
and threshold-specific classification are different facts; multiple thresholds do not duplicate
one AUC.

The canonical field-level fact table contains:

`fact_id, report_id, study_id, entity_type, entity_id, field_name, raw_value,
normalized_value, value_status_code, status_rationale, evidence_id, extractor_id,
review_round, branch_status, adjudication_status, status_rule_id, context_json, writeback_table,
writeback_key`.

The evidence table contains:

`evidence_id, report_id, source_file_id, source_sha256, page_or_location, table_figure_section,
evidence_span, extraction_method, search_scope, reviewer_id, timestamp`.

For interpreted values, retain raw text and normalized code/value together. A normalized value
without raw source evidence is invalid unless it is explicitly derived; derived facts must link
all inputs and the derivation rule.

## 3. Controlled value-status codes

Use one code per tracked fact:

| Code | Meaning | Required conditions |
|---|---|---|
| `OBSERVED` | Reported or validly derived value is available | raw and/or normalized value plus evidence; derivation method when derived |
| `NR_SOURCE` | Applicable field was actively searched in the complete accessible source package and was not reported | nonempty search scope and rationale; never assigned from a missing JSON/CSV key |
| `NA_STRUCTURAL` | Field cannot apply to this entity/design | deterministic structural rule and rationale; no invented entity row |
| `NOT_CALCULABLE` | Desired value cannot be calculated from available valid inputs | missing inputs or arithmetic reason documented |
| `NOT_RUN` | Analysis/procedure was explicitly not performed or cannot exist for the retained component | evidence or deterministic design rule; absence alone is insufficient |
| `NOT_CAPTURED` | Field has not yet been systematically extracted or is a legacy placeholder | blocks field-complete closure |
| `UNCLEAR` | Source is accessible but meaning, denominator, unit, or mapping remains ambiguous | evidence and ambiguity rationale; eligible for review question |
| `PENDING_REVIEW` | Extraction/adjudication workflow has not resolved the field | open review question required for material fields |
| `SOURCE_NOT_ACCESSIBLE` | Required source page/file/supplement cannot be reliably accessed | source/access log required; report may be blocked |
| `CONFLICT` | Two or more credible source/extractor values conflict | all competing evidence and an open adjudication question required |

`0` is an observed value only when the source explicitly reports zero or valid denominators prove
zero. A blank is never a final tracked value. Do not store literal `NR`, `NA`, `N/A`, `unknown`,
or `not reported` in raw/normalized value columns as a substitute for a status code.

Legacy migration is conservative:

- blank, `NR`, `NA`, `N/A`, `unknown` -> `NOT_CAPTURED` by default;
- promote to `NR_SOURCE` only after complete-source targeted search;
- promote to `NA_STRUCTURAL` only from a documented deterministic rule;
- preserve the legacy cell in a migration/audit column;
- never overwrite a frozen source artifact.

Every `NA_STRUCTURAL` fact must link `status_rule_id` to a versioned structural-rule table with
`rule_id, entity_type, field_name, condition_field, condition_operator, condition_value,
rule_version, rationale, active_01`. Evaluate the rule against the fact's `context_json`; merely
registering or naming a rule is insufficient. Free-text "not applicable" is not a rule. Every
`NR_SOURCE` fact must link a machine-readable search scope matching its study, entity type, entity
ID, and field, and covering all accessible relevant source files in the source manifest.

## 4. Extraction prompts and response validation

Generate prompts per candidate unit and field block, not one report-wide fixed schema. Supply the
relevant source passages and tables plus the unit identity. Require structured output with entity
keys, fact values, value-status codes, evidence spans/locators, confidence, and unresolved issues.

Reject an extraction response when it has schema drift, unknown fields/codes, missing entity keys,
unverifiable evidence, values outside valid ranges, or a different unit than requested. Missing
keys are extraction failures (`NOT_CAPTURED`), not source non-reporting (`NR_SOURCE`).

Use targeted retrieval after the first pass for unresolved high-value fields: cohort N/events,
outcome/reference standard, predictor definitions, model formula/score, dataset split and role,
AUC/CI, calibration, threshold/2x2, missing-data handling, and appraisal evidence.

## 5. Independent extraction and adjudication

A and B must receive the same versioned source package, schema, unit inventory, and field list but
not each other's answers. Preserve their raw outputs before normalization and comparison.

Compare by semantic entity key and field, not row order. Distinguish:

- equivalent normalization or formatting;
- one branch `NOT_CAPTURED` versus the other having evidence;
- conflicting values/evidence;
- missing or extra entities;
- different dataset/model/outcome granularity.

Material disagreements and every entity split/merge go to a third adjudicator. The adjudicator
must replay the source evidence. If arbitration, parsing, API, or source retrieval fails, write
`PENDING_REVIEW` and keep the branch open. Never fall back silently to A, B, Round 1, the first
nonmissing value, or the smaller schema.

## 6. Question-based human review

Create a review question only when a genuine judgment remains after targeted retrieval and
automated QA. Do not ask users to resolve `NA_STRUCTURAL` or confirmed `NR_SOURCE`. Do not convert
bulk `NOT_CAPTURED` legacy fields into thousands of questions; re-extract those fields first.

Each question must include:

`question_id, priority, report_id, entity_type, entity_id, field_name, issue_type,
evidence_a, evidence_b, source_locator, recommended_answer, recommendation_basis,
options_json, user_answer, adjudication_rationale, status, writeback_table, writeback_key,
writeback_field, expected_type, allowed_values, created_at, resolved_at`.

Options must be mutually exclusive and collectively sufficient for the known issue, normally two
to five choices. Include `无法判定/需补证据` only when it is a legitimate terminal or routing
state. A nonblank recommendation must be one of the listed options; it is not a final value until
confirmed/adjudicated. Writeback must validate
type, allowed vocabulary, entity identity, and old-value/version precondition, and must append a
change-log row.

## 7. Merge and workbook export

Merge by schema version and canonical keys, never by filename order or raw row position. Before
concatenation, validate:

- required headers and field types;
- source/report/study identity and hashes;
- primary/foreign keys and duplicate active facts;
- entity granularity and SEMKEY crosswalks;
- dataset role and validation axes;
- allowed value-status codes and evidence requirements;
- A/B/final branch state and unresolved adjudication;
- numerical ranges, CI order, denominators, 2x2 arithmetic, and scale;
- dependency, model-family, and synthesis-group IDs;
- prohibited literal missing tokens and silent fallback markers.

Long fact/evidence/appraisal tables are authoritative. Wide sheets are generated views scoped to
one entity type or reporting purpose. Structural cells in a wide view may display blank or the
localized label for `NA_STRUCTURAL`, but must not create canonical facts or inflate `NR` counts.
Publish a missingness audit by table, field, entity, and code, separating `NR_SOURCE` from
`NOT_CAPTURED` and structural non-applicability.

When legacy schemas, independently reviewed branches, or companion value tables are involved,
also apply `schema-recovery-v57.md`. Field-level overlay and keyed companion materialization are
mandatory. A narrow final row, ordered header union, or display-only missing-token replacement is
not a valid merge. Every nonmissing source field must be mapped, classified as provenance, or
reported as a blocking unmapped field.

## 8. Closure gates

A report cannot be `CLOSED_FIELD_COMPLETE` while a required field is `NOT_CAPTURED`,
`PENDING_REVIEW`, or `CONFLICT`, while evidence/foreign keys are invalid, or while a material unit
has not completed A/B/adjudication. `SOURCE_NOT_ACCESSIBLE` routes to
`BLOCKED_SOURCE_UNAVAILABLE`, not field-complete closure.

Run `scripts/qa_extraction_package_v56.py` with the fact, evidence, source-manifest,
structural-rule, and review-question tables in branch mode during extraction and freeze mode before
writeback. Run `scripts/regression_check.py` and the existing identity, semantic-key, eligibility,
pool, and coverage gates before synthesis.
