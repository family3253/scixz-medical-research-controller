# External Project Absorption Map for AWAS

## Guiding Rule

The following external projects can be absorbed into AWAS at the level of:
- capability patterns
- routing intelligence
- workflow design
- quality standards
- safe operating rules

They should **not** be absorbed as wholesale copied systems.

## 1. scitex-python

### What can be absorbed
- reproducible research mindset
- session-based organization of analysis and writing artifacts
- connection between data / stats / figures / writing
- tool-platform awareness for end-to-end academic workflows
- manuscript support that respects upstream evidence and generated outputs

### What should not be copied wholesale
- full Python platform architecture
- broad module namespace design
- MCP server internals
- optional dependency sprawl

### How it strengthens cycwrite
- makes `Methods`, `Results`, and figure-aware writing more evidence-grounded
- reinforces the rule that manuscript drafting should respect upstream analytical artifacts
- strengthens the concept that academic writing is downstream of structured research outputs, not isolated prose generation

## 2. Auto-claude-code-research-in-sleep (ARIS)

### What can be absorbed
- research -> review -> revise automation mindset
- iterative paper improvement loops
- skill-chaining / workflow composition thinking
- idea-discovery to experiment-plan to paper-writing continuity
- external-review-aware revision logic

### What should not be copied wholesale
- exact orchestration commands
- environment-specific automation assumptions
- overnight autonomous execution claims
- model-specific operational dependencies

### How it strengthens cycwrite
- upgrades AWAS from writing skill to lifecycle-aware writing skill
- strengthens revision, re-review, and reviewer-response subworkflows
- improves stage diagnosis for users who are somewhere between idea, draft, review, and revision

## 3. academic-research-skills

### What can be absorbed
- rigorous academic workflow framing
- explicit integrity and citation discipline
- paper writing / review / pipeline separation of concerns
- guided planning and paper-structure coaching
- stronger academic quality gates before output

### What should not be copied wholesale
- full agent-team design
- exact pipeline internals and all modes verbatim
- large prompt blocks without adaptation

### How it strengthens cycwrite
- improves paper-mode routing
- strengthens bilingual abstract and paper-planning awareness
- improves editorial-review and revision-roadmap logic
- reinforces integrity-first drafting and stage-aware writing

### Current local integration decision
- treat this repository as functionally covered when local `deep-research`, `academic-paper`, `academic-paper-reviewer`, and `academic-pipeline` are already installed
- do not add it as a second co-equal academic core if those local skills already exist
- borrow quality gates and routing ideas, not duplicate entry points

## 4. research-plugins

### What can be absorbed
- plugin-style breadth of academic micro-capabilities
- modular research skill taxonomy
- large-scope resource organization mindset
- distinction between reusable skills, API wrappers, and reference-only configs

### What should not be copied wholesale
- all plugin contents as one giant mega-skill
- reference-only configs pretending to be executable guarantees
- count-driven breadth without coherent routing

### How it strengthens cycwrite
- justifies splitting heavy capabilities into reference files and future subskills
- improves modularization of review, submission, translation, and citation operations
- supports treating AWAS as a hub skill rather than a monolith

## 4B. claude-scholar

### What can be absorbed
- selective project-memory and literature-memory workflows
- startup-phase `research-ideation` logic when the user wants a dedicated idea -> gap -> method lane
- post-analysis `results-report` logic when the user wants a decision-oriented experiment report rather than manuscript prose
- Zotero-to-Obsidian bridge patterns when the user explicitly wants canonical paper notes and collection coverage

### What should not be copied wholesale
- the entire parallel academic stack as a second routing universe
- broad overlap paths for paper writing, rebuttal, self-review, or anti-AI cleanup when stronger local owners already exist
- OpenCode/Claude-branch-specific installation or config assumptions as if they were native to AWAS

### How it strengthens cycwrite
- adds a narrower ideation lane without replacing AWAS intake
- adds a cleaner post-analysis report lane after strict analysis is done
- adds one explicit literature-memory bridge for Zotero + Obsidian users
- reinforces the rule that AWAS should expose one downstream owner per bottleneck, not multiple parallel academic stacks

### Current local integration decision
- keep only low-overlap downstream paths such as `research-ideation`, `results-report`, and `zotero-obsidian-bridge`
- skip its overlapping broad writing/review/rebuttal skills when local owners already exist

## 4E. PlotCase (local desktop plotting application)

### What can be absorbed
- local bundled-example search before plotting decisions are finalized
- GUI-first, template-driven high-end plotting handoff for users who want interactive R-style chart construction
- a conservative workflow where AWAS first decides the figure family and only then routes to PlotCase for local exploration or reproduction

