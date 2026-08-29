# External research tools: JANE and iPubMed

SciXZ uses the following public services as mandatory auxiliary evidence sources for the journal-selection and citation-management routes. They are not Skills and are never the sole basis for journal choice, citation acceptance, misconduct claims, or current metric claims.

## Mandatory-call policy

For a SciXZ `journal-selection` run, both JANE and iPubMed must be invoked. For a SciXZ `citation-management` run, or a submission-preflight run whose reference-proofreading branch is in scope, both must also be invoked. The two calls may run in parallel, but each needs its own run record and auditable result.

The canonical owner still performs the final work: `find-journal` ranks and explains the submission cascade; `verify-refs` verifies bibliographic identity and claim support. External results remain `external-signal` until that verification.

If either mandatory adapter is unavailable, blocked by the browser boundary, or cannot produce a result artifact, SciXZ must stop before publishing the final ranked journal list or reference-proofreading conclusion. It may report a diagnostic partial state and the exact missing artifact, but it must not silently substitute a local fallback. Relaxing this requirement requires an explicit change to the user's mandate.

## JANE

JANE accepts a title/abstract or keyword query and returns similar journals, authors, or papers. Its documented URL interface supports `suggestions.php?findJournals`, `findAuthors`, and `findPapers`; a SOAP WSDL is also documented. Use the URL interface for auditable, low-complexity calls and keep the exact query URL in the run manifest.

Use JANE for:

- an independent PubMed-similarity shortlist during journal selection;
- finding candidate papers that may support an introduction/discussion claim;
- identifying a possible author or journal cluster for literature mapping.

Do not use JANE to infer acceptance probability, current APC, current impact factor, editorial policy, or citation validity. Its own FAQ states that results are based on PubMed data, the data is updated monthly, and predatory journals may appear; MEDLINE and DOAJ labels are useful screening signals but not a complete quality certificate.

## iPubMed

iPubMed is a dynamic Shiny application whose public interface exposes journal matching from title/abstract/keywords, filtered literature retrieval, Excel/EndNote/Zotero export, citation tracing, IF/APC lookup, and title-level suspicious-reference checks.

Because the public page does not expose a stable API description, SciXZ treats iPubMed as `browser-assisted-shiny`:

- use an approved browser session or user-provided export;
- record the input summary, filters, date, result/export path, and tool status;
- do not assume that a page load means a query completed;
- do not place API keys or third-party Base URLs in the SciXZ registry or run manifest;
- do not send an unpublished full manuscript, peer-review material, PHI, or restricted data without explicit authorization and a policy check.

Use iPubMed for:

- a second journal shortlist using its filters and local export formats;
- citation-trace and title-level checks that help triage suspicious or mismatched references;
- discovering DOI/PMID/PMCID candidates before canonical verification.

Its outputs remain `external-signal` until verified. IF, APC, indexing, retraction, preprint status, and citation metadata must be checked with authoritative sources. A suspicious-title signal is not a fabrication, misconduct, or retraction verdict.

## Combined routing policy

### Journal selection

`find-journal` owns the final ranked recommendation and fallback cascade. JANE is the reproducible PubMed-similarity branch and iPubMed is the browser/export branch. Both are required evidence tickets for every SciXZ journal-selection run.

The final report must separate:

1. scope/article-type fit;
2. design and acceptance-feasibility assessment;
3. JANE similarity evidence;
4. iPubMed search/filter evidence;
5. current journal policy/metric verification;
6. unresolved conflicts and the reason for the final ranking.

### Citation proofreading

`verify-refs` owns citation validity. JANE must be called for candidate-paper discovery and iPubMed must be called for citation-trace/title triage. Every accepted reference must still be matched by PMID/DOI/title/authors and, where relevant, opened at the source. Keep uncertain or suspicious items visible in the audit; never silently replace them. If either external run is missing, the proofreading conclusion is blocked.

For introduction/discussion writing, preserve the section citation ledger. External-tool candidates do not enter the final bibliography until verified and assigned to a specific claim. Shared introduction/discussion references require a reuse reason.

## External-tool run record

```yaml
external_tool_run:
  tool: jane | ipubmed
  mode: public-url-api | browser-assisted-shiny | user-export
  query_fingerprint: "stable hash or local input ID"
  input_scope: title | abstract | keywords | claim-paraphrase | reference-list
  requested_at: "timestamp"
  result_path: "absolute path or null"
  status: completed | partial | unavailable | blocked
  evidence_state: external-signal | verified | unresolved
  verification_owner: find-journal | verify-refs | sci-manuscript-preflight
  limitations: []
```
