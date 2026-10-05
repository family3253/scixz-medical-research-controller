# Skill selector

Use this selector only after the controller reaches `APPROVED_FOR_EXECUTION`. Use the smallest sufficient set. Prefer a local, domain-specific skill over a broad generic one. The names below are logical Skill names; resolve each one to a readable active `SKILL.md` and callable dependencies before invoking.

| Task | Primary owner | Supporting perspectives |
|---|---|---|
| broad academic workflow | `academic-write-all-skill` or `academic-pipeline` | `context-master`, `verification` |
| literature search/synthesis | `deep-research` or `research-lit` | `pubmed-database`, `search-lit`, `novelty-check` |
| systematic review/meta-analysis | `meta-analysis` or `cross-disciplinary-review-writer` | `deep-research`, `check-reporting`, `verify-refs` |
| clinical question/design | `clinical-research-idea`, `design-study`, `experiment-plan` | `clinical-decision-support`, `check-reporting` |
| protocol/ethics | `write-protocol` or `fill-protocol` | `check-reporting`, `deidentify`, `anthropics-docx` |
| sample size | `calc-sample-size` | `analyze-stats`, `statistical-analysis` |
| data preparation | `clean-data` or `generate-codebook` | `deidentify`, `version-dataset`, `anthropics-xlsx`; for auditable OCR/image batches use `image-to-table-qa` after file reading |
| causal/RWE/TTE | `design-study` or `statistical-analysis` | `analyze-stats`, `marginaleffects`, `check-reporting` |
| manuscript writing | `academic-paper` or `scientific-writing` | `research-lit`/`deep-research` for missing evidence, `bib-search-citation`/`manage-refs` for claim-to-source allocation, `verify-refs`, `academic-paper-reviewer` or `scientific-critical-thinking` for depth critique, `check-reporting` |
| manuscript review | `nature-review-studio` or `academic-paper-reviewer` | `scientific-critical-thinking`, `check-reporting`, `peer-review`; optional explicitly authorized `paperreview-ai` as a simultaneous isolated branch, followed by a fresh fusion sub-agent and bilingual Word rendering when both same-fingerprint artifacts complete |
| submission preflight | `sci-manuscript-preflight` | `paper-audit`, `verify-refs`, `check-reporting`, `scientific-writing`, `academic-expression-polisher` |
| source-data/research-integrity audit | `paperconan` when source tables/assets are supplied | `sci-manuscript-preflight`, `verify-refs`, `scientific-critical-thinking` |
| reviewer response | `reviewer-response-assistant` | `nature-review-studio`, `academic-write-all-skill`, `verification` |
| revision after review | `academic-paper` or `revise` | `reviewer-response-assistant`, `scientific-writing`, `analyze-stats`, `make-figures`, `verify-refs`, `check-reporting` |
| known-journal lookup | `sci-select` | ShowJCR data or `jcr_mcp` for JCR/CAS/XinRui fields; `agent-browser` or `chrome:control-chrome` for LetPub/official-source verification; `find-journal` only when scope fit or submission ranking is also requested |
| journal fit | `find-journal` | required external adapters `jane` (PubMed-similarity) and `ipubmed` (browser-assisted filters/exports), `journal-format-converter`, `venue-templates`, `sync-submission` |
| citation/reference work | `manage-refs` or `verify-refs` | required external adapters `jane` (candidate discovery) and `ipubmed` (citation-trace/title triage), `citation-management`, `academic-citation-manager`, `zotero-reviewed-import` |
| figures/presentations | `make-figures` or `scientific-visualization` | `academic-python-plotting`, `present-paper`, `scientific-slides` |
| project/reproducibility | `manage-project` | `version-dataset`, `sync-submission`, `verification` |
| prompt/repository capability absorption | `skill-creator` | `deterministic-local-file-reading`, the matching document reader, `n8n-to-skill` for sanitized n8n manifests, `verification`; use `self-improving-agent` only for durable error/lesson capture |
| academic research suite | `academic-research-suite` | `deep-research`, `scientific-writing`, `paper-audit`, `bib-search-citation` |
| medical/grant peer review | `openclaw-medical-peer-review` or `peer-review` | `academic-paper-reviewer`, `check-reporting`, `scientific-critical-thinking` |
| post-writing/citation cleanup | `scientific-writing` or `paper-audit` | `bib-search-citation`, `verify-refs`, `humanizer`, `academic-expression-polisher`; for introduction/discussion depth use the section-depth reference and a claim/evidence critic |
| bulk RNA-seq/GEO | `bulk-rnaseq` or `research-lit` | `pathway-enrichment`, `scientific-visualization`, `check-reporting` |
| scRNA-seq | `scanpy` | `pathway-enrichment`, `scientific-critical-thinking`, `statistical-analysis` |
| multiomics/mechanism | `multiomics-analysis` | `research-lit`, `pathway-enrichment`, `scientific-schematics`, `clinical-research-idea` |
| local manuscript/file intake | `deterministic-local-file-reading` | `anthropics-pdf`, `anthropics-docx`, `anthropics-xlsx`, `anthropics-pptx` |

Do not invoke two skills merely because their names overlap. If a canonical Skill already owns the task, record other candidates as alternatives in the handoff rather than running them redundantly. If a listed Skill is not installed or callable, use the controller's availability/fallback gate instead of silently substituting it.
## Nature Skills suite integration (additive extension layer)

The Nature Skills suite is **not a replacement router**. Keep the existing SciXZ primary owner and add a Nature Skill only when the request explicitly asks for Nature-style output or when a clearly scoped supplemental capability is needed.

| Existing SciXZ route | Optional Nature extension | Additive role |
|---|---|---|
| manuscript-writing | `nature-writing` | Nature-style drafting pass or argument refinement after/beside the original writing owner |
| language polishing | `nature-polishing` | Nature-style language, translation, or compression pass; preserve facts and evidence boundaries |
| manuscript-review | `nature-reviewer` | Additional Nature-style reviewer perspective; preserve the original council and review contract |
| reviewer-response | `nature-response` | Additional rebuttal/cover-letter audit or Nature-style response pass |
| literature-review / citation-management | `nature-academic-search`, `nature-citation`, `nature-ref-verifier` | Supplemental search, claim-to-source mapping, or reference verification; existing JANE/iPubMed gates remain mandatory where applicable |
| figure-presentation | `nature-figure` | Optional publication-figure audit, refinement, or export pass |
| paper presentation | `nature-paper2ppt`, `nature-image2ppt` | Optional paper-to-PPT or editable-slide production alongside the existing presentation route |
| paper reading | `nature-reader`, `nature-paper-card` | Optional bilingual reader or evidence-chain card in addition to the requested summary/review |
| statistics / data availability | `nature-statistics`, `nature-data` | Optional reporting-transparency and Data/Code Availability checks |

The original primary Skill remains the owner. If a Nature extension is dispatched, record it as `optional_extension` in the handoff and do not duplicate or silently replace the primary deliverable.

## DOCX delivery invariant

For every route that creates or modifies Word output, add the `docx_author_metadata` verification step. The required metadata author is `chenyechao`; do not infer it from the manuscript's visible author list.
