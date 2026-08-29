---
name: academic-write-all-skill
description: Use when the user needs academic writing, thesis/manuscript planning, review writing, revision, statistics-to-prose conversion, methods/results help, structured manuscript review, academic plotting or figure-guided writing, literature retrieval, experiment-to-report packaging, or academic formatting adaptation. Also use when the request involves qualitative-review committee simulation, theoretical contribution challenge, methods transparency audit, literature-gap validation, logic-chain diagnosis, desk-reject risk, reference formatting, three-line tables, abstract structure polishing, journal resubmission adaptation, Zotero-to-Obsidian literature workflows, or mentions missing data, Table 1, mediation, interaction, RERI, survival analysis, Kaplan-Meier, Cox, ROC, calibration, nomogram, prediction models, statistical learning, xgboost, mlr3, or dynamic prediction, because awas should act as the single academic routing-and-coordination entry point and proactively check the local reusable course/code library before drafting.
---

# academic-write-all-skill

## Overview

`academic-write-all-skill` is a unified academic-writing and academic-workflow orchestration skill.

Its governing principle is: **write in stages, route by task type, and never let polished prose outrun verified evidence**. High-quality academic writing depends on structure, evidence control, genre routing, journal fit, revision logic, and submission readiness—not just elegant sentences.

This skill supports Chinese, English, and bilingual workflows across journal manuscripts, theses, proposals, literature reviews, evidence reviews, cover letters, reviewer-response packages, outline-first paper planning, abstract-only work, citation-check passes, late-stage format-convert tasks, and idea-to-paper lifecycle planning.

It should also behave as a **multi-agent academic workflow coordinator** whenever the task involves systematic review, meta-analysis, prediction-model appraisal, evidence extraction, methodology audit, stage-heavy academic production, figure/report pipelines, or Zotero/Obsidian-backed literature synthesis. In those cases, `academic-write-all-skill` should not act like a solo prose writer; it should decide which companion agents, downstream skills, scripts, and artifacts need to run in parallel before trustworthy drafting begins.

It also supports a guarded self-update behavior: when its own absorbed capability set is not enough, it should first route to stronger local skills and bundled references, then learn cautiously from GitHub or official external implementations, while keeping all new outputs evidence-bound and clearly labeled.

The shorthand **`awas`** should be treated as referring to `academic-write-all-skill` unless the user explicitly means something else.

AWAS should be treated as the **single default entry point** for academic writing, academic plotting, literature retrieval, results-to-report packaging, and knowledge-base-linked research writing in this environment. It should own intake, stage diagnosis, routing, and integrity gates, while delegating one clearly chosen bottleneck to one primary downstream specialist or `awas-*` subagent.

AWAS should also treat the local `superpowers-*` skills as its **default process layer** whenever planning, brainstorming, parallel dispatch, or completion verification becomes relevant. In other words: AWAS owns the academic routing decision; `superpowers` owns the generic execution discipline around that decision.

### Priority Order

Use this priority order whenever OMO agents, AWAS, local specialists, and `superpowers-*` might all plausibly apply:

1. **OMO system layer first — but only for system/meta scope**
   - if the task is primarily about platform architecture, repository-wide planning, external reference discovery, meta review, or skill/agent ecosystem design, let OMO agents lead
2. **AWAS intake layer next — for academic domain scope**
   - if the task is academically scoped, AWAS should become the first intake and routing owner even when OMO support agents are present
3. **One downstream academic execution owner**
   - after AWAS fixes the route, choose exactly one primary local skill or `awas-*` subagent to own the bottleneck
4. **superpowers process layer overlays the route**
   - `superpowers-*` should shape planning, execution, review, and verification after the owner is already known; they do not replace the academic owner

Do not invert this order unless the task is explicitly about editing the skill/agent system itself.

## When to Use

Use this skill when the user needs help with any of the following:

- topic ideation, research-question refinement, or proposal framing
- research idea discovery, novelty-check framing, or literature-to-idea narrowing
- literature reading, literature search strategy, evidence synthesis, or review-article planning
- Chinese thesis retrieval, CNKI/Wanfang/university repository discovery, or learning from authorized thesis exports and PDFs
- China Pharmaceutical University thesis / dissertation formatting, chapter planning, abstract, front matter, reference style, or template-constrained drafting
- statistics-heavy writing, methods explanation, or results-to-workflow translation when the topic overlaps with common medical-statistics or modeling knowledge points that may already exist in the local reusable course/code library
- thesis statement sharpening, outline building, and argument structuring
- master's thesis / dissertation chapter planning, chapter-level drafting, or thesis-to-manuscript adaptation
- section drafting: `Introduction`, `Methods`, `Results`, `Discussion`, abstract, conclusion
- title, keywords, highlights, graphical abstract copy, or cover letter drafting
- experiment-to-writing handoff, result interpretation planning, or figure/compile-aware writing coordination
- translation, polishing, shortening, rewriting, anti-AI-tone revision, or style repair
- pre-submission review, journal-fit evaluation, acceptance-risk triage, or desk-reject risk screening
- reviewer comment response, revision mapping, rebuttal writing, or simulated review-committee assessment
- qualitative manuscript auditing for theoretical contribution, methods transparency, literature-gap strength, logic-chain integrity, or editor-style first-pass screening
- academic formatting adaptation such as reference-style conversion, three-line table generation, abstract-structure diagnosis, or journal resubmission formatting
- paper outline generation, chapter-by-chapter planning, abstract-only drafting, citation-check, or format-convert requests
- review-type routing for narrative, scoping, systematic, umbrella, critical, or prediction-model reviews
- literature-search and screening workflows for related work, review corpora, evidence matrices, PRISMA-style record tracking, and review-project artifacts
- high-frequency academic microtasks such as grammar checks, reference-format checks, logic repair, and statistics-to-prose conversion

Do **not** use this skill for purely mechanical formatting if a narrower formatting skill already covers the task fully.

## Core Operating Rule

Always determine **what stage the user is actually in** before generating text.

Bad pattern:
- user asks for polished prose
- assistant skips missing evidence, structure, and genre decisions
- output sounds academic but is weak, generic, or unverifiable

Good pattern:
1. identify genre and stage
2. inspect available materials
3. locate missing critical information
4. choose the right subworkflow
5. draft or revise only at the right level
6. run integrity and overclaim checks

When tables, figures, legends, or statistical outputs are available, treat them as first-class evidence artifacts rather than background attachments.

## Routing Precedence

To keep routing stable when several overlapping paths appear possible, use this precedence order:

1. **Choose the primary task family first**
   - paper-production
   - review-project
   - late-stage operations
2. **Choose the narrowest honest submode inside that family**
   - for example: `revision-coach`, `citation-check`, `format-convert`, `Prediction-Model Review Mode`, or `Qualitative Review-Committee Routing`
3. **Prefer one clearly matching specialist skill over parallel equivalents**
   - if a narrow skill fully fits the task, route to it first and let awas remain the stage-aware wrapper
4. **Do not keep multiple active paths for the same bottleneck**
   - pick one primary implementation path, mention the specialist boundary, and avoid duplicating the same job across modes

## Capability Consolidation Rule

`academic-write-all-skill` should behave like a **capability consolidator**, not a capability fan-out hub.

For any one user-facing function, first decide whether the package already has:

- one native closed loop that should own the job end-to-end
- one primary downstream specialist that should own the bottleneck
- only a narrow downstream supplement that can safely attach after the main route is chosen

Hard anti-divergence rules:

1. one function -> one primary path
   - do not let one request activate several near-equivalent routes as co-equal implementations
2. native closed loops outrank loose skill lists
   - if awas already has a stable internal loop for that function, use it instead of spraying adjacent skills
3. specialists are downstream, not parallel, unless they solve genuinely different stages
   - if a specialist only sharpens one substep, attach it after the main route is fixed
4. do not split one rhetorical job into unrelated microtasks unless the user explicitly asks for decomposition
5. when several paths appear plausible, choose the narrowest honest owner and explain the boundary briefly

This rule applies especially to:

- introduction drafting
- anti-AI cleanup
- logic repair
- review-response work
- figure-guided writing
- formatting adaptation

Examples of preferred precedence:
- reference-format conversion -> `ai4scholar-排版助手` or `apa7-citation-formatter`, not both unless the user explicitly needs both scopes
- qualitative theory/method/gap/logic/desk-reject auditing -> `Qualitative Review-Committee Routing`, not generic `academic-paper-reviewer`
- reviewer response writing -> `reviewer-response-assistant`, with awas providing stage control rather than duplicating rebuttal logic
- table generation vs full formatting adaptation -> prefer the narrow formatting skill first, then fall back to awas-level coordination only if the task crosses stages
- mixed citation + abstract-structure + resubmission-format requests -> prefer `ai4scholar-排版助手` as the single primary path; reserve `apa7-citation-formatter` for APA-only citation normalization
- logic-repair requests -> prefer the argument-structure path first; do not parallelize `logic-skeleton-rewriter`, deep manuscript rewriting, and expression polishing unless the user explicitly asks for staged passes
- prose-from-figures plus figure-refinement requests -> prefer `figure-and-compile-aware` as the primary awas path, then invoke narrower figure skills only downstream

### Routing Tie-Breakers for Common Overlaps

Use these tie-breakers when two or more routes look plausible:

- **qualitative committee audit vs generic review**
  - if the user explicitly asks for theory / methods / gap / logic / desk-reject lenses, prefer `Qualitative Review-Committee Routing`
  - reserve `academic-paper-reviewer` for broader external-style review requests

- **single-style citation cleanup vs multi-part formatting adaptation**
  - if the task is only APA 7 reference-list or in-text normalization, prefer `apa7-citation-formatter`
  - if the task bundles references with abstract structure, three-line tables, or journal resubmission formatting, prefer `ai4scholar-排版助手` as the single primary formatting path

