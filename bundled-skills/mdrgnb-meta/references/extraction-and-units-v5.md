# Extraction and Unit Protocol v5.6

Use `extraction-data-contract-v56.md` for source reading, field-level facts, missingness,
adjudication failure, review questions, merging, and export. Its rules supersede legacy `NR`/`NA`
defaults while this file remains authoritative for entity meaning and dataset roles.

## Identity hierarchy

Use stable keys:

`source_record_id -> report_id -> study_id -> cohort_id -> outcome_id -> model_id -> dataset_id -> performance_id -> threshold_id/calibration_id`.

Also assign:

- `independent_cohort_id` for statistical independence;
- `model_family_id` for development/validation reports of the same model;
- `dependent_effect_cluster_id` for multiple effects from the same participants;
- `synthesis_group_id` for clinically/statistically comparable effects.

Duplicate reports and overlapping cohorts are different problems. Link repeated reports without
counting them twice; retain distinct reports that evaluate the same named model in different
cohorts.

## Atomic unit

The extraction unit is:

`report × study × cohort × outcome × model × dataset × metric × threshold/subgroup/timepoint`.

`study_id` remains a required foreign key even when a cohort uniquely determines its study.
Subgroup and timepoint are explicit dimensions of the performance unit, not free-text notes.

Do not manufacture a performance row for a training dataset when no training/apparent result was
reported. A dataset can exist without a performance effect.

## Cross-report semantic-granularity contract

The normative syntax, encoding, suffix order, crosswalk, and migration rules are in
`semantic-key-v1.md`. This section defines entity meaning; it must not override that contract.

Use identical semantic keys across all 40 reports. Equal granularity means equal decision rules,
not equal row counts. A richly reported paper may legitimately have more rows, but the same fact
must never be split more finely merely because more prose is available.

| Entity | One row means | Split only when |
|---|---|---|
| `report` | one publication/source report | a genuinely distinct publication exists |
| `study` | one research project represented by the report | the report explicitly contains separable research projects with distinct designs/cohorts |
| `cohort` | one physical source population/sample | participants, site/time source, or sampling frame differs |
| `dataset` | one role instance of a cohort | model-development/evaluation role, analysis population, or external-validation axis differs |
| `outcome` | one target-state × T0 × reference-standard signature | target, T0, reference standard, or case/control definition materially differs |
| `model` | one fixed deployable equation/score/algorithm specification | fitted parameters/rule, predictor set, algorithm, or model version differs |
| `performance` | one model × outcome × dataset × analysis population × metric × subgroup/timepoint context | any member of that key differs |
| `threshold` | one threshold-specific classification result linked to one performance context | threshold or threshold-selection context differs |
| `calibration` | one calibration/utility metric in one performance context | metric, dataset, analysis population, subgroup, or timepoint differs |
| `predictor` | one predictor construct/coding within one model role | construct, window, unit, coding, or model coefficient differs |

Rules:

- Multiple thresholds do not create duplicate AUC/performance rows.
- Multiple algorithms evaluated on the same participants are separate models but dependent effects.
- Pooled and site-specific estimates from overlapping participants are separate atomic estimates linked
  to one dependency cluster; they are not independent cohorts.
- Training and apparent-performance role instances on the same participants share physical cohort and
  independent-cohort IDs.
- A different analysis population creates a separate performance/PROBAST Evaluation scope even when
  model, dataset label, and metric name are unchanged.
- Hyperparameter trials are not separate deployable models unless the report presents them as fixed,
  separately evaluated model specifications.
- Identical semantic keys within a report are duplicates, not additional evidence.
- Required fields use explicit missingness codes; sparse reporting never justifies a coarser entity key.

Every branch must produce `granularity_alignment.tsv` with:

`alignment_id, report_id, study_id, entity_type, entity_id, semantic_key, physical_cohort_id,
analysis_population_id, outcome_signature, model_signature, dataset_role_code, metric_context,
split_link_code, parent_or_peer_entity_id, alignment_rationale, source_evidence_id, reviewer_id,
review_round, adjudication_status`.

Allowed split/link codes:

- `BASE_ENTITY`
- `SPLIT_DIFFERENT_PHYSICAL_COHORT`
- `SPLIT_DIFFERENT_TARGET`
- `SPLIT_DIFFERENT_REFERENCE_STANDARD`
- `SPLIT_DIFFERENT_T0`
- `SPLIT_DIFFERENT_FIXED_MODEL`
- `SPLIT_DIFFERENT_DATASET_ROLE`
- `SPLIT_DIFFERENT_ANALYSIS_POPULATION`
- `SPLIT_DIFFERENT_METRIC_CONTEXT`
- `SPLIT_DIFFERENT_SUBGROUP_TIMEPOINT`
- `LINK_SAME_PHYSICAL_COHORT`
- `LINK_SAME_MODEL_FAMILY`
- `DEPENDENT_SAME_PARTICIPANTS`
- `DUPLICATE_SEMANTIC_KEY_REMOVED`

The first five-report pilot is not grandfathered. Re-audit and, when needed, split/link/merge its
entities under this same contract before combining it with later batches. Preserve all corrections
in the change log; never silently rewrite a frozen row.

Every adjudicated batch must also produce `semantic_key_crosswalk.tsv` using the exact columns and
mapping decisions in `semantic-key-v1.md`. Keep v5.3 source keys immutable and add v5.4 final keys;
do not normalize frozen branch strings in place. Coarse-to-fine source splits and many-to-one
merges require the relation-group and branch-specific cardinality fields from that contract;
repeating a convenient first source ID across unrelated final entities is invalid.

## Eligibility-scope relationship

