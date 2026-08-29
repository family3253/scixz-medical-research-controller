# Manuscript and supplementary-material schema v5.9.2

## Scope

This schema defines the minimum extraction facts and generated Excel views needed for the main
manuscript and supplementary materials of the adult MDR-GNB current-state diagnostic prediction
model review. Liu 2024 and its supplement are field-coverage references only.

The current review remains diagnostic-only. Do not import or reproduce Liu's prognostic model
tables, future-event predictor frequencies, mixed diagnostic/prognostic counts, or eligibility of
known-current-organism and organism-restricted cohorts.

## Compact workbook views

Do not create one worksheet for every Liu supplementary table. Absorb compatible fields into the
existing entity tables and generate publication supplements later.

1. `01_研究资格`: citation, design, population, adult basis, target, T0, organism/phenotype,
   reference standard, and branch eligibility.
2. `02_队列数据集`: physical cohort, sites/centres, recruitment dates, dataset role, split/
   resampling method, N/events/non-events, external-validation axis, investigator relation, and
   model-lock timing. Materialize at `dataset × analysis population`; add linked outcome and
   analysis-population IDs so one dataset with outcome-specific event counts is not collapsed.
3. `03_模型预测因子`: one table with an explicit row-type field. Model rows expose the v5.8
   algorithm family/superclass, traditional-vs-ML code, regularization/ensemble, mother-model
   lineage, role, family and dependency, plus candidate/final parameter counts, data modality,
   feature selection, missing data, continuous-variable handling, class imbalance,
   hyperparameter tuning, optimism correction, sample-size rationale, intended user/input burden,
   implementation, impact evaluation, and fairness. Predictor rows expose source term, minimal
   construct, domain, modifier, coding, unit, threshold, lookback, T0 availability, role,
   coefficient, adjusted effect/CI, and feature-importance type/value/rank. Shared display columns
   may be polymorphic, but effect types must remain separately labelled.
4. `04_性能`: the reader-facing and meta-ready performance table in one view, joined to model
   algorithm, branch eligibility, outcome, phenotype/T0, dataset role, N/events, validation axes,
   independent cohort, dependency cluster, model family, and source/derivation.
5. `05_阈值四格`: threshold, selection method, TP/FP/FN/TN, sensitivity, specificity, PPV/NPV.
6. `06_校准临床价值`: calibration intercept/slope/O:E/Brier/H-L/plot and DCA/net benefit kept
   as distinct metric types and linked to model/dataset/outcome context.
7. `07_评分范围`, `08_TRIPOD_AI`, `09_PROBAST_AI`: report component, development model, and
   evaluation-context scopes with item-level evidence. Use TRIPOD+AI 2024 and PROBAST+AI 2025,
   not the older tools used by Liu 2024.
8. `10_局限性`: author-reported, review-identified, and reporting-gap facts kept separate.
9. `11_补提写回审计`: field-level provenance and adjudication changes.

The Liu crosswalk belongs in this protocol/data dictionary, not as a routinely maintained
worksheet. Predictor-frequency, distribution, and correlation tables are generated outputs from
`03_模型预测因子`; they are not additional manual extraction sheets.

## Liu Table S1 crosswalk

Retain but split composite cells:

- study, country, setting, centre count, design;
- development population and adult basis;
- model algorithm and number of final predictors;
- diagnostic target, phenotype, organism scope, infection/colonization state, and T0;
- development/evaluation N and events by dataset role;
- discrimination with estimate, uncertainty, scale, and source/derivation;
- calibration by metric type;
- internal validation by split/resampling role;
- external validation with temporal/geographic axis separate from investigator relation.

Do not use Liu's single table row as an atomic unit. The current atomic performance unit remains
`report × study × cohort × outcome × model × dataset × metric × analysis population × context`.

## Predictor supplementary tables

The authoritative input is predictor-type rows in `03_模型预测因子`, not hand-entered
frequencies. Store:

- verbatim source variable;
- minimal clinical construct;
- modifier dimensions, including drug class, condition subtype, data source, prior/current
  status, and measurement window;
- coding, unit, threshold, transformation, reference category, and interaction;
- predictor role: candidate, final input, reused fixed-model input, generic feature set, or
  importance-only feature;
- coefficient, adjusted effect, CI, feature-importance type/value/rank, and direction as
  different fields; never combine ORs, coefficients, SHAP, Gini, and permutation importance.

Generate frequency tables only after field-level adjudication:

- primary count: one per `eligible development report × minimal construct`;
- also report model-family and model counts;
- fixed-model external evaluations do not add predictor-selection frequency;
- scores and their mother regressions do not duplicate predictors;
- stratify, when supported, by setting, T0 bucket, infection/colonization/mixed state,
  phenotype, clinical syndrome, and algorithm superclass;
- language is never a subgroup.

Liu-style correlations between predictor distributions are optional exploratory analyses, not
required extraction fields. If used, recompute from the adjudicated binary report-by-construct
matrix, state the coefficient and denominator, and avoid interpretation when strata are sparse.

## Fields excluded from this review

- prognostic/future acquisition, mortality, recurrence, deterioration, or long-term outcome data;
- diagnostic models restricted to a known current organism/GNB/Enterobacterales/species at T0;
- Liu's aggregate PROBAST counts and predictor frequencies;
- study-language subgroup;
- a single free-text `calibration` cell that conflates H-L, slope, intercept, plot, O:E, and
  Brier score;
- a single free-text `external validation` label that conflates temporal, geographic, and
  investigator independence.

## Release checks

- Every displayed value must join to a fact/evidence entity or be labelled as a generated mapping.
- No blank is interpreted as source-not-reported.
- Model-level branch eligibility must precede algorithm or performance synthesis.
- `04_性能` is a candidate meta-ready view; the locked synthesis-membership table remains
  authoritative for final meta-analysis.
- Supplementary counts must reconcile with the 40-report audit pool, 39-report primary set, and
  38-report strict-adult sensitivity set.
- Every observed performance row in `04_性能` must have nonblank model, dataset, and outcome links.
  Legacy sibling contexts may be recovered only by an exact documented context key/crosswalk.
- Dataset-role aliases must be mapped to the active role vocabulary. Internal/development roles may
  show generated structural labels for external-validation fields; unresolved external fields
  remain explicit pending extraction, never blank or `NR_SOURCE`.
- Penalized regression must be recognized before generic logistic mapping. Derived scores,
  nomograms, and fixed rules inherit the mother model algorithm; export must expose the mother
  relation or leave the lineage pending rather than classifying it as an expert rule.
- `02_队列数据集` must not select only the first analysis population when a dataset has multiple
  outcome-specific denominators. Every displayed N/event pair carries an analysis-population ID.
- Observed threshold and calibration/utility records must have nonblank model, dataset, and
  outcome context. Exact sibling context keys or documented generated mappings are required.
