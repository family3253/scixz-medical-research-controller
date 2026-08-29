# LitMesh 工具参数速查（direct 模式，36 个，免 API Key）

> 通用调用：`node litmesh.mjs <tool> '<json>' [--render]`
> 查某工具精确 schema：`node litmesh.mjs --schema <tool>`

共 36 个工具（direct 模式）。

## `auto_cite`

Add real citations to a passage of academic text. Key-free mode: the plugin splits the text into sentences, searches Semantic Scholar (PubMed fallback) for each citation point, inserts numbered markers, and returns the reference list (IEEE, APA, Vancouver, Nature, or numbered style) plus BibTeX. Local keyword matching is humbler than the paid service but uses only free APIs. Text must be 100–10,000 characters. Use it when the user pastes a paragraph and asks for citations/references.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "text": {
      "type": "string",
      "description": "Academic text to annotate (100–10,000 characters). In manual mode, mark citation points with [CITE]."
    },
    "mode": {
      "type": "string",
      "description": "auto (default): detect citation points; manual: use [CITE] markers in the text.",
      "enum": [
        "auto",
        "manual"
      ]
    },
    "min_citations": {
      "type": "integer",
      "description": "Minimum citations to add in auto mode (default 10, max 50)."
    },
    "field": {
      "type": "string",
      "description": "Academic field to bias the search, e.g. \"computer science\", \"oncology\"."
    },
    "year_preference": {
      "type": "integer",
      "description": "Preferred publication year for cited papers, e.g. 2024."
    },
    "exclude_preprints": {
      "type": "boolean",
      "description": "Exclude preprints (default false)."
    },
    "exclude_conferences": {
      "type": "boolean",
      "description": "Exclude conference papers (default false)."
    },
    "citation_style": {
      "type": "string",
      "description": "Reference format (default ieee).",
      "enum": [
        "ieee",
        "apa",
        "vancouver",
        "nature",
        "numbered"
      ]
    },
    "preferred_venues": {
      "type": "array",
      "description": "Journal or venue names to prefer (a hint, not a guarantee).",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "text"
  ]
}
```

## `download_arxiv`

Get the abstract page and direct PDF URL for an arXiv paper by id. Free.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "paper_id": {
      "type": "string",
      "description": "arXiv identifier, e.g. \"2106.12345\" or \"hep-th/9901001\"."
    }
  },
  "required": [
    "paper_id"
  ]
}
```

## `download_biorxiv`

Get the article page and direct full-text PDF URL for a bioRxiv preprint by DOI. Free.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "paper_id": {
      "type": "string",
      "description": "bioRxiv DOI, e.g. \"10.1101/2024.01.01.123456\" (optionally with a version suffix like v2)."
    }
  },
  "required": [
    "paper_id"
  ]
}
```

## `download_by_doi`

Resolve a DOI and try to obtain the article PDF: open-access copies work anywhere; paywalled publishers work only on a network with institutional access (campus/VPN). Returns the PDF URL that answered. Free.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "doi": {
      "type": "string",
      "description": "DOI, e.g. \"10.1038/s41586-021-03819-2\"."
    }
  },
  "required": [
    "doi"
  ]
}
```

## `download_medrxiv`

Get the article page and direct full-text PDF URL for a medRxiv preprint by DOI. Free.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "paper_id": {
      "type": "string",
      "description": "medRxiv DOI, e.g. \"10.1101/2024.01.01.123456\" (optionally with a version suffix like v2)."
    }
  },
  "required": [
    "paper_id"
  ]
}
```

## `download_semantic`

Look up a paper's open-access PDF URL on Semantic Scholar by identifier. Returns available=false when the platform lists no open-access copy (then try download_by_doi or the arXiv id).

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "paper_id": {
      "type": "string",
      "description": "Paper identifier (paperId, DOI:, ARXIV:, PMID:, CorpusId:)."
    }
  },
  "required": [
    "paper_id"
  ]
}
```

## `get_pubmed_citations`

