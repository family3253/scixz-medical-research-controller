# SEMKEY_V1 contract

Use identical semantic keys across all reports. Equal granularity means identical split rules, not
equal row counts. Keep raw source terms outside keys.

## Encoding

Every key begins:

`v=SEMKEY_V1|entity=<entity>|report=<report_id>|study=<study_id>`

Encode each value as UTF-8, then percent-encode `%`, `|`, and `=` as `%25`, `%7C`, and `%3D`.
Accept only uppercase hex in canonical final keys. Decode before comparing values. Use
`NA_STRUCTURAL` for deterministic non-applicability, `NR_SOURCE` only after a complete-source
targeted search, and `UNCLEAR` for insufficient evidence. `NOT_CAPTURED`, `PENDING_REVIEW`,
`CONFLICT`, and legacy `NA`/`NR` are forbidden in frozen final keys.

## Fixed suffixes

| Entity | Ordered suffix |
|---|---|
| study | `project` |
| cohort | `source, site_time, sampling` |
| dataset | `cohort, role, population, axis` |
| outcome | `target, t0, reference, case_control` |
| model | `family, algorithm, predictors, version` |
| performance | `model, outcome, dataset, population, metric, subgroup, timepoint` |
| threshold | `performance, threshold, selection` |
| calibration | `performance, metric` |
| predictor | `model, construct, window, unit, coding, coefficient` |

One active entity is unique on `(report_id, study_id, entity_type, entity_id)`. One final key may
identify only one active entity. Validate foreign keys and controlled vocabulary in addition to
string shape.

## Crosswalk

Keep A, B, blind-third, and final keys. Required columns:

`crosswalk_id, report_id, study_id, entity_type, a_entity_id, a_semantic_key,
b_entity_id, b_semantic_key, third_entity_id, third_semantic_key, final_entity_id,
final_semantic_key, mapping_decision, mapping_rationale, final_evidence_id,
adjudicator_id, adjudication_timestamp, qa_status, relation_group_id,
a_source_cardinality, b_source_cardinality, third_source_cardinality,
final_cardinality, relation_basis_code, relation_evidence_id`.

Allowed `mapping_decision`:

- `ONE_TO_ONE`
- `MERGED_TO_FINAL`
- `SPLIT_TO_FINAL`
- `REMOVED_DUPLICATE`
- `REMOVED_INELIGIBLE_ENTITY`
- `ADDED_BY_ADJUDICATION`

Every non-`NA` source entity must have exactly one explicit destination/removal decision. Every
final entity must have at least one crosswalk row. A/B disagreement cannot be resolved by changing
spelling to create artificial entities.

### Auditable split/merge relations

One source entity may legitimately map to several final entities only through an explicit
`SPLIT_TO_FINAL` relation group. This is required when, for example, a reviewer extracted one
coarse age-category predictor while final adjudication separates three age levels. A relation group
contains one row per final entity and repeats the coarse source entity only within that group.

`a_source_cardinality`, `b_source_cardinality`, and `third_source_cardinality` are the number of
unique source entities from each represented branch in the relation group; `final_cardinality` is
the number of unique final entities. The relation is valid only when all rows share one
`relation_group_id`, one valid `relation_basis_code`, and one nonblank `relation_evidence_id`.
Allowed bases are `IDENTITY`, `SOURCE_COARSE_TO_FINER`, `SOURCE_CATEGORY_GROUP_TO_LEVELS`,
`SOURCE_COMPOSITE_TO_COMPONENTS`, `MULTIPLE_SOURCE_TO_ONE_FINAL`, `SOURCE_REMOVAL`, and
`ADJUDICATOR_ADDITION`.

- `ONE_TO_ONE`: one source from each represented branch and one final entity, one row.
- `SPLIT_TO_FINAL`: at least two final entities, one row per final, and at least one repeated
  coarse source entity.
- `MERGED_TO_FINAL`: at least two source entities in at least one branch and one final entity.
- removal: represented sources and zero final entities.
- adjudicator addition: zero source entities and one final entity.

Source reuse outside an explicit, cardinality-consistent split relation is a blocking error. In
particular, attaching the first source predictor ID to unrelated final predictors cannot be made
valid merely by relabeling the rows as a split: the group needs a coherent basis and evidence.

## Split/link rules

Use the following codes:

`BASE_ENTITY, SPLIT_DIFFERENT_PHYSICAL_COHORT, SPLIT_DIFFERENT_TARGET,
SPLIT_DIFFERENT_REFERENCE_STANDARD, SPLIT_DIFFERENT_T0, SPLIT_DIFFERENT_FIXED_MODEL,
SPLIT_DIFFERENT_DATASET_ROLE, SPLIT_DIFFERENT_ANALYSIS_POPULATION,
SPLIT_DIFFERENT_METRIC_CONTEXT, SPLIT_DIFFERENT_SUBGROUP_TIMEPOINT,
LINK_SAME_PHYSICAL_COHORT, LINK_SAME_MODEL_FAMILY, DEPENDENT_SAME_PARTICIPANTS,
DUPLICATE_SEMANTIC_KEY_REMOVED`.

One physical training cohort may have fitting and apparent-performance dataset roles but must
share cohort/independent-cohort IDs. Multiple thresholds do not duplicate AUC. Multiple algorithms
on the same participants are models in one dependency cluster. Changed analysis populations split
performance and PROBAST Evaluation scopes. Pooled and centre-specific estimates sharing
participants remain dependent. Hyperparameter trials are not deployable models unless fixed and
separately evaluated.

## Compatibility

Never rewrite a frozen v5.3 key. Store it as a source key and create a v5.4 canonical final key via
crosswalk. `--compat-v53` may downgrade noncanonical escaping or legacy mapping decisions to
warnings during a forward audit; it must never suppress duplicate final keys, orphan entities,
report/study mismatches, or repeated source entities in a legacy crosswalk lacking an explicit
v5.4 relation group.
