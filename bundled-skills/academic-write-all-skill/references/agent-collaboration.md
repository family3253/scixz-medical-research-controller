# Agent Collaboration for AWAS

## Purpose

This file defines how companion agents, scripts, and the AWAS skill collaborate without collapsing into one monolithic system.

## Layering Rule

- provider adapters handle source-specific access, retries, browser automation, and export capture
- agents execute stage work
- scripts normalize or compute
- templates record state and handoffs
- AWAS defines writing rules, safety, routing, and evidence-faithful transformation

## Recommended Stage Order

1. retrieval
2. screening
3. evidence extraction
4. appraisal / audit
5. decision loop
6. writing
7. final gate / packaging

## State Driver

Use `scripts/session_state_driver.py <project_dir>` to inspect the current stage and missing required files.

Use `scripts/session_state_driver.py <project_dir> --advance` only after the current stage is ready and you intentionally want to move the manifest to the next stage.

This keeps the ecosystem lightweight while still giving it a concrete staged state machine.

## Recommended File Contracts

### Retrieval -> Screening
- `candidate_pool.csv`
- `session_manifest.md`
- `search_strategy.md`
- provider adapter config or workflow file when retrieval depends on a browser workstation or API signature

### Screening -> Evidence Extraction
- `title_abstract_screening.csv`
- `fulltext_acquisition.csv`
- `fulltext_screening.csv`
- `fulltext_review_register.csv`
- `gate_report.md`

### Evidence Extraction -> Writing
- `gate_report.md`
- `decision_packet.md`
- `proceed_case.md`
- `refine_case.md`
- `pivot_case.md`
- `decision_record.md`
- `evidence_extraction.csv`
- `claim_mapping.md`
- `outline.md`
- `visual_evidence_pack.md`

### Evidence Extraction -> Appraisal / Audit
- `evidence_extraction.csv`
- `prediction_model_appraisal.csv`
- `risk_of_bias_register.csv`
- `reporting_audit.csv`
- `audit_summary.md`

### Appraisal / Audit -> Writing
- `audit_summary.md`
- `prediction_model_appraisal.csv`
- `risk_of_bias_register.csv`
- `reporting_audit.csv`
- `claim_mapping.md`
- `outline.md`

### Writing -> Final Gate
- `draft_sections.md`
- `deliverables_manifest.md`
- `gate_checklist.md`
- `sentinel_watch_report.md`
- `citation_authenticity_report.md`

## Interaction Rule

The writing coordinator should not redo retrieval or screening work.
The retrieval and screening agents should not pretend to write final scholarly prose.
The retrieval layer may use official APIs, authorized browser sessions, or manual export/import loops, but it must hand downstream agents normalized artifacts rather than brittle click-by-click state.
Each agent updates the session manifest so downstream agents know which artifacts are authoritative.
Appraisal and audit work should happen before high-confidence synthesis claims are drafted, especially for prediction-model reviews and AI-heavy evidence bases.

## Multi-Agent Defaults for Review / Meta Work

When the task is a systematic review, meta-analysis, or prediction-model review, prefer this default collaboration pattern:

1. retrieval orchestrator prepares or normalizes the corpus
2. screening analyst stabilizes inclusion / exclusion state
3. evidence extractor converts included studies into structured fields
4. appraisal / audit stage checks risk of bias, reporting quality, validation, calibration, and clinical utility
5. debate loop determines whether evidence is strong enough to proceed, refine, or pivot
6. writing coordinator drafts only after the upstream artifacts are stable enough

This prevents the writing layer from compensating for unresolved study-selection, extraction, or appraisal uncertainty.

## Two-Reviewer Plus Arbitrator Pattern

For high-impact extraction and appraisal tasks, use this default conflict-handling structure:

1. scorer / extractor A produces an independent output
2. scorer / extractor B produces an independent output
3. compare outputs for material disagreement
4. if disagreement exists, launch a third adjudicator
5. preserve the adjudicated result in the operational artifact while keeping the earlier outputs inspectable

This pattern should be preferred for:

- prediction-model split classification
- retained-model selection
- TRIPOD / TRIPOD+AI rescoring
- PROBAST / PROBAST+AI rescoring
- critical data extraction fields that affect pooled analysis

The writing layer should consume the adjudicated result, not whichever upstream opinion happened to arrive first.

## Code-Aware Review / Meta Pattern

For review and meta-analysis tasks, prefer code-backed or script-backed helper stages when they improve reproducibility:

- retrieval and citation expansion scripts for corpus growth
- deduplication and artifact-normalization scripts before screening
- structured extraction tables before narrative synthesis
- explicit appraisal registers before summary judgments
- statistical synthesis tools only after extraction and appraisal artifacts are stable

The writing-facing skill should describe and coordinate these steps, not impersonate a full statistical runtime by itself.

For review and meta-analysis work, code-backed helpers and agent parallelism should reinforce each other: scripts normalize and compare structured outputs, while multiple agents provide independent judgments that can be adjudicated when necessary.

## Practical Mapping to scitex / AutoResearchClaw Style Systems

The closest mapping is:

- retrieval/scholar subsystem -> `awas-retrieval-orchestrator`
- provider-specific API or browser access layer -> retrieval adapters coordinated by `awas-retrieval-orchestrator`
- screening / evidence-state subsystem -> `awas-screening-analyst`
- structured knowledge extraction -> `awas-evidence-extractor`
- appraisal / audit subsystem -> structured appraisal artifacts plus local or external audit logic coordinated by AWAS
- proceed / refine / pivot debate -> `awas-proceed-advocate`, `awas-refine-advocate`, `awas-pivot-advocate`, `awas-decision-synthesizer`
- sentinel / consistency watchdog -> `awas-sentinel-watchdog`
- citation authenticity audit -> `awas-citation-authenticity-auditor`
- downstream manuscript writer / reviewer -> `awas-writing-coordinator` + AWAS

This preserves the valuable part of those systems: staged artifact-driven collaboration.

For a fully auditable debate loop, do not stop at `decision_record.md`; keep all three stance files so later reviewers can inspect why a project proceeded, refined, or pivoted.

## Boundary

Do not turn AWAS into a full autonomous experiment platform.
Do not turn AWAS into a browser-automation monolith either.
Use this collaboration model to keep writing standards strong while execution remains modular.
Do not skip the appraisal / audit layer just because extraction artifacts already exist; for meta-analysis and prediction-model review tasks, extracted data and judged quality are different deliverables.

When browser automation is required, keep selectors, login/profile assumptions, and download behavior in adapter config files rather than scattering them through the writing-facing skill text.
