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
| manuscript review | `nature-review-studio` or `academic-paper-reviewer` | `scientific-critical-thinking`, `check-reporting`, `peer-review` |
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
