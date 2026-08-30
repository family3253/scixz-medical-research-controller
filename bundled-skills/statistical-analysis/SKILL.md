---
name: statistical-analysis
description: Validate a statistical analysis plan before execution, including estimand, design, data structure, assumptions, missing-data handling, and sensitivity analyses. Use for analysis planning or preflight; do not use it to fabricate results without data.
---

# Statistical Analysis Preflight

Use this Skill to turn an analysis request into a verifiable plan before any computation.

Require an analysis unit, outcome, estimand, design, primary analysis, assumptions, missing-data approach, and at least one sensitivity analysis. Keep causal, predictive, and descriptive objectives separate. Missing elements are a block to result-producing analysis, not an invitation to infer them.

Run `scripts/validate_analysis_plan.py --input plan.json --output preflight.json` for a deterministic intake artifact. A passing preflight confirms plan completeness only; it does not validate a model, calculate an effect, or certify a conclusion.

When data are supplied, preserve the raw input, record provenance and versions, then use the smallest appropriate analysis runtime. Report diagnostics, uncertainty, and failed assumptions alongside any result.