Get PubMed papers that cite the given paper, by PMID.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "pmid": {
      "type": "string",
      "description": "PubMed identifier."
    },
    "max_results": {
      "type": "integer",
      "description": "Number of results (default 10, max 50)."
    }
  },
  "required": [
    "pmid"
  ]
}
```

## `get_pubmed_paper_batch`

Get metadata for many PubMed papers in one call by PMID (up to 200 ids).

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "pmids": {
      "type": "array",
      "description": "PubMed identifiers, e.g. [\"39575807\", \"30102808\"].",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "pmids"
  ]
}
```

## `get_pubmed_paper_detail`

Get metadata and the full abstract of one PubMed paper by PMID.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "pmid": {
      "type": "string",
      "description": "PubMed identifier, e.g. \"39575807\"."
    }
  },
  "required": [
    "pmid"
  ]
}
```

## `get_pubmed_related`

Get PubMed papers related to the given paper (PubMed similar-articles ranking), by PMID.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "pmid": {
      "type": "string",
      "description": "PubMed identifier."
    },
    "max_results": {
      "type": "integer",
      "description": "Number of results (default 10, max 50)."
    }
  },
  "required": [
    "pmid"
  ]
}
```

## `get_semantic_author_batch`

Get many Semantic Scholar author profiles in one call (up to 200 author ids).

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "author_ids": {
      "type": "array",
      "description": "Semantic Scholar author ids.",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "author_ids"
  ]
}
```

## `get_semantic_author_detail`

Get one Semantic Scholar author profile by author id: name, affiliations, homepage, h-index, paper and citation counts, external ids.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "author_id": {
      "type": "string",
      "description": "Semantic Scholar author id, e.g. \"1741101\"."
    }
  },
  "required": [
    "author_id"
  ]
}
```

## `get_semantic_author_papers`

List a Semantic Scholar author's papers by author id, newest first, with citation counts. Supports offset pagination.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "author_id": {
      "type": "string",
      "description": "Semantic Scholar author id, e.g. \"1741101\"."
    },
    "max_results": {
      "type": "integer",
      "description": "Number of papers (default 10, max 50)."
    },
    "offset": {
      "type": "integer",
      "description": "Pagination offset (default 0)."
    }
  },
  "required": [
    "author_id"
  ]
}
```

## `get_semantic_citations`

Get papers that cite the given paper from the Semantic Scholar citation graph, with citation contexts and intents when available. Supports offset pagination.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "paper_id": {
      "type": "string",
      "description": "Paper identifier (paperId, DOI:, ARXIV:, PMID:, CorpusId:)."
    },
    "max_results": {
      "type": "integer",
      "description": "Number of results (default 10, max 50)."
    },
    "offset": {
      "type": "integer",
      "description": "Pagination offset (default 0)."
    }
  },
  "required": [
    "paper_id"
  ]
}
```

## `get_semantic_paper_authors`

List the authors of a Semantic Scholar paper with their profiles (affiliations, h-index, paper and citation counts, author ids).

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "paper_id": {
      "type": "string",
      "description": "Paper identifier (paperId, DOI:, ARXIV:, PMID:, CorpusId:)."
    },
    "max_results": {
      "type": "integer",
      "description": "Number of authors (default 10, max 50)."
    },
    "offset": {
      "type": "integer",
      "description": "Pagination offset (default 0)."
    }
  },
  "required": [
    "paper_id"
  ]
}
```

## `get_semantic_paper_batch`

Get metadata for many Semantic Scholar papers in one call (up to 200 ids). Accepts paperIds or prefixed ids (DOI:, ARXIV:, PMID:, CorpusId:). Ids the platform cannot resolve are listed in the warning.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "paper_ids": {
      "type": "array",
      "description": "Paper identifiers.",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "paper_ids"
  ]
}
```

## `get_semantic_paper_detail`

Get metadata and the full abstract of one Semantic Scholar paper by identifier. Accepts a Semantic Scholar paperId, or a prefixed id: DOI:<doi>, ARXIV:<id>, PMID:<id>, CorpusId:<id>, URL:<url>.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "paper_id": {
      "type": "string",
      "description": "Paper identifier, e.g. \"649def34f8be52c8b66281af98ae884c09aef38b\", \"DOI:10.1038/nature14539\", \"ARXIV:1706.03762\", \"PMID:19872477\"."
    }
  },
  "required": [
    "paper_id"
  ]
}
```

## `get_semantic_recommendations`

Recommend papers similar to a set of positive example papers (and unlike optional negative examples) using the Semantic Scholar recommendation model. Good for expanding a reading list from a few seed papers.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "positive_paper_ids": {
      "type": "array",
      "description": "Seed papers to be similar to (paperId or prefixed ids).",
      "items": {
        "type": "string"
      }
    },
    "negative_paper_ids": {
      "type": "array",
      "description": "Papers to steer away from.",
      "items": {
        "type": "string"
      }
    },
    "max_results": {
      "type": "integer",
      "description": "Number of recommendations (default 10, max 50)."
    }
  },
  "required": [
    "positive_paper_ids"
  ]
}
```

