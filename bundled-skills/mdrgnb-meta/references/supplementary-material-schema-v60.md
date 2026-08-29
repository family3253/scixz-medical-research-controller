# Manuscript and supplementary-material schema v6.0

This schema supersedes the v5.9.2 worksheet-layout guidance while retaining its controlled
fields and evidence contract. The review remains diagnostic-only: exclude future acquisition,
mortality, recurrence, deterioration, and other prognostic outcomes.

## Compact workbook views

1. `01_研究资格`: citation, design, population, adult basis, target state, phenotype, organism
   scope, current-unobserved T0, reference standard, and branch eligibility.
2. `02_队列数据集`: physical cohort, centre/site, recruitment, dataset role, split/resampling,
   N/events/non-events, analysis population, outcome, external axis, investigator relation, and
   model-lock timing. Materialize at `dataset × analysis population`.
3. `03_模型`: one row per minimal model unit. Include source and normalized algorithm, algorithm
   family/superclass, traditional-versus-ML code, regularization, ensemble status, model role,
   mother-model and model-family IDs, dependency cluster, candidate/final parameter counts,
   data modality, feature selection, missing data, continuous-variable handling, class imbalance,
   hyperparameter tuning, optimism correction, sample-size rationale, intended user/input burden,
   implementation, impact evaluation, fairness, and extraction status.
4. `03_预测因子`: one row per model-predictor entity. Include verbatim source variable, minimal
   clinical construct, domain, modifier, coding, unit, threshold, lookback, T0 availability,
   predictor role, coefficient, adjusted effect/CI, transformation/reference/interaction, and
   feature-importance type/value/rank. Do not merge effect types.
5. `04_性能`: one row per model × dataset × outcome × analysis population × metric/context,
   including estimate, uncertainty, scale, validation level, source/derivation, phenotype/T0,
   independent cohort, dependency cluster, and synthesis candidate status.
6. `05_阈值四格`: threshold, selection method, sensitivity, specificity, PPV/NPV and TP/FP/FN/TN.
7. `06_校准临床价值`: calibration intercept/slope/O:E/Brier/H-L/plot and DCA/net benefit as
   distinct metric types with complete context links.
8. `07_评分范围`, `08_TRIPOD_AI`, `09_PROBAST_AI`: item-level report, development-model, and
   evaluation-context scopes; never calculate numeric PROBAST totals.
9. `10_局限性`: author-reported, review-identified, and reporting-gap limitations separately.
10. `11_补提写回审计`: field-level provenance, status, evidence, and adjudication changes.

Do not create one worksheet per Liu table. Liu 2024 remains a field-coverage comparator only.
Generate predictor-frequency and other supplementary result tables from adjudicated long-form
facts after duplicate and dependency rules are applied.

## Release invariants

- `03_模型` and `03_预测因子` must remain separate and share stable model IDs.
- Every observed performance/threshold/calibration row has model, dataset, outcome, and analysis
  population links.
- Every dataset row has an explicit role and analysis population.
- Legacy missing tokens are status-coded, not stored as observed values.
- Primary and strict-adult analysis pools are defined by branch eligibility, not by workbook row
  order.
