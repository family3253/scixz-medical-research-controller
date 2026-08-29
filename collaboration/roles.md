# Collaboration roles

Every role has one job and one handoff contract. A role may use only a Skill pre-authorized in its ministry ticket, and its report must state which Skill was invoked and what evidence it used.

| Role | Owns | Must not do |
|---|---|---|
| `coordinator` | brief, task graph, role selection, dependencies, budget, final assembly | decide a scientific issue without evidence |
| `research` | question, novelty, hypotheses, feasibility | claim novelty without a search boundary |
| `literature` | reproducible retrieval and evidence synthesis | treat snippets or unverified references as evidence |
| `clinical` | applicability, outcome meaning, care-pathway relevance, safety | provide autonomous patient care |
| `methodology` | design validity, bias, confounding, time zero, external validity | substitute a design without naming the estimand |
| `statistics` | estimand, models, assumptions, missingness, multiplicity, uncertainty | endorse a model with unchecked assumptions |
| `bioinformatics` | data modality, QC, batch, identifiers, replication, validation | infer mechanism from an unvalidated association |
| `reviewer` | constructive major/minor concerns and evidence anchors | rewrite the manuscript unless asked |
| `editor` | priority, decision threshold, novelty, journal risk | convert disagreement into certainty |
| `journal` | scope, article type, current fit, fallback cascade | rely on stale metrics without verification |
| `critic` | adversarial cross-check and contradiction detection | introduce a new claim without an evidence anchor |
| `consensus` | agreement matrix, arbitration, uncertainty | average incompatible estimands or hide minority views |
| `verifier` | reproducibility, paths, numbers, citations, output contract | silently repair scientific content |
| `finalizer` | assemble only verified findings into the approved user-facing artifact | change scientific claims, hide dissent, or publish an unverified result |

## Worker report contract

```yaml
role: statistics
status: complete | partial | failed
question: "The one question this role answered"
claims:
  - id: S-01
    statement: "Claim in plain language"
    evidence: [E-03, E-07]
    confidence: high | moderate | low
assumptions: []
risks: []
recommendation: "Concrete action"
handoff_to: [methodology, consensus]
authorized_ticket: T-001
```

Empty evidence arrays are permitted only for a clearly labeled hypothesis or request for missing information. A worker must not return a polished conclusion without a status and confidence.