### What should not be copied wholesale
- undocumented API or CLI claims
- treating PlotCase as a second code-first plotting owner parallel to Python / Stata plotting skills
- promising reproducible automation beyond local example search and GUI launch without stronger evidence

### How it strengthens cycwrite
- gives AWAS one local high-end plotting handoff for users who prefer template search and GUI refinement
- strengthens figure selection and example discovery without weakening the current code-first plotting lanes

### Current local integration decision
- use PlotCase only as a narrow downstream plotting specialist after AWAS has fixed the plotting bottleneck
- prefer `academic-python-plotting` or `stata-academic-graphing` when the user needs programmable figure generation rather than local GUI exploration

## 4C. research-writing-skill

### What can be absorbed
- strict brainstorming -> chapter-writing -> LaTeX thesis workflow
- discipline-aware chapter sequencing and file-oriented thesis drafting
- stronger staged drafting for users who explicitly want Norman-bury style execution

### What should not be copied wholesale
- a second general-purpose academic router competing with AWAS
- duplicate writing, review, or polishing ownership when AWAS already has a clearer local owner

### How it strengthens cycwrite
- offers one stricter process-first lane for users who explicitly want that workflow
- sharpens thesis/chapter execution without replacing AWAS stage diagnosis

### Current local integration decision
- treat this repository as functionally covered when local `research-writing-assistant` already exists
- route there only on explicit Norman-bury / research-writing-skill requests

## 4D. poco-claw

### What can be absorbed
- almost nothing at the AWAS skill-routing level beyond a reminder that office/media tooling can exist outside the current stack

### What should not be copied wholesale
- its document, PDF, spreadsheet, presentation, or multimodal generation toolchain as a second office stack
- any platform/runtime assumptions as if they were AWAS-native academic workflow stages

### How it strengthens cycwrite
- mostly by clarifying what should remain out of scope for AWAS's academic routing core

### Current local integration decision
- skip installation for AWAS purposes when local docx/pdf/xlsx/pptx and office workflows already exist
- do not treat poco-claw as an academic subworkflow source for AWAS

## 5. humanizer (local skill source)

### What can be absorbed
- pattern-based detection of AI-sounding prose
- avoidance of inflated symbolism, promo tone, vague attributions, and formulaic cadence
- rhythm variation and voice repair
- anti-pattern inventory for late-stage polishing

### What should not be copied wholesale
- full personality-writing philosophy in contexts requiring strict neutrality
- over-humanization that changes technical precision

### How it strengthens cycwrite
- sharpens `Revision / Polishing Mode`
- strengthens anti-AI-tone rewriting without sacrificing academic accuracy
- helps distinguish clean, human academic prose from generic LLM polish

## 6. PRISMA / PRISMA-S guidance sources

### What can be absorbed
- reporting awareness for search documentation
- record-flow thinking across identification, screening, eligibility, and inclusion
- explicit recoverability of exclusion reasons and source lists
- distinction between doing a search and reporting a search transparently

### What should not be copied wholesale
- pretending AWAS is a standards-compliance engine
- claiming PRISMA or PRISMA-S compliance without the underlying records

### How it strengthens cycwrite
- improves literature-search-and-screening outputs for review-grade work
- adds traceable project-artifact expectations without turning AWAS into a full review platform

## 7. scitex-python

### What can be absorbed
- modular research-system thinking: scholar -> stats -> figures -> writer -> verify
- session-based artifact organization from upstream evidence to downstream manuscript outputs
- strong separation between tool substrate and orchestration layer
- reproducibility-aware handoff between retrieval, analysis, visualization, and writing
- agent-facing interface design where tools expose structured outputs and writing happens downstream of those outputs

### What should not be copied wholesale
- the full Python platform scope
- the entire MCP server/tool surface
- environment-heavy installation and configuration assumptions
- statistics / plotting / dataset subsystems unrelated to cycwrite's core mission

### How it strengthens cycwrite
- clarifies that AWAS should sit above retrieval / analysis / figure tools as the writing-and-evidence coordination layer
- strengthens project-session thinking so writing outputs stay linked to search, screening, extraction, and figure artifacts
- justifies pairing AWAS with agent orchestration instead of bloating the skill itself into a monolithic automation stack

## 8. academic-write (legacy repository)

### What can be absorbed
- research-lifecycle continuity from idea discovery to paper planning
- novelty-check framing before premature drafting
- stronger linkage between literature review, experiment/result packaging, and manuscript writing
- iterative review and paper-improvement mindset
- paper-plan, paper-write, paper-compile, and figure-aware workflow coordination patterns

