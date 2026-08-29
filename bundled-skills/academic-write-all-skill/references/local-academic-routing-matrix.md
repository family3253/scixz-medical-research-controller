# Local Academic Routing Matrix for AWAS

## Purpose

This file is the canonical ownership matrix for **local academic routing**.

Use it when a task could plausibly trigger more than one local academic skill, `awas-*` subagent, or OMO platform agent. Its job is to keep one task from turning into several parallel owners.

## Core Rule

For each user-facing academic bottleneck:

1. choose **one primary owner**
2. allow only narrowly justified downstream specialists
3. allow OMO agents only as support, not as co-equal owners
4. forbid parallel owner paths unless they solve genuinely different stages

## Layer Model

## Priority Order

Use this order when several layers might apply at once:

1. **OMO system layer**
   - highest priority only for system/meta tasks such as platform architecture, global planning, external reference search, or skill/agent ecosystem design
2. **AWAS intake layer**
   - highest priority for academically scoped tasks; once the task is academic, AWAS should be the intake owner
3. **One academic execution owner**
   - one local skill or one `awas-*` subagent group owns the actual academic bottleneck
4. **superpowers process layer**
   - overlays planning, dispatch, review, and verification after the owner is already fixed

This means OMO is **higher-priority at the system layer**, but not a higher-priority academic execution owner once AWAS has accepted the task.

### Layer 1 — Intake / Routing Owner
- default: `academic-write-all-skill` / AWAS
- exception: only when the task is explicitly outside academic content routing and is instead about the skill ecosystem itself

### Layer 2 — Academic Execution Owner
- one narrow skill or one `awas-*` subagent group owns the academic bottleneck

### Layer 3 — OMO Support Agents
- `explore`, `librarian`, `oracle`, `metis`, `momus` support analysis, search, and review
- they do not become the academic workflow owner unless the task itself is platform/architecture work

### Layer 4 — superpowers Process Layer
- `superpowers-*` controls planning, dispatch, review, and verification
- `superpowers-writing-skills` only owns skill/agent ecosystem editing

## Routing Matrix

