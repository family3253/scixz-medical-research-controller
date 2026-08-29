# Academic Writing Orchestrator Capability Map

## Source Families Absorbed

### 1. 迪娜学姐 2.0 提示词合集
Strengths extracted:
- journal-aware section writing
- staged drafting by section
- introduction / methods / results / discussion decomposition
- title, abstract, highlights, graphical abstract
- pre-submission review
- journal selection and reviewer-response workflows
- requirement that Methods often depends on figures, legends, and full manuscript context

### 2. 医学AI干货科研写作提示词
Strengths extracted:
- highly structured role-task-request format
- anti-hallucination and academic-integrity safeguards
- proposal / outline / argument / logic / method / data / discussion / submission pipeline
- explicit distinction between review writing, research design, writing structure, and publishing tasks
- strong paragraph-level and section-level writing instructions

### 3. 提示词目录（TXT / DOCX）
Strengths extracted:
- targeted execution prompts for Introduction / Methods / Discussion / translation / review / rebuttal
- reviewer-dimension frameworks
- acceptance-probability and journal-fit style heuristics
- grammar / reference / title / abstract / cover letter operations
- style polishing, rewriting, de-duplication, and anti-AI-language tactics

### 4. 综述神器 / 综述神器升级版 / 综述相关 JSON & ZIP
Strengths extracted:
- workflow automation for review production
- PubMed query generation and ISSN / IF / partition filtering workflows
- end-to-end review pipeline: query -> retrieval -> abstract integration -> framework -> drafting -> export
- evidence-pipeline thinking rather than single-prompt generation
- explicit multi-node orchestration mindset for literature review generation

### 5. cross-disciplinary-review-writer project inside zip
Strengths extracted:
- review-type routing
- gate-based evidence thresholds
- reproducible search / screening / extraction / drafting pipeline
- review framework selection rules
- project templates and structured review artifacts

### 6. 小魏博士科研指令合集
Strengths extracted:
- dense operational library for SCI/SSCI writing
- polishing, rewriting, abstracting, introduction, discussion, cover letter, reference insertion
- paragraph logic, sentence logic, grammar, formatting, title generation, journal matching
- high-frequency microtasks researchers repeatedly need late in the pipeline

## Unified Capability Model

The final skill package should cover 5 layers:

1. **Intake and routing**
   - identify task type, document type, field, journal, language, stage, evidence state

2. **Research and structure**
   - topic ideation, proposal, literature mapping, outline, thesis sharpening, review routing

3. **Section drafting**
   - introduction, methods, results, discussion, abstract, title, conclusion, highlights

4. **Revision and quality control**
   - anti-hallucination, argument strengthening, statistics interpretation, style polishing, translation, de-AI-ification

5. **Submission and review response**
   - journal fit, acceptance-risk estimation, pre-review, cover letter, rebuttal package, revision matrix

6. **Literature search and screening**
   - search strategy, database routing, candidate corpus, screening, evidence matrix, citation governance

## Final Package Architecture

- `SKILL.md`
  - lightweight orchestration layer
  - trigger coverage
  - routing logic
  - safety / integrity rules
  - output modes

- `references/literature-search-and-screening.md`
  - query design, source routing, screening, evidence extraction, citation-governance handoff

- `references/section-workflows.md`
  - deep rules for Introduction / Methods / Results / Discussion / Abstract / Conclusion / Title

- `references/review-and-submission.md`
  - review article routing, journal selection, pre-review, cover letter, reviewer response, acceptance-risk heuristics

- `references/quality-and-integrity.md`
  - anti-hallucination, citation discipline, evidence boundaries, style polishing, translation rules, de-AI-ification

## Guiding Design Choice

This package should not behave like a pile of prompts.
It should behave like a **routing and standards system** that chooses the right academic-writing subworkflow based on:
- stage
- material completeness
- evidence strength
- output genre
- submission pressure

## Deliberate Omissions

The skill should not directly promise:
- fully automatic literature retrieval correctness
- guaranteed real citation generation without verification tools
- guaranteed acceptance probability
- automatic execution of external workflow platforms

Instead it should:
- define safe operating patterns
- surface missing evidence
- route users to the right subworkflow
- keep claims calibrated
