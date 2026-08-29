# Literature Search and Screening

## Purpose
This file upgrades AWAS from literature-search awareness to literature-search competence, including Chinese thesis discovery and authorized browser-assisted retrieval workflows.

It does **not** replace dedicated research skills. Instead, it gives AWAS a strong, reusable literature layer for planning, running, and organizing evidence retrieval workflows in a writing-centric context.

## Core Principle

Search is not just finding papers.
A good academic search workflow must handle:
1. question framing
2. query construction
3. source selection
4. retrieval
5. de-duplication
6. screening
7. evidence extraction
8. citation governance
9. handoff to writing

For review-grade work, the search layer should also preserve a minimal project record so the writing stage can explain where the evidence came from and how records were filtered.

For PDF-heavy review work, retrieval is not complete when the files are merely downloaded. The workflow must also decide whether each PDF is text-based, layout-heavy, supplement-heavy, or scan-based, because that changes the extraction path.

## PDF-Heavy Review Workflow

When the review corpus is dominated by PDFs, especially papers with supplementary appendices, use this reading logic:

1. triage the PDF type: text, layout-heavy, supplement-heavy, or scan/mixed
2. extract core text reproducibly
3. extract tables and appendix content separately when they contain metrics or model definitions
4. escalate to OCR for scanned or ambiguous regions
5. preserve page / figure / table provenance for anything that may enter an extraction table

Do not assume the article body contains all review-relevant information. In prediction-model reviews, essential performance details may live in supplements, appendix tables, or figure panels.

## When to Use

Use this layer when the user needs any of the following:
- literature search strategy
- keyword design
- PubMed / Crossref / arXiv / web search planning
- CNKI / Wanfang / institutional thesis discovery
- authorized browser workflow planning for export-based retrieval workstations
- review corpus building
- related work discovery
- screening and inclusion logic
- evidence map preparation
- DOI verification and metadata cleanup
- claim-to-citation preparation before writing

## Search Modes

### 1. Quick Related-Work Search
Use when the user needs a small, practical set of key papers fast.

Output:
- 5-15 papers
- grouped by theme or approach
- short relevance notes
- obvious gaps or disagreements

### 2. Structured Literature Review Search
Use when the user needs a stronger review foundation.

Output:
- topic decomposition
- concept groups
- keyword expansion
- source plan
- candidate corpus
- screening logic

### 3. Review-Grade Evidence Search
Use when the user is writing a narrative / scoping / systematic / umbrella review and needs traceable search logic.

Output:
- explicit search strategy
- database selection
- query variants
- inclusion / exclusion criteria
- corpus management fields
- downgrade rules if evidence remains weak
- project artifacts for candidate pool, screening, evidence extraction, and exclusion reasons

### 4. Chinese Thesis Discovery and Learning
Use when the user needs master's-thesis or dissertation discovery from CNKI, Wanfang, university repositories, or a browser-based workstation and wants to learn from those artifacts before writing.

Output:
- provider and access-mode plan
- institution-filtered search strategy
- thesis-aware candidate corpus
- access-state tracking for metadata-only vs authorized full text
- learning memo describing what the thesis corpus contributes to chapter design, methods wording, or evidence framing

## Source Routing

### Default source roles
- **PubMed**: biomedical and life-science priority source
- **Crossref / DOI metadata**: citation normalization and metadata completion
- **arXiv**: preprints and frontier technical literature
- **general web / scholarly search**: broad discovery and triangulation
- **CNKI**: Chinese journals and Chinese theses/dissertations when thesis discovery or Chinese-language evidence matters
- **Wanfang**: Chinese journals, theses, and official platform APIs/workstations where available
- **institutional repositories**: university-hosted dissertations, thesis abstracts, and full-text mirrors when legitimately accessible
- **authorized browser workstations**: export-first platforms such as IPubMed or provider portals that are usable through an existing login, institution session, or plugin-based workflow
- **local library / Zotero / Obsidian if available**: user-owned evidence first, and when an installed Zotero MCP is available, use Zotero as the verified-reference source of truth after authenticity and metadata repair gates pass

### Routing rule
Pick sources based on domain and task type:
- medicine / life science -> PubMed first
- AI / CS frontier topic -> arXiv + web + local library
- broad review topic -> local + web + structured database search
- citation cleanup -> DOI / metadata workflow first
- Chinese thesis or dissertation learning -> CNKI / Wanfang / institutional repositories + local library + export normalization

### Access Mode Priority

When the source can be reached in more than one way, prefer this order:

1. official APIs or structured exports
2. direct metadata pages and documented platform features
3. identifier resolution paths such as DOI -> provider landing page when the source already has stable identifiers
4. authorized browser automation against an existing session or institution-linked workstation
5. manual export / import fallback

Anti-bot, retries, session persistence, and brittle browser steps belong to provider adapters and retrieval agents, not to the writing logic itself.