## `get_semantic_recommendations_for_paper`

Recommend papers similar to one paper (Semantic Scholar recommendation model). "recent" pool favors recent papers; "all-cs" covers all computer-science papers.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "paper_id": {
      "type": "string",
      "description": "Seed paper identifier (paperId or prefixed id)."
    },
    "max_results": {
      "type": "integer",
      "description": "Number of recommendations (default 10, max 50)."
    },
    "pool": {
      "type": "string",
      "description": "Candidate pool (default recent).",
      "enum": [
        "recent",
        "all-cs"
      ]
    }
  },
  "required": [
    "paper_id"
  ]
}
```

## `get_semantic_references`

Get papers the given paper cites (its reference list) from the Semantic Scholar citation graph, with citation contexts and intents when available. Supports offset pagination.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "paper_id": {
      "type": "string",
      "description": "Paper identifier (paperId, DOI:, ARXIV:, PMID:, CorpusId:)."
    },
    "max_results": {
      "type": "integer",
      "description": "Number of results (default 10, max 50)."
    },
    "offset": {
      "type": "integer",
      "description": "Pagination offset (default 0)."
    }
  },
  "required": [
    "paper_id"
  ]
}
```

## `read_arxiv_paper`

Download an arXiv paper's PDF and return its extracted full text. Free. Long papers are returned in slices: use offset/max_chars to continue (default slice 60000 characters).

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "paper_id": {
      "type": "string",
      "description": "arXiv identifier, e.g. \"2106.12345\"."
    },
    "offset": {
      "type": "integer",
      "description": "Character offset to start from (default 0)."
    },
    "max_chars": {
      "type": "integer",
      "description": "Characters to return (default 60000)."
    }
  },
  "required": [
    "paper_id"
  ]
}
```

## `read_biorxiv_paper`

Download a bioRxiv preprint's PDF and return its extracted full text. Free. Long papers are returned in slices: use offset/max_chars to continue.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "paper_id": {
      "type": "string",
      "description": "bioRxiv DOI, e.g. \"10.1101/2024.01.01.123456\"."
    },
    "offset": {
      "type": "integer",
      "description": "Character offset to start from (default 0)."
    },
    "max_chars": {
      "type": "integer",
      "description": "Characters to return (default 60000)."
    }
  },
  "required": [
    "paper_id"
  ]
}
```

## `read_by_doi`

Resolve a DOI, download the PDF (open access anywhere; paywalled publishers need institutional network access), and return its extracted full text in slices. Free.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "doi": {
      "type": "string",
      "description": "DOI, e.g. \"10.1038/s41586-021-03819-2\"."
    },
    "offset": {
      "type": "integer",
      "description": "Character offset to start from (default 0)."
    },
    "max_chars": {
      "type": "integer",
      "description": "Characters to return (default 60000)."
    }
  },
  "required": [
    "doi"
  ]
}
```

## `read_medrxiv_paper`

Download a medRxiv preprint's PDF and return its extracted full text. Free. Long papers are returned in slices: use offset/max_chars to continue.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "paper_id": {
      "type": "string",
      "description": "medRxiv DOI, e.g. \"10.1101/2024.01.01.123456\"."
    },
    "offset": {
      "type": "integer",
      "description": "Character offset to start from (default 0)."
    },
    "max_chars": {
      "type": "integer",
      "description": "Characters to return (default 60000)."
    }
  },
  "required": [
    "paper_id"
  ]
}
```

## `read_semantic_paper`

