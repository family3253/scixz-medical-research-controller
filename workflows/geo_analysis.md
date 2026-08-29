# GEO/bulk RNA-seq workflow

## Entry and scope

Use for GEO dataset selection, bulk RNA-seq, differential expression, enrichment, and validation planning. Discovery signals are not mechanism proof.

## Inputs

Require GEO accession or search topic, species, tissue, disease/control or exposure definition, platform, sample/replicate metadata, batch, and validation target.

## Route

Controller → 户部 validates accession and metadata → 中书省 fixes discovery question → `panel` or `council`. Primary: `bulk-rnaseq` or `research-lit`. Supporting: `pathway-enrichment`, `scientific-visualization`, `statistical-analysis`, `check-reporting`.

## Outputs

Dataset rationale, metadata audit, QC/normalization/quantification route, statistical unit, DEG/enrichment plan, figures, validation strategy, and limitations.

## Verification

Check dataset identity, species/tissue, replicate structure, batch, gene IDs, background universe, multiple testing, QC gates, and independent validation. Keep discovery and validation separate.

## Failure/fallback

If metadata or biological replication is insufficient, stop at a dataset-quality warning or return a search plan. Do not run or interpret differential expression from an unverified grouping.