Eligibility is not a report-only label. Create one `eligibility_scope_id` for each
`report × study × cohort × outcome × fixed/provisional model branch × T0 signature` and link it to
the canonical outcome/model entities. When a base and optimized branch differ in current-organism
inputs, or one outcome is current and another future, they require separate eligibility scopes.

Store the full field contract from `eligibility-protocol-v5.md`. In particular, keep
`current_organism_input_at_t0_01` separate from `organism_restricted_cohort_01`; store both level
and basis codes. A provisional branch with an unreported final predictor set remains in inventory
but cannot own an active performance or synthesis membership until fixed/adjudicated.

## Dataset roles

Resolve the source label and the harmonized role separately:

| Code | Operational definition |
|---|---|
| `DEVELOPMENT_TRAINING` | Used to estimate model parameters or learn rules. |
| `TUNING_VALIDATION` | Used for hyperparameter/feature/threshold tuning; not an unbiased evaluation set. |
| `APPARENT_TRAINING_PERFORMANCE` | Performance evaluated on data used for fitting without optimism correction. |
| `INTERNAL_RESAMPLING_OOF` | Bootstrap/CV/out-of-fold performance from the development source population. |
| `INTERNAL_HOLDOUT_TEST` | Participant-level holdout from the same source/timeframe before fitting. |
| `EXTERNAL_TEMPORAL_EVALUATION` | Later period from the same intended setting/site. |
| `EXTERNAL_GEOGRAPHIC_EVALUATION` | Different site/system/region without a material temporal shift. |
| `EXTERNAL_TEMPORAL_GEOGRAPHIC_EVALUATION` | Both later period and different geography/system. |
| `EXTERNAL_EVALUATION_UNCLEAR_AXIS` | External evaluation is established but its temporal/geographic axis cannot be resolved. |
| `UNCLEAR_DATASET_ROLE` | Source insufficient; requires adjudication. |

Record two orthogonal external attributes in addition to the role:

- `external_validation_axis_code`: `NONE`, `TEMPORAL`, `GEOGRAPHIC`,
  `TEMPORAL_GEOGRAPHIC`, or `UNCLEAR`;
- `investigator_relation_code`: `SAME_DEVELOPER_TEAM`, `PARTIAL_DEVELOPER_OVERLAP`,
  `INDEPENDENT_INVESTIGATORS`, or `UNCLEAR`.

Investigator independence is not a mutually exclusive dataset role. Do not overwrite a temporal,
geographic, or temporal-geographic evaluation label with investigator independence.

If the same physical development data are both used for fitting and used to report apparent
performance, create linked `DEVELOPMENT_TRAINING` and `APPARENT_TRAINING_PERFORMANCE` role
instances. They must share cohort and independent-cohort identifiers and be linked as nested/same
physical data; never count them as independent cohorts.

Record split level (patient/episode/specimen/site), split method, recruitment dates, sites,
developer overlap, tuning use, and whether preprocessing/selection occurred before the split.

## Required extraction blocks

1. Report/study: citation, country, setting, design, recruitment, prospective/retrospective,
   eligibility, adult basis, funding/conflicts.
2. Cohort/dataset: source, sites, dates, N, events/non-events, prevalence, inclusion flow,
   dataset role and external-validation axes.
3. Outcome/reference standard: current-state target, infection/colonization/mixed, phenotype,
   species scope, specimen, laboratory method, standard/year, timing.
4. Model: name, family, algorithm, candidate/final status, predictors, formula/accessibility,
   preprocessing, feature selection, hyperparameter tuning, class imbalance, missing data.
5. Performance: metric raw/normalized, estimate, CI/SE, scale, analysis population, subgroup,
   derivation, apparent/internal/external label.
6. Threshold/2×2: threshold, TP/FP/FN/TN, sensitivity, specificity, PPV, NPV, derivation status.
7. Calibration/utility: calibration plot, intercept, slope, O:E, Brier score, DCA/net benefit,
   decision threshold and clinical-use claim.
8. Implementation: intended user, T0 data availability, usability, external evaluation, impact
   study, code/calculator, fairness, and clinical readiness.
9. Eligibility scope: outcome/model-branch/T0 identity, current target, known-organism input,
   organism-restricted cohort, final branch status, synthesis eligibility, and evidence.

## Standardization

For interpreted terms store at least:

- `*_raw`;
- `*_normalized_code` and bilingual label when useful;
- mapping version, rationale, confidence, reviewer, and adjudication status.

Do not merge predictors solely by similar wording. Preserve construct, measurement window,
measurement unit, drug class, and availability at T0. Language is provenance, not an analysis
stratum.

For v5.5 model and predictor classification, `analysis-set-and-taxonomy-v55.md` is authoritative.
Model algorithm, presentation form, data modality, model role, and review task are orthogonal
dimensions. Predictor frequency uses the source variable -> minimal clinical construct -> modifier
-> operationalization chain and is primarily counted once per independent development report.

For every model, additionally apply `algorithm-taxonomy-v58.md`. Algorithm fields belong to the
MODEL entity, not the PREDICTOR entity. A score/nomogram must preserve its mother-model link, and
all algorithms evaluated on the same participants must share a dependency cluster.

## Dual extraction

Extractor A and B receive the same source package, schema version, and candidate unit list but
not each other's outputs. Each returns row-shaped records plus evidence anchors. Compare at the
field level. Send disagreements that alter eligibility, identity, N/events, outcome, dataset role,
model, performance, or synthesis grouping to a third adjudicator.

Store reviewer A, reviewer B, and final evidence IDs separately for all dual-reviewed judgments.
A shared evidence ID does not demonstrate independent extraction.

Before finalizing each performance value, reproduce reported percentages and check denominator
consistency. Never back-calculate 2×2 cells from conflicting rounded metrics. Mark derivation as
`REPORTED`, `DERIVED_VALIDATED`, `NOT_CALCULABLE`, or `CONFLICT`.