Download a paper's open-access PDF (as listed by Semantic Scholar) and return its extracted full text in slices. Fails when no open-access copy exists (then try read_arxiv_paper or read_by_doi).

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "paper_id": {
      "type": "string",
      "description": "Paper identifier (paperId, DOI:, ARXIV:, PMID:, CorpusId:)."
    },
    "offset": {
      "type": "integer",
      "description": "Character offset to start from (default 0)."
    },
    "max_chars": {
      "type": "integer",
      "description": "Characters to return (default 60000)."
    }
  },
  "required": [
    "paper_id"
  ]
}
```

## `search_arxiv`

Search arXiv preprints (physics, mathematics, computer science, quantitative biology, statistics, and more). Free; no API key needed. Returns title, authors, abstract, arXiv id, categories, and PDF link. Supports the arXiv query syntax (e.g. ti:"graph neural network" AND cat:cs.LG) and date filtering.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Search query; plain keywords or arXiv field syntax (ti:, au:, abs:, cat:)."
    },
    "max_results": {
      "type": "integer",
      "description": "Number of results (default 10, max 50)."
    },
    "offset": {
      "type": "integer",
      "description": "Pagination offset (default 0). Use the returned nextOffset to fetch the next page."
    },
    "sort_by": {
      "type": "string",
      "description": "Sort order (default relevance).",
      "enum": [
        "relevance",
        "lastUpdatedDate",
        "submittedDate"
      ]
    },
    "date_from": {
      "type": "string",
      "description": "Only papers submitted on or after this date, YYYY-MM-DD."
    }
  },
  "required": [
    "query"
  ]
}
```

## `search_biorxiv`

List recent bioRxiv preprints in a subject category within a look-back window (the bioRxiv API browses by category and date, not by free text — filter the returned titles/abstracts for the topic). Free; no API key needed.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "bioRxiv category, e.g. \"neuroscience\", \"cell biology\", \"bioinformatics\", \"genomics\"."
    },
    "max_results": {
      "type": "integer",
      "description": "Number of results (default 10, max 50)."
    },
    "days": {
      "type": "integer",
      "description": "Look-back window in days (default 30, max 3650)."
    }
  },
  "required": [
    "query"
  ]
}
```

## `search_google_scholar`

Search scholarly works across publishers, theses, and books (broad coverage). Key-free mode answers from OpenAlex — 250M+ works with cited-by counts — because Google Scholar itself has no public API. Returns title, authors, venue, year, cited-by count, abstract, and an open-access PDF link when available. Supports a year range.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Search query."
    },
    "max_results": {
      "type": "integer",
      "description": "Number of results to return (default 10, max 50); fetched in pages of 10."
    },
    "year_from": {
      "type": "integer",
      "description": "Earliest publication year, e.g. 2020."
    },
    "year_to": {
      "type": "integer",
      "description": "Latest publication year, e.g. 2025."
    }
  },
  "required": [
    "query"
  ]
}
```

## `search_medrxiv`

List recent medRxiv preprints in a subject category within a look-back window (the medRxiv API browses by category and date, not by free text — filter the returned titles/abstracts for the topic). Free; no API key needed.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "medRxiv category, e.g. \"epidemiology\", \"oncology\", \"cardiovascular medicine\", \"public and global health\"."
    },
    "max_results": {
      "type": "integer",
      "description": "Number of results (default 10, max 50)."
    },
    "days": {
      "type": "integer",
      "description": "Look-back window in days (default 30, max 3650)."
    }
  },
  "required": [
    "query"
  ]
}
```

## `search_papers`

Search several platforms in one call and merge the results: duplicates are collapsed by DOI / arXiv id / PMID / title, papers found on more than one platform rank first, then by citation count. Good first call for a topic; use the platform tools for filters and paging. Available platforms: Semantic Scholar, PubMed, arXiv, Google Scholar (default Semantic Scholar + PubMed; all free public APIs, no key needed; google-scholar answers from OpenAlex).

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Topic or keywords; sent to every selected platform as-is."
    },
    "sources": {
      "type": "array",
      "description": "Platforms to query (default [\"semantic-scholar\",\"pubmed\"]).",
      "items": {
        "type": "string",
        "enum": [
          "semantic-scholar",
          "pubmed",
          "arxiv",
          "google-scholar"
        ]
      }
    },
    "max_results_per_source": {
      "type": "integer",
      "description": "Results requested from each platform (default 10, max 50)."
    },
    "year_from": {
      "type": "integer",
      "description": "Earliest publication year."
    },
    "year_to": {
      "type": "integer",
      "description": "Latest publication year."
    }
  },
  "required": [
    "query"
  ]
}
```

