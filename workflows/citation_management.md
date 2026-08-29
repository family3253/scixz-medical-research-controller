# Citation-management workflow

## Entry and scope

Use for local BibTeX/Zotero search, citation support, DOI/reference verification, duplicate detection, bibliography normalization, and allocating evidence between manuscript sections. It does not generate citations from memory.

## Inputs

Require `.bib`, `.biblatex`, RIS, NBIB, DOI/title list, or the manuscript claim needing support. For introduction/discussion allocation, also require the current section text or outline and a citation ledger if one exists. If the user asks to verify a source but provides no source or searchable locator, mark it blocked.

## Route

Controller → 户部 resolves the reference file → 中书省 defines the claim-to-source and section-allocation task → 门下省 checks source fit, introduction/discussion overlap, and external-tool privacy → 尚书省 issues mandatory `jane` and `ipubmed` tickets. Primary: `bib-search-citation`, `manage-refs`, or `verify-refs`. Supporting: `citation-management`, `academic-citation-manager`, `zotero-reviewed-import`, and `research-lit`/`deep-research` for evidence discovery.

## Outputs

Verified/uncertain reference table, normalized entries, claim-to-citation suggestions, duplicate findings, introduction-only and discussion-only reference pools, justified shared-reference list, unresolved DOI/metadata fields, mandatory JANE/iPubMed run records, and export format requested by the user.

## Verification

Normalize DOI/PMID/arXiv identifiers, compare title/authors/year, distinguish preprints from peer-reviewed sources, map each source to the proposition it supports, flag secondary sources used where primary evidence is available, report introduction/discussion overlap with reuse reasons, and preserve uncertainty when a match is not exact. JANE/iPubMed candidates remain external signals until `verify-refs` or another authoritative source confirms them.

## Failure/fallback

If APIs or web access are unavailable, mark the route `BLOCKED` until both mandatory external run records are available. A local-only diagnostic may be prepared, but it cannot be presented as the completed proofreading conclusion. Never fill missing bibliographic data by guessing.
