# Multiomics workflow

## Entry and scope

Use for transcriptomics, proteomics, metabolomics, epigenomics, spatial integration, and mechanism-oriented multiomics. It does not convert association networks into causal mechanism.

## Inputs

Require biological question, matched samples, omics modalities, feature types, missingness, batch, normalization/scaling plan, and validation design.

## Route

Controller → 户部 checks sample matching and provenance → 中书省 defines integration unit → `council` when mechanism or clinical translation is claimed. Primary: `multiomics-analysis` for reproducible preflight and `research-lit` for design. Supporting: `pathway-enrichment`, `scientific-critical-thinking`, `statistical-analysis`, `scientific-schematics` when available.

## Outputs

Integration method rationale, preprocessing/QC plan, feature-selection rules, cross-omics model, validation strategy, biological interpretation, and limitations.

## Verification

Check sample alignment, leakage, batch, scaling, missingness, multiple testing, feature stability, independent validation, and whether the claim is associative, predictive, or mechanistic.

## Failure/fallback

If modalities are not matched or validation is absent, narrow the claim to exploratory association and report the design ceiling. Do not invent cross-omics links.

## Executable preflight

Run `bundled-skills/multiomics-analysis/scripts/validate_multiomics_plan.py` on a JSON plan before integration. It blocks unmatched samples, unverified provenance, missing batch/missingness handling, and absent validation design. A successful preflight validates intake only; it cannot be reported as a biological result.
