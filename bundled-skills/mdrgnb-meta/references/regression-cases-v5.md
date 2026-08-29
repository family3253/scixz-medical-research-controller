# Regression Cases v5.5

Run `scripts/regression_check.py` after changing eligibility, SEMKEY, identity, pool, scoring, or
synthesis rules. All legacy 24 eligibility and 6 granularity cases remain executable.

## Legacy cases retained

- broad UTI/current ESBL etiology, admission CRE carriage, active CR-GNB sepsis, and febrile-
  neutropenia current MDR-GNB: include;
- current infection/colonization composite: include with exact-target flag;
- known GNB/Enterobacterales/genus/species input or organism-restricted cohort: exclude;
- baseline-negative future acquisition and death: prognostic exclusion;
- factors-title with model/AUC, absent formula, and leakage: retain with applicable flags;
- >=16 cohort: include with sensitivity flag;
- training dataset without performance: inventory only, not a performance effect;
- external-validation-only: Evaluation appraisal only;
- tuning set: not unbiased evaluation.

Granularity cases retain same-cohort fitting/apparent roles; one AUC/multiple thresholds; multiple
dependent algorithms; changed analysis population; pooled/site-dependent estimates; and duplicate
semantic-key removal.

## v5 branch and timing cases retained in v5.5

| Case | Branch result | Required companion result |
|---|---|---|
| Current bacterial pneumonia distinguishes MDR-AB from several other bacteria | include current etiology | timing/leakage flag only; “onset” is not prognosis |
| Baseline CRE-negative, first detected later in hospital | future-event exclude | audit=1; synthesis=0 |
| Base model uses current organism/ESBL; optimized branch uses clinical features only | base exclude; optimized include | report branch-only; only optimized synthesis eligible |
| Other optimized branch has no final feature set | pending specification | inventory only; synthesis=0 |
| Admission colonization model plus later hospital infection model | admission include; later infection exclude | separate outcome/model/eligibility/performance units |
| ICU-CARB applied before screening result returned | include current carriage | organism unknown at T0=1 |
| Broad cohort, one branch consumes current GNB/species result | branch exclude known input | not cohort-restriction reason |
| Cohort post-hoc restricted to current Enterobacterales/species | exclude restricted cohort | even if predictor set is clinical only |
| Prior colonization/infection history only | may include | current-organism input=0 |
| Organism/AST revealed only by post-T0 reference standard | may include current state | result time is not model-input time |
| Source-index rows/files reordered | IDs unchanged | row-order reconstruction must fail |

## QA negative cases

Tests must fail for malformed/duplicate SEMKEYs, unescaped reserved characters, orphan or
incomplete crosswalks, included branches with any known-current-organism track, mixed current/
future outcomes sharing a scope, audit pools other than 40 reports, pending/ineligible synthesis
members, and source IDs that disagree with `01_Source_Report_Index`.
