# Skill fusion map

Fusion means aligning routing or metadata while preserving platform-specific implementations when they differ materially.

|Skill family|Canonical decision|Action|
|-|-|-|
|`analyze-results`|AWAS-routed description|Aligned `.agents` metadata with the Codex variant; implementation retained|
|`research-lit`|AWAS-routed description|Aligned `.agents` metadata with the Codex variant; implementation retained|
|`research-pipeline`|Explicit full-lifecycle-only trigger|Aligned `.agents` metadata with the Codex variant; implementation retained|
|`find-skills`|Codex fallback-capable variant|Added `skills.sh` fallback to `.agents` copy|
|`cross-disciplinary-review-writer`|Codex resources + AWAS trigger boundary|Updated Codex frontmatter; retained the `.agents` platform variant|
|`paper-plan`, `paper-figure`, `paper-write`, `paper-compile`|`academic-paper`|Archived `.agents` compatibility wrappers; full Codex aliases remain for compatibility|
|`paper-writing`|`academic-pipeline`|Archived `.agents` compatibility wrapper; full Codex alias remains|
|`superpowers-brainstorming`|Platform variants|No merge: small behavioral differences are environment-specific|
|`superpowers-writing-plans`|Platform variants|No merge: execution handoff differs by harness capability|
|`academic-research-skills` / `academic-research-skills-codex`|`academic-research-suite`|The Codex adapter is installed; the original suite is recorded as upstream, not installed twice|
|`academic-writing-skills`|`paper-audit` + `bib-search-citation` + existing writing/verification Skills|Install only distinct subskills; route post-processing and citation work separately|
|`OpenClaw-Medical-Skills/peer-review`|`openclaw-medical-peer-review`|Namespaced optional reviewer; local `peer-review` remains the default canonical medical reviewer|
|`sci-manuscript-preflight`|submission-preflight owner|Pre-submission readiness and claim/figure/reference gate|
|`paperconan`|source-data integrity branch|Only with source tables/assets; signal not verdict|

Exact content exposed through symbolic links is recorded as `link-alias`, not treated as a duplicate folder. Exact copies in `.agents` and `.claude` are recorded as `cross-environment-mirror`; they remain because they support different agent environments.
