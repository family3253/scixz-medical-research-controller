---
name: clinical-research-idea
description: Generate, verify, stress-test, and prioritize clinically meaningful and feasible research questions and protocol concepts. Use for requests about 临床科研选题、研究问题构建、研究假设、创新性或可行性评估, or when Codex needs to develop or refine PICO/PECO/PIRD/PICOTS questions, evidence gaps, study-design options, protocol concepts, clinical prediction or AI/ML ideas, real-world studies, diagnostic/prognostic studies, trials, or systematic reviews. Apply evidence, feasibility, bias, ethics, registration, and reporting-guideline gates before recommending an idea.
---

# Clinical Research Idea

Convert a broad clinical interest or available dataset into a small set of evidence-grounded, clinically useful, methodologically defensible Idea Cards. Treat generated ideas as provisional until their sources, data access, design, and ethics requirements are verified.

## Core Rules

1. Separate brainstorming from verification. Label unsupported possibilities as hypotheses, not gaps or discoveries.
2. Never invent citations, registry records, sample sizes, event counts, effect estimates, approvals, data access, or feasibility.
3. Search recent literature and active/completed registrations before claiming novelty. Prefer primary and authoritative sources.
4. Optimize for a clinical decision or patient-relevant outcome, not novelty, model complexity, or citation volume alone.
5. Distinguish reporting completeness from design quality and risk of bias.
6. Keep protected health information local. Do not upload identifiable or unpublished patient-level data without explicit authorization and an approved destination.
7. Require human confirmation before fixing the final question, protocol, analysis plan, or registration strategy.

## Load References Progressively

Read only the files needed for the current task:

- Read [question-frameworks.md](references/question-frameworks.md) when the question is broad, ambiguous, or needs PICO/PECO/PIRD/PICOTS framing.
- Read [study-type-router.md](references/study-type-router.md) before selecting a design, reporting guideline, or bias tool.
- Read [evidence-and-registration.md](references/evidence-and-registration.md) for literature searches, novelty checks, trial registries, or source verification.
- Read [methods-and-quality-gates.md](references/methods-and-quality-gates.md) for feasibility, sample/event adequacy, causal validity, ethics, privacy, or scoring.
- Read [clinical-ml.md](references/clinical-ml.md) for prediction models, machine learning, AI, multimodal data, omics, imaging, or EHR models.
- Read [output-schema.md](references/output-schema.md) before producing final Idea Cards or machine-readable JSON.

Verify the current version of any guideline from its official source at execution time. Do not rely on a remembered publication year when it could have changed.

## Workflow

### 1. Capture the Research Brief

Collect or infer, then clearly label assumptions for:

- clinical domain and decision to improve;
- target population and setting;
- intervention, exposure, index test, predictors, or phenomenon;
- comparator and patient-relevant outcomes;
- time zero, follow-up, and prediction horizon when applicable;
- available data, biospecimens, recruitment access, software, team, budget, and timeline;
- intended study type, target journal/funder, and jurisdiction;
- constraints, including ethics, privacy, registration, and data-use terms.

Ask only questions that materially change design or feasibility. If the user wants rapid exploration, proceed with explicit provisional assumptions.

### 2. Route the Study Type

Use `study-type-router.md` to classify each candidate. Do not mix diagnostic, prognostic, causal, descriptive, and prediction aims in one primary question. State the estimand or intended use when relevant.

### 3. Formulate Candidate Questions

Use the appropriate framework from `question-frameworks.md`. Generate three to five distinct candidates by varying a clinically meaningful dimension such as population, decision point, comparator, outcome, time horizon, or implementation setting. Do not generate cosmetic title variants.

### 4. Build an Evidence and Registration Ledger

Search guidelines, recent systematic reviews, pivotal studies, recent primary studies, and applicable registries. Record stable identifiers such as PMID, DOI, NCT, ISRCTN, or PROSPERO. Distinguish:

- established evidence;
- conflicting or uncertain evidence;
- ongoing but unpublished work;
- a true evidence, validation, implementation, safety, equity, or generalizability gap;
- absence of evidence caused only by an incomplete search.

### 5. Stress-Test Feasibility and Validity

Apply `methods-and-quality-gates.md`. Check data access, eligibility, outcome ascertainment, time alignment, sample size or event count, missingness, confounding, measurement error, selection, transportability, analytic complexity, ethics, privacy, registration, and reproducibility.

For clinical AI/ML, also apply `clinical-ml.md`. Reject ideas that depend on leakage, unavailable labels, circular predictors, implausible event counts, or an undefined clinical use case.

### 6. Rank Without Hiding Vetoes

Score clinical impact, novelty evidence, feasibility, methodological validity, ethics, and reproducibility on 0-5 scales. Keep hard blockers separate from the weighted score; a high score cannot override a blocking ethics, data, validity, or verification failure.

### 7. Produce the Deliverable

Use `output-schema.md` to return:

1. a concise Research Brief with assumptions;
2. a search and registration ledger;
3. a comparison table for three to five candidates;
4. complete Idea Cards for the top one to three candidates;
5. rejected or deferred ideas with reasons;
6. the next human decisions and minimum evidence needed before protocol development.

If JSON is saved, run:

```powershell
python scripts/validate_idea_card.py path\to\idea-card.json
```

Fix structural errors. Treat warnings as prompts for human review, not automatic clinical decisions.

## Completion Gate

Do not label an idea `recommended` unless all are true:

- the clinical decision and target population are explicit;
- literature and relevant registry searches are current and traceable;
- key identifiers have been verified;
- data or recruitment feasibility is plausible and labeled;
- the design matches the question and intended inference;
- major bias, ethics, privacy, and registration issues are addressed;
- the reporting guideline and separate risk-of-bias tool are identified;
- no hard blocker remains.

Otherwise label the idea `provisional`, `shortlisted`, `deferred`, or `reject` and state what would change the status.
