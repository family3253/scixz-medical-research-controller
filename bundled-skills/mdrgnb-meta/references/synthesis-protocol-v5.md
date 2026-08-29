# Synthesis Protocol v5.5

## Principle

Atomic extraction maximizes fidelity; synthesis restores comparability and independence. The
same performance row can be eligible for one analysis and ineligible for another. Never delete
an atomic row because it is not selected for the primary pool.

Use the two-pool contract in `pool-governance-v5.md`: `AUDIT_POOL_40` is a fixed report audit set;
diagnostic synthesis pools are versioned branch/performance membership tables. Never use a
report-level `CANDIDATE_ACTIVE` value as evidence that every model branch or effect is eligible.
The main report-level set is `PRIMARY_DIAGNOSTIC_39`; `STRICT_ADULT_38` is a prespecified age
sensitivity set.

## Required grouping fields

- `eligibility_scope_id`
- `synthesis_membership_id` and `pool_version`

- `independent_cohort_id`
- `dependent_effect_cluster_id`
- `model_family_id`
- `algorithm_family_v58`, `algorithm_superclass_v58`, and `traditional_vs_ml_code`
- `author_designated_final_01`, `model_role_code`, and `ensemble_status`
- `clinical_task_bucket`
- `outcome_bucket` (infection, colonization/carriage, mixed current state)
- `phenotype_bucket`
- `setting_bucket`
- `dataset_role`
- `metric_code`, scale, threshold, subgroup
- `synthesis_group_id`
- primary/secondary eligibility and selection rationale

Every active membership must have final diagnostic eligibility, a fixed model specification,
resolved performance/analysis population, final evidence, and no pending reason. Mixed reports
contribute only eligible branches. A future acquisition, known-current-organism-input, or
organism-restricted branch remains in the audit inventory and never enters a quantitative or
narrative synthesis of eligible diagnostic models as an included unit.

## Analysis families

1. Same named model family across independent cohorts: preferred when >=3 comparable evaluation
   cohorts exist. Pool discrimination, calibration, or threshold performance by metric.
2. MDR-GNB field-level discrimination across eligible models: a v5.5 exploratory main analysis of
   out-of-sample AUCs. Its estimand is the distribution and average reported discrimination of the
   model field, not the performance of one common model. Use a three-level structure and report
   phenotype, target-state, validation and model-family stratifications.
3. Multiple models/effects per cohort: secondary multilevel meta-analysis or cluster-robust variance
   estimation with CR2 small-sample correction when dependency IDs are complete. When within-cluster
   correlations are unknown, use a prespecified grid of plausible correlations and report whether
   conclusions change; do not rely on one arbitrary correlation value.
4. Sparse/incomparable evidence: structured narrative synthesis or SWiM-style grouping.

## Effect selection hierarchy

For a one-effect-per-independent-cohort primary pool, select without looking for the largest AUC:

1. independent external evaluation over developer-led evaluation;
2. external temporal/geographic evaluation over internal holdout;
3. internal holdout over resampling/out-of-fold;
4. resampling/out-of-fold over apparent training performance;
5. author-designated final/pre-specified model over exploratory variants;
6. most clinically implementable model when otherwise tied, with rationale.

Nested pooled and site-specific estimates from the same participants cannot both enter the same
analysis. Regression models and derived scores from the same cohort are dependent.

## Metrics

### AUC/C-statistic

For the broad field-level analysis, include only eligible out-of-sample effects and explicitly
label the result as cross-model and cross-phenotype. Prefer random-effects meta-analysis on logit
AUC with SE derived from a reported CI when defensible; retain the original scale and derivation
method. Use effect within independent cohort within report levels plus study-clustered CR2 when
estimable. Report tau²/variance components, prediction interval, influence and leave-one-report-out
diagnostics. Narrower clinically homogeneous groups remain mandatory stratifications; small groups
remain narrative.

### Sensitivity/specificity

Use bivariate/HSROC only when threshold-level TP/FP/FN/TN or equivalent valid data, reference
standard, target, and threshold interpretation are comparable. Do not separately pool sensitivity
and specificity as if independent. When thresholds differ meaningfully, prefer HSROC or narrative
threshold profiles.

### Calibration and overall accuracy

Pool calibration slope, calibration-in-the-large/intercept, O:E, or Brier score only when definitions
and time horizon/target are comparable. Otherwise tabulate and narrate. A calibration plot alone is
not a numeric effect. DCA/net benefit generally remains narrative unless thresholds and harm-benefit
scales are aligned.

## Heterogeneity and advanced models

- Primary: REML random effects; use Hartung-Knapp style uncertainty where appropriate.
- Secondary: three-level model (`effect within cohort within synthesis group`) or robust variance
  estimation with CR2 small-sample correction. For unknown within-cluster correlations, repeat the
  analysis over a prespecified correlation grid and report stability of point estimates and uncertainty.
- Consider Bayesian hierarchical models for sparse groups or joint AUC/calibration structures only
  with transparent priors and sensitivity analyses.
- Meta-regression/subgroups require adequate independent cohort count and prespecification. Candidate
  modifiers: validation type, infection vs colonization/mixed, phenotype, ICU/transplant/hematology,
  prospective vs retrospective, traditional vs ML, publication era, and PROBAST+AI evaluation risk.

Do not use language as a subgroup. Do not treat I² alone as a complete heterogeneity assessment.

## Sensitivity analyses

- exclude `ADULT_ACCEPTED_16PLUS`;
- external evaluation only;
- low/unclear vs high PROBAST+AI evaluation risk;
- one effect per independent cohort under alternative hierarchy;
- remove probable/confirmed overlapping cohorts;
- pure current infection versus current infection/colonization mixed targets;
- exclude composite labels combining a current infection with prior MDR-GNB infection/colonization history;
- reported performance only versus derived SE/effects;
- traditional versus ML, without selecting each family's best observed AUC.

The algorithm subgroup must follow `algorithm-taxonomy-v58.md`. Use a subgroup coefficient/
interaction from the joint model, not an informal comparison of separately pooled estimates.
Scores inherit the superclass of their fitted mother model. Expert-only rules and unresolved
algorithms do not enter the binary traditional-versus-ML contrast.

Publication-bias tests are exploratory and underpowered for small k. Do not use a standard DTA
funnel method for AUC pools without methodological justification.
