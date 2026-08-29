---
name: "citation-management"
description: "Manages academic citations, DOI lookup, and BibTeX/EndNote exports. Invoke when the user asks to add/verify references, resolve DOIs, or format citations."
---

# Citation Management

Use this skill to help with academic reference workflows. It focuses on consistent citation handling, DOI verification, and exportable formats for manuscripts.

## What It Does

- Resolve DOI metadata and verify reference details
- Normalize author/title/journal fields and detect missing data
- Generate BibTeX, RIS, and EndNote-compatible outputs
- Deduplicate references and enforce consistent formatting

## When to Invoke

- The user asks to add, verify, or clean a reference list
- The user needs DOI lookup or metadata completion
- The user wants BibTeX/RIS/EndNote exports
- The user requests citation formatting or deduplication

## Output Conventions

- Prefer structured outputs (tables or JSON) when asked for batch results
- Include DOI, title, authors, journal, year, volume, issue, pages, and URL when available
- Flag missing fields explicitly

## Examples

**User:** “把这批 DOI 补全成 BibTeX”

**Assistant:** Use this skill to resolve DOI metadata and return BibTeX entries, highlighting any missing fields.

**User:** “帮我清理重复引用并统一期刊名”

**Assistant:** Use this skill to deduplicate and normalize the reference list.