## Query Construction Workflow

### Step 1: Define the information need
Classify what the user really wants:
- key papers?
- comprehensive review corpus?
- only recent work?
- methods benchmark?
- theory background?
- contradictory findings?

### Step 2: Build concept groups
Break the topic into 2-4 concept groups, for example:
- disease / problem
- intervention / method
- outcome / task
- population / context
- institution / degree / advisor / thesis type when the target corpus is Chinese dissertations

### Step 3: Expand terms
For each concept group, list:
- standard term
- synonyms
- abbreviations
- spelling variants
- field-specific variants
- controlled vocabulary if relevant (e.g. MeSH)

### Step 4: Assemble queries
Use Boolean structure and source-specific syntax.

#### Generic pattern
`(Concept A synonyms) AND (Concept B synonyms) AND optional filters`

#### Example: PubMed-style mindset
- exact concept via phrase matching where needed
- MeSH when relevant
- date window when needed
- publication type filters when justified

### Step 5: Sanity-check query quality
Before running, ask:
- is it too narrow?
- is it missing obvious synonyms?
- is it mixing concept levels?
- is it over-filtered too early?
- does it confuse intervention with outcome?

### Chinese Thesis Query Dimensions
When the source is CNKI, Wanfang, or an institutional thesis repository, also consider:
- granting institution or university cluster
- degree level (master / doctoral)
- thesis type if visible
- advisor or lab lineage when the field relies on school-level traditions
- defense year and language

## Screening Workflow

### Level 1: title / abstract screening
Decide whether the record is:
- clearly relevant
- maybe relevant
- clearly irrelevant

Record why.

Recommended fields:
- citation ID
- title
- source database
- topic tag
- include / maybe / exclude
- reason for decision
- screener / date if the workflow is formal

### Level 2: full-text screening
For items that matter to writing, decide whether they can support:
- background only
- method comparison
- core claim
- contradiction analysis
- exclusion

Recommended additional fields:
- full-text availability status
- reason for exclusion
- evidence grade / confidence note
- whether the paper enters evidence extraction

### Strong rule
Do not write strong consensus language from title/abstract impressions alone when the task requires submission-grade rigor.

## Evidence Extraction Workflow

For each kept source, extract at minimum:
- citation identity
- research question / objective
- study type or paper type
- method / data / corpus
- key finding
- limitation
- how this source will be used in our writing
  - background
  - method support
  - contrast point
  - evidence for claim
  - limitation / caution

Helpful optional fields for review-grade work:
- topic cluster / chapter destination
- evidence strength or bias concern
- contradiction marker
- trace-back location (page / table / figure / section when visible)

### Extraction-First Rule for Review / Meta Work

For systematic review and meta-analysis tasks, extraction is not a clerical afterthought; it is the main substrate for everything downstream.

Prefer this order:
1. stabilize inclusion / exclusion state
2. build or repair the extraction register
3. audit extraction quality and missingness
4. only then tighten narrative synthesis

If the user already has spreadsheets, extraction templates, or audit sheets, prefer improving field-level extraction fidelity before expanding prose.

### Prediction-Model Review / Meta Add-On

If the kept corpus is about clinical prediction models, extract more than generic study characteristics.

At minimum, preserve:
- population and setting
- prediction target and horizon
- model stage and exact split (`training`, `internal validation`, `internal test`, `external validation`, `external test`, `update`)
- sample size and event count when visible
- predictor set and final model form
- discrimination metric name and value
- calibration metric type and value if reported
- utility / DCA / threshold information if reported
- study-level transportability or applicability concerns

Do not flatten these details into generic “performance was good” notes if later synthesis may compare models across studies.

If the article reports multiple datasets or splits, preserve them in separate fields instead of merging them into one “validation” bucket.

## Citation Governance Workflow

### Required behaviors
- resolve DOI metadata where possible
- normalize author / title / journal / year fields
- detect duplicates
- flag missing fields explicitly
- distinguish verified citations from placeholders
- classify each item by source type: journal article, book, chapter, thesis, webpage, report, guideline, conference item, or unknown
- repair real but malformed references before formatting them
- search for replacement candidates when a cited item appears nonexistent, but never silently substitute them
- treat China Pharmaceutical University professional-master thesis reference work as local-authority-first and GB/T 7714-2015-priority

### Good outputs
- clean citation table
- BibTeX-ready records
- DOI completion list
- duplicate cluster list
- references requiring manual verification
- replacement-candidate list clearly labeled as needing confirmation
- verified-reference register with source type, authenticity verdict, repair status, replacement-candidate status, and Zotero import state when applicable

## Project Artifacts for Traceable Review Work

When the task is closer to review production than quick related-work search, prefer a small artifact set rather than loose notes.

