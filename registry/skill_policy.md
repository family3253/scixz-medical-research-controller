# Skill quality, merge, and archive policy

## Parse

For every active user-level Codex Skill, inspect directory identity, `SKILL.md` frontmatter, trigger specificity, workflow clarity, references/scripts/assets, missing references, encoding, line count, and safety signals. Compare exact hashes and normalized names across active roots.

## Keep

Keep skills that have a valid `SKILL.md`, a specific trigger description, a coherent workflow or reference purpose, and a distinct capability. Keep general-purpose skills when they are a safe dependency for file intake, verification, writing, statistics, or reproducibility.

## Merge

Merge at the routing layer when two skills overlap but have different strengths. Choose one canonical owner, keep the other as an explicit fallback, and document the mapping. Do not merge by deleting content unless the replacement has been verified to cover the old contract.

## Archive

Archive only exact duplicate copies, broken/empty skill directories, stale aliases whose canonical replacement is verified, or index-only wrappers with no executable/reference value. Use a dated, recoverable archive outside the active namespace. Never touch `.system`, runtime directories, or external-manager symlinks without explicit confirmation.

## Install

Install an external Skill only when it has a standard `SKILL.md`, a clear license/source, a distinct capability, no unsafe instructions, and no active equivalent. Prefer a narrow subskill over an entire repository. Re-scan the installed copy before enabling it in the router.

## Current external candidates

Approved for evaluation from public repositories: `academic-research-suite` from `Imbad0202/academic-research-skills-codex`; `scientific-writing`, `scientific-critical-thinking`, `bulk-rnaseq`, `scanpy`, `pathway-enrichment`, and `clinical-decision-support` from `k-dense-ai/scientific-agent-skills`. `Alibaba-NLP/DeepResearch` is a Python application rather than a Codex Skill and is not installed as one. Bare names such as `MetaScreener` and `sci-select` are not installed without an unambiguous upstream path.

Submission-preflight integrations now installed and audited: `sci-manuscript-preflight` from `VivalavidaLu/sci-manuscript-preflight`; `paperconan` from `zixixr/paperconan`; `paper-audit` and `bib-search-citation` from `bahayonghang/academic-writing-skills`; `openclaw-medical-peer-review` from `FreedomIntelligence/OpenClaw-Medical-Skills/skills/peer-review`. `Imbad0202/academic-research-skills` is represented through the installed Codex adapter's `upstream_suite` metadata and is not duplicated.

## Local governance artifacts

- `local_skill_catalog.json` — combined logical catalog across `.codex`, `.agents`, and `.claude` user roots.
- `skill_taxonomy.md` — category index without moving physical Skill folders.
- `skill_conflicts.md` — link aliases, cross-environment mirrors, and true same-name variants.
- `fusion_map.md` — canonical routing and metadata-fusion decisions.
- `<private-skill-archive>/consolidation/archive_manifest.md` — recoverable physical cleanup record.
- `scixz_bindings.json` — the allowlisted SciXZ bundle with per-Skill status, route roles, and runtime state.
- `runtime_bindings.json` — executable/runtime bindings, currently including the isolated `paperconan` 0.8.5 CLI.
- `external_tools.json` — explicitly allowlisted public research-tool adapters; external results remain advisory until canonical verification.
