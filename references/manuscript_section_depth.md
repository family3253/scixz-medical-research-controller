# Manuscript section depth and citation allocation

This reference is required for SciXZ manuscript-writing, reviewer-response, and revision-after-review routes when the user asks for stronger正文、引言、讨论、文献论证 or deeper interpretation.

## Core contract

The goal is not to make every section longer. Each paragraph must perform a distinct scientific job, and each external claim must be supported by an appropriate, verified source. Drafting and evidence verification remain separate stages.

Use a section brief before drafting:

```yaml
section_brief:
  section: introduction | methods | results | discussion | conclusion
  purpose: "one sentence"
  paragraph_jobs: []
  key_claims: []
  required_evidence: []
  prohibited_moves: []
  acceptance_checks: []
```

## Section-by-section depth standard

### Section dependency graph

Do not treat manuscript sections as independent prompt slots. Use this evidence order when an artifact depends on study findings:

```text
study facts + Methods inputs
  -> verified analyses/tables/figures
  -> figure legends + Results
  -> Discussion
  -> abstract + conclusion + highlights + final title
```

The Introduction may be planned earlier, but its final gap/objective must remain consistent with the actual design and completed evidence. If an upstream artifact is missing, provide a clearly labeled scaffold or placeholder list rather than a falsely complete downstream section.

### Title and abstract

- Identify the population, exposure/intervention, outcome, design, or central contribution that the study actually supports.
- Keep the abstract claim-calibrated: objective, design, population, principal methods, effect estimates/uncertainty, and bounded conclusion.
- Do not turn background language into a novelty claim, and do not cite references in the abstract unless the target venue explicitly requires them.
- Generate the final title, abstract, conclusion, keywords, and highlights only after the principal results and design language are stable. Check that every result-dependent statement has a matching source result and that character/word limits are measured rather than guessed.

### Introduction

Build a problem-to-question chain rather than a topic summary:

1. Establish why the clinical or scientific problem matters.
2. Synthesize what is already known using the strongest relevant evidence, not a citation list.
3. Identify a specific unresolved gap, contradiction, limitation, or unmet decision need.
4. Explain why the present design can address that gap.
5. State the objective, prespecified hypothesis, or research question and the contribution supported by the study.

For each paragraph, record `claim -> evidence -> unresolved implication`, and keep a claim-to-source map that can be audited later. Avoid importing the discussion's interpretation into the introduction. The introduction should motivate the study, not preview unsupported mechanisms or claim that the study is the first unless novelty has been verified.

Use a deliberate evidence mix where available: landmark or foundational work for definitions, recent primary studies for the current state, systematic reviews or guidelines for consensus, and context-specific studies for the exact population or exposure. Prefer sources that directly support the proposition; do not cite a famous paper merely because it is related.

### Methods

Depth means reproducibility, not verbosity. Make design decisions auditable:

- study design, setting, dates, eligibility, sampling, and analysis population;
- exposure/intervention, comparator, outcomes, covariates, time zero, and estimand;
- data provenance, preprocessing, missing-data handling, confounding/bias controls, model specification, sensitivity analyses, and software;
- ethics, registration, reporting guideline, and deviations from the protocol when applicable.

Do not use the methods section to justify results after seeing them. Any post hoc decision must be labeled as such.

Build a missing-detail register before prose. Sample size, dates, eligibility, doses, reagents, instruments, software versions, preprocessing, model options, and ethics identifiers absent from the source remain `[TO CONFIRM: field]`; they are not inferable from a figure, result, neighboring paper, or “typical practice.” Ask only for details that block reproducibility or the requested output.

### Results

Organize results around the prespecified questions and analysis population. Report denominators, effect estimates, uncertainty intervals, relevant absolute measures, and multiplicity or model diagnostics when applicable. Keep interpretation out of the results section; explain meaning in the discussion. Every number must reconcile with tables, figures, supplements, and the consistency manifest.

For figure-led studies, create a `figure_evidence_map` before writing:

```yaml
figure_evidence_map:
  - panel: Figure 1A
    question: "what this panel tests"
    population_or_sample: "source-defined denominator"
    variables: []
    estimate_or_pattern: "source value only"
    uncertainty_and_test: "source value or TO CONFIRM"
    legend_metadata_missing: []
```

