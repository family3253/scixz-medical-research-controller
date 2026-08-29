# Analysis set and taxonomy protocol v5.5

## Locked report-level analysis sets

- `AUDIT_POOL_40`: immutable provenance pool of 40 unique reports reconstructed from 41 source
  records. Inclusion in this audit pool does not imply review eligibility.
- `PRIMARY_DIAGNOSTIC_39`: the 39 reports with at least one eligible adult MDR-GNB current-state
  diagnostic model branch.
- `STRICT_ADULT_38`: `PRIMARY_DIAGNOSTIC_39` excluding `STU-016` because the author-defined adult
  liver-transplant cohort reports an age range of 12--76 years.
- `STU-005` is a report-level exclusion: baseline CRE-negative patients were followed for future
  incident/first CRE/CRO detection. This is prognosis/future acquisition, not current-state
  diagnosis.
- `STU-016` is included in the primary set because the report defines an adult cohort and has a
  median age of 54 years. It is excluded only from the strict-adult sensitivity analysis.

Every table and manuscript count must identify which set is used. Do not call the 40-report audit
pool the included set.

## Role of Liu 2024

Liu 2024 is an external methodological comparator only. It may inform discussion of diagnostic
versus prognostic concepts, calibration, external validation, or prior review gaps. Do not import
its model classes, predictor groups, predictor frequencies, PROBAST proportions, study-level
limitations, eligibility of known-organism classification, or pooled results into this review.
All reported counts and judgments must be recomputed from this review's eligible branches.

## Model classification: orthogonal dimensions

For algorithm fields and traditional-versus-machine-learning subgroup assignment,
`algorithm-taxonomy-v58.md` is authoritative and supersedes the v5.5 family list below. The
remaining v5.5 dimensions continue to apply.

Do not force model labels into one mutually exclusive column when they describe different
properties. Code each eligible fixed model on all applicable dimensions:

1. `review_task_code`: `NEW_MODEL_DEVELOPMENT`, `MODEL_UPDATE_RECALIBRATION`,
   `EXTERNAL_EVALUATION_ONLY`, or `DEVELOPMENT_AND_EXTERNAL_EVALUATION`.
2. `algorithm_family_v55`: `REGRESSION_UNPENALISED`, `REGRESSION_PENALISED`,
   `POINT_SCORE_OR_RULE`, `TREE_OR_SINGLE_TREE`, `TREE_ENSEMBLE_OR_BOOSTING`,
   `KERNEL_OR_INSTANCE_BASED`, `NEURAL_OR_DEEP_LEARNING`, `STACKED_OR_OTHER_ENSEMBLE`,
   or `OTHER_UNCLEAR`.
3. `presentation_form_code`: probability equation, nomogram, integer/additive score, decision rule,
   black-box software output, or fixed model evaluated without re-presentation. Multiple forms may
   be linked to one model family.
4. `data_modality_code`: routine clinical/EHR, clinical plus routine laboratory, local ecology or
   cross-institution history, microbiome/omics, imaging, or multimodal.
5. `model_role_code`: author-designated final, simplified derivative, updated/recalibrated,
   comparator/candidate, or externally evaluated fixed model.

Primary descriptive counts use independent reports. Also provide model-family and model counts.
Do not count a nomogram and its integer score as independent evidence when they arise from the same
fitted model; link them by `model_family_id`.

## Predictor normalization

Use a four-level traceable chain:

1. source variable verbatim;
2. minimal clinical construct;
3. modifier dimensions (drug class, condition subtype, measurement source, prior/current status);
4. operationalization (unit, threshold, reference category, transformation, lookback window,
   interaction, and T0 availability).

The v5.5 parent domains are: demographics; comorbidity and immune status; function/frailty;
prior healthcare exposure; prior antimicrobial exposure; prior microbiology/infection history;
devices/procedures; current clinical presentation/infection site; current vital signs/laboratory/
severity; institution/environmental epidemiology; specialist testing/omics/imaging; and healthcare
utilization/EHR-derived features.

Main predictor frequency is one count per `report x minimal construct` among independent
development reports. Repeated external evaluation of a fixed model does not add predictor-selection
frequency. Separately report cohort, model-family, and model counts. Candidate variables, final
model inputs, fixed-model reused components, generic feature sets, and unreported feature sets are
distinct roles. Never combine coefficients, odds ratios, SHAP values, Gini importance, and
permutation importance as one effect measure.

## Bias, reporting, and limitations

- PROBAST+AI Development and Evaluation are separate scope types. Preserve signalling questions,
  domain/overall judgments, evidence, and applicability; never calculate a numeric total score.
- TRIPOD+AI assesses reporting completeness, not risk of bias.
- `AUTHOR_REPORTED_LIMITATION` must be supported by an author statement with a source locator. A
  reviewer inference cannot populate this field.
- `REVIEW_IDENTIFIED_LIMITATION` is coded independently from PROBAST+AI/TRIPOD+AI evidence and must
  state the anticipated impact.
- `REPORTING_GAP` is reserved for missing/partial TRIPOD+AI information. Do not relabel it as high
  risk of bias without the applicable PROBAST+AI logic.

At minimum, review-identified method codes cover selection/design, sample size/events, missing data,
continuous-variable handling, feature selection, class imbalance, overfitting/optimism, data
leakage, validation level, calibration, threshold selection, reconstructability, T0 availability,
reference-standard consistency, fairness/subgroup assessment, decision-curve/net benefit, impact
evaluation, and updating/maintenance.

## Field-level AUC synthesis

The v5.5 broad analysis estimates the distribution and average of reported out-of-sample
discrimination across eligible adult MDR-GNB current-state diagnostic models. It is not the
performance of one common model. Use logit-AUC, a three-level random-effects structure and
study-clustered CR2 uncertainty when estimable; report a prediction interval and leave-one-report-
out influence analysis.

Mandatory stratification or sensitivity dimensions are validation level, phenotype, infection
versus colonization/current mixed state, clinical setting, algorithm family, T0 availability, and
strict-adult set. Apparent/training performance is descriptive only. Fixed-model repeated external
validations remain a narrower model-specific synthesis. Threshold sensitivity/specificity requires
compatible thresholds and valid 2x2 data; otherwise use structured narrative synthesis.
