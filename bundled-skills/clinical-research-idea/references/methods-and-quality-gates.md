# Methods and Quality Gates

## Feasibility Checklist

### Population and data

- Define eligibility, setting, recruitment or database source, and expected representativeness.
- Confirm legal and practical data access; distinguish “available in principle” from approved access.
- Define time zero, look-back, exposure/predictor window, follow-up, censoring, and outcome window.
- Confirm that exposure, intervention, predictors, comparator, outcomes, and key confounders are measured with adequate timing and quality.
- Estimate plausible total sample size, event count, prevalence, attrition, cluster count, and missingness from verified sources or pilot data.

### Design and analysis

- Match the design to descriptive, causal, diagnostic, prognostic, or predictive inference.
- Define the primary estimand, outcome, contrast, and analysis population.
- Identify confounding, selection, measurement, immortal-time, informative-missingness, and competing-risk threats.
- Prespecify the primary analysis and limited sensitivity analyses; avoid an unbounded analytic menu.
- Separate exploratory, confirmatory, and validation aims.
- Require independent statistical review for fragile designs, complex causal methods, adaptive trials, or high-stakes prediction models.

### Operations

- Assess recruitment rate, follow-up burden, biospecimen handling, assay availability, outcome adjudication, software, expertise, cost, and timeline.
- Confirm that the study can produce an interpretable result even if the primary hypothesis is null.
- Identify dependencies on collaborators, vendors, registries, or data custodians.

## Ethics, Privacy, and Registration

- Determine whether IRB/ethics review, exemption, consent, waiver, data-use approval, trial registration, review registration, or device/drug regulation applies.
- Minimize data collection and external transfer. Remove direct identifiers and assess re-identification risk.
- Address vulnerable populations, fairness, access, burden, incidental findings, and downstream harms.
- Do not generate approval language or registration numbers. Record them only from verified documents.
- Follow the current ICMJE guidance for AI-assisted publishing and disclose actual use; an AI system is not an author.

## Hard Blockers

Label an idea `deferred` or `reject` when any remains unresolved:

- the clinical question or intended use is undefined;
- the necessary population, outcome, exposure, intervention, predictor, reference standard, or follow-up is unavailable;
- expected sample or event count is clearly inadequate with no feasible redesign;
- the design cannot support the intended inference;
- a serious data-leakage or circular-label mechanism is unavoidable;
- data access, consent, privacy, safety, or regulatory requirements cannot be met;
- the proposed study duplicates an ongoing or completed study without a meaningful justification;
- the idea requires fabricated or inaccessible results to appear feasible.

## Scoring Rubric

Score each dimension 0-5 and explain the evidence:

| Dimension | Weight | 0 anchor | 5 anchor |
|---|---:|---|---|
| Clinical impact | 25% | No defined decision or patient benefit | Could materially improve a defined decision or patient-relevant outcome |
| Novelty evidence | 15% | Duplicate or unverified | Current literature and registries support a meaningful gap |
| Feasibility | 20% | Data/recruitment/resources unavailable | Access, sample/events, measures, team, cost, and timeline are plausible |
| Methodological validity | 20% | Design cannot answer the question | Design and analysis align with the intended inference |
| Ethics and equity | 10% | Unacceptable or unresolved major harm | Proportionate risk, privacy, fairness, and approvals are plausible |
| Reproducibility | 10% | Inputs and decisions cannot be traced | Protocol, code, provenance, and outputs can be audited and shared appropriately |

Calculate a weighted score only after displaying hard blockers. Do not use the score as a substitute for judgment.

## Status Definitions

- `provisional`: promising but evidence or feasibility checks remain incomplete.
- `shortlisted`: no obvious fatal flaw; key verification or human decisions remain.
- `recommended`: all completion gates pass and no hard blocker remains.
- `deferred`: potentially useful, but blocked by remediable evidence, data, methods, or governance issues.
- `reject`: clinically trivial, duplicative, unethical, infeasible, or methodologically incapable of answering the question.
