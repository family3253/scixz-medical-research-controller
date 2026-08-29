# SciXZ

SciXZ is a user-level Codex Skill with a central controller for coordinating medical-research workflows. It uses a three-department gate—中书省拟定、门下省审核、尚书省执行—and six execution ministries so that the system processes the user's instruction before deciding which Skills to call.

This repository contains the portable SciXZ controller and workflow contracts. It intentionally does not vendor a user's entire local Skill installation, private profiles, manuscript files, API keys, runtime caches, or machine-specific path registries.

For complex or consequential requests, SciXZ enters multi-agent collaboration mode: a coordinator creates the brief, domain workers analyze independently, a critic challenges the reports, consensus arbitrates disagreement, and a verifier gates publication. When native sub-agents are unavailable, the same stages run as labeled sequential passes rather than being misrepresented as parallel agents.

## Use

```text
/scixz 审稿 manuscript.pdf
/scixz 设计 INSPIRE target-trial emulation
/scixz 分析 GEO 数据并设计验证方案
/scixz 选择适合的 SCI 期刊
/scixz 回复 reviewer comments
```

The entry point is `SKILL.md`. The router keeps task classification, skill selection, role boundaries, workflows, consensus rules, and memory templates in separate files so that only the relevant material needs to be loaded.

The collaboration contract lives in `collaboration/mode.md`, `collaboration/protocol.md`, `collaboration/roles.md`, and `collaboration/state_schema.md`.

The controller contract lives in `controller/command_interpreter.md`, `controller/three_departments_six_ministries.md`, `controller/skill_decision_engine.md`, and `controller/state_machine.md`.

Operational governance adds a strict permission matrix, isolated worker contexts, flow/progress/error logs, intervention controls, stalled-task escalation, and verified snapshot rollback. See `controller/permission_matrix.md` and `controller/observability_recovery.md`.

## Design principles

- reuse existing skills before adding another overlapping one;
- keep independent evidence passes separate until consensus;
- distinguish association, prediction, and causation;
- make uncertainty and missing information visible;
- archive rather than permanently delete during maintenance.

## Dependencies

SciXZ is a router, not a self-contained medical-research toolchain. Install only the Skills required by the route you use. The route matrix and setup notes are in [`DEPENDENCIES.md`](DEPENDENCIES.md).

### Minimal core

- Codex-compatible Skill runtime
- This repository installed as the `scixz` Skill

### Common medical-manuscript route

- `deterministic-local-file-reading`
- one manuscript reader: `anthropics-docx`, `anthropics-pdf`, or `anthropics-xlsx`
- `nature-review-studio` or `academic-paper-reviewer`
- `check-reporting`
- `verify-refs`
- `revise` for post-review revisions

### Conditional route skills

- `analyze-stats` and `make-figures` when a new analysis or figure is required
- `find-journal` for journal fit and submission cascade
- `research-lit` or `deep-research` for literature retrieval
- `clean-data`, `deidentify`, `generate-codebook`, and `version-dataset` for data work
- `calc-sample-size` for power/precision planning
- `sync-submission`, `venue-templates`, and `paper-audit` for submission packaging

### External adapters

The journal-selection and citation-management routes require JANE and iPubMed as external evidence adapters. They are public services, not bundled Skills; do not place API keys, unpublished manuscripts, PHI, or restricted data in their queries without explicit authorization.

## Installation model

Install this repository as the `scixz` Skill, then install route-specific dependencies from their authoritative Skill repositories or local Skill catalog. Do not copy absolute paths from one machine into `registry/`; use the portable templates in this repository and resolve paths at runtime.

## Public-release boundary

The public package excludes `memory/`, local audit logs, private journal profiles, machine-specific binding files, user manuscript archives, and research datasets. Before publishing a fork, scan the tree for credentials, personal contact details, PHI, absolute local paths, and unpublished research material.
