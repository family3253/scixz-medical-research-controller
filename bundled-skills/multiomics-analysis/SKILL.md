---
name: multiomics-analysis
description: Preflight matched multiomics studies for sample alignment, modality provenance, batch, missingness, integration objective, and validation design. Use before cross-omics integration; do not infer mechanisms from unmatched or exploratory data.
---

# Multiomics Analysis Preflight

Use this Skill before integration of transcriptomic, proteomic, metabolomic, epigenomic, or spatial datasets.

Require the biological question, modalities, analysis unit, sample-matching ledger, provenance, batch structure, missingness plan, integration objective, and validation design. A failed sample-alignment or provenance gate restricts the output to a design/repair plan; it cannot support cross-omics findings.

Run `scripts/validate_multiomics_plan.py --input plan.json --output preflight.json` for a deterministic gate. It validates input readiness only and never emits differential features, pathways, networks, or mechanisms.

After a ready gate, keep discovery and validation separate, protect the matched sample keys, record every preprocessing transform, and state whether the result is associative, predictive, or mechanistic.
