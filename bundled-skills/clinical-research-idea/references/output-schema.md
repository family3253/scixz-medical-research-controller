# Clinical Research Idea Card Output

## Comparison Table

Compare three to five candidates with these columns:

| Candidate | Clinical decision | Study type | Evidence gap | Data/recruitment | Main validity threat | Guideline + bias tool | Hard blockers | Weighted score | Status |
|---|---|---|---|---|---|---|---|---:|---|

Scores never hide hard blockers.

## Full Idea Card

### 1. Working title

Use a neutral, design-informative title. Do not announce a positive result.

### 2. Status

Choose `provisional`, `shortlisted`, `recommended`, `deferred`, or `reject`.

### 3. Clinical decision and relevance

State who would use the result, at what point in care, what decision could change, and which patient-relevant benefit or harm matters.

### 4. Structured research question

Provide the selected PICO, PECO, PIRD, PICOTS, or SPIDER fields and one-sentence question.

### 5. Study design and intended inference

State the design, setting, estimand or intended use, primary hypothesis when applicable, and why the design fits.

### 6. Population and timing

Define eligibility, source population, time zero, measurement windows, follow-up, censoring, and analysis population.

### 7. Intervention, exposure, index test, or predictors

Define timing, dose or measurement, availability, and operationalization.

### 8. Comparator and outcomes

Define the comparator, primary outcome, harms, secondary outcomes, measurement method, and time horizon.

### 9. Data or recruitment feasibility

State verified access status, plausible sample and event counts, missingness, recruitment rate, required variables, assays, expertise, cost, and timeline. Mark unknowns.

### 10. Evidence gap and source ledger

Describe the gap and list guidelines, reviews, pivotal studies, recent studies, and registry entries with stable identifiers and verification scope.

### 11. Analysis outline

Give the minimum defensible analysis, key assumptions, sensitivity analyses, and validation strategy. Do not fabricate expected results.

### 12. Bias, ethics, and governance

List major bias threats, privacy and fairness risks, IRB/consent status, registration needs, data-use restrictions, and mitigations.

### 13. Reporting and appraisal standards

Name the reporting guideline and the separate risk-of-bias or quality tool.

### 14. Scores, blockers, and decision

Show six dimension scores, weighted total, hard blockers, status, and what would change the decision.

### 15. Next steps

List the minimum human decisions, documents, pilot counts, searches, and approvals required before protocol development.

## JSON Contract

Use this structure when a machine-readable card is requested:

```json
{
  "title": "",
  "status": "provisional",
  "clinical_decision": "",
  "research_question": "",
  "study_type": "",
  "framework": "PICOTS",
  "population": "",
  "intervention_exposure_test_or_predictors": "",
  "comparator": "",
  "outcomes": "",
  "time_horizon": "",
  "data_source": "",
  "evidence_gap": "",
  "key_sources": [
    {
      "citation": "",
      "identifier": "PMID/DOI/NCT/URL",
      "source_type": "guideline/review/primary/registry",
      "verification_scope": "metadata/abstract/sections/full_text",
      "verified": false,
      "supports": ""
    }
  ],
  "analysis_outline": "",
  "feasibility": {
    "data_access": "",
    "sample_size_or_events": "",
    "timeline": "",
    "resources": ""
  },
  "bias_risks": [],
  "ethics_registration": {
    "irb": "",
    "consent": "",
    "registration": "",
    "privacy": ""
  },
  "reporting_guideline": "",
  "risk_of_bias_tool": "",
  "scores": {
    "clinical_impact": 0,
    "novelty_evidence": 0,
    "feasibility": 0,
    "methodological_validity": 0,
    "ethics_equity": 0,
    "reproducibility": 0
  },
  "quality_gates": {
    "current_evidence_searched": false,
    "registry_searched": false,
    "identifiers_verified": false,
    "design_reporting_separated": true,
    "no_fabricated_results": true,
    "privacy_checked": false
  },
  "hard_blockers": [],
  "assumptions": [],
  "next_steps": []
}
```

Run `scripts/validate_idea_card.py` after saving JSON. A valid structure is not proof that the clinical idea is valid.