### Minimal artifact stack
1. `search strategy memo`
2. `candidate pool table`
3. `title/abstract screening record`
4. `full-text retrieval / screening record`
5. `evidence extraction table`
6. `claim-to-citation or evidence matrix`

Concrete bundled versions now exist in `assets/templates/`, and the canonical schema lives in `scripts/review_project_schema.py`.

If the user is starting from scratch on a review-grade project, initialize a scaffold with `scripts/init_review_project.py` rather than inventing ad hoc filenames.

### Suggested field discipline for those artifacts

#### Candidate pool table
At minimum track:
- citation ID
- title
- database / source
- source provider
- access mode
- retrieval batch or search round
- year
- authors
- venue
- granting institution when the source is a thesis
- degree level / thesis type when visible
- advisor when visible and relevant
- institution filter used during search
- DOI or URL
- topic tag
- duplicate status
- full-text availability
- title/abstract relevance
- initial decision
- exclusion note if already obvious

#### Title / abstract screening record
At minimum track:
- citation ID
- include / maybe / exclude
- inclusion criterion hit
- exclusion criterion hit
- reason for decision
- screener / date if formal

#### Full-text retrieval / screening record
At minimum track:
- citation ID
- retrieval status
- retrieval source
- access mode
- whether an authorized browser session or institution session was used
- version / copyright note if relevant
- full-text include / exclude
- exclusion reason
- evidence grade or confidence note
- whether it enters extraction

#### Evidence extraction table
At minimum track:
- citation ID
- objective / question
- study or paper type
- granting institution / degree level when the source is a thesis
- method / data / corpus
- key finding
- limitation
- evidence strength / bias concern
- contradiction marker
- manuscript use
- trace-back page / table / figure / section if visible

### Why this matters
- prevents writing from vague memory
- preserves reasons for exclusion
- makes PRISMA-style or appendix-style reporting much easier later
- separates retrieval, screening, extraction, and writing so weak evidence is easier to spot

### Concrete tooling now bundled
- `scripts/init_review_project.py <output_dir>`
- `scripts/import_and_dedupe_candidates.py <input_csv...> --output <candidate_pool.csv>`
- `scripts/generate_gate_report.py <project_dir>`
- `scripts/citation_authenticity_sentinel.py <project_dir>`
- `scripts/wanfang_topic_api_adapter.py <keyword> --output <candidate_pool.csv> --config <wanfang_topic_api_config.json>`
- `scripts/cnki_doi_adapter.py <doi> --output <candidate_pool.csv>`
- `scripts/doi_acquisition_adapter.py <doi> --candidate-output <candidate_pool.csv> --acquisition-output <fulltext_acquisition.csv> --text-output <artifact.txt>`
- `scripts/classify_acquisition_artifact.py --acquisition-csv <fulltext_acquisition.csv> --text-file <artifact.txt>`
- `scripts/handoff_acquisition_to_project.py --project-dir <project_dir> --candidate-csv <candidate_pool.csv> --acquisition-csv <fulltext_acquisition.csv> --text-file <artifact.txt>`
- `scripts/cnki_browser_adapter.py --output <candidate_pool.csv> --query <topic>`
- `scripts/ipubmed_browser_adapter.py --output <candidate_pool.csv> --query <topic>`
- `scripts/browser_workstation_adapter.py --config <workflow.json> --output <candidate_pool.csv>`
- `assets/templates/provider_adapter_examples.md`

These are intentionally lightweight and writing-oriented. They do not replace dedicated retrieval platforms, but they do eliminate a large amount of repeated clerical setup.

The import path can also normalize CNKI, Wanfang, or browser-workstation exports into the same candidate-pool schema when the source columns can be mapped cleanly.

## Literature Authenticity Sentinel

For citation-sensitive writing, add a narrow four-layer authenticity pass before handoff:

1. identity
2. source status
3. claim support
4. manuscript binding

This is the point where a citation stops being merely present and becomes safe to use.

Use `references/literature-authenticity-sentinel.md` and `scripts/citation_authenticity_sentinel.py` for this step.

### Authenticity -> Repair -> Replacement -> Zotero Loop
When the user provides a manuscript plus a reference list, or a standalone messy reference list, extend citation governance like this:

1. classify each item by source type: journal article, book, chapter, thesis, webpage, report, guideline, conference item, or unknown
2. verify identity and support status
3. repair metadata when the item is real but malformed or incomplete
4. if the cited item appears nonexistent, search for the closest real replacement candidate but never silently substitute it
5. require explicit confirmation before binding a replacement candidate to the manuscript or importing it into Zotero
6. import only PROCEED items, and REFINE items that become PROCEED after repair, into Zotero when the installed MCP and library credentials are available
7. default import destination is the Zotero cpu collection unless the user names a different target
8. default duplicate policy is keep-both; do not auto-merge or auto-deduplicate imported items unless the user explicitly asks for cleanup
9. prefer MCP-first DOI import for journal articles and other identifier-clean scholarly items, and prefer API-first structured import for non-journal sources such as reports, webpages, guidelines, UN/WHO institutional documents, and other source-type-sensitive records
10. treat Zotero as the canonical verified-reference store before processor-specific recitation into Word or conservative/static recitation into WPS


