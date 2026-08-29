# Journal-lookup workflow

## Entry and scope

Use when the user supplies one or more known journal names and asks for their current metadata, metrics, partitions, indexing, warning status, or review speed. This route reports objective journal information; it does not by itself rank the journals, judge manuscript quality, or predict acceptance.

## Inputs

Require one or more journal names. Accept ISSN/eISSN, publisher, or a preferred edition/year when supplied. Treat requests for scope fit, manuscript matching, or challenge/target/safety ordering as a secondary `journal-selection` handoff.

## Route

Controller → normalize journal title and identity → primary `sci-select` known-journal lookup when installed → merge EasyScholar API fields when `EASY_SCHOLAR_SECRET_KEY` is configured → merge ShowJCR-derived local data or the `jcr_mcp` adapter for JCR/CAS/XinRui fields → use LetPub live lookup (or `agent-browser`/`chrome:control-chrome` fallback) for review-speed text and public metric hints → verify JIF/JCR/CAS/indexing against authoritative sources when accessible → journal Agent formats the card → verifier checks field-level provenance, dates, conflicts, and missing values.

Prefer `sci-select` plus a ShowJCR-derived CSV/SQLite index when the response must expose
separate JCR, CAS, and XinRui columns. The current `jcr_mcp` implementation is useful as
an MCP query surface but returns a general partition field and does not itself provide the
full field-level provenance contract or LetPub review speed.

EasyScholar is an optional third-party API branch. It can fill `sciif`, JCR/CAS-upgraded,
XinRui, and warning fields, but its secret must come from `EASY_SCHOLAR_SECRET_KEY` and
must never be written to a manifest, README, log, or command-line argument. Read the
adapter's `references/easyscholar.md` before enabling it.

Clarivate release years and metric data years must be kept separate. As of August 2026,
the current Clarivate Journal Citation Reports release is the 2026 JCR release, and it
reflects 2025 citation/JIF data. Prefer output such as `JCR release: 2026; JIF/JCR data
year: 2025` when both fields are available.

`find-journal` or `journal-recommender` is not required for an exact lookup. Invoke one only when the user also asks whether the journal fits a manuscript or requests a ranked submission strategy.

The repository smoke runner is `scripts/journal_lookup.py`. It loads the installed
`sci-select`, calls its local-index/LetPub path, optionally calls the EasyScholar adapter,
and emits a JSON journal card. It fails closed when `sci-select` is absent and skips
EasyScholar without sending a request when `EASY_SCHOLAR_SECRET_KEY` is not configured.

## Outputs

Return one card per journal with:

- canonical journal title, abbreviation, ISSN/eISSN, publisher, homepage, and author-guideline URL when available;
- Impact Factor/JIF with the JCR release year, data/JIF year, and source/status;
- JCR quartile(s), preserving category labels, year, source, and status;
- `2025 CAS major quartile` and `2025 CAS minor quartile` (中科院大类/小类) with category, edition, source, and status;
- `2026 Emerging/New Journal classification` (2026 新锐分区) when explicitly listed, with category, source, and status;
- LetPub review-speed text, page URL, and retrieval date; never convert a text range into an invented numeric probability or guarantee;
- EasyScholar normalized fields (`sciif`, JCR/CAS/XinRui/warning keys) when configured, labelled as third-party API evidence;
- indexing/coverage (SCIE/SSCI/ESCI/PubMed/Scopus as applicable), OA/APC, warning status, and optional CiteScore/SJR/SNIP;
- `_source_status` for every material source and a short conflict/missing-field note.

Use `Not available / not verified` for a missing current value and `Not listed` only when the relevant source explicitly does not list the journal (especially for 2026 Emerging/New Journal classification).

## Verification

Verify journal identity before merging records; prefer ISSN/eISSN matches over fuzzy title matches. Treat EasyScholar, ShowJCR, LetPub, and iPubMed as third-party or auxiliary sources. Use Clarivate JCR/Master Journal List for JIF, JCR quartile, and coverage when available; use the dated Chinese Academy of Sciences release for CAS major/minor and Emerging/New Journal classification; use the journal/publisher page for homepage, author guidelines, OA, and APC; record the LetPub page and retrieval date for review speed. Do not call JANE/iPubMed/EasyScholar outputs authoritative for these metrics.

## Failure/fallback

If `sci-select` is not installed, return the missing-dependency state and offer the EasyScholar adapter (when a local environment variable is configured), ShowJCR/`jcr_mcp` lookup, plus browser verification as a manual fallback. If a source is blocked, record `attempted` with the exact reason and keep the field unverified. Never fill missing IF, quartile, Emerging/New Journal status, or review speed from memory or neighboring journals. If the user asks for a ranked recommendation, hand off to `journal-selection`; for that route, the mandatory JANE and iPubMed evidence gate still applies.