| Scenario | Primary owner | Allowed downstream | Allowed OMO support | Forbidden parallel paths | Required superpowers layer | Preferred `awas-*` agent |
|---|---|---|---|---|---|---|
| Broad academic request, mixed manuscript/review/format/retrieval ask | `academic-write-all-skill` | one selected downstream specialist only | `metis`, `oracle` when routing is ambiguous | direct parallel routing into `academic-paper` + `research-lit` + plotting skills | `superpowers-brainstorming` if task still vague | none until route fixed |
| China Pharmaceutical University professional-master's thesis / school-format-constrained thesis writing | `academic-write-all-skill` | CPU-local thesis references and thesis-specific downstream specialists only after route is fixed | `oracle` only for difficult boundary judgments, not as academic owner | 同等学历 template as default owner, or generic thesis defaults overruling local CPU requirements | `superpowers-writing-plans` when the chapter/package work is multi-step | `awas-writing-coordinator` |
| Startup-phase idea -> gap -> method planning | `academic-write-all-skill` | `research-ideation` | `librarian` for external literature checks | `academic-paper` as co-equal owner | `superpowers-brainstorming` | `awas-research-ideation-coordinator` |
| Corpus building / provider routing / thesis-source acquisition | `academic-write-all-skill` | retrieval scripts and provider adapters | `librarian`, `explore` | `research-lit` as a second owner while AWAS is already building artifacts | `superpowers-dispatching-parallel-agents` when sources are independent | `awas-retrieval-orchestrator` |
| Title/abstract screening and inclusion-exclusion decisions | `academic-write-all-skill` | screening artifacts only | `oracle` for difficult adjudication | direct jump to writing while screening is unresolved | `superpowers-writing-plans` if the screening workflow needs explicit execution steps | `awas-screening-analyst` |
| Structured evidence extraction from included papers | `academic-write-all-skill` | appraisal/audit helpers | `oracle` for ambiguous extraction logic | writing and extraction as co-equal primary paths | `superpowers-writing-plans` | `awas-evidence-extractor` |
| Proceed / refine / pivot decision on review-project readiness | `academic-write-all-skill` | debate artifacts only | `oracle`, `momus` as high-level reviewers | independent external review and internal decision loop both acting as owners | `superpowers-dispatching-parallel-agents` if multiple stance agents are used | `awas-proceed-advocate`, `awas-refine-advocate`, `awas-pivot-advocate`, `awas-decision-synthesizer` |
| Manuscript drafting from already-structured artifacts | `academic-write-all-skill` | `academic-paper` when the task is already paper-production scoped | `oracle` for architecture-level writing judgments | `academic-paper` + `research-writing-assistant` as co-equal owners | `superpowers-writing-plans` or `superpowers-subagent-driven-development` when execution is staged | `awas-writing-coordinator` |
| Reviewer comments -> response package | `academic-write-all-skill` | `reviewer-response-assistant` | `oracle` for difficult stance disputes | submission review + rebuttal drafting as co-equal primary paths | `superpowers-verification-before-completion` before claiming package is done | `awas-writing-coordinator` |
| Pure literature retrieval / paper understanding bottleneck | `academic-write-all-skill` | `research-lit` | `librarian` | `research-lit` + AWAS review-project execution both owning the task | none by default | `awas-retrieval-orchestrator` if artifacts are needed |
| Submission-grade review project / corpus-based review execution | `academic-write-all-skill` | `cross-disciplinary-review-writer` | `oracle`, `momus` | `academic-paper-reviewer` as a second review-project owner | `superpowers-writing-plans` for explicit staged execution | `awas-writing-coordinator` plus upstream review agents |
| Analyze finished experiment outputs and compare runs | `academic-write-all-skill` | `analyze-results` | `oracle` for hard interpretation disputes | `results-report` before analysis is stable | none by default | `awas-results-report-coordinator` only after analysis is complete |
| Convert already analyzed results into an internal experiment report | `academic-write-all-skill` | `results-report` | `oracle` if recommendation framing is uncertain | `analyze-results` rerun as a co-equal primary path without evidence of a gap | `superpowers-verification-before-completion` | `awas-results-report-coordinator` |
| Python code-first academic plotting | `academic-write-all-skill` | `academic-python-plotting` | none by default | `plotcase` as co-equal owner | none by default | none |
| Stata code-first academic plotting | `academic-write-all-skill` | `stata-academic-graphing` | none by default | `plotcase` as co-equal owner | none by default | none |
| PlotCase-first template search / GUI plotting | `academic-write-all-skill` | `plotcase` | `librarian` only if checking undocumented capability evidence | `academic-python-plotting` or `stata-academic-graphing` as co-equal owners | none by default | `awas-plotcase-orchestrator` |
| Zotero -> Obsidian knowledge-base workflow | `academic-write-all-skill` | `zotero-obsidian-bridge` | none by default | manuscript drafting as a co-equal owner before note/synthesis state is stable | `superpowers-writing-plans` if the bridge is part of a larger staged workflow | `awas-zotero-obsidian-coordinator` |
| Editing AWAS itself, route rules, local academic skill ecosystem, or agent system | AWAS ecosystem maintenance | `superpowers-writing-skills`, `opencode-agent-creator`, `skill-creator` | `momus`, `oracle`, `explore` | normal academic content skills as owners | `superpowers-writing-skills` | none |

## OMO vs AWAS Boundary

### OMO agents should usually own:
- repository-wide planning outside the academic content domain
- external reference lookup
- architecture review
- plan review and meta reasoning

### AWAS and `awas-*` should usually own:
- literature workflow artifacts
- review-project state
- manuscript-state transitions
- results-report packaging
- PlotCase handoff
- Zotero/Obsidian academic memory routing

### Practical anti-conflict rule

If an OMO agent is already active for a task:
- let it support search / planning / judgment
- do **not** let it become a second academic workflow owner when AWAS has already fixed the route

If AWAS has already fixed the academic route:
- downstream local skill or `awas-*` agent owns the bottleneck
- OMO agents stay advisory or search-oriented

## Route Evaluation Checklist

Before finalizing a route, confirm:

- Is AWAS still the intake owner?
- Is there exactly one primary academic execution owner?
- Are OMO agents only in support roles?
- Are `superpowers-*` being used as process/quality layer rather than academic content owner?
- Is any near-equivalent parallel path being left alive without a strong stage distinction?

If any answer is wrong, the route is not stable enough yet.
