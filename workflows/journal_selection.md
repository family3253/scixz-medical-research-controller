# Journal-selection workflow

## Entry and scope

Use when the user asks where to submit a manuscript, how to rank journals, or how to build a fallback submission cascade. It does not guarantee acceptance and does not use stale metrics as current facts. For a known journal name with no manuscript-ranking request, route to `journal-lookup` instead.

## Inputs

Require manuscript title/abstract or full text, article type, methods/design, population, contribution, target audience, language, and user priorities such as scope, speed, APC, impact, or risk.

## Route

Controller → 中书省 extracts manuscript positioning and decision criteria → 门下省 checks design ceiling, policy freshness, external-tool privacy, and desk-reject risks → `panel`. Primary: `find-journal`. Required external tickets: `jane` (public URL/API) and `ipubmed` (browser-assisted/export). Supporting: `research-lit` or `deep-research` for recent comparators, `desk-reject-screening-editor`, `paper-audit` or `sci-manuscript-preflight`, `journal-format-converter`, `venue-templates`, `sync-submission`, and `verification`.

## Outputs

Return the `journal-selection` evidence report, not a short list of journal names. The final
ranking requires successful JANE and iPubMed run artifacts. For every candidate, include:

- rank and candidate status; canonical title/ISSN; article-type and scope fit status with official
  URL, scope evidence, recent comparable-paper count, and examples;
- a decomposed score: scope/precedent evidence, risk penalty, and separate venue-context score;
  state explicitly that it is a ranking aid, not an acceptance probability or manuscript-quality score;
- IF/JIF with release/data year; JCR quartile and categories; 2025 CAS major/minor quartiles; 2026
  XinRui classification; coverage; OA/APC; warning status; LetPub review-speed text with URL/date;
- fit reasons, policy/desk-screening risks, missing/currentness conflicts, source-status map, and
  one concrete next verification or submission-preflight action.

At report level include a manuscript-derived semantic profile (direction, population, question,
methods, and contribution type), constraints, JANE/iPubMed query/date/evidence status, blocked
requirements, method for ordering candidates, a diagnostic candidate list when blocked, and
separate boundaries for desk screening, peer review, and acceptance probability. This profile is
not a content fingerprint: never compute or store the manuscript's SHA-256, raw manuscript path,
or local run directory in a selection report. Keep full artifact paths in the private run only.

Default to ordinal readiness/fit and scenario analysis rather than an exact acceptance probability. A numeric probability is allowed only when the model has journal- and article-type-specific, independent calibration data with a stated cohort, time window, discrimination, calibration, and validation limits. A hand-built rubric, impact factor, abstract similarity, or assumed prior acceptance rate is not a calibrated probability. Separate desk-screening and peer-review risks.

## Verification

Verify current journal homepage, author guidelines, article type, indexing/policy/APC/speed claims at authoritative sources. Rank scope and design fit before impact factor. Record the date and source for time-sensitive facts. Treat JANE/iPubMed rankings as candidate-generation signals; record query/filter details and do not promote their metric or quality labels without independent verification. Reject uncalibrated numeric acceptance estimates and label any calibrated estimate with uncertainty and applicability limits.

## Failure/fallback

If the manuscript is insufficient for fit assessment, return the missing-input list and do not publish a final ranking. If JANE or iPubMed is unavailable, mark the route `BLOCKED` and report the missing run artifact; do not continue with a final `find-journal` recommendation. If current metrics or policies cannot be verified, mark them stale/unknown rather than guessing.

Run `python scripts/journal_selection.py` with the manuscript text (or a precomputed
`sci-select` bundle) and both external run artifacts to generate the machine-readable report.
The runner returns a diagnostic report but exits nonzero when either mandatory artifact is absent,
unless `--allow-diagnostic` was selected explicitly.
For text-driven runs it refreshes selected candidate cards through the full `sci-select` known-
journal lookup path so the report can include LetPub speed/OA fields when available; use
`--skip-live-enrichment` only for a deliberately offline or deterministic rerun.