- **review-stage routing vs rebuttal-package ownership**
  - if the user needs a response letter, stance decomposition, or reviewer-by-reviewer answer strategy, prefer `reviewer-response-assistant` as the primary downstream specialist
  - keep `Submission / Review Mode` as the stage wrapper, not as a parallel rebuttal implementation

- **logic repair vs language polishing / deep rewriting**
  - if the bottleneck is argument flow or reasoning structure, prefer `logic-skeleton-rewriter`
  - only prefer `academic-expression-polisher` or `academic-manuscript-rewriter` when the main problem is wording density or full-text reconstruction rather than logic-chain repair

- **figure-guided writing vs figure-specialist execution**
  - if the user is still writing from figures/tables while also mentioning figure optimization, keep `figure-and-compile-aware` as the primary awas path
  - use plotting / polishing / new-media figure skills only as downstream specialists after the primary writing path is chosen

## Routing Flow

```text
Need help with topic or proposal?
  -> ideation / proposal mode
Need to go from idea discovery or novelty check into a paper plan?
  -> research lifecycle mode
Need help organizing paper logic?
  -> outline / argument mode
Need a qualitative simulated review committee or manuscript vulnerability scan?
  -> submission / review mode + qualitative review-committee routing
Need a paper plan, abstract, citation check, or format convert?
  -> paper-production submode selection
Need one manuscript section?
  -> section drafting mode
Need a review article?
  -> review-type routing first
Need a clinical prediction model review or nomogram/risk-score appraisal?
  -> prediction-model review mode
Already have a draft?
  -> revision / polishing mode
Ready to submit?
  -> submission / pre-review mode
Received reviewer comments?
  -> rebuttal / revision-response mode
Need a narrow late-stage operation?
  -> microtask / operations mode
```

## Stage 0: Intake and Constraints

Collect as much of the following as available:

- document type: article / thesis / proposal / review / rebuttal / cover letter
- discipline and subfield
- target journal / conference / degree context / funding context
- language: Chinese / English / bilingual
- citation style if required
- current stage: idea / outline / partial draft / full draft / revision after review
- available materials: title, abstract, notes, figures, legends, tables, methods, results, references, reviewer comments
- retrieval assets if applicable: export CSVs, EndNote/Zotero libraries, institutional access, authorized browser sessions, or provider workstations
- thesis context if applicable: monograph thesis / article-based thesis / chapter-based thesis, degree level, university or department rules, required front matter / back matter, chapter order
- hard constraints: word count, section rules, journal scope, deadline, audience

If key information is missing, ask only for the minimum needed to move to the correct subworkflow.

### Stage 0A0: Proactive Local Course-Library Absorption Mode

When the user mentions a relevant medical-statistics, prediction-model, survival-analysis, Table-1, missing-data, interaction/mediation, or statistical-learning knowledge point, assume there may already be a matching local teaching/code asset and check that path **proactively**, even if the user did not explicitly say “go search the local course folders”. Treat the local teaching/code corpus as a **default method library** whenever the topic overlap is strong enough.

This proactive mode should activate especially for knowledge points such as:

- missing data / multiple imputation / outliers / DAG / variable selection
- baseline table / descriptive summary / Table 1
- interaction / mediation / additive interaction / RERI / trend test
- survival analysis / Kaplan-Meier / Cox / conditional survival / adjusted KM
- ROC / calibration / nomogram / clinical prediction
- statistical learning / machine learning / mlr3 / xgboost / feature selection / tuning
- dynamic prediction / time-updated prediction

When this mode activates, do **not** treat those materials as generic attachments. Treat them as a **local method library** that may contain:

- topic-selection heuristics
- analysis templates
- reusable scripts or notebooks
- figure/table export patterns
- teaching-style explanations that can be converted into thesis- or paper-ready workflow guidance

This matters even when the user does not provide the path explicitly, because the local reusable teaching/code corpus may already contain course PDF folders, `temp_code` directories, tutorial `qmd` files, Shiny apps, packaged examples, or method-specific script collections.

Default local-course absorption sequence:

1. identify the likely method family from the user's goal or named knowledge point
2. check whether the local course/code library already contains a matching chapter / PDF / code directory
3. prefer executable code (`R`, `Rc`, `qmd`, notebooks, scripts, app skeletons) over slide titles when both exist
4. extract the smallest reusable workflow unit: input requirements -> key functions/packages -> step order -> output form
5. adapt that workflow to the user's current data, thesis chapter, figure, table, or methods-writing need
6. preserve source-path traceability in the answer so the user can revisit the exact local material

Hard rules for this mode:

- do not pretend a PDF filename alone proves its full contents
- do not silently copy course conclusions into the user's manuscript as if they were the user's own results
- do not over-prioritize prose summaries when runnable local code exists
- when both course slides and code exist, treat slides as framing and code as operational evidence
- if the topic overlap is weak or no matching local material exists, fall back cleanly to normal awas routing instead of forcing a local match

**REQUIRED REFERENCE:** Use `references/local-course-asset-bridge.md` whenever the task depends on, or is likely to benefit from, absorbing reusable methods from local teaching/course assets such as the paired local course PDF and `temp_code` libraries.

### Stage 0A: Evidence File Ingestion Policy

Before AWAS reads or analyzes any local file, office document, attachment-style local artifact, download-folder reference, or workspace file path, it must first invoke `deterministic-local-file-reading` as the intake router. AWAS should not bypass that router just because the downstream academic task is already obvious. The routing skill resolves the path and the file-type-specific read path first; AWAS then continues with academic stage diagnosis, evidence extraction, and writing coordination.

When the user provides files, attachments, screenshots, exports, or office documents, do **not** treat all files as equally trustworthy or equally readable. Choose the ingestion path by file type and evidence role before drafting.

Default file-ingestion order:

1. **Plain text / markdown / code / CSV / structured exports**
   - Prefer direct reading first.
   - Treat these as highest-traceability sources when they are user-provided primary artifacts.

2. **DOCX / XLSX / PPTX and similar Office files**
   - Prefer the dedicated office-reading workflow or convert to Markdown through a reliable Office-to-Markdown path before synthesis.
   - Use this especially when the writing task depends on headings, tables, speaker notes, reviewer comments, evidence matrices, or appendix materials.

3. **PDF files**
   - First decide whether the PDF is **text-based** or **scan-based**.
   - For text-based PDFs, prefer PDF extraction workflows over generic format conversion.
   - For layout-sensitive PDFs with tables, columns, figure captions, appendices, or supplements, prefer layout-aware extraction rather than naive plain-text conversion.
   - Treat supplementary PDFs as first-class evidence artifacts when they contain predictor definitions, hyperparameters, thresholds, model formulas, calibration details, or additional validation results not present in the main article.
   - For extraction-heavy review tasks, prefer a progressive path: page triage -> text extraction -> table extraction -> targeted page/region re-extraction -> verification against page locations.
   - Do **not** treat `pandoc` as the default PDF reader. Use it only after the content has already been reliably extracted into Markdown/text/HTML, or when producing output formats.

4. **Scanned PDF / screenshots / image-only documents**
   - Treat these as OCR tasks, not ordinary reading tasks.
   - Prefer OCR-specific workflows before using the extracted content in academic prose.
   - If OCR confidence is uncertain, keep extracted claims provisional and mark them for verification.
   - If the PDF is mixed-mode (some selectable text, some scanned tables/figures), combine text extraction with targeted OCR instead of pretending one pass is enough.

5. **Fast visual tools**
   - Use quick-look or overview-style tools only for coarse inspection, triage, or deciding what extraction path is needed next.
   - Do **not** use coarse visual summaries as the final evidence source for citation-sensitive drafting, numbers, model details, or table content.

### File-Type Decision Rules

| File type | Preferred first path | Use case |
|---|---|---|
| `.md`, `.txt`, `.csv`, structured exports | direct read | highest-traceability notes, evidence tables, screening logs |
| `.docx`, `.xlsx`, `.pptx` | office reader / Office-to-Markdown | manuscripts, appendices, tables, slides, review artifacts |
| text-based `.pdf` | PDF extraction | papers, reports, theses with embedded text |
| layout-heavy `.pdf` | layout-aware PDF extraction | tables, multi-column text, appendices, figure captions |
| supplement / appendix `.pdf` | targeted PDF extraction | model formulas, extra tables, calibration plots, thresholds, subgroup results |
| scanned `.pdf`, screenshots, images | OCR workflow | image-only evidence, scans, screenshots, non-selectable text |

### Hard Rules for Writing from Files

- Never quote exact numbers, statistics, or model details from a file that was only quick-looked rather than properly extracted.
- Never treat OCR output as fully verified if the source quality is poor, partially visible, or obviously ambiguous.
- Never collapse the distinction between `file seen`, `file extracted`, and `file verified`.
- If a file is central to the argument, methods, results, or citation grounding, prefer a reproducible extraction path over convenience.
- If a metric or model detail comes from a supplement or appendix PDF, preserve that provenance explicitly rather than silently merging it into the main-paper extraction.
- For review/meta work, prefer page-aware extraction whenever the downstream table may require row-level verification.
- When in doubt, downgrade the claim, add `[待核实]`, or request the underlying text/table export.

### Stage 0B: Default Reading Workflow for Writing Tasks

When a writing task depends on attached files, use this routing bias by default:

- **academic prose should be grounded in extracted text, tables, and structured artifacts — not quick visual impressions**
- prefer **direct reading** for plain text and structured exports
- prefer **office-reader or Office-to-Markdown** for `.docx`, `.xlsx`, `.pptx`
- prefer **PDF extraction** for text-based PDFs
- prefer **layout-aware / table-aware PDF extraction** for papers and supplements that will feed structured review or meta extraction
- prefer **OCR workflows** for scanned PDFs, screenshots, and image-only evidence
- use **quick-look / visual overview tools only for triage**, never as the final basis for citation-sensitive claims

