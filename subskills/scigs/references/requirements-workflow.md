# Requirements Evidence

1. Start from the target journal's current Instructions for Authors and article-type page.
2. Record the exact URL, access date, article type, review model, and a text snapshot hash.
3. Treat family profiles, cached templates, and third-party summaries as discovery aids only.
4. Review candidate rules produced by `fetch_official_requirements.py`; mark each one `verified` only after human/agent confirmation against the official page.
5. Convert confirmed rules into explicit `actions`. Free-text rules must not trigger automatic DOCX edits.
6. Keep conflicts and unknowns in `conflicts`/`unverified_items`; unresolved mandatory items block `READY`.

Minimum categories: manuscript structure, title page, abstract, word limits, headings, references, tables, figures, supplements, review model, declarations, ethics, data/code, cover letter, and required portal files.
