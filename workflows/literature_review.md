# Literature-review workflow

## Entry and scope

Use for narrative, scoping, systematic, or evidence-synthesis work. It does not treat search snippets, unverified citations, or preprints as equivalent to peer-reviewed evidence.

## Inputs

Require review type, question/PICO, databases, date/language limits, inclusion/exclusion criteria, target output, and citation style. A systematic review without eligibility logic is blocked.

Choose the strongest honest output level before drafting: `submission-grade review draft`, `review-grade evidence synthesis`, `evidence map/scoping output`, or `framework memo/outline`. The requested label does not override corpus readiness.

## Route

Controller → 中书省 defines protocol and search boundary → 门下省 checks reproducibility and bias risks → `panel` or `council` depending stakes. Primary: `deep-research`, `research-lit`, `meta-analysis`, or `cross-disciplinary-review-writer`. Supporting: `pubmed-database`, `search-lit`, `fulltext-retrieval`, `check-reporting`, `verify-refs`.

Use a recoverable artifact sequence: versioned query -> raw export -> normalized/de-duplicated candidate pool -> title/abstract decisions -> full-text acquisition/status -> full-text decisions -> evidence extraction/appraisal -> claim-evidence matrix -> framework/outline -> draft -> citation-order and reporting verification. Provider-specific n8n or model workflows may inform this sequence but are not runtime requirements.

## Outputs

Search strategy/version/date, source ledger, deduplicated candidate pool, screening/extraction plan or tables, risk-of-bias approach, synthesis, evidence gaps, and PRISMA/reporting artifacts when applicable.

Also report the chosen output level, the gate evidence supporting it, subtopic coverage, abstract-only/full-text limitations, contradictory findings, and the final first-appearance citation mapping when a numbered style is requested.

## Verification

Verify database queries, dates, inclusion counts, DOI/PMID metadata, source tier, duplicate handling, risk-of-bias decisions, and claim-to-source links. Reconcile counts between every pipeline stage and retain exclusion reasons. Quantitative synthesis requires a compatible estimand and outcome definition. Do not treat journal IF/partition filters as study-quality appraisal.

## Failure/fallback

If full text or a database is unavailable, label the evidence gap and use only the approved fallback source. Do not infer study results from abstracts when the requested claim requires full text. Downgrade the output level rather than producing a pseudo-submission-grade review from a small, unappraised, or abstract-only corpus.