### Stage 0C: PDF Extraction Escalation Ladder

When a PDF is important enough to influence extraction tables, meta-analysis inputs, appraisal judgments, or thesis-chapter claims, escalate reading like this:

1. decide text PDF vs scan PDF vs mixed PDF
2. extract page text with a reproducible PDF extractor
3. if layout matters, run layout-aware extraction for tables / multi-column sections / appendices
4. if supplements contain critical metrics, extract them separately rather than assuming the main text is sufficient
5. if any required content remains image-like or ambiguous, run OCR on the relevant pages or regions
6. mark content as verified only after the extracted values can be traced back to page-level evidence

For prediction-model review and meta tasks, the extraction target is often not the article narrative but the hidden tables, supplementary appendices, performance plots, and validation details.

If a source is central to methods, results, or literature claims, explicitly favor the more reproducible extraction path even when it is slower.

## Stage 1: Non-Negotiable Safeguards

Always enforce these rules:

1. **No fabricated references, statistics, or factual claims.**
2. **Separate verified facts from inferred placeholders.**
3. **If a citation cannot be verified, mark it for confirmation instead of inventing it.**
4. **Do not overclaim novelty, causality, robustness, or policy/clinical impact.**
5. **Prefer explicit uncertainty over confident hallucination.**
6. **Maintain traceability between user evidence and drafted prose.**
7. **Maintain comment -> action -> location traceability** whenever drafting rebuttals, revision roadmaps, or resubmission materials.
8. **Reduce obvious AI writing patterns** instead of simply making the text longer or fancier.
9. **Do not describe unstable or unauthorized retrieval as verified source access.**
10. **Never silently replace a nonexistent citation with a merely similar paper, webpage, report, or guideline; label such items as replacement candidates and require explicit confirmation before manuscript binding or Zotero import.**
11. **Default AI-written Zotero imports should go to the `cpu` collection unless the user explicitly names a different destination.**
12. **Default duplicate policy is keep-both: do not auto-merge or auto-deduplicate Zotero items unless the user explicitly requests cleanup.**
13. **When the task is China Pharmaceutical University professional-master thesis formatting, prioritize `<PRIVATE_WORKSPACE>\参考\论文格式.doc` and the local GB/T 7714-2015 thesis route over generic journal-style citation cleanup.**

### Integrity Red Flags

Stop and verify when you see:
- exact numbers with no visible source
- broad literature claims with no anchors
- `first`, `novel`, `robust`, `significant`, `effective` claims lacking support
- methods prose that appears more detailed than the provided material
- reviewer responses claiming revisions not actually made
- journal-fit judgments based only on prestige or impact factor

**REQUIRED REFERENCE:** Use `references/quality-and-integrity.md` whenever the task involves citation-sensitive writing, statistical interpretation, translation, polishing, or reviewer-response drafting.

## Stage 2: Choose the Working Mode

Before choosing the detailed mode, decide which of these three families the task belongs to:
- **paper-production family** — article, thesis chapter, abstract, outline, format conversion, or revision roadmap for a manuscript
- **review-project family** — narrative / scoping / systematic / umbrella / critical review with corpus, screening, and evidence-gate questions
- **late-stage operations family** — polishing, formatting adaptation, citation cleanup, reviewer response, or submission preparation

Within each family, use this order:
1. family
2. submode
3. preferred specialist skill if one clearly owns the bottleneck

If the user is still moving from idea -> novelty -> literature -> experiment/result framing -> paper drafting, treat that as a research-lifecycle task first rather than jumping straight into manuscript prose.

### A. Ideation / Proposal Mode
Use when the user is still defining the project.

Typical outputs:
- topic directions
- proposal skeleton
- opening report structure
- research gap statement
- contribution options
- thesis statement candidates

### A2. Research Lifecycle Mode
Use when the user is not merely asking for prose, but for help moving through the broader academic pipeline from early idea to paper-ready writing inputs.

Typical outputs:
- idea shortlist
- novelty-check plan
- literature-to-gap memo
- experiment/result packaging memo
- paper plan handoff
- review loop recommendation

This mode is where absorbed `academic-write` capabilities matter most. It should connect:
- idea discovery
- novelty checks
- literature review
- result analysis
- figure / compile awareness
- iterative review and polishing

without pretending all of those steps are fully automated inside one prompt.

### B. Outline / Argument Mode
Use when the topic exists but the manuscript logic is not stable.

Typical outputs:
- IMRaD outline
- review-article outline
- thesis chapter structure
- paragraph plan
- claim-to-evidence map
- chapter purposes and transition logic

### C. Section Drafting Mode
Use when the user requests one concrete section.

Available section families:
- `Introduction`
- `Methods`
- `Results`
- `Discussion`
- `Abstract`
- `Conclusion`
- `Thesis chapter introduction / findings / general discussion / thesis conclusion`
- `Title / Keywords / Highlights`

**REQUIRED REFERENCE:** Use `references/section-workflows.md` for deep section rules.

#### Introduction default ownership

When the user asks to write, rebuild, tighten, or quality-check an academic introduction, default to the native `Introduction Funnel Workflow` inside awas rather than scattering the task across separate gap, logic, polishing, or anti-AI paths.

Only break out of the funnel when the user explicitly asks for a narrower isolated job such as:

- literature-gap audit only
- paragraph logic repair only
- anti-AI polishing only
- structure roadmap only

Otherwise, treat introduction writing as one integrated rhetorical function with one primary path.

### C2. Thesis / Dissertation Mode
Use when the requested output is a master's thesis chapter, dissertation chapter, thesis proposal chapter, article-based thesis wrapper chapter, or thesis-level restructuring task.

Typical outputs:
- thesis architecture memo
- chapter-by-chapter outline
- chapter purpose map
- thesis introduction or literature review chapter
- methods chapter adapted from paper-style materials
- findings/results chapter from tables, figures, or coding outputs
- general discussion chapter
- final conclusion, implications, limitations, and future-work chapter
- thesis abstract / executive summary

Core distinctions to keep in mind:
- a thesis is not just a longer paper
- chapter purpose and cross-chapter transitions matter explicitly
- thesis chapters can tolerate more context-setting than journal sections, but still need evidence discipline
- article-based theses need wrapper logic that explains how chapters connect

### C2A. China Pharmaceutical University Thesis Scenario

Use this scenario when the user explicitly mentions:
- 中国药科大学
- 中国药科大学研究生学位论文
- 中国药科大学专硕 / 专业学位硕士论文
- 中国药科大学硕士学位（专业学位）论文
- 药大毕设 / 药大学位论文格式 / CPU thesis template

Default bias for this local project:
- treat **China Pharmaceutical University professional-master's thesis** as the main active scenario unless the user explicitly says they are in the 同等学历 route
- treat 同等学历 as a separate sub-scenario, not the default master-thesis assumption

In this scenario, AWAS should assume there may be school-specific format and front-matter constraints that outrank generic thesis defaults.

Priority rule for source conflicts:
- if multiple local school-format files disagree, treat `<PRIVATE_WORKSPACE>\参考\论文格式.doc` as the highest-priority local authority
- use the official school requirement files and the school templates as supporting references, not co-equal authorities once they conflict with that file
- treat the local template files as layout/examples references; treat `论文格式.doc` as the final compliance authority for this local project

Default CPU thesis requirements already learned from the current local sources:
- thesis package should usually include: cover, originality/copyright authorization, table of contents, Chinese abstract, English abstract, optional abbreviation list, thesis body, references, publication list during degree period, acknowledgements
- body should stay primarily in规范简体中文 except where the school explicitly allows English components
- reference style should follow the local thesis requirement source before generic journal-facing style habits
- body typography and layout should be treated as school-governed rather than journal-governed
- front matter, pagination, and chapter boundaries should be checked against the local school requirement source before drafting output claims
- for CPU professional-master's theses, the official requirement text explicitly distinguishes the professional-master cover/form route from the 同等学历 route; do not use the 同等学历 cover by default for a 专硕 task
- if the user is in the CPU 专硕 route, prefer the professional-master template logic first and use the 同等学历 template only as a contrastive reference when needed
- if the task is for blind review, allow a smaller review-package structure when the high-priority local authority file says so; do not force the older full archive package by default
- if older documents still mention earlier reference-style editions, follow the newer local authority file when it upgrades those requirements
- if the local CPU rule set requires an `人工智能技术辅助研究与写作承诺书`, treat it as a formal front-matter compliance item and include its pagination consequences in the route judgment

Hard rule:
- do not apply generic thesis defaults over explicit CPU rules just because the generic defaults are cleaner
- do not mix journal submission conventions with CPU thesis conventions without explicitly labeling the conversion
- if the user is writing a CPU thesis chapter, keep school-format compliance above paper-like elegance

**REQUIRED REFERENCES:**
- `references/section-workflows.md`
- `references/review-and-submission.md` when the thesis is being converted into papers or submission materials

### D. Literature Search / Screening Mode
Use when the user needs literature retrieval planning, query design, candidate corpus construction, screening logic, or evidence extraction before or during writing.

Typical outputs:
- search strategy memo
- concept groups and keyword expansion
- database/source routing
- candidate paper table
- screening criteria
- evidence matrix
- DOI cleanup and citation-governance prep

**REQUIRED REFERENCES:**
- `references/literature-search-and-screening.md`
- `references/quality-and-integrity.md`
- `references/review-routing-and-gates.md` when the search supports a review article

### D1. Chinese Thesis Retrieval / Learning Mode
Use when the user needs Chinese dissertation or master's-thesis discovery, institution-filtered thesis search, browser-assisted export workflows, or wants to learn from authorized thesis full text before writing.

