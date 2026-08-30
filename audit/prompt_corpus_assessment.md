# Prompt corpus, repository, and n8n workflow assessment

Assessment date: 2026-08-30

This audit records a capability-level study of user-supplied prompt libraries, template/tool
collections, n8n workflow stores, and four GitHub repositories. Source instructions were treated as
reference material. No source executable, installer, container, workflow, or credential was run.

## Source boundary

| Source family | Scale inspected | Rights/risk state | Release decision |
|---|---:|---|---|
| Dyna 2.0 academic-writing prompts | 18 PDF prompt modules | Explicit copyright and personal-use restrictions | Concepts only; no text, examples, identifiers, or PDFs copied |
| Technical-route templates | 191 files: 38 XML/PDF/PPTX/VSDX/JPG sets plus notes | Redistribution status unknown | Absorb provenance-bearing DSL and extraction/render split only |
| Medical-AI academic-writing prompts | 30 unique prompts duplicated as TXT and Markdown | Redistribution status not established | Deduplicate; absorb staged task/output/verification patterns only |
| R visualization collection | 18,339 mixed files: open-source packages, TidyTuesday assets, custom templates | Mixed upstream licenses and local/custom assets | Do not vendor; absorb chart-routing and source-first reuse rules |
| Batch image-to-table package | 992 files including n8n JSON/SQLite, binaries, scripts, logs, and runtime state | Embedded credential finding; high execution and privacy risk | Static graph study only; converted to provider-neutral `image-to-table-qa` |
| Miscellaneous research prompts | 18 TXT + 3 DOCX | Redistribution status unknown | Capability-level section/review/diagram rules only |
| Submission-tool guide | 2 TXT + 9 JPG | External browser side effects; source data fidelity emphasis | Absorb source-locked read-before-write loop; no automated submission action |
| Review tool | 96 files including n8n database and installers | Credential/runtime/user/execution tables present | Exclude runtime; absorb PubMed/search/dedupe/evidence/export stages |
| Upgraded review tool | 48 files including two 39-node n8n workflows and reference-order scripts | Local journal data and runtime state; mixed provenance | Absorb citation-order verification and deterministic schema logic only |
| XiaoWei research-command collection | 40-page PDF, 51 prompt families | Personal/reference material; redistribution status unknown | Concepts only; reject generic one-shot and unsupported certainty patterns |
| `family3253/skill` | 62 Skill entry points; commit `9fa25de` | Bundle with per-Skill provenance; no root repository license found | Use as discovery/provenance catalog, not a single canonical owner |
| `family3253/academic-write-all-skill` | 116 files; commit `64185a` | No root license found | Reference for stage routing, evidence gates, corpus downgrade, and project artifacts |
| `family3253/academic-write` | 635 files; commit `32914a` | Vendored upstream collection; no root license found | Treat as legacy capability catalog; do not absorb monolithically |
| `family3253/cycwrite-skill` | 96 files; commit `8d014a` | Repository states it is superseded; no root license found | Canonicalize to `academic-write-all-skill`; do not maintain duplicate owner |

## n8n workflow findings

Read-only inspection covered workflow exports and `workflow_entity` records while deliberately not
reading credential values.

| Workflow family | Observed graph | Capability decision |
|---|---|---|
| image/report OCR to CSV | 15-node and 20-node variants | New `image-to-table-qa` Skill: source ID, schema union, unit/flag preservation, confidence/review queue, QA export |
| PubMed search to review draft | 41-node and 46-node variants | Merge into SciXZ literature-review/citation/manuscript routes; existing owners already cover the output |
| upgraded review with reference ordering | two 39-node variants | Adopt deterministic first-appearance renumbering as a verification concept; do not copy workflow/database |
| literature monitoring/push | 77-node and 98-node variants | Existing `wenxian`/`mdrgnb-daily-push` own recurring retrieval and notification |
| generic workflow conversion | multiple JSON/SQLite forms | New `n8n-to-skill` Skill for sanitized manifest extraction and canonical-owner decisions |

One workflow export contained a hard-coded API credential. Its value is intentionally absent from
this audit. Treat the credential as exposed and rotate/revoke it. The original workflow JSON and all
n8n databases are excluded from the public repository.

## Capability decisions

| Capability | Decision | SciXZ destination |
|---|---|---|
| stage diagnosis before writing | strengthen | `workflows/manuscript_writing.md` |
| outline/evidence/draft/critic/verify sequence | strengthen | manuscript writing and review workflows |
| Introduction framework -> evidence pack -> draft | strengthen | `references/manuscript_section_depth.md` |
| Methods missing-detail placeholders | strengthen | `references/manuscript_section_depth.md` |
| figure-first Results and legends | strengthen | manuscript and figure workflows |
| finding/comparison/explanation/boundary Discussion | already strong; refine | section-depth reference |
| title/abstract/conclusion/highlights dependency on stable results | add explicit gate | section-depth reference |
| translation/polishing meaning-drift ledger | add | section-depth reference |
| source-locked batch form entry | adapt with authority gate | controller and submission workflow |
| citation authenticity and first-appearance ordering | strengthen | citation-management workflow |
| review corpus readiness/downgrade levels | already covered | literature-review workflow |
| technical-route document -> traceable DSL -> render | add | figure-presentation workflow |
| chart choice from estimand/data/claim | add | figure-presentation workflow |
| OCR image -> auditable table | new Skill | `bundled-skills/image-to-table-qa` |
| n8n workflow -> safe Skill | new Skill | `bundled-skills/n8n-to-skill` |
| exact journal acceptance probability from fixed formula | reject | journal-selection/preflight guard |
| copying prompt corpora and examples | reject | capability-absorption workflow |
| hard-coded API credentials/model bindings | reject | capability-absorption and n8n conversion |
| running downloaded installers to “learn” | reject | capability-absorption workflow |
| AI-detector evasion as a primary objective | reject | integrity/humanization boundary |

## Quality conclusions

The strongest reusable idea across the corpus is not a particular persona or prompt wording. It is
the repeated separation of intake, structure, evidence, drafting, critique, and verification. SciXZ
already had much of this architecture, so the upgrade focuses on missing traceability edges and
safe conversion rather than adding another mega-prompt.

The weakest patterns were false precision, one-shot completion pressure, generic “top journal”
style claims, method/citation completion by inference, and provider-specific workflows with embedded
credentials. These were explicitly rejected or converted into visible uncertainty and authority
gates.

