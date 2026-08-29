# Bundled companion Skills

This repository now includes a deduplicated public bundle of the top-level companion Skills that were available in the local catalog when this release was prepared.

- Bundled top-level Skills: 260
- Full readable inventory: [`BUNDLED_SKILL_MANIFEST.md`](BUNDLED_SKILL_MANIFEST.md)
- Machine-readable inventory: [`registry/bundled_skill_manifest.json`](registry/bundled_skill_manifest.json)
- Bundle directory: [`bundled-skills/`](bundled-skills/)

The purpose is portability: a user who clones this repository can reproduce the SciXZ routing environment without guessing which local-only or public-source Skills were present on the original machine.

## Installation

Install all bundled Skills into `CODEX_HOME/skills` or `~/.codex/skills`:

```text
python scripts/install_bundled_skills.py
```

Install selected Skills:

```text
python scripts/install_bundled_skills.py find-journal sci-select --overwrite
```

The generic `skills` installer can also install one subdirectory at a time:

```text
npx skills add ./bundled-skills/find-journal --skill find-journal -g
```

## Public-source Skills

Public-source Skills are included when they were present in the local catalog. Their upstream URLs remain documented so users can inspect source history, licenses, and updates:

- `nature-review-studio`: [mumdark/nature-review-studio/skill](https://github.com/mumdark/nature-review-studio/tree/main/skill)
- `academic-paper-reviewer`: [bystander563/academic-paper-reviewer-portable](https://github.com/bystander563/academic-paper-reviewer-portable) or [fbdeme/academic-paper-reviewer](https://github.com/fbdeme/academic-paper-reviewer)
- `check-reporting`: [Aperivue/check-reporting/skills/check-reporting](https://github.com/Aperivue/check-reporting/tree/main/skills/check-reporting)
- `verify-refs`: [Aperivue/verify-refs/skills/verify-refs](https://github.com/Aperivue/verify-refs/tree/main/skills/verify-refs)
- `sci-manuscript-preflight`: [VivalavidaLu/sci-manuscript-preflight](https://github.com/VivalavidaLu/sci-manuscript-preflight/tree/master)
- `academic-paper`: [Imbad0202/academic-research-skills/academic-paper](https://github.com/Imbad0202/academic-research-skills/tree/main/academic-paper)
- `research-lit`: [wanshuiyin/Auto-claude-code-research-in-sleep/skills/research-lit](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/tree/main/skills/research-lit)
- `deep-research`: [Imbad0202/academic-research-skills/deep-research](https://github.com/Imbad0202/academic-research-skills/tree/main/deep-research)
- `sci-select`: [keros68/sci-select](https://github.com/keros68/sci-select)
- `journal-recommender`: [zero565656/journal-recommender](https://github.com/zero565656/journal-recommender)

## Deliberately excluded

- `scixz`, because the controller itself is the root Skill of this repository.
- `anthropics-docx`, `anthropics-pdf`, `anthropics-xlsx`, and `anthropics-pptx`, because their source metadata explicitly marks them Proprietary.
- System-managed Skills and plugin-cache copies.
- Virtual environments, dependency caches, `node_modules`, Python bytecode, browser state, local logs, machine-specific binding registries, manuscript archives, datasets, credentials, tokens, and API keys.
- JANE, iPubMed, Clarivate/JCR access, ShowJCR data services, LetPub pages, and EasyScholar credentials. These are external evidence sources or runtime services, not redistributable bundled secrets.

## Licensing note

The top-level MIT license applies to the SciXZ controller and repository-authored documentation. Bundled companion Skills keep their own provenance and license status. When a bundled component has no standalone license declaration, treat it as included for this repository's portability goal and do not repackage it as an independent third-party library without confirming redistribution rights.