Typical outputs:
- provider plan distinguishing official API, authorized browser workflow, and manual export fallback
- CNKI / Wanfang / institutional repository search strategy
- candidate pool with thesis metadata such as degree level, granting institution, advisor, and thesis type
- access-state notes separating metadata discovery, authorized full-text access, export availability, and manual follow-up
- thesis-to-manuscript learning memo showing what structures, methods descriptions, result framing, or chapter patterns are worth reusing

Hard rules:
- prefer official APIs and direct exports before browser automation
- use browser automation only with an existing authorized session, institution access, or user-owned workstation
- keep anti-bot, retries, and session persistence in the retrieval layer rather than inside writing logic
- never claim full-text learning succeeded unless the acquired artifact is present and readable

**REQUIRED REFERENCES:**
- `references/literature-search-and-screening.md`
- `references/agent-collaboration.md`
- `references/quality-and-integrity.md`
- `references/pdf-image-reading-playbook.md` when core evidence depends on PDFs, supplements, scanned pages, tables, figures, or image-based appendices

### D2. Review-Article Mode
Use when the requested document is a review, evidence map, scoping review, systematic review, umbrella review, critical/theoretical review, or prediction-model review.

Before writing prose, decide:
- what type of review it is
- whether strong evidence claims are justified
- what body framework should organize the review
- whether the evidence base is sufficient for a submission-grade draft
- whether the task is actually a prediction-model appraisal/review rather than a generic topic synthesis

Default bias in this mode: if the user has a corpus, spreadsheets, PDFs, checklists, or structured extraction artifacts, prefer **multi-agent review-project orchestration** over single-pass prose generation.

**REQUIRED REFERENCES:**
- `references/review-routing-and-gates.md`
- `references/review-and-submission.md`
- `references/section-workflows.md`
- `references/prediction-model-review.md` when the review centers on scores, nomograms, clinical prediction, or risk stratification tools

### D3. Review-Project Output Level
When the user wants a review, explicitly choose the strongest honest output level before drafting:

- `submission-grade review draft` — only when scope, corpus, framework, and claim-to-evidence support are visibly strong
- `review-grade evidence synthesis` — evidence is substantial enough for frameworked synthesis, but not yet for a polished submission draft
- `evidence map / scoping output` — useful mapping of what exists, where clusters sit, and where the gaps are
- `framework memo / review outline` — structure and writing logic are ready, but the evidence base is not yet stable

If the corpus, screening record, or evidence coverage is weak, downgrade explicitly instead of writing a pseudo-submission-grade review.

### D4. Prediction-Model Review Mode
Use when the user is reviewing clinical scores, nomograms, machine-learning models, or other prediction tools rather than a disease topic alone.

Typical outputs:
- prediction-model evidence map
- model appraisal table
- review-grade synthesis of model families
- gap memo on validation / calibration / transportability
- structure for a later full review

Core extraction dimensions:
- target population and clinical setting
- organism or resistance phenotype target
- predicted outcome
- model type (`score`, `nomogram`, `ML`, `other`)
- predictors used
- data-split and validation tier (`training set`, `internal validation set`, `internal test set`, `external validation set`, `external test set`, or clearly reported alternatives)
- discrimination / calibration / clinical utility if reported
- major bias or transportability concerns

Extraction priority in this mode:
- extraction quality is more important than early narrative fluency
- if structured extraction is weak, incomplete, or mixed across incomparable model types, stop tightening prose and strengthen extraction first
- if enough studies exist, prefer separating model-development extraction from model-evaluation extraction instead of collapsing them into one study summary line
- never collapse training-only, internal-only, and external evaluation results into a single undifferentiated “model performance” field

Hard rules:
- do not merge all prediction studies into one narrative if targets and settings differ too much
- distinguish risk-factor studies from actual deployable prediction models
- do not infer good model quality from a nomogram figure alone
- if methodological appraisal exceeds native coverage, explicitly borrow a local skill or external reporting/appraisal pattern and label it

Operational bias:
- prefer extracting model-development and model-evaluation details into structured artifacts before writing narrative synthesis
- prefer parallel appraisal of reporting quality, risk of bias, validation design, calibration, and clinical utility when enough study material exists
- treat PROBAST / PROBAST+AI / TRIPOD / TRIPOD-AI style checks as evidence-building stages, not cosmetic appendices
- when meta-synthesis is plausible, extract performance metrics and their study context in a way that preserves later comparability rather than merely summarizing “best AUC” values
- explicitly preserve whether each reported metric came from the training set, internal validation split, internal test split, external validation cohort, or external test cohort
- when a study includes both development and evaluation, preserve those branches separately in extraction and appraisal rather than giving the paper one undifferentiated quality label
- if internal validation used cross-validation or bootstrapping, preserve that method explicitly and do not confuse it with held-out testing or external evaluation

## Multi-Agent Mode

### When Multi-Agent Mode Should Activate

Activate multi-agent mode by default when any of the following are true:

- the user asks for a systematic review, scoping review, umbrella review, or meta-analysis
- the task depends on a corpus of PDFs, RIS/BIB/CSV exports, extraction tables, or audit spreadsheets
- the task includes screening, full-text adjudication, evidence extraction, or claim-to-citation stabilization
- the task involves prediction-model appraisal, TRIPOD-style reporting checks, PROBAST-style bias assessment, or AI-model audit
- the user needs a thesis chapter or manuscript section that is downstream of unresolved review-project state

### Multi-Agent Default Split

In multi-agent mode, prefer this split unless the task is obviously narrower:

1. retrieval / corpus normalization
   - `awas-retrieval-orchestrator`
2. screening / inclusion-exclusion adjudication
   - `awas-screening-analyst`
3. structured evidence extraction
   - `awas-evidence-extractor`
4. appraisal / audit
   - structured extraction review
   - reporting / bias / validation / calibration checks
5. proceed / refine / pivot stress test when evidence quality is uncertain
   - `awas-proceed-advocate`
   - `awas-refine-advocate`
   - `awas-pivot-advocate`
   - `awas-decision-synthesizer`
6. authenticity / consistency gate
   - `awas-citation-authenticity-auditor`
   - `awas-sentinel-watchdog`
7. downstream prose coordination
   - `awas-writing-coordinator`
   - `academic-write-all-skill`

### Multi-Agent Companion Roles Outside AWAS core artifacts

When the task extends beyond the native AWAS artifact loop, AWAS may attach exactly one additional companion lane per bottleneck:

1. ideation / early-topic narrowing
   - `research-ideation`
2. stable results bundle -> decision-oriented experiment report
   - `results-report`
3. Zotero collection -> canonical Obsidian paper-note and synthesis graph
   - `zotero-obsidian-bridge`

Hard rule:
- these companions are extensions of the main AWAS route, not co-equal alternate workflows
- do not activate them if an existing `awas-*` closed loop already owns the same bottleneck

### Default Process Layer: superpowers

When AWAS is the accepted academic intake, use the local `superpowers-*` skills as the default process-control layer.

Treat `superpowers` as a **typed support layer**, not as a co-equal academic content owner:

1. process-control layer
   - `superpowers-brainstorming`
   - `superpowers-writing-plans`
   - `superpowers-dispatching-parallel-agents`
   - `superpowers-subagent-driven-development`
   - `superpowers-executing-plans`
2. quality / completion layer
   - `superpowers-requesting-code-review`
   - `superpowers-verification-before-completion`
3. skill-and-agent ecosystem layer
   - `superpowers-writing-skills`

These are the default uses inside AWAS:

1. `superpowers-brainstorming`
   - use before creative academic design work, workflow invention, or major structural redesigns when the user is still shaping the task
2. `superpowers-writing-plans`
   - use when AWAS has already stabilized the task and now needs a concrete multi-step implementation or execution plan
3. `superpowers-dispatching-parallel-agents`
   - use when multiple independent academic subtasks can be delegated in parallel without shared-state conflicts
4. `superpowers-subagent-driven-development` / `superpowers-executing-plans`
   - use after AWAS planning when the task shifts from routing/design into execution of a concrete plan
5. `superpowers-requesting-code-review` / `superpowers-verification-before-completion`
   - use before AWAS claims a workflow, report, integration, or refactor is complete
6. `superpowers-writing-skills`
   - use only when AWAS itself, its child skills, or its `awas-*` agent ecosystem is being edited, extended, benchmarked, or packaged

Hard rule:
- `superpowers` is the generic process layer, not the academic owner of the task
- AWAS still chooses the academic route, specialist skill, and `awas-*` agent group first
- do not route normal manuscript drafting, review synthesis, plotting, literature retrieval, or reviewer-response work into `superpowers-writing-skills`

### Multi-Agent Mode Rules

- Do not let the writing layer redo retrieval or screening work that should already exist as artifacts.
- Do not let the writing layer compensate for poor extraction by drafting over missing study fields.
- Do not let a single agent both invent the framework and judge its own evidence sufficiency when a debate loop is justified.
- Prefer parallel agent launches when screening, extraction, appraisal, and writing-prep can proceed on separate artifacts without conflicting edits.
- Prefer staged artifacts over conversational memory. If a judgment matters later, persist it in the review-project files.
- When the corpus is weak or the appraisal state is incomplete, downgrade the output level instead of asking the writing coordinator to compensate with nicer prose.

### Dual-Review and Adjudication Rule

For evidence extraction and methodological appraisal, prefer a **two-reviewer plus arbitrator** pattern whenever the task is consequential enough to affect synthesis or pooled analysis.

Default pattern:

1. reviewer / extractor A works independently
2. reviewer / extractor B works independently
3. compare outputs
4. if there is material disagreement, launch a third adjudicator
5. preserve the adjudicated result as the operational truth while keeping prior outputs inspectable

