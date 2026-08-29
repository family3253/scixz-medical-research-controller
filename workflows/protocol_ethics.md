# Protocol and ethics workflow

## Entry and scope

Use for research protocols, IRB/ethics applications, consent plans, governance artifacts, and reporting-readiness checks. It does not grant ethics approval or replace institutional review.

## Inputs

Require research question, population, intervention/exposure, comparator, outcomes, data source, recruitment/consent plan, and target template. Missing study objective, population, or data source is blocking.

## Route

Controller → 中书省 protocol design → 门下省 ethics/privacy/scope review → 尚书省 tickets. Primary: `write-protocol` or `fill-protocol`. Supporting: `check-reporting`, `deidentify`, `anthropics-docx`, and `design-study` when the estimand or eligibility is unclear.

## Outputs

Protocol draft or completed template, study-flow description, data/privacy/consent checklist, reporting-guideline map, unresolved institutional decisions, and source/evidence ledger.

## Verification

Check consistency among objectives, endpoints, sample, eligibility, time zero, follow-up, consent, data retention, and analysis plan. Verify that no patient identifier or invented institutional requirement was introduced.

## Failure/fallback

If no template is supplied, produce a clearly labeled generic protocol skeleton. If a legal or institutional requirement is uncertain, mark it for local confirmation and do not present the draft as approved.
