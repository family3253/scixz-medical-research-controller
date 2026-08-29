# scRNA-seq workflow

## Entry and scope

Use for single-cell QC, normalization, integration, clustering, annotation, differential expression, trajectory, and cell communication. It does not treat cell-level associations as independent biological replication.

## Inputs

Require raw/processed format, sample identities, biological replicates, species/tissue, QC fields, batch structure, and biological question.

## Route

Controller → 户部 checks sample/data integrity → 中书省 fixes analysis question → `panel` or `council` when interpretation is consequential. Primary: `scanpy`. Supporting: `pathway-enrichment`, `scientific-critical-thinking`, `statistical-analysis`, and an available integration/trajectory Skill only after availability checks.

## Outputs

QC thresholds, normalization/integration decision, dimensionality reduction/clustering plan, annotation evidence, replicate-aware downstream analysis, validation plan, and figures.

## Verification

Check nFeature/nCount/mitochondrial thresholds, doublets, batch correction, clustering resolution, marker specificity, pseudoreplication, differential-expression unit, and annotation confidence.

## Failure/fallback

If raw data, sample labels, or biological replication are missing, provide a limitation and analysis plan only. Do not claim cell types or mechanisms from cluster labels alone.
