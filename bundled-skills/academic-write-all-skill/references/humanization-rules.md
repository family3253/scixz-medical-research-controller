# Humanization Rules

## Purpose
This file adapts the strongest useful parts of the local `humanizer` skill into AWAS's academic polishing layer.

The goal is **not** to make academic prose casual or theatrical. The goal is to remove obvious machine-written patterns while preserving scholarly precision.

## Use when
- a passage sounds generic, inflated, or suspiciously LLM-like
- the user asks to reduce AI tone
- the text is technically correct but stylistically sterile
- polishing has made the prose smoother but less human

## Patterns to detect and reduce

### 1. Inflated significance language
Watch for:
- pivotal
- crucial in the evolving landscape
- testament to
- underscores the profound importance of
- marks a significant turning point

Preferred fix:
- replace symbolic or promotional phrasing with direct factual description

### 2. Promotional tone disguised as academic tone
Watch for:
- vibrant
- rich and dynamic
- profound implications
- transformative potential
- groundbreaking unless truly justified

Preferred fix:
- describe the actual contribution and boundary, not marketing-style significance

### 3. Vague attribution
Watch for:
- studies have shown
- it is widely believed
- scholars agree
- evidence suggests, when no evidence is visible

Preferred fix:
- anchor the claim to visible evidence
- or mark it `[待核实文献]`

### 4. Formulaic AI cadence
Watch for:
- repeated sentence openings
- repeated transition phrases
- every sentence equally balanced and polished
- repetitive summary phrases like "overall," "in conclusion," "it is worth noting"

Preferred fix:
- vary sentence rhythm
- cut empty transitions
- preserve only transitions that do real logical work

### 5. Hollow abstraction
Watch for:
- broad conceptual nouns with no operational meaning
- empty phrases like "offers valuable insights" or "has important significance" without saying what changed

Preferred fix:
- replace abstract praise with concrete consequence, mechanism, or scope

### 6. Over-smoothed neutrality
Sometimes text is not obviously AI because of bad words, but because it has no pulse.

Preferred fix in academic context:
- use sharper verbs
- tighten claims
- let the argument sound deliberate rather than padded
- preserve discipline-specific voice instead of generic journalese

## Humanization rules for academic text

1. **Precision beats flourish**
2. **Specificity beats grandiosity**
3. **Real evidence beats generic authority tone**
4. **Controlled variation beats perfectly even rhythm**
5. **Scholarly voice beats content-farm polish**

## Safe transformations

### Good
- remove empty hype
- vary syntax
- replace vague attribution with explicit support language
- tighten paragraph openings
- replace repeated generic transitions
- sharpen verbs and nouns

### Dangerous
- changing the claim strength
- removing hedging where the evidence is genuinely uncertain
- making scientific prose sound conversational when the venue requires formal restraint
- inserting personality where neutrality is required

## Recommended fallback phrases
Use these instead of fake certainty:
- `the available evidence suggests`
- `within the scope of the present data`
- `the current results indicate`
- `this interpretation remains provisional`
- `further verification is needed`

## Quick anti-AI pass

Before returning a polished passage, ask internally:
1. What still makes this sound obviously AI-generated?
2. Are there inflated symbolic or promotional phrases left?
3. Are there vague attributions with no source?
4. Is the rhythm too uniform?
5. Did polishing accidentally make the prose less precise?

Then revise once more.
