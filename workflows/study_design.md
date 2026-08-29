# Study-design workflow

## Entry and scope

Use for cohort, case-control, RCT, diagnostic, prognostic, RWE, target-trial, and protocol design. It does not replace IRB review or produce patient-care decisions.

## Inputs

Require target population, eligibility, exposure/intervention and comparator, time zero, follow-up, estimand, outcomes, data source, and intended causal/predictive/descriptive claim.

## Route

Controller → 中书省 drafts design and estimand → 门下省 challenges bias and feasibility → `council` for consequential causal or clinical designs. Primary: `design-study`, `clinical-research-idea`, or `experiment-plan`. Supporting: `clinical-decision-support`, `check-reporting`, `define-variables`, `calc-sample-size`, `statistical-analysis`.

## Outputs

Design diagram, estimand, eligibility/time-zero specification, outcome/censoring definitions, bias map, analysis handoff, sample-size assumptions, reporting checklist, and limitations.

## Verification

Check that eligibility, time zero, treatment strategies, outcome window, censoring, confounding control, missingness, and sensitivity analyses support the same estimand. Separate association, prediction, and causation.

## Failure/fallback

If the database cannot support the intended estimand, narrow the claim or return a design limitation. Do not silently substitute a different causal contrast.
