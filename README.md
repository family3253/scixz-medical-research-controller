# SciXZ — Scientific eXpert Zone

[简体中文](README.zh-CN.md)

SciXZ is a portable Codex Skill that coordinates medical-research workflows. It acts as a central controller: it normalizes the request, reviews the proposed route, selects the smallest sufficient set of Skills, and gates the final output with consensus and verification.

The controller uses a three-department gate—中书省 (draft), 门下省 (review), and 尚书省 (execute)—plus six execution ministries. This keeps planning, domain work, critique, consensus, and publication verification separate.

## What is included

- The portable `scixz` controller and its routing contracts.
- Collaboration, role, workflow, consensus, evaluation, and verification contracts.
- The local-only companion Skills that are otherwise difficult to discover: `revise`, `find-journal`, `deterministic-local-file-reading`, and `manage-refs`. See [`BUNDLED_SKILLS.md`](BUNDLED_SKILLS.md).
- Portable runtime-binding examples; machine-specific paths and private state are intentionally excluded.
- A complete download matrix for Skills that users must obtain separately: [`DOWNLOAD_GUIDE.md`](DOWNLOAD_GUIDE.md).

## Quick start

Install this repository as the `scixz` Skill, then invoke it with a coordinated research request:

```text
/scixz 审稿 manuscript.pdf
/scixz 设计 INSPIRE target-trial emulation
/scixz 分析 GEO 数据并设计验证方案
/scixz 选择适合的 SCI 期刊
/scixz 回复 reviewer comments
```

The entry point is [`SKILL.md`](SKILL.md). For complex requests, SciXZ creates independent evidence passes, a critic pass, a consensus decision, and a verification gate. If native sub-agents are unavailable, the same stages run as explicitly labelled sequential passes.

## Bundled versus external Skills

The local-only companion Skills are placed under [`bundled-skills/`](bundled-skills/) so others can find and install them independently. They are not silently relicensed by the top-level MIT license; see the per-component notes in [`BUNDLED_SKILLS.md`](BUNDLED_SKILLS.md).

Skills that already have public GitHub sources are referenced but not duplicated. Skills with an explicit proprietary license, such as the `anthropics-*` document readers, are not copied into this public repository. Install them from their authoritative distribution when a route needs them. JANE and iPubMed are external evidence adapters, not bundled Skills.

## Typical manuscript route

For review, revision, journal selection, and citation QC, the usual route is:

1. `deterministic-local-file-reading` plus the reader for the file type.
2. A public review Skill such as `nature-review-studio` or `academic-paper-reviewer`.
3. A public reporting/preflight Skill such as `check-reporting` or `sci-manuscript-preflight`.
4. The bundled local-only `revise` Skill for point-by-point responses.
5. The bundled local-only `manage-refs` Skill or public `verify-refs` after citation edits.
6. The bundled local-only `find-journal` Skill, with auditable JANE and iPubMed evidence branches.

See [`DEPENDENCIES.md`](DEPENDENCIES.md) for route-by-route requirements and runtime notes.

If you are setting up SciXZ on a new machine, start with [`DOWNLOAD_GUIDE.md`](DOWNLOAD_GUIDE.md). It distinguishes bundled local-only Skills, public Skills to download separately, proprietary readers, and external JANE/iPubMed adapters.

## Safety and public-release boundary

SciXZ supports research planning and evaluation, not autonomous patient care, diagnosis, prescribing, or ethics approval. Keep clinical outputs research-only unless a separate governance artifact is explicitly requested.

This release contains no manuscripts, patient-level data, extraction workbooks, private journal profiles, local audit logs, API keys, tokens, browser state, or machine-specific binding registries. Do not send unpublished manuscripts, PHI, restricted data, credentials, or API keys to external adapters by default.

## Design principles

- Reuse an existing Skill before adding an overlapping one.
- Keep independent evidence passes separate until consensus.
- Distinguish association, prediction, and causation.
- Make uncertainty, missing evidence, and route limitations visible.
- Archive rather than permanently delete during maintenance.

## License

The SciXZ controller and repository-authored documentation are released under the MIT License. Bundled companion Skills retain the provenance and licensing notes recorded in [`BUNDLED_SKILLS.md`](BUNDLED_SKILLS.md); inspect those notes before redistributing a component on its own.
