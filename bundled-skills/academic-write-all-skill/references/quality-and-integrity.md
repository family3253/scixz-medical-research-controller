# Quality and Integrity Rules

## 1. Anti-Hallucination Rules

Never invent:
- references
- DOI numbers
- page numbers
- sample sizes
- effect sizes
- p-values
- reagent IDs
- ethics approvals
- software versions
- reviewer comments or journal requirements

If evidence is missing, use one of three moves:
1. ask for the missing input
2. mark a placeholder
3. downgrade confidence explicitly

## 2. Citation Discipline

### Allowed
- user-provided verified references
- references clearly visible in supplied materials
- citations retrieved from trusted tools when explicitly available

### Not allowed
- fabricated “supportive” citations
- fake recent literature summaries
- backfilled citations that merely sound plausible

### Good fallback language
- `[待核实文献]`
- `此处需补充一篇权威综述或代表性研究作为支撑`
- `该结论目前仅基于用户提供材料，尚未进行外部文献核验`

### Authenticity reminder
- a citation that resolves is not automatically a citation that safely supports the claim
- when in doubt, run a citation authenticity sentinel pass and downgrade confidence

## 3. Evidence Boundaries

Distinguish clearly between:
- user-provided facts
- assistant inferences from materials
- conventional academic phrasing scaffolds
- speculative suggestions for future revision

## 4. Style Polishing Rules

### Improve
- precision
- coherence
- sentence rhythm
- terminology consistency
- paragraph transitions
- rhetorical efficiency

### Avoid
- empty intensifiers
- repetitive transition words
- formulaic AI cadence
- faux-authoritative claims
- ornamental complexity that weakens meaning

## 5. De-AI-ification Rules

When reducing obvious AI tone:
- vary sentence openings
- remove hollow summary phrases
- replace generic evaluative words with discipline-specific descriptions
- keep concrete nouns and verbs stronger than vague abstractions
- preserve actual meaning rather than merely making the text sound “human”

## 6. Translation Rules

### Preserve
- meaning
- structure where required
- citations and numbering
- figure/table callouts
- terminology consistency

### Adapt only when requested
- style elevation
- journal-style recasting
- sentence splitting or merging
- rhetoric tightening

## 7. Statistical Interpretation Rules

When converting stats to prose:
- keep method and variable names explicit
- preserve sign, magnitude, and significance faithfully
- do not imply causal strength beyond the design
- distinguish objective reporting from interpretive commentary

## 8. Final Integrity Checklist

Before outputting academic prose, verify:
- every strong claim has visible support
- no pseudo-citations exist
- no journal-fit statement overreaches available evidence
- methods details are not embellished beyond input materials
- reviewer response claims correspond to actual edits or proposed edits
- translation did not distort meaning
- polishing did not introduce new facts
