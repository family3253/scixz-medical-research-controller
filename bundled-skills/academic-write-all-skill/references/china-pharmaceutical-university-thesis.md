# China Pharmaceutical University Thesis Scenario

## Purpose

This file is the school-specific authority summary for China Pharmaceutical University thesis and dissertation work inside AWAS.

Use it when the user is writing, revising, structuring, or formatting a China Pharmaceutical University thesis and the task should not be treated as a generic thesis workflow.

## Local Authority Order

When local files conflict, use this priority:

1. `<PRIVATE_WORKSPACE>\参考\论文格式.doc`
2. official CPU graduate-thesis requirement documents
3. school-issued CPU template files
4. generic AWAS thesis defaults

Hard rule:
- do not let a nicer-looking template outrank the controlling local authority file
- do not silently merge conflicting school files into a blended pseudo-standard

Interpretation rule for this local project:
- the local `论文格式.doc` should be treated as reflecting a later and stricter rule layer than the older school-issued template files when their details diverge
- therefore, template files are mainly layout/examples references, while `论文格式.doc` is the decision source for final compliance judgments

## Current Project Bias

For this local project, assume the main route is:

- **China Pharmaceutical University professional-master's thesis**

Do **not** default to the `同等学历` route unless the user explicitly says that is the correct track.

## What the current local evidence already supports

### Core package structure

The local authority materials support a thesis package that usually includes:

1. cover
2. originality statement and copyright authorization
3. table of contents
4. Chinese abstract
5. English abstract
6. optional abbreviation/symbol list
7. thesis body
8. references
9. publication list during degree period
10. acknowledgements

Additional 26-version authority signal from `论文格式.doc`:
- the current local high-priority rule set may use a **blind-review package** with a reduced major-part structure for review submission, rather than the full final-archive package shown in older official documents
- AWAS should therefore distinguish `blind-review package` from `final degree-archive package` instead of assuming one universal package state
- the current local high-priority rule set explicitly recognizes an **AI-assisted research-and-writing commitment sheet** as a front-matter item that affects package completeness and pagination exclusions

### Language and body defaults

- the thesis body should default to simplified Chinese except where the school explicitly allows English components
- English title and English abstract remain school-recognized components, not reasons to treat the thesis like a journal paper

### Formatting and layout constraints already visible

- paper size: A4
- body line spacing: 20 pt fixed
- formulas: 1.5x line spacing
- margins: upper/binding side 25 mm, lower/outside side 20 mm, with limited micro-adjustment if necessary
- page headers: odd/even page split with school-defined header content
- header separator line: horizontal solid line below header
- page numbering split:
  - front matter such as contents / abstracts / abbreviation list uses Roman numerals
  - body and later sections use Arabic numerals

Additional 26-version visible constraints from `论文格式.doc`:

- blind-review package may exclude some front-matter items that appear in the full school archive package
- page numbering exclusions now explicitly include the AI-assisted research-and-writing commitment sheet when that sheet is required
- front matter and review package sequencing should therefore be checked against the local high-priority file before claiming compliance

### Typography already visible

- chapter title: 3rd-size black font, centered
- section title: 4th-size black font, left aligned
- lower-level title: small-4 black font, left aligned
- body: small-4 Song
- references: 5th-size Song, no first-line indent
- page numbers: 5th-size Song
- letters and numbers: Times New Roman

### Figures and tables already visible

- tables should follow the school three-line-table convention
- figures should be centered with captions below
- tables use captions above
- figure and table numbering should follow chapter-based numbering

26-version authority refinements visible from `论文格式.doc`:

- three-line tables use stronger line-width guidance in the high-priority local rule set
- figure captions should explicitly explain statistical methods and all symbols/markers used in the figure
- figure image quality, resolution, and single-column / double-column width suitability are school-controlled presentation constraints, not optional aesthetics

### Reference style

- references should follow the thesis-side local rule first
- if local files conflict, the controlling file in this project is `<PRIVATE_WORKSPACE>\参考\论文格式.doc`
- do not switch to journal-style reference habits unless the user explicitly asks for a thesis-to-paper conversion stage

26-version authority refinements visible from `论文格式.doc`:

- prefer the current local rule that points to **GB/T 7714-2015** when it conflicts with older school documents still naming earlier editions
- treat page-range completeness, author truncation rules, and superscript in-text citation style as hard compliance points rather than optional cleanup

## CPU Professional-Master vs Same-Equivalent Route

The local materials show that the school distinguishes at least these routes:

- master's academic degree
- master's professional degree
- same-equivalent application for master's degree

For this project:

- treat **professional-master** as the default route
- treat `同等学历` as a distinct route with its own cover/front-matter implications
- do not borrow the same-equivalent cover or front-matter by default for a professional-master task
- use the local `03【专硕】论文模板.docx` as the preferred professional-master template example for cover/front-matter field layout

## Writing Implications for AWAS

When AWAS is handling a CPU professional-master task:

- prioritize school compliance over journal-like compactness
- prefer chapter-role clarity over paper-style compression
- keep front matter, abstract structure, pagination, references, and chapter sequencing under school control
- treat thesis-to-paper conversion as an explicit second-stage transformation
- if the task is for blind review, prefer the reduced review-package logic from `论文格式.doc` over the fuller archive-package structure from older documents/templates
- if the local CPU package includes the AI-assisted research-and-writing commitment sheet, treat it as a formal front-matter compliance artifact rather than a disposable note

## Route Ownership Guidance

Recommended ownership inside AWAS:

- intake owner: `academic-write-all-skill`
- preferred execution owner: `awas-writing-coordinator`
- allowed support: `oracle` only for difficult boundary judgments, not as academic owner
- forbidden parallel owner: generic thesis defaults overriding school rules; `同等学历` route as default; immediate journal-style conversion as co-equal goal

## What to double-check before claiming compliance

Before AWAS says a CPU thesis output is compliant, check at least:

- route is really professional-master vs same-equivalent
- package state is really blind-review package vs final archive package
- front matter set is complete
- AI-assisted research-and-writing commitment sheet is present or intentionally omitted under the correct rule set
- abstract / keyword handling matches school expectations
- pagination split is correct
- references are thesis-compliant rather than merely journal-pretty
- chapter structure is thesis-scale rather than article-scale

## Reusable Checklist Template

Use this template when AWAS needs an operational compliance pass rather than only narrative guidance:

- `assets/templates/cpu-professional-master-thesis-checklist.md`

Preferred use:
- duplicate the checklist into the current project workspace or manuscript support notes
- mark package state first (`blind-review package` vs `final archive package`)
- then complete the front-matter, pagination, typography, figure/table, and reference sections in order
