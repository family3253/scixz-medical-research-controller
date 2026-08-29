# Review and Submission Workflows

## 1. Journal Selection

### Evaluate journals by
- scope fit
- article type fit
- expected novelty threshold
- audience fit
- tolerance for the user’s methodology and data type
- practical factors: review speed, open access burden, formatting burden

### Preferred journal-fit memo structure
Return a compact table with:
- candidate venue
- why the paper fits
- why it may fail
- article-type compatibility
- evidence / novelty threshold impression
- formatting or policy burden
- confidence level (`high` / `medium` / `low`)

### Desk-reject risk scan
Before recommending submission, explicitly check:
- scope mismatch
- wrong article type for venue
- contribution unclear in title / abstract / introduction
- methods or data type outside journal tolerance
- reporting or ethics omissions likely to trigger editorial triage
- references, figures, or language problems visible from the current draft

### Do not
- rank only by impact factor
- recommend journals outside scope for prestige reasons
- present low-confidence suitability as certainty

## 2. Acceptance-Risk / Submission Readiness Estimation

### Allowed use
- use as heuristic triage, not prophecy
- assess fit, structure, novelty, rigor, evidence completeness, and reviewer vulnerability

### Suggested dimensions
- journal fit
- novelty / contribution clarity
- methods rigor
- evidence sufficiency
- result interpretation discipline
- writing quality
- transparency / ethics / data availability

### Not allowed
- fake numerical acceptance probabilities without explicit heuristic framing
- pretend to have real editorial statistics if none are available

## 3. Pre-Submission Review

### Review on two levels
#### Macro level
- research question clarity
- contribution and novelty
- logic from problem to claim
- methods-result-claim consistency
- journal fit

#### Micro level
- paragraph coherence
- grammar and style
- figure/table references
- citation formatting consistency
- terminology stability

### Feedback format
For each issue provide:
- location
- problem description
- why it matters
- concrete revision suggestion
- revised wording if useful

### Strong optional artifact
When the manuscript contains many claims or a vulnerable argument chain, produce a `claim-evidence-citation matrix` with:
- claim / assertion
- current evidence
- citation status
- overclaim or ambiguity risk
- revision needed
- manuscript location

## 3B. Revision-Coach Workflow

Use when the user has reviewer comments, editorial feedback, or an unstructured revision task but does not yet need a full polished response letter.

### Preferred outputs
- revision priority table
- comment clustering by theme or severity
- revision roadmap
- response matrix skeleton
- unresolved-risk list

### Core rule
Turn messy review comments into an executable plan before polishing prose. A good roadmap should separate:
- what must be changed in the manuscript
- what must be answered in the response package
- what evidence or re-analysis is still missing

## 4. Cover Letter Workflow

### Inputs
- title
- target journal
- concise contribution summary
- why the manuscript fits the journal
- originality / exclusivity statement if needed

### Rules
- do not oversell
- emphasize fit and contribution, not vanity claims
- keep concise and editor-facing

## 4B. Format-Convert Awareness

Use when the user needs conversion between manuscript packaging expectations rather than fresh drafting.

### Typical cases
- Markdown -> LaTeX expectations
- LaTeX -> DOCX / submission-package expectations
- citation style conversion awareness
- journal-specific front-matter or abstract packaging

### Rules
- do not claim a format is submission-ready unless the required fields and sections are visibly present
- separate prose revision from packaging conversion
- if low-level compile or template work is the bottleneck, route mentally to `latex-compile-qa` or `venue-templates` logic instead of improvising

## 5. Reviewer Response Workflow

### Ideal structure
- quote or faithfully paraphrase the comment
- thank reviewer
- state action taken or reasoned disagreement
- provide revised text or revision summary
- identify revision location if possible

### Tone rules
- calm
- specific
- non-defensive
- never sarcastic or wounded

### Common mistakes
- thanking but not answering
- claiming changes without showing them
- mixing multiple reviewer points into one vague reply
- responding with emotion instead of argument

### Response package bundle
When the user has real reviewer or editor comments, prefer a package rather than one free-form letter:
1. revision priority table
2. comment-by-comment response matrix
3. response letter skeleton or full draft
4. unresolved issues list
5. re-review verification checklist

### Response stance labels
For each comment, classify the stance explicitly:
- `accept` — implement fully
- `partially accept` — implement the valid portion and explain limits
- `reasoned disagreement` — do not implement as requested, but answer with scholarly rationale
- `cannot implement now` — genuine constraint; offer fallback, limitation text, or future-work wording

### Response matrix fields
Use columns such as:
- comment ID
- reviewer / editor source
- comment summary
- stance
- action taken
- revised text or revision summary
- manuscript location
- evidence still needed
- tone risk / escalation need

### Response letter rules
- mirror the reviewer's concern faithfully before answering
- make the change easy to verify with section / page / figure / table references when available
- if disagreeing, argue from method, evidence, scope, or journal norms — not emotion
- if a comment reveals ambiguity, revise the manuscript even when the reviewer technically misunderstood
- if a requested change was not made, say so directly and justify it calmly

### Re-review verification memo
Before declaring the revision ready, check:
- every reviewer point has a visible disposition
- every accepted change has a manuscript location
- every disagreement has explicit rationale
- no response claims changes that are absent from the manuscript
- the revised manuscript and response package tell the same story

## 5B. Reviewer-Comment Parsing Heuristic

When comments arrive as a raw block rather than tidy numbered bullets, normalize them into:
- source (`editor`, `reviewer 1`, `reviewer 2`, or `unknown reviewer`)
- issue type (`scope`, `method`, `analysis`, `writing`, `citation`, `figure/table`, `fit`, `ethics`, `other`)
- severity (`blocking`, `important`, `optional`)
- action channel (`manuscript`, `response letter`, `both`, `needs evidence first`)

This makes later revision-roadmap and response-matrix work far more reliable.

## 6. Review Writing / Evidence-Synthesis Integration

The expanded material set shows that review writing is not just another section-writing task. It needs its own routing.

### Before drafting a review, decide:
- narrative review / integrated review
- scoping review / evidence map
- systematic evidence review
- umbrella review
- critical / theoretical review

### Then decide body framework
- time evolution
- topic modules
- method routes
- application scenarios
- debate / contradiction
- mechanism -> evidence -> limitation
- problem -> solution

### Review writing gate
A review should not be written as a polished article unless the user has at least:
- a reasonably defined scope
- a visible corpus or evidence set
- a chosen organizing framework
- at least a provisional claim-to-evidence map

## 8. Output Artifacts to Offer

Depending on user stage, offer one of:
- journal shortlist
- pre-submission review memo
- desk-reject risk memo
- revision priority table
- reviewer response matrix
- response letter skeleton
- cover letter draft
- review-type routing memo
- evidence-to-claim matrix
- re-review verification memo