### What should not be copied wholesale
- the entire old repository as a second monolith
- all vendored skills as separate subskills inside the main package
- external tool wrappers pretending to be guaranteed runtime support
- environment-specific orchestration assumptions from the legacy project

### How it strengthens academic-write-all-skill
- upgrades the skill from writing-aware to research-lifecycle-aware
- improves stage diagnosis before a manuscript fully exists
- supports idea -> literature -> experiment/result -> paper transitions without overpromising automation

## 9. MetaScreener

### What can be absorbed
- staged review workflow thinking: criteria initialization -> screening -> extraction -> risk-of-bias assessment -> evaluation -> export
- multi-model or multi-agent review routing with confidence-aware adjudication
- reproducibility features such as seeded runs, explicit exports, and evaluation checkpoints
- the idea that review automation should produce structured artifacts before final prose

### What should not be copied wholesale
- its full application stack or UI assumptions
- claims that every review stage can be safely automated end-to-end without human oversight
- environment-specific package/runtime assumptions

### How it strengthens cycwrite
- gives AWAS a stronger default shape for multi-agent review projects
- reinforces that screening, extraction, appraisal, and writing are distinct deliverables
- improves orchestration language for systematic review and meta-analysis tasks

## 10. ASReview

### What can be absorbed
- active-learning mindset for title/abstract screening prioritization
- relevance-feedback loops and explicit screening-state updates
- evidence-first ranking rather than static one-pass screening

### What should not be copied wholesale
- the whole ML screening engine as if it were natively bundled
- claims of equivalent performance without task-specific validation

### How it strengthens cycwrite
- improves screening-stage routing for larger corpora
- justifies explicit screening prioritization before full-text work
- supports the idea that agent-assisted review projects should adapt as labels accumulate

## 11. LatteReview

### What can be absorbed
- explicit multi-agent role design for literature-review tasks
- reviewer-persona separation and hierarchical coordination patterns
- structured collaboration across retrieval, judgment, and synthesis layers

### What should not be copied wholesale
- exact agent implementation or provider-specific assumptions
- unrestricted role proliferation that makes the skill unreadable

### How it strengthens cycwrite
- sharpens multi-agent defaults inside `academic-write-all-skill`
- reinforces that different review subtasks should be owned by different agents or stages
- helps the skill speak more natively about companion-agent orchestration

## 12. paperfetcher

### What can be absorbed
- citation-chasing and snowballing as explicit review-stage utilities
- handsearch support as a structured extension of retrieval rather than an ad hoc afterthought
- separation between corpus growth and downstream synthesis

### What should not be copied wholesale
- all package internals or installation assumptions
- overpromising automated full-text access

### How it strengthens cycwrite
- improves retrieval-stage completeness for review and meta-analysis tasks
- makes citation expansion a first-class recoverability pattern in evidence synthesis workflows

## 13. metafor / RoBMA / PyMARE style meta-analysis tooling

### What can be absorbed
- strict separation between extraction-ready study data and downstream statistical synthesis
- explicit reporting of model choice, heterogeneity, sensitivity analyses, and publication-bias checks
- the rule that meta-analysis computation belongs to a computation layer, while manuscript writing belongs downstream

### What should not be copied wholesale
- pretending the whole statistical engine is natively embedded in AWAS
- silent statistical defaults without visible assumptions

### How it strengthens cycwrite
- strengthens meta-analysis awareness without turning the skill into a stats platform
- improves the wording of when to stop at extraction/appraisal versus when synthesis is justified
- reinforces evidence-to-analysis-to-writing layering

## Absorption Outcome for cycwrite

After absorbing these projects conceptually, AWAS becomes:
- more lifecycle-aware (`ARIS`, `academic-research-skills`)
- more reproducibility-aware (`scitex-python`)
- more modular and extensible (`research-plugins`)
- more natural in late-stage prose cleanup (`humanizer`)
- more transparent in review-grade literature-search reporting (`PRISMA`, `PRISMA-S`)
- better positioned as an orchestration-ready writing layer above a broader research tool substrate (`scitex-python`)
- more explicitly multi-agent for systematic review and meta-analysis work (`MetaScreener`, `LatteReview`)
- better at screening prioritization and corpus expansion logic (`ASReview`, `paperfetcher`)
- more disciplined about the boundary between extraction, appraisal, synthesis, and prose (`metafor`-style tooling)

## Non-Negotiable Boundary

AWAS must remain coherent.
It should absorb:
- standards
- routing
- heuristics
- quality controls
- reference structures

It should not become:
- a full coding platform
- a giant copy of multiple skill repos
- an unreadable prompt warehouse