## `search_pubmed`

Search biomedical and life-science literature on PubMed. Returns title, authors, journal, publication date, PMID, DOI, MeSH terms, and abstract. Supports a date range and relevance/date sorting.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "PubMed query; field tags such as [Title/Abstract] and boolean operators are supported."
    },
    "max_results": {
      "type": "integer",
      "description": "Number of results to return (default 10, max 50)."
    },
    "offset": {
      "type": "integer",
      "description": "Pagination offset (default 0). Use the returned nextOffset to fetch the next page."
    },
    "sort": {
      "type": "string",
      "description": "Sort order (default relevance).",
      "enum": [
        "relevance",
        "date"
      ]
    },
    "min_date": {
      "type": "string",
      "description": "Earliest publication date, YYYY, YYYY/MM, or YYYY/MM/DD."
    },
    "max_date": {
      "type": "string",
      "description": "Latest publication date, YYYY, YYYY/MM, or YYYY/MM/DD."
    }
  },
  "required": [
    "query"
  ]
}
```

## `search_semantic`

Search academic papers on Semantic Scholar (200M+ papers, all fields). Returns title, authors, year, venue, citation count, identifiers, and abstract. Supports year filtering and offset pagination.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Search query, e.g. \"graph neural networks drug discovery\"."
    },
    "max_results": {
      "type": "integer",
      "description": "Number of results to return (default 10, max 50)."
    },
    "offset": {
      "type": "integer",
      "description": "Pagination offset (default 0). Use the returned nextOffset to fetch the next page."
    },
    "year": {
      "type": "string",
      "description": "Year filter: \"2019\", \"2016-2020\", \"2010-\" (from 2010), or \"-2015\" (up to 2015)."
    }
  },
  "required": [
    "query"
  ]
}
```

## `search_semantic_authors`

Search Semantic Scholar authors by name. Returns author ids with affiliations, h-index, paper and citation counts. Follow up with get_semantic_author_detail or get_semantic_author_papers.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Author name, e.g. \"Yann LeCun\"."
    },
    "max_results": {
      "type": "integer",
      "description": "Number of authors (default 10, max 50)."
    },
    "offset": {
      "type": "integer",
      "description": "Pagination offset (default 0)."
    }
  },
  "required": [
    "query"
  ]
}
```

## `search_semantic_bulk`

Bulk paper search on Semantic Scholar for large result sets: pages of up to 1000 matches with a continuation token, sortable by citation count, date, or paper id. Only the first max_results papers of the page are returned to keep context small; pass the returned nextToken to continue. Use search_semantic for ordinary relevance-ranked queries.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Search query; supports the bulk query syntax (boolean operators, quotes, prefix*)."
    },
    "max_results": {
      "type": "integer",
      "description": "Papers to return from this page (default 10, max 50)."
    },
    "token": {
      "type": "string",
      "description": "Continuation token from a previous bulk search."
    },
    "year": {
      "type": "string",
      "description": "Year filter: \"2019\", \"2016-2020\", \"2010-\", or \"-2015\"."
    },
    "sort": {
      "type": "string",
      "description": "Sort, e.g. \"citationCount:desc\", \"publicationDate:asc\", \"paperId\"."
    }
  },
  "required": [
    "query"
  ]
}
```

## `search_semantic_paper_match`

Find one paper on Semantic Scholar by its title (closest title match). Use it to resolve a known title to its identifiers, DOI, and metadata.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "The paper title, e.g. \"Attention Is All You Need\"."
    }
  },
  "required": [
    "query"
  ]
}
```

## `search_semantic_snippets`

Search inside paper full texts on Semantic Scholar. Returns ~500-word excerpts (from titles, abstracts, and body text) that match the query, each with its source paper. Use it to find where a concept is discussed, not to list papers.

参数（JSON schema）：

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Phrase or question to locate in full texts."
    },
    "max_results": {
      "type": "integer",
      "description": "Number of snippets (default 10, max 50)."
    }
  },
  "required": [
    "query"
  ]
}
```
