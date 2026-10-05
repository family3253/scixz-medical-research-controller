# References and Citations

Classify the manuscript before conversion:

- dynamic Word/Zotero/EndNote/Mendeley fields
- plain-text numeric citations and bibliography
- mixed or broken fields

Dynamic fields are preserved by default. `reference_style.py` blocks replacement when fields are detected unless the user explicitly overrides it; the default is never to flatten citation-manager data.

For plain numeric references, fetch DOI metadata with `fetch_references.py`, review fallbacks, then run `reference_style.py`. Run `reference_audit.py` afterward. Audit citations in body text, tables, captions, footnotes, and supplements where applicable. Never invent DOI, PMID, authors, pages, or journal abbreviations.
