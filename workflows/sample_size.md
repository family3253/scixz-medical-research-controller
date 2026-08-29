# Sample-size workflow

## Entry and scope

Use for power, precision, event-per-variable, or sample-size planning. It produces assumptions and reproducible calculations, not a guarantee of study success.

## Inputs

Require design, primary outcome, effect or precision target, alpha, power, allocation, expected missingness, and cluster/repeated-measure structure. Missing the primary estimand or outcome is blocking.

## Route

Controller → 中书省 defines the estimand and assumptions → 门下省 checks feasibility → 尚书省 ticket. Primary: `calc-sample-size`. Supporting: `analyze-stats`, `statistical-analysis`, `design-study`, and `clinical-research-idea` when effect assumptions are uncertain.

## Outputs

Calculation method, assumptions table, result with units, sensitivity scenarios, reproducible code or calculation record, and limitations.

## Verification

Recalculate the primary result, check parameter units and direction, inspect sensitivity to attrition/effect size, and ensure the calculation matches the planned analysis and unit of randomization.

## Failure/fallback

If inputs are incomplete, return an assumptions request rather than a fabricated number. If no calculator is callable, provide a documented formula and a blocked execution status.
