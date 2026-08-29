# Journal metrics and classification output schema

Use this schema for every ranked journal in a `find-journal` result. It is a reporting contract, not a permission to guess missing values.

## Required fields

| Field | Meaning | Required provenance |
|---|---|---|
| `impact_factor` | Journal Impact Factor (IF) | JCR edition/year, source URL or institutional record, verification date |
| `jcr_quartile` | JCR category quartile | JCR category, year, source URL, verification date; preserve multiple categories when present |
| `cas_major_quartile` | 中科院大类分区 | CAS release/edition year, category, source URL, verification date |
| `cas_minor_quartile` | 中科院小类分区 | CAS release/edition year, category, source URL, verification date |
| `cas_emerging_classification` | 中科院新锐/新兴期刊分区或分类（明确列出时） | CAS release/edition year, category, source URL, verification date; otherwise `Not listed / not verified` |
| `letpub_review_speed` | LetPub page-displayed review-speed text | LetPub page URL and retrieval date; preserve verbatim text and never infer an acceptance probability |

## Recommended fields

- `citescore` with Scopus year and source
- `sjr` and `snip` with SCImago/Scopus year and source
- `indexing` (SCIE/SSCI/ESCI/PubMed/Scopus/etc.) with the authoritative index and verification date
- `open_access` and `apc` with publisher page and currency/date
- `acceptance_feasibility` with the design-ceiling reason, not an acceptance probability

## Status vocabulary

- `verified current`: checked against an authoritative source for the stated edition/year.
- `profile snapshot`: taken from a dated local profile but not rechecked in the current run.
- `conflicting`: two sources disagree; show both values and explain the conflict.
- `not available / not verified`: no reliable current value was available.
- `not listed`: the source does not list the journal for the requested classification (use only for the CAS Emerging/New Journal field when appropriate).

## Source rules

1. JANE and iPubMed are candidate-discovery/triage branches. They must not be treated as authoritative sources for IF, JCR quartile, CAS quartiles, or Emerging/New Journal classification.
2. Do not infer JCR or CAS quartiles from a generic tier, IF, CiteScore, SJR, or a neighboring category.
3. Record the edition/year for every time-varying metric. A value without a year is incomplete.
4. If institutional access prevents verification, preserve the missing state instead of copying an undated third-party number.
5. Keep JCR and CAS categories separate. If a journal belongs to multiple categories, report all relevant categories or state the selection rule.