Every Results sentence and legend clause must map to a panel/table or recorded analysis. Do not infer units, significance tests, replicate definitions, normalization, abbreviations, or software settings.

### Discussion

Use a finding-to-meaning-to-boundary structure:

1. Open with the main findings in relation to the objective, without repeating the abstract verbatim.
2. Interpret each important finding: what it means, what mechanism or explanation is plausible, and what alternative explanations remain.
3. Compare with prior evidence at the level of population, design, exposure, outcome, effect direction, magnitude, and uncertainty. Explain concordance or discordance instead of writing “consistent with previous studies.”
4. Distinguish evidence-supported mechanism from speculation. Mechanistic claims require the study's own results plus appropriate external evidence; if evidence is indirect, say so.
5. State clinical, scientific, or policy implications only within the design's ability to support them. Observational associations do not become causal recommendations through wording.
6. Give specific strengths and limitations, including residual confounding, selection, measurement error, missingness, multiplicity, transportability, external validation, and alternative explanations when relevant.
7. State what the study changes, what it does not establish, and the next discriminating experiment, validation, or dataset needed.

Deep discussion is demonstrated by explicit reasoning, not by length. A useful paragraph normally contains `finding -> comparison -> explanation -> boundary`; omit any element that the evidence cannot support. Do not simply repeat the introduction's literature review. Reuse a source only when it is genuinely necessary for the central comparison, a defining guideline, or a seminal concept, and record the reason.

### Conclusion

Answer the research question in proportion to the design and evidence. Include the practical or scientific implication only when it follows from the findings and limitations. Do not introduce a new result, new citation-dependent claim, or untested mechanism in the conclusion.

### Translation, polishing, and shortening

- Freeze terminology/glossary, numbers, units, citation markers, headings, and paragraph order before translation when the user requests structural fidelity.
- Use an internal `source -> draft -> checked final` sequence. The checked final must preserve negation, direction, magnitude, uncertainty, causal strength, and attribution.
- Diagnose before rewriting. Ordinary polishing, substantive rewriting, shortening, and similarity-reduction are different operations and require different authority.
- A target-journal exemplar may guide information density, tense, or section shape, but it is not evidence and must not be imitated closely.
- Humanization should remove formulaic rhythm and inflated language without altering scientific meaning. Do not promise or optimize for detector scores.

## Introduction/discussion citation allocation

Maintain a citation ledger with separate section roles:

```yaml
citation_ledger:
  - ref_id: E001
    section_roles: [introduction]
    supports: "current burden or knowledge gap"
    source_type: primary | systematic-review | guideline | methods | foundational
    verification: verified | uncertain | pending
    reuse_reason: null
```

Use mostly disjoint evidence pools for the introduction and discussion. The target is not an artificial zero-overlap rule: retain overlap only when the same source is the necessary authority for a definition, guideline, landmark method, or central comparator. Every overlap must have a `reuse_reason`; unexplained overlap is a revision issue.

The controller must produce a citation allocation check containing:

- references used only in the introduction;
- references used only in the discussion;
- references shared by both sections and the reason for each reuse;
- external claims without a verified citation;
- citations that do not clearly support the surrounding claim;
- duplicate works, secondary citations used in place of primary evidence, and outdated sources where current evidence is required.

Do not fabricate references or fill metadata from memory. Use `research-lit`/`deep-research` for discovery, `bib-search-citation` or `manage-refs` for local retrieval and normalization, and `verify-refs` for audit. If the source cannot be opened or its proposition cannot be confirmed, mark it unresolved.

## Acceptance gate

A section-level writing ticket is complete only when:

- every paragraph has a documented job and does not duplicate another paragraph;
- the introduction ends in a precise question/objective rather than a generic aim;
- the discussion interprets findings, compares evidence, addresses mechanisms and alternatives, and bounds implications;
- methods/results remain faithful to the recorded study and numbers;
- all external factual claims have evidence anchors and all citations are verified or explicitly unresolved;
- introduction/discussion citation overlap has been reviewed and justified;
- no new unsupported result, causal claim, novelty claim, mechanism, or recommendation was introduced;
- unresolved evidence gaps are visible in the handoff rather than silently smoothed over.
- figure-led Results and legends reconcile to the figure evidence map, and downstream front matter contains no finding absent from the stable Results;
- translation/polishing preserves numbers, citations, terminology, modality, and causal strength.
