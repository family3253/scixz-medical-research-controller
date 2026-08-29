# Model algorithm taxonomy v5.8

## Purpose

This protocol makes algorithm extraction comparable across all 40 audit reports and directly
supports the prespecified secondary subgroup of traditional statistical models versus machine
learning models. It applies at the fixed-model level. It does not alter eligibility, and it must
not import diagnostic/prognostic decisions or study counts from Liu 2024.

## Required model-level fields

Store the following as separate facts for every fixed eligible or candidate model:

| Field | Meaning |
|---|---|
| `algorithm_name_raw` | Verbatim algorithm/model label in the source. |
| `algorithm_name_normalized` | Specific normalized algorithm name. |
| `algorithm_family_v58` | Mutually exclusive technical family below. |
| `algorithm_superclass_v58` | `TRADITIONAL_STATISTICAL`, `MACHINE_LEARNING`, `EXPERT_OR_HEURISTIC_RULE`, or `OTHER_UNCLEAR`. |
| `traditional_vs_ml_code` | `TRADITIONAL`, `MACHINE_LEARNING`, or `NOT_CLASSIFIABLE`. |
| `regularization_code` | `NONE_REPORTED`, `LASSO_L1`, `RIDGE_L2`, `ELASTIC_NET`, `OTHER`, or `UNCLEAR`. |
| `ensemble_status` | `NOT_ENSEMBLE`, `BAGGING_RANDOMIZED_TREES`, `BOOSTING`, `STACKING_VOTING`, `OTHER_ENSEMBLE`, or `UNCLEAR`. |
| `mother_model_id` | Fixed fitted model from which a score, nomogram, or simplified rule was derived; structural NA only when truly not derived. |
| `score_derivation_code` | `NOT_SCORE`, `COEFFICIENT_BASED_INTEGER_SCORE`, `NOMOGRAM`, `SIMPLIFIED_RULE`, `EXPERT_RULE`, `OTHER`, or `UNCLEAR`. |
| `author_designated_final_01` | Whether authors designated this model as final/preferred. |
| `model_role_code` | Author-final, simplified derivative, candidate/comparator, updated/recalibrated, or fixed external-evaluation model. |
| `dependent_effect_cluster_id` | Shared participant/evaluation cluster for correlated algorithm effects. |

`model_family_id` remains a lineage identifier and must not be used as the algorithm class.
Presentation form, algorithm, model role, and data modality are orthogonal.

## Technical families

Use one `algorithm_family_v58`:

- `LOGISTIC_REGRESSION_UNPENALISED`
- `LOGISTIC_REGRESSION_PENALISED`
- `OTHER_CONVENTIONAL_REGRESSION`
- `DISCRIMINANT_OR_BAYES_CLASSIFIER`
- `EXPERT_OR_HEURISTIC_RULE`
- `DECISION_TREE_SINGLE`
- `RANDOM_FOREST_OR_EXTRA_TREES`
- `GRADIENT_BOOSTING_TREE`
- `SUPPORT_VECTOR_MACHINE`
- `K_NEAREST_NEIGHBOURS`
- `NEURAL_NETWORK_OR_DEEP_LEARNING`
- `STACKED_VOTING_OR_OTHER_ENSEMBLE`
- `OTHER_ALGORITHM`
- `ALGORITHM_UNCLEAR`

## Superclass and binary mapping

Map unpenalized/penalized logistic regression, other conventional regression, and classical
discriminant/Bayes classifiers to `TRADITIONAL_STATISTICAL` and `TRADITIONAL`.

Map a data-trained single decision tree, random forest/Extra Trees, gradient boosting including
GBDT/XGBoost/LightGBM/CatBoost, SVM, KNN, neural/deep learning, and data-trained stacking/voting
to `MACHINE_LEARNING` and `MACHINE_LEARNING`.

Map a purely expert/heuristic rule without a fitted mother model to
`EXPERT_OR_HEURISTIC_RULE` and `NOT_CLASSIFIABLE`. Do not force it into the two-level subgroup.
Unclear or other algorithms remain `OTHER_UNCLEAR`/`NOT_CLASSIFIABLE` pending adjudication.

## Boundary rules

1. LASSO, ridge, and elastic-net logistic regression are traditional statistical models for the
   binary subgroup. Preserve their penalization in `regularization_code`.
2. A nomogram, integer score, or bedside rule derived from regression inherits the mother's
   algorithm superclass. Presentation as points does not create a new algorithm.
3. A score and its mother regression may be separate deployable model entities, but they share
   lineage. Do not count both as independent evidence.
4. Recalibration, coefficient shrinkage, intercept update, and complete coefficient re-estimation
   create model versions/roles; they do not automatically change the algorithm family.
5. Feature selection is not the prediction algorithm. LASSO used only for feature selection
   followed by an unpenalized final logistic fit is coded by the final fit, with selection details
   stored separately.
6. SMOTE, imputation, normalization, and hyperparameter search are preprocessing/training
   procedures, not algorithms.
7. A paper's use of the term "machine learning" is not decisive. Store
   `author_claimed_ml_01` separately when useful and apply this protocol consistently.
8. Multiple algorithms on one train/test split are distinct models but dependent effects. They
   share `dependent_effect_cluster_id`; none is an independent study.
9. Do not choose the highest AUC within a study to represent an algorithm class. Prefer the
   author-designated final model under the prespecified effect-selection hierarchy. Sensitivity
   analyses may use all effects with multilevel or CR2 methods.

## Liu 2024 Table 1 field-coverage crosswalk

Liu 2024 Table 1 is a coverage reference, not an eligibility or counting authority. The current
review should retain these concepts using its stricter diagnostic-only schema:

| Liu concept | Current-review field/block |
|---|---|
| Publication year, country | Report/study metadata |
| Single/multicentre | `centre_count`, `site_scope_code`, cohort sites |
| Target setting | `setting_bucket` plus raw clinical setting |
| Target timing | `t0_raw`, `t0_bucket`, prediction-time availability |
| Infection/colonization type | `outcome_bucket`, clinical syndrome |
| MDRO phenotype | `phenotype_bucket`, organism/species and resistance phenotype |
| Study design | design plus prospective/retrospective and sampling design |
| Development/validation N and events | analysis-population rows linked to dataset roles |
| Modelling method | the v5.8 model-level algorithm fields |
| Discrimination | performance rows, metric, estimate, uncertainty and derivation |
| Calibration | intercept, slope, O:E, Brier, plot, H-L separately |
| Internal validation | dataset role and resampling/split method |
| External validation | temporal/geographic axis and investigator relation as orthogonal fields |

Unlike Liu 2024, do not combine prognostic/future-event models, known-current-organism
classification, or organism-restricted cohorts with this diagnostic review.

## Synthesis use

The traditional-versus-ML comparison is secondary. The preferred analysis uses out-of-sample AUC
effects only, preserves validation level and phenotype, and accounts for study/cohort dependence.
Run it only with adequate independent cohorts in both groups. Report the subgroup coefficient or
interaction with its uncertainty rather than comparing two pooled point estimates informally.
If sparse, tabulate and narrate.

At minimum report:

- number of independent reports/cohorts/models in each superclass;
- apparent versus out-of-sample performance separately;
- author-final versus comparator/candidate models;
- sensitivity analysis restricted to one prespecified effect per independent cohort;
- multilevel or cluster-robust analysis when all algorithm effects are retained.