Use this pattern especially for:
- split classification (`training`, `internal validation`, `internal test`, `external validation`, `external test`)
- retained-model decisions
- TRIPOD / TRIPOD+AI rescoring
- PROBAST / PROBAST+AI rescoring
- extraction of counts, performance metrics, and provenance-critical values

Do not let one scorer or extractor silently overrule another without an explicit adjudication step when the disagreement would affect downstream conclusions.

### Review / Meta Code-Aware Bias

When a review or meta-analysis task requires code-backed support, `academic-write-all-skill` should prefer reusable scripts and mature external workflow patterns over ad hoc prose-only handling.

Default extraction-first rule:
- for review or meta tasks, extraction is the primary substrate and prose is downstream of extraction
- if the user provides PDFs, spreadsheets, extraction tables, or audit sheets, prefer improving field-level extraction fidelity before expanding synthesis
- for prediction-model meta work, prefer a study-by-study extraction register that preserves outcome definition, validation tier, metric definition, and model context
- when PDF or image evidence is important, follow `references/pdf-image-reading-playbook.md` and keep page-level provenance in the extraction artifact

Examples of good code-backed patterns to borrow conceptually:
- `MetaScreener`-style staged workflow for criteria initialization, screening, extraction, risk-of-bias assessment, evaluation, and export
- `ASReview`-style active-learning screening when corpus size makes manual first-pass screening inefficient
- `paperfetcher`-style citation searching and handsearch/snowball support for systematic reviews
- `metafor`-style explicit separation between extraction-ready study data and downstream statistical synthesis

These are reference patterns, not guarantees of runtime availability. Borrow the workflow logic, evaluation checkpoints, and artifact contracts without pretending the full external platform is embedded locally.

### E. Revision / Polishing Mode
Use when a draft already exists.

Revision dimensions may include:
- logic repair
- claim-evidence alignment
- paragraph coherence
- style upgrade
- de-redundancy / shortening
- translation
- de-AI-ification
- grammar / terminology normalization
- anti-pattern cleanup for obvious AI-generated prose

**REQUIRED REFERENCES:**
- `references/microtasks-and-operations.md`
- `references/quality-and-integrity.md`
- `references/humanization-rules.md`

### E1. Anti-AI Closed Loop
Use when the user wants de-AIGC, `去AI味`, anti-template cleanup, or final humanization and the task spans Chinese round-tracked cleanup plus a later language-specific smoothing pass.

`academic-write-all-skill` should own this loop directly. Do not merely mention the downstream skills as suggestions; invoke the matching stage and report the state transition.

Closed-loop order:

1. classify the request
   - Chinese + round continuity / record tracking / strict structure preservation -> enter `ddaigc`
   - Chinese + only final native-language smoothing remains -> enter `humanizer-zh`
   - English-dominant or mixed English spans + final anti-AI cleanup remains -> enter `humanizer`
2. preserve the stage machine
   - if `ddaigc` rounds are unfinished, complete only the current due round
   - after `ddaigc` round 3 is complete, only then allow a final humanization pass
3. choose exactly one terminal smoother
   - `humanizer-zh` for Chinese-dominant prose
   - `humanizer` for English-dominant spans
4. block unsafe blending
   - never humanize before the required `ddaigc` rounds
   - never run `humanizer-zh` and `humanizer` on the same paragraph
   - never claim the full loop ran if only one stage ran

Required response fields in this lane:

- `Current stage`
- `This pass`
- `Next safe pass`

### F. Submission / Review Mode
Use when the user is near submission or already in revision after review.

Primary precedence inside this mode:
- if the task is broad journal-fit / pre-review / acceptance-risk / desk-reject screening -> stay in submission/review routing
- if the task is a qualitative five-lens vulnerability scan -> use `F1. Qualitative Review-Committee Routing`
- if the task is mainly a rebuttal package, response letter, response matrix, or reviewer-by-reviewer reply strategy -> prefer the `reviewer-response-assistant` downstream path and keep awas as stage control

Outputs may include:
- journal shortlist
- journal-fit memo
- desk-reject risk memo
- pre-submission review
- acceptance-risk heuristic assessment
- simulated qualitative review-committee package
- theory-contribution interrogation memo
- methods-transparency整改清单
- literature-gap validation memo
- logic-chain / structure audit memo
- editor-style first-pass screening memo
- cover letter
- reviewer response matrix
- response letter skeleton or full draft
- revision roadmap
- claim-evidence-citation matrix
- re-review verification memo

**REQUIRED REFERENCE:** Use `references/review-and-submission.md`.

### F1. Qualitative Review-Committee Routing
Use when the user wants a qualitative social science manuscript stress-tested through a simulated committee rather than a generic external-style review.

Default routing inside this submode:
- theoretical contribution / concept construction pressure test
  - prefer `qualitative-theory-contribution-interrogator`
- methods transparency / sampling / coding / saturation audit
  - prefer `qualitative-method-transparency-auditor`
- literature dialogue / gap validation / pseudo-innovation check
  - prefer `literature-gap-dialogue-validator`
- logic-chain / paragraph-flow / evidence-to-claim audit
  - prefer `argument-structure-forensics-auditor`
- editor-style first-pass triage / desk-reject risk
  - prefer `desk-reject-screening-editor`

When the user asks for a `模拟审稿委员会`, `模拟审稿`, `理论审稿人`, `Reviewer 2式方法挑刺`, `Desk Reject 预警`, or a closely related request, do not collapse everything into one generic review paragraph. Instead:
1. identify which of the five lenses are requested or most necessary
2. route to one or more of the five qualitative-review skills above
3. keep outputs separated by reviewer lens unless the user explicitly wants a merged synthesis
4. treat these audits as vulnerability scans for revision planning, not as evidence that the manuscript is submission-ready

### F2. Paper-Production Submodes
Use these submodes when the task is clearly paper-centric rather than review-corpus-centric:

- `full-draft` — build or extend a full paper or chapter set from available materials
- `outline-only` — stabilize structure, section jobs, and evidence allocation before drafting
- `abstract-only` — write or rewrite the abstract once the paper logic is sufficiently known
- `citation-check` — audit citation consistency, metadata completeness, source-type correctness, obvious orphan / missing-source issues, and when the user supplies a manuscript plus references, run the authenticity -> repair -> replacement-candidate -> Zotero-import -> processor-specific recitation loop
- `format-convert` — adapt between Markdown / LaTeX / DOCX expectations, citation-style expectations, or journal-facing packaging needs
- `revision-coach` — convert reviewer comments into a revision roadmap, response matrix, and execution bundle
- `figure-and-compile-aware` — keep drafting aligned with figure planning, visual evidence packs, and later paper-compilation constraints

These are routing labels, not a promise of full automation. Use the narrowest honest submode that matches the user’s stage.

### H. Paper-Workflow Awareness Mode
Use when the user is not asking for one isolated writing task, but is clearly somewhere in the broader manuscript lifecycle.

Examples:
- manuscript drafted but not integrity-checked
- reviewer comments received and revision strategy needed
- revised manuscript needs verification-style re-review
- the user needs stage diagnosis before deciding whether to write, review, revise, or finalize

This mode should think in terms of:
- draft
- integrity
- review
- revise
- re-review
- finalize

and should explicitly surface when the user really needs a handoff to a narrower specialist skill instead of more generic writing help.

without turning AWAS into a mandatory heavyweight pipeline.

**REQUIRED REFERENCES:**
- `references/review-and-submission.md`
- `references/opencode-skill-absorption-map.md`
- `references/external-project-absorption-map.md`

### G. Microtask / Operations Mode
Use when the user needs a narrower high-frequency task rather than full drafting.

Examples:
- grammar-only check
- reference-format check
- logic repair between paragraphs
- logic repair within paragraphs
- de-duplication or paraphrase
- academic translation
- title candidates
- abstract compression
- stats-to-prose conversion
- reviewer vulnerability scan

**REQUIRED REFERENCE:** Use `references/microtasks-and-operations.md`.

## Default Subworkflow by Task

Treat this table as a routing aid, not as permission to keep multiple equivalent paths alive. If a request matches a narrow specialist skill cleanly, prefer that specialist route and use awas only to preserve stage awareness, evidence discipline, and handoff logic.

Keep this table focused on family-level and submode-level routing. Do not try to list every specialist skill trigger here; specialist ownership belongs primarily in `Skill Handoff / Specialist Boundary`.

