# Statistical-analysis workflow

## Entry and scope

Use for test selection, regression, survival, causal inference, prediction metrics, missingness, power, uncertainty, and sensitivity analysis. It does not certify a model without data and assumptions.

## Inputs

Require analysis unit, outcome/exposure, estimand, design, variable types, sample size, missingness, clustering/repeated measures, and primary/sensitivity objectives.

## Route

Controller → 户部 checks data/provenance → 中书省 fixes estimand → 门下省 checks assumptions and overclaim → `panel` or `council`. Primary: `analyze-stats` or `statistical-analysis`. Supporting: `marginaleffects`, `pandas-pro`, `clean-data`, `calc-sample-size`, `check-reporting`.

## Outputs

Analysis plan, assumptions, model/test choice, effect estimates and uncertainty, missing-data/multiplicity plan, sensitivity analyses, reproducible code route, and claim-to-analysis map.

## Verification

Check data types, independence, distribution/model assumptions, missingness, multiplicity, calibration/discrimination, positivity/overlap, convergence, and whether the result supports the stated claim.

## Failure/fallback

If assumptions fail, report the failure and offer a defensible alternative or sensitivity analysis. If data are unavailable, produce a plan with assumptions, not fabricated results.

## Executable preflight

Run `bundled-skills/statistical-analysis/scripts/validate_analysis_plan.py` on a JSON plan before computation. It requires an explicit objective, estimand, primary analysis, assumptions, missing-data plan, and sensitivity analyses. A successful preflight validates plan completeness only and does not generate estimates.