Hard rules:
- do not silently convert a webpage/report/guideline into a journal article just to satisfy a style template
- do not fabricate bibliographic facts for incomplete nontraditional sources
- do not silently replace nonexistent citations; label them as replacement candidates
- when the scene is China Pharmaceutical University professional-master thesis formatting, prioritize the local thesis authority and GB/T 7714-2015 over generic journal-style cleanup

### PRISMA / PRISMA-S awareness
For systematic or scoping review grade work, be aware that high-quality reporting usually requires:
- information sources to be listed clearly
- search strings or search logic to be documented
- duplicate handling to be described
- screening stages to be distinguishable
- full-text exclusion reasons to be recoverable

Do not pretend to have fully satisfied PRISMA or PRISMA-S unless those records actually exist.

## Handoff to Writing

A good literature search should hand off one of these artifacts to the writing workflow:
- related-work table
- evidence matrix
- candidate core references list
- review framework memo
- claim-to-citation map
- verified-reference register with source type, authenticity verdict, repair status, replacement-candidate status, and Zotero import state when applicable

Writing should begin from those artifacts, not from vague memory of search results.

## Agent-Orchestrated Workflow Pattern

For larger research systems, a good pattern is:
- retrieval agent or provider adapter populates candidate pool, source metadata, and access-state notes
- screening / evidence agent updates screening and extraction artifacts
- analysis / figure agent prepares visual evidence packs or result-support artifacts
- AWAS then drafts or revises from those explicit artifacts

This keeps AWAS focused on writing, synthesis, and evidence-faithful transformation rather than turning it into a full autonomous research platform.

In other words:
- provider adapters access sources, retry, cache, and export
- agents execute
- tools compute
- templates record
- AWAS writes and reviews against the recorded evidence

## Absorbed Capability Patterns

### From `research-lit`
- source-priority thinking
- local library first if available
- paper table + narrative landscape summary
- grouping by theme and disagreement

### From `deep-research`
- research-question-first framing
- source verification and evidence hierarchy awareness
- contradiction handling and synthesis before prose

### From `pubmed-database`
- Boolean + field-tag + MeSH literacy
- programmatic-search mindset
- article type / date / language filtering discipline
- systematic-review search awareness

### From `citation-management`
- DOI resolution
- metadata normalization
- deduplication
- export-oriented citation cleaning

### From `cross-disciplinary-review-writer`
- gate-based review corpus logic
- candidate pool -> screening -> evidence extraction -> framework -> writing sequence
- downgrade honesty when the corpus is insufficient

### Review-project gate reminder
When the user is asking for a polished review article, the literature layer must surface not only what was found, but also whether the corpus is mature enough for:
- `submission-grade review draft`
- `review-grade evidence synthesis`
- `evidence map / scoping output`
- `framework memo / review outline`

Search and screening outputs should make this downgrade decision easier rather than burying it.

### From `scitex-python`
- modular toolchain thinking across retrieval, analysis, figures, and writing
- session-based artifact organization
- writing as a downstream consumer of structured scientific outputs

## Common Failure Patterns

- searching before clarifying the question
- over-narrowing the query too early
- treating the first 5 papers found as “the literature”
- writing a review without a corpus management step
- citing unverified metadata
- failing to separate peer-reviewed evidence from preprints
- treating title/abstract screening as full evidence extraction
- not recording why a paper matters to the manuscript

## Output Templates

### Template A: Quick Related-Work Table
| Paper | Year | Type | Method / Data | Key finding | Why it matters |

### Template B: Search Strategy Memo
- topic
- target output
- concept groups
- query variants
- source plan
- filters
- expected limitations

### Template B2: Candidate Pool Table
| Citation ID | Title | Database / Source | Year | DOI | Topic tag | Duplicate status | Full-text status | Initial relevance |

### Template B3: Title / Abstract Screening Record
| Citation ID | Include? | Why | Topic tag | Screener / date |

### Template B4: Full-Text Screening Record
| Citation ID | Include? | Use type | Exclusion reason if excluded | Evidence grade | Notes |

### Template C: Evidence Matrix
| Citation | Claim supported | Evidence strength | Use in manuscript | Verification status |

## Boundary

AWAS should become competent at literature-search planning, organization, and evidence governance.
It should **not** pretend to be a full autonomous retrieval platform or a browser-bypass engine.

When deep, domain-specific, or large-scale research is the main task, route to stronger dedicated research skills rather than overextending the writing skill.