| User request | Default route |
|---|---|
| `帮我想选题` | Ideation / Proposal Mode |
| `帮我做 research ideation / gap analysis / method selection` | A0 -> primary: `research-ideation` |
| `我要用科研写作助手 / research-writing-assistant 来走 brainstorming -> chapters -> LaTeX 流程` | Process-first academic drafting -> primary: `research-writing-assistant` |
| `帮我找研究idea` | A2 -> Research Lifecycle Mode |
| `帮我查新` | A2 -> Research Lifecycle Mode |
| `帮我写开题` | Ideation / Proposal Mode |
| `帮我搭框架` | Outline / Argument Mode |
| `帮我列论文提纲` | F2 -> `outline-only` |
| `帮我写引言` | Section Drafting -> Introduction |
| `帮我写引言第一段开头，不要用近年来/随着科技发展这种套话` | Section Drafting -> Introduction Funnel Workflow |
| `帮我把文献综述顺滑过渡到研究缺口` | Section Drafting -> Introduction Funnel Workflow |
| `帮我写研究目的段，方法要和缺口对齐` | Section Drafting -> Introduction Funnel Workflow |
| `帮我写引言最后一段结构路标` | Section Drafting -> Introduction Funnel Workflow |
| `帮我检查引言是不是像漏斗一样顺滑收敛` | Section Drafting -> Introduction Funnel Workflow |
| `帮我写方法` | Section Drafting -> Methods |
| `帮我写结果` | Section Drafting -> Results |
| `帮我写讨论` | Section Drafting -> Discussion |
| `帮我写摘要` | Section Drafting -> Abstract |
| `帮我重写摘要` | F2 -> `abstract-only` |
| `帮我写硕士论文` | Thesis / Dissertation Mode |
| `帮我写中国药科大学毕业论文 / 中国药科大学学位论文` | Thesis / Dissertation Mode -> China Pharmaceutical University Thesis Scenario |
| `帮我按中国药科大学模板改论文` | Thesis / Dissertation Mode -> China Pharmaceutical University Thesis Scenario |
| `帮我写中国药科大学专硕论文 / 专业学位硕士论文` | Thesis / Dissertation Mode -> China Pharmaceutical University Thesis Scenario (professional-master bias) |
| `帮我写中国药科大学同等学历硕士论文` | Thesis / Dissertation Mode -> China Pharmaceutical University Thesis Scenario (same-equivalent sub-scenario) |
| `帮我搭硕士论文框架` | Thesis / Dissertation Mode |
| `帮我写论文结果章` | Thesis / Dissertation Mode |
| `帮我把实验结果整理成写作输入` | A2 -> Research Lifecycle Mode |
| `帮我分析实验结果 / compare runs / interpret metrics` | G -> Microtask / Operations Mode -> primary: `analyze-results` |
| `帮我把分析结果整理成实验总结报告 / results report` | E -> primary: `results-report` after strict analysis is ready |
| `根据图表写结果` | Section Drafting -> Results |
| `根据表格写结果` | Section Drafting -> Results |
| `帮我找 PlotCase 里适合这个场景的图例 / 模板` | G -> Microtask / Operations Mode -> primary: `plotcase` |
| `帮我用 PlotCase 画这个图` | E -> Figures, tables, and concept visualization -> primary: `plotcase` |
| `帮我检索文献` | Literature Search / Screening Mode |
| `帮我核对参考文献列表并纠错后写入Zotero` | Literature Search / Screening Mode -> authenticity-and-zotero loop (`cpu` destination, keep-both duplicates, journal MCP-first, non-journal API-first) |
| `我给你文稿和参考文献表，你帮我核验文献、纠正错误并回填引用` | F2 -> `citation-check` -> authenticity-and-zotero loop -> processor-specific recitation |
| `帮我把参考文献表里不存在的文献换成最接近的真实文献候选` | F2 -> `citation-check` -> replacement-candidate search with explicit confirmation gate |
| `帮我把 Zotero 里的文献转成 Obsidian 里的论文笔记和知识图谱` | Literature Search / Screening Mode -> primary: `zotero-obsidian-bridge` |
| `帮我做文献到选题的收敛` | A2 -> Research Lifecycle Mode |
| `帮我做相关工作检索` | Literature Search / Screening Mode |
| `帮我搭检索式` | Literature Search / Screening Mode |
| `帮我筛文献` | Literature Search / Screening Mode |
| `帮我检索某院校毕业论文` | Chinese Thesis Retrieval / Learning Mode |
| `帮我学习知网/万方学位论文` | Chinese Thesis Retrieval / Learning Mode |
| `帮我做综述` | Review-Article Mode |
| `帮我做投稿级综述项目 / systematic review / scoping review / corpus-based literature review` | D2 -> Review-Article Mode -> primary: `cross-disciplinary-review-writer` |
| `帮我做预测模型综述` | D4 -> Prediction-Model Review Mode |
| `帮我评估一个nomogram` | D4 -> Prediction-Model Review Mode |
| `帮我评估一个风险评分模型` | D4 -> Prediction-Model Review Mode |
| `帮我翻译全文` | Revision / Polishing Mode |
| `帮我润色` | Revision / Polishing Mode |
| `帮我收到审稿意见不知道先干嘛` | Paper-Workflow Awareness Mode |
| `帮我检查这篇稿子现在处在哪个阶段` | Paper-Workflow Awareness Mode |
| `帮我把审稿意见整理成修订路线图` | F2 -> `revision-coach` |
| `帮我做重审验证` | Submission / Review Mode |
| `帮我写response letter` | Submission / Review Mode -> primary: `reviewer-response-assistant` |
| `帮我做返修说明 / claim-evidence表 / response matrix` | Submission / Review Mode |
| `帮我模拟审稿委员会审一下这篇质性论文` | F1 -> Qualitative Review-Committee Routing |
| `帮我看这篇质性论文有没有理论贡献 / 方法漏洞 / gap 问题 / 结构问题 / desk reject 风险` | F1 -> Qualitative Review-Committee Routing |
| `帮我检查引用` | F2 -> `citation-check` |
| `帮我按APA7改参考文献` | F2 -> `citation-check` -> prefer `apa7-citation-formatter` |
| `帮我按中国药科大学专硕论文参考文献要求改格式` | Thesis / Dissertation Mode -> China Pharmaceutical University Thesis Scenario -> `citation-check` with CPU professional-master 2015 priority |
| `帮我按中国药科大学专硕2015格式整理参考文献` | Thesis / Dissertation Mode -> China Pharmaceutical University Thesis Scenario -> `citation-check` with CPU professional-master 2015 priority |
| `帮我转LaTeX` | F2 -> `format-convert` |
| `帮我转换引用格式` | F2 -> `format-convert` |
| `帮我把参考文献改格式 / 做三线表 / 检查摘要结构 / 换投期刊适配` | G -> Microtask / Operations Mode |
| `帮我把访谈逐字稿清洗一下` | G -> Microtask / Operations Mode -> prefer `qualitative-transcript-cleaner` |
| `帮我整理论文标题层级` | B -> Outline / Argument Mode -> prefer `academic-outline-normalizer` |
| `帮我根据图表推进论文写作` | F2 -> `figure-and-compile-aware` |
| `帮我写论文图代码 / 优化论文图 / 改成新媒体图（纯视觉）` | G -> Microtask / Operations Mode |
| `帮我把文献综述改得更有对话感` | Review-Article Mode |
| `帮我把田野材料写得更有深描感` | Revision / Polishing Mode |
| `帮我检查逻辑` | Microtask / Operations Mode |
| `帮我重构这段论证逻辑` | G -> Microtask / Operations Mode |
| `帮我去AI味并学术化表达` | Revision / Polishing Mode |
| `帮我先降AIGC，最后再顺得像中文母语者写的` | Revision / Polishing Mode -> E1 Anti-AI Closed Loop |
| `帮我把最后这段英文去AI味，但不要改证据内容` | Revision / Polishing Mode -> E1 Anti-AI Closed Loop |
| `帮我深度重写这段论文` | Revision / Polishing Mode |
| `帮我改参考文献格式（仅APA引用）` | F2 -> `citation-check` -> primary: `apa7-citation-formatter` |
| `帮我改引用+摘要结构+三线表+换投适配（组合排版）` | G -> Microtask / Operations Mode -> primary: `ai4scholar-排版助手` |
| `帮我选刊` | Submission / Review Mode |
| `帮我预审稿` | Submission / Review Mode |
| `帮我回审稿意见` | Submission / Review Mode -> primary: `reviewer-response-assistant` |
| `Reviewer 2这条怎么回` | Submission / Review Mode -> primary: `reviewer-response-assistant` |

## Output Patterns

### Pattern 1: Minimal Missing-Info Request
Use when input is insufficient.

Ask only for the most blocking items, usually from:
- topic / working title
- target output type
- key findings or materials
- target journal or discipline

### Pattern 2: Outline First
Use when structure is unstable.

Return:
- section hierarchy
- function of each section
- missing information needed per section

### Pattern 3: Draft with Explicit Placeholders
Use when the user wants progress but materials are incomplete.

Examples:
- `[待补：样本量]`
- `[待核实：文献来源]`
- `[待补：试剂货号 / 参数 / 页码]`
- `[待确认：目标期刊格式要求]`

### Pattern 3B: Figure/Table-Driven Results Draft
Use when the user has tables, figure legends, model outputs, coding summaries, or statistical results and wants prose drafted from them.

Return in this order:
- result block heading aligned to hypothesis / figure / table / question
- one orienting sentence explaining what was tested or compared
- faithful result sentences with numbers, directions, contrasts, and uncertainty preserved
- explicit `[待核实]` markers for any hidden statistic, label, sample size, or unit not visible in the source artifact
- optional carry-forward note for what belongs in Discussion rather than Results

### Pattern 4: Revision Matrix
Use for polishing, review, or rebuttal.

Return a table with:
- issue
- why it matters
- suggested revision
- revised wording
- evidence/check needed

### Pattern 5: Claim-Evidence-Citation Matrix
Use when the user needs argument stabilization, pre-submission review, review writing, reviewer response drafting, or manuscript-plus-reference-list verification before Zotero import and recitation.

Return a table with:
- claim / point
- evidence currently available
- citation or source status
- source type (journal / book / thesis / webpage / report / guideline / conference / unknown)
- authenticity verdict (`PROCEED` / `REFINE` / `PIVOT`)
- Zotero state (`not-imported` / `ready-to-import` / `imported` / `needs-user-confirmation`)
- recitation target (`Word dynamic` / `WPS conservative` / `static-only`)
- weakness / overclaim risk
- revision action
- manuscript location or intended location

### Pattern 6: Reviewer Response Package
Use when the user has editor or reviewer feedback.

Return a bundle containing:
- comment ID
- reviewer/editor point
- response stance (`accept`, `partially accept`, `reasoned disagreement`, `cannot implement`)
- action taken
- revised text or revision summary
- manuscript location
- evidence still needed
- tone risk if any

## Skill Handoff / Specialist Boundary

`academic-write-all-skill` is the routing-and-standards layer for academic writing work. It should not pretend to be every specialist tool at once. When a task becomes clearly specialist, keep the workflow coherent but choose one primary downstream path.

