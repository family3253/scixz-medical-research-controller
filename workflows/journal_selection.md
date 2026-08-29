# Journal-selection workflow

## Entry and scope

Use when the user asks where to submit a manuscript, how to rank journals, or how to build a fallback submission cascade. It does not guarantee acceptance and does not use stale metrics as current facts.

## Inputs

Require manuscript title/abstract or full text, article type, methods/design, population, contribution, target audience, language, and user priorities such as scope, speed, APC, impact, or risk.

## Route

Controller → 中书省 extracts manuscript positioning and decision criteria → 门下省 checks design ceiling, policy freshness, external-tool privacy, and desk-reject risks → `panel`. Primary: `find-journal`. Required external tickets: `jane` (public URL/API) and `ipubmed` (browser-assisted/export). Supporting: `research-lit` or `deep-research` for recent comparators, `desk-reject-screening-editor`, `paper-audit` or `sci-manuscript-preflight`, `journal-format-converter`, `venue-templates`, `sync-submission`, and `verification`.

## Outputs

Ranked primary target and fallback cascade, scope/article-type fit, recent comparable-paper evidence, current policy/metric facts, desk-reject risks, submission preparation gaps, recommended order of submission, and mandatory external-tool run records separating JANE similarity evidence, iPubMed browser/export evidence, and canonical verification.

## Verification

Verify current journal homepage, author guidelines, article type, indexing/policy/APC/speed claims at authoritative sources. Rank scope and design fit before impact factor. Record the date and source for time-sensitive facts. Treat JANE/iPubMed rankings as candidate-generation signals; record query/filter details and do not promote their metric or quality labels without independent verification.

## Failure/fallback

If the manuscript is insufficient for fit assessment, return the missing-input list and do not publish a final ranking. If JANE or iPubMed is unavailable, mark the route `BLOCKED` and report the missing run artifact; do not continue with a final `find-journal` recommendation. If current metrics or policies cannot be verified, mark them stale/unknown rather than guessing.
