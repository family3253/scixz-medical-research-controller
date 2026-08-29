# Literature Authenticity Sentinel

## Purpose

This reference defines a lightweight but concrete four-layer authenticity check for citation-sensitive AWAS workflows.

It is designed to prevent a common failure mode: a citation looks plausible, resolves at metadata level, but still does not safely support the manuscript claim.

## The Four Layers

### Layer 1 — Identity

Check whether the citation has a structurally valid identity:
- DOI format
- arXiv identifier format
- or, at minimum, stable bibliographic identity (title + year + venue)

If identity is broken, the citation cannot proceed.

### Layer 2 — Source Status

Check what the source actually is:
- peer-reviewed article
- conference paper
- preprint
- report / grey literature
- unknown status

This layer prevents overclaiming review strength from preprints or weak sources.

### Layer 3 — Claim Support

Check whether the extracted evidence supports the manuscript role assigned to the citation.

Examples:
- background support
- method comparison
- core claim support
- contradiction / limitation anchor

If a citation exists but does not support the assigned role, downgrade it.

### Layer 4 — Manuscript Binding

Check whether the citation is actually tied to:
- claim mapping
- draft sections
- rebuttal points
- figure/table interpretation

This prevents “floating citations” that exist in the corpus but are not safely attached to manuscript claims.

## Decision Outputs

- `PROCEED` — citation is safe enough for current manuscript use
- `REFINE` — citation may remain, but metadata/support/binding needs repair
- `PIVOT` — citation should not carry the intended claim and must be replaced, downgraded, or removed

## Strong Rules

- a valid DOI is not sufficient by itself
- preprint status must remain visible when it matters
- unsupported claim roles should trigger `REFINE` or `PIVOT`, not silent acceptance
- if the manuscript claim is stronger than the evidence row, trust the evidence row

## Good Report Outputs

- citation authenticity table
- blocking-risk summary
- list of citations safe to proceed
- list of citations requiring metadata or support repair
- list of citations that should be removed or downgraded