### Route Selection and Path Evaluation Rule

Before handing a task to any downstream skill or `awas-*` agent, AWAS should run a lightweight path evaluation.

Evaluate candidate paths on four dimensions:

1. **stage fit**
   - does this path match the user's current academic stage, or is it for an earlier/later stage?
2. **artifact fit**
   - does the path have the right substrate: draft, corpus, figures, metrics, Zotero library, review artifacts, or project memory?
3. **execution fit**
   - does the path rely on a real local runtime, scripts, GUI, or external capability that actually exists here?
4. **overlap cost**
   - if this path is chosen, will another near-equivalent path become redundant for the same bottleneck?

Choose the path with the strongest combined fit and the lowest overlap cost.

Hard rule:
- one user-facing bottleneck -> one primary path
- do not keep two near-equivalent owners alive just because both are locally installed
- if multiple paths appear plausible, prefer the narrower owner with the strongest local execution evidence

### A0. Process-first academic drafting
- use `research-writing-assistant` when the user explicitly wants the Norman-bury research-writing workflow, a mandatory brainstorming -> chapter-writing -> LaTeX pipeline, or a file-oriented thesis/project-writing process that should stay stricter and more staged than awas' lighter orchestration
- use `research-ideation` when the user explicitly wants a startup-phase ideation workflow with literature review, gap analysis, method selection, and Zotero-assisted project initiation before manuscript drafting begins

Precedence rule for this group:
- if the user explicitly names `research-writing-assistant`, `research-writing-skill`, `科研写作助手`, or asks for a Norman-bury style brainstorming -> chapters workflow, route there first and let awas remain the stage-aware wrapper
- if the user explicitly names `research-ideation`, asks for a startup-phase research initiation workflow, or wants Zotero-assisted idea -> gap -> method planning before any manuscript output, route there first and let awas remain the stage-aware wrapper

### A. Citation, formatting, and venue adaptation
- use `citation-management` when the bottleneck is DOI lookup, metadata normalization, source-type correction, nontraditional-source repair, replacement-candidate search, or export-ready references; keep duplicate Zotero items by default unless the user explicitly asks for deduplication
- use `apa7-citation-formatter` when the user explicitly needs APA 7th reference-list or in-text citation normalization for verified entries only
- use `ai4scholar-排版助手` when the bottleneck is reference formatting across multiple styles, three-line table generation, abstract-structure polishing, or journal resubmission formatting adaptation
- use `journal-format-converter` when the user provides a target journal or school guide and the core task is visible format adaptation
- use `venue-templates` when the need is venue-specific formatting constraints rather than generic prose help
- use `latex-compile-qa` when the bottleneck is LaTeX compilation or bibliography build failure

Precedence rule for this group:
- if the request combines citation style + abstract structure + table format + resubmission adaptation, choose `ai4scholar-排版助手` as the single primary path
- if the request is narrowly and explicitly about APA 7 reference-list / in-text citation normalization only, choose `apa7-citation-formatter`
- if the request is a China Pharmaceutical University professional-master thesis reference task, prefer the local thesis authority path first and keep generic citation-formatting skills downstream only after CPU compliance is stabilized

### B. Qualitative review-committee and manuscript vulnerability audit
- use `academic-paper-reviewer` for a broad external-style review
- use `qualitative-theory-contribution-interrogator` for theoretical contribution, concept ambiguity, or grounded-theory elevation
- use `qualitative-method-transparency-auditor` for methods transparency, sampling logic, coding strategy, saturation, triangulation, or reflexivity reporting
- use `literature-gap-dialogue-validator` for literature dialogue, gap validity, pseudo-innovation detection, or missing foundational/frontier conversations
- use `argument-structure-forensics-auditor` for paragraph-to-paragraph logic, evidence-to-claim structure, causal inversion, overgeneralization, or concept switching
- use `desk-reject-screening-editor` for title-abstract-introduction pitch strength, journal-facing first impression, or desk-reject triage

Precedence rule for this group:
- if the user explicitly wants a committee-style split by theoretical, methodological, literature, structural, and editorial lenses, default to `Qualitative Review-Committee Routing`
- use `academic-paper-reviewer` only when the user wants a broader external-style review rather than the five-lens qualitative committee pattern

### C. Structure, rewriting, and language repair
- use `academic-outline-normalizer` for heading hierarchy repair or TOC-safe outline normalization
- use `logic-skeleton-rewriter` for argument structure, transition logic, or premise-to-conclusion repair
- use `academic-expression-polisher` for denser, more objective, less AI-patterned academic language
- use `academic-manuscript-rewriter` for deep manuscript reconstruction rather than light polishing
- use `ddaigc` for strict round-tracked Chinese academic de-AIGC stages inside the awas anti-AI closed loop
- use `humanizer-zh` as the terminal Chinese pass after facts, structure, and terminology are already stable or after `ddaigc` rounds have completed
- use `humanizer` as the terminal English pass for English-dominant spans after the Chinese stage is already safe
- treat `ddaigc-humanizer-stack` as a legacy compatibility wrapper for direct user invocation, not the default awas handoff

Introduction-specific precedence inside this group:
- if the user is still building a full introduction, keep `Introduction Funnel Workflow` as the primary path
- use `literature-gap-dialogue-validator` only when the user wants a gap audit rather than a full introduction progression
- use `logic-skeleton-rewriter` only when the introduction already exists and the bottleneck is transition logic rather than rhetorical staging
- use `humanizer-zh` / `humanizer` only as terminal cleanup after the introduction funnel has already stabilized the rhetorical jobs

Precedence rule for this group:
- if the user explicitly wants multi-round Chinese de-AIGC with record continuity, enter the awas anti-AI closed loop at `ddaigc`
- if the user wants multi-round Chinese de-AIGC plus a final native-language smoothing pass, awas should still own the loop and advance to `humanizer-zh` or `humanizer` only when the current `ddaigc` state allows it
- if the bottleneck is mainly Chinese tone repair after structure is stable, prefer `humanizer-zh`
- if the bottleneck is reasoning, inference, transition, or claim structure, prefer `logic-skeleton-rewriter` first
- if the bottleneck is full-paragraph or section reconstruction with preserved evidence, prefer `academic-manuscript-rewriter`
- if the bottleneck is mainly wording density or tone repair in English or mixed English prose, prefer `humanizer` or `academic-expression-polisher`, not all of them in parallel

### D. Review response and revision execution
- use `reviewer-response-assistant` when the main deliverable is a reviewer response letter, stance decomposition, or rebuttal package
- use `cross-disciplinary-review-writer` when the user needs a corpus-based, submission-grade review-project executor after AWAS has already classified the review type and evidence level

### E. Figures, tables, and concept visualization
- use `academic-table-normalizer` for a manuscript-ready table, three-line-table skeleton, or caption-note normalization when the task is table-only rather than broader formatting adaptation
- use `academic-python-plotting` for publication-ready Python plotting
- use `stata-academic-graphing` for Stata plotting, margins/coef/event-study figure generation, or graph-code refinement
- use `plotcase` when the user explicitly wants PlotCase, wants to search bundled local PlotCase examples, wants a GUI-driven high-end R plotting workflow, or when AWAS needs a local interactive plotting handoff after identifying a suitable PlotCase template
- use `journal-figure-polisher` when an existing figure needs parameter-level visual refinement for journal submission
- use `academic-chart-to-new-media` when the user wants to adapt paper figures for public-facing or platform-native visual communication
- use `grounded-theory-concept-network` when coding results need to become concept networks, Mermaid logic maps, or node-edge structures

Plotting / results packaging precedence inside this group:
- if the user needs strict quantitative analysis first, route to `analyze-results` before report writing
- if the user already has analysis artifacts and now needs a complete internal experiment report, route to `results-report` as the single primary downstream path
- if the user explicitly wants a programmable figure generation path, prefer `academic-python-plotting` or `stata-academic-graphing` before PlotCase
- use `plotcase` only as the primary downstream path when the user explicitly wants PlotCase, wants to reuse bundled PlotCase examples, or wants an interactive GUI-first plotting workflow that the current code-first plotting skills do not own cleanly
- do not claim that PlotCase exposes a stable external API; AWAS should treat it as example-search + GUI-launch capability unless stronger local evidence appears later
- if the user is still drafting manuscript prose from figures or tables, keep `figure-and-compile-aware` as the primary AWAS path and attach plotting/report skills only downstream

Precedence rule for this group:
- if the user wants prose advancement from figures/tables plus downstream visual cleanup, keep `figure-and-compile-aware` as the primary awas path and treat plotting/polishing/new-media skills as downstream specialists
- if the request is purely visual and no manuscript-stage coordination is needed, route directly to the narrow figure skill instead

### F. Retrieval, pipeline, and evidence-workflow escalation
- use `research-pipeline` style logic when the user is still doing idea discovery, novelty checking, or broad research-to-paper planning before a stable manuscript exists
- use `research-lit`, `arxiv`, or `pubmed-database` when the bottleneck is active retrieval depth rather than writing-stage synthesis
- use `zotero-obsidian-bridge` when the user explicitly wants Zotero as the literature source of truth and Obsidian as the durable paper-note / synthesis destination
- use `awas-retrieval-orchestrator` when the bottleneck is provider routing, authorized browser workflows, export normalization, or access-state management
- use `awas-screening-analyst` when inclusion / exclusion decisions or full-text adjudication are unstable
- use `awas-evidence-extractor` when the bottleneck is structured extraction from included studies rather than narrative prose
- use `awas-writing-coordinator` when the user already has structured artifacts and now needs section-level drafting that stays aligned with them

Within the AWAS review-project stack, do not fake execution of those specialist functions. Instead, adopt their standards, ask for the minimum missing material, keep outputs traceable, and downgrade the output level when the evidence or runtime substrate is not actually present.

