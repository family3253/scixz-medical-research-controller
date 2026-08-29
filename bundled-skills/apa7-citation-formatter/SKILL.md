---
name: apa7-citation-formatter
description: Use when the user wants messy references, in-text citations, or bilingual source information normalized into strict APA 7th style. Make sure to use this whenever the request involves APA 7, in-text citation correction, reference-list cleanup, DOI completion, Chinese-English mixed references, et al. rules, or reformatting citations for a manuscript, thesis, dissertation, or submission package.
---

# APA 7 Citation Formatter

## Purpose

Turn messy or incomplete citation material into disciplined APA 7th references and in-text citation suggestions without inventing bibliographic facts.

## When to Use

Use this skill whenever the user:
- asks to format references in APA 7th style
- wants to correct in-text citations such as `(Author, Year)` forms
- has Chinese-English mixed references that need consistent handling
- wants help with `et al.`, author separators, capitalization, journal-title formatting, or DOI presentation
- needs a reference list cleaned for a paper, thesis, dissertation, course assignment, or journal resubmission

## Core Rule

Never fabricate references, DOI values, page ranges, publishers, or publication details.

If metadata are incomplete:
- standardize what is known
- flag what is missing
- offer a likely lookup target only when clearly labeled as unverified

## Output Priorities

Unless the user asks otherwise, provide:
1. cleaned APA 7th reference entries
2. matching in-text citation forms
3. a short note on missing or uncertain fields

## Bilingual Handling Rules

Pay special attention to Chinese-English mixed formatting.

- Do not collapse Chinese and English naming conventions into one style blindly.
- Handle multi-author Chinese references with appropriate `和` or `等` logic when relevant to the requested output.
- Handle English multi-author references using APA 7 rules, including `&` in reference lists and `et al.` in text where appropriate.

## Workflow

1. Read the raw citation or paragraph context.
2. Identify source type if possible: journal article, book, chapter, thesis, webpage, report, conference item.
3. Normalize authors, year, title, source container, volume/issue/pages, and DOI/URL.
4. Format the reference in APA 7th style.
5. Generate corresponding in-text citation examples if useful.
6. Flag unresolved fields explicitly.

## Response Style

Be precise and conservative. Prefer a clearly marked incomplete entry over a polished hallucination.