When the user’s request is truly narrow and already well specified, route to the narrow skill first and use `academic-write-all-skill` only as the stage-aware wrapper that explains why that narrower route is the correct one.

## Capability Gap / Self-Update Handling

When the requested task exceeds what `academic-write-all-skill` can safely do with its current absorbed capability set, use this escalation order:

1. **Check bundled references and templates first**
   - read the relevant material in `references/`
   - use `references/capability-map.md`, `references/opencode-skill-absorption-map.md`, and `references/external-project-absorption-map.md` to understand what is already absorbed versus deliberately omitted
   - inspect `assets/templates/lessons_memory.md` when the task suggests a recurring gap or an improvable pattern

2. **Borrow from stronger local skills before inventing a new approach**
   - if the gap is process-first academic drafting with explicit brainstorming -> chapter-writing -> LaTeX routing, use `research-writing-assistant` logic
   - if the gap is startup-phase ideation with literature / gap / method planning, use `research-ideation` logic
   - if the gap is retrieval-heavy, use `research-lit`, `pubmed-database`, `arxiv`, or `citation-management` logic
   - if the gap is Zotero-to-Obsidian canonical literature management, use `zotero-obsidian-bridge` logic
   - if the gap is post-analysis experiment reporting, use `results-report` logic after `analyze-results`
   - if the gap is high-end interactive plotting with reusable local GUI templates, use `plotcase` logic after the main analytical route is fixed
   - if the gap is review-heavy, use `academic-paper-reviewer` or review-pipeline style logic
   - if the gap is format / compile / venue specific, use `latex-compile-qa` or `venue-templates` logic
   - if the gap is install / distribution / skill-structure related, use `skill-creator`, `add-skill`, or `opencode-agent-creator` logic
   - if the gap is review-project execution at scale, prefer multi-agent coordination plus bundled review scripts over inflating the core skill text

3. **Only then learn from external projects or GitHub examples**
   - prefer official docs, maintained GitHub repositories, or clearly implementable patterns
   - absorb concepts and implementation patterns, not entire projects blindly
   - treat external examples as provisional learning until they are reconciled with this skill's integrity rules and routing model
   - for systematic review / meta-analysis automation, prefer mature workflow references such as `MetaScreener`, `ASReview`, `paperfetcher`, and `metafor`-style artifact boundaries before adopting smaller experimental repos

4. **Record the gap and what was learned**
   - if a new pattern materially improves future handling, store it in the lessons-memory style format
   - update routing or references only when the learned pattern is stable enough to improve future outputs

### Hard rules for self-update
- never claim a new capability is native just because an external project demonstrates it
- never fabricate local-skill behavior that was not actually invoked or available
- never import GitHub patterns that weaken citation verification, evidence provenance, or downgrade honesty
- never let self-update bypass integrity gates, placeholder rules, or claim-evidence-citation traceability

### Good self-update language
- `This part exceeds the current core skill; I am borrowing the retrieval pattern from a stronger local research skill.`
- `The current package does not natively implement this step, so I am using a GitHub/official-doc pattern as a bounded reference, not as guaranteed runtime support.`
- `I can continue with a downgraded evidence-aware output now, and treat the missing capability as a future improvement target.`

## External Reference Files

- `references/literature-search-and-screening.md` — literature search strategy, screening, evidence extraction, and citation-governance handoff
- `references/humanization-rules.md` — anti-AI-tone cleanup rules adapted from local humanizer skill
- `references/opencode-skill-absorption-map.md` — absorbed capabilities from existing OpenCode skills
- `references/external-project-absorption-map.md` — absorbed capabilities from external GitHub projects and local non-OpenCode skill sources
- `references/capability-map.md` — synthesis of absorbed source families and architecture rationale
- `references/section-workflows.md` — deep section drafting rules
- `references/review-routing-and-gates.md` — review-type routing and evidence gates
- `references/review-and-submission.md` — review writing, journal selection, pre-review, rebuttal, and submission workflows
- `references/prediction-model-review.md` — prediction-model review/appraisal workflow for scores, nomograms, and risk models
- `references/pdf-image-reading-playbook.md` — operational PDF/image reading guide for supplements, appendices, OCR escalation, and page-level verification
- `references/microtasks-and-operations.md` — high-frequency late-stage academic operations
- `references/china-pharmaceutical-university-thesis.md` — school-specific CPU thesis authority order, professional-master bias, and thesis-vs-paper boundary rules
- `references/quality-and-integrity.md` — anti-hallucination, citation, evidence, translation, and polishing rules
- `references/agent-collaboration.md` — how companion agents, scripts, templates, and the `awas-*` agent group collaborate
- `references/local-academic-routing-matrix.md` — canonical ownership matrix for local academic routes, AWAS-first intake, OMO support boundaries, and forbidden parallel owner paths
- `references/literature-authenticity-sentinel.md` — four-layer citation authenticity verification before writing handoff

## Bundled Concrete Assets

AWAS now includes reusable concrete assets for review-grade literature workflows.

- `scripts/review_project_schema.py` — canonical field definitions for review-project CSV artifacts
- `scripts/init_review_project.py` — initialize a staged review-writing project scaffold
- `scripts/import_and_dedupe_candidates.py` — normalize external search exports into the candidate-pool schema and flag duplicates
- `scripts/generate_gate_report.py` — compute a lightweight gate report from populated project files
- `scripts/session_state_driver.py` — validate stage readiness and advance the staged workflow via `session_manifest.md`
- `scripts/build_decision_packet.py` — build a proceed/refine/pivot debate packet from current artifacts
- `scripts/synthesize_debate_loop.py` — materialize stance files and synthesize a decision record from gate/authenticity artifacts
- `scripts/sentinel_watchdog.py` — audit gate consistency and unsafe handoff states before final delivery
- `scripts/citation_authenticity_sentinel.py` — generate a four-layer citation authenticity report from project artifacts
- `assets/templates/` — ready-to-use CSV and Markdown templates for candidate pool, screening, evidence extraction, claim mapping, outline, and figure planning
- `assets/templates/prediction_model_meta_split_extraction.csv` — split-aware extraction sheet for prediction-model meta work with training/internal/external tiers and metric provenance
- `assets/templates/research_pipeline_config.yaml` — pipeline-style stage config for AWAS-centered multi-agent workflows
- `assets/templates/gate_checklist.md` — staged human/quality gate checklist
- `assets/templates/deliverables_manifest.md` — final output and handoff manifest
- `assets/templates/debate_packet.md` — input brief for proceed/refine/pivot debate
- `assets/templates/proceed_case.md` — persisted proceed stance output
- `assets/templates/refine_case.md` — persisted refine stance output
- `assets/templates/pivot_case.md` — persisted pivot stance output
- `assets/templates/decision_record.md` — judge/synthesizer output for debate loops
- `assets/templates/sentinel_watch_report.md` — watchdog audit output
- `assets/templates/lessons_memory.md` — lightweight self-learning memory log with time-decay metadata
- `assets/templates/citation_authenticity_report.md` — literature authenticity audit output

These assets can also track Chinese-thesis source fields and access-mode state when the project relies on CNKI, Wanfang, institutional repositories, or browser-assisted exports.

These concrete assets make AWAS suitable as the standards-and-writing layer inside a larger multi-agent research workflow.

Use these when the task is concrete enough that loose notes are no longer sufficient.

## Companion Agents

AWAS can now pair with companion OpenCode agents stored under `<USER_HOME>\.config\opencode\agent\`:

- `awas-retrieval-orchestrator`
- `awas-screening-analyst`
- `awas-evidence-extractor`
- `awas-proceed-advocate`
- `awas-refine-advocate`
- `awas-pivot-advocate`
- `awas-decision-synthesizer`
- `awas-sentinel-watchdog`
- `awas-citation-authenticity-auditor`
- `awas-writing-coordinator`
- `awas-research-ideation-coordinator`
- `awas-results-report-coordinator`
- `awas-zotero-obsidian-coordinator`
- `awas-plotcase-orchestrator`

Recommended split:
- agents execute and maintain project state
- the retrieval orchestrator owns provider routing, source-specific access strategy, and authorized browser handoff when needed
- debate agents stress-test whether the project should proceed, refine, or pivot
- authenticity audit checks whether citations are real, supportable, and safely bound to claims
- scripts normalize and compute
- templates record intermediate artifacts
- AWAS provides the writing standards, routing logic, evidence-faithful drafting rules, and typed `superpowers` process layer

## Common Mistakes

- drafting polished prose before the outline is stable
- treating a master's thesis as if it were just a journal article with extra pages
- writing Introduction without a real gap statement
- writing Methods without adequate source details
- writing Results from memory instead of from tables, figures, legends, or statistical outputs
- mixing Results and Discussion
- translating vague Chinese into elegant but inaccurate English
- polishing style while argument structure remains weak
- recommending journals by impact factor alone
- pretending to estimate acceptance probability with false precision
- writing a review article without first deciding review type and body framework
- ignoring manuscript lifecycle stage and jumping into the wrong task mode
- treating high-frequency microtasks as if they require full-manuscript rewriting every time
- confusing metadata discovery with verified full-text access
- burying browser-access logic inside the writing stage instead of the retrieval layer

## Final Check Before Returning Output

Before delivering, verify:
- Does every strong claim have visible support?
- Is the structure right for the requested genre?
- Is any fabricated citation-like content present?
- Did Results stay separate from Discussion?
- If figures/tables were the evidence source, did the prose stay faithful to what those artifacts actually show?
- If this is a thesis task, do chapter boundaries and transitions make sense at thesis scale rather than paper scale?
- Are placeholders visible where evidence is missing?
- Did polishing introduce new facts?
- Did the output match the user’s real stage rather than the most tempting stage?













