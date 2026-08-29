---
name: ddaigc-humanizer-stack
description: Use when the user wants a Chinese academic or technical document to go through strict `ddaigc` round-tracked de-AIGC first and then receive a final humanization pass with `humanizer-zh` or `humanizer`. Trigger this skill when the request combines phrases like `降AIGC`, `去AI味`, `保留术语和结构`, `最后再自然一点`, `更像中文母语者写的`, or asks to fuse `ddaigc` with `humanizer-zh` / `humanizer` rather than using any one of them alone.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
---

# DDAIGC Humanizer Stack

This is an orchestration skill. It does not replace `ddaigc`, `humanizer-zh`, or `humanizer`.

Its job is to decide the safe execution order when the user wants both:

- strict Chinese academic de-AIGC control with round tracking
- a later humanization pass that makes the text sound less assembled and more native

## Core Rule

`ddaigc` always owns the round-tracked stage.

Do not let `humanizer-zh` or `humanizer` break `ddaigc`'s state machine.
Do not merge the three `ddaigc` rounds into one pass.
Do not run broad humanization first and then pretend the document is still in a clean `ddaigc` round state.

## Safe Execution Order

1. Check whether the task is a real `ddaigc` task.
   - Chinese thesis, paper, report, proposal, or technical document
   - user explicitly wants multi-round de-AIGC or round continuation
   - the document must preserve terms, numbering, citations, and structure

2. If yes, inspect the `ddaigc` round state first.
   - If the document has not finished round 1/2/3, route to `ddaigc` for the current due round only.
   - If the document has already finished all required `ddaigc` rounds, only then consider a humanization pass.

3. Choose the humanization layer after `ddaigc`.
   - Use `humanizer-zh` for Chinese-native rhythm, anti-translation-cadence cleanup, and final tone smoothing.
   - Use `humanizer` only for English or mixed-language segments that should retain their English voice.

4. Keep the humanization pass narrow.
   - Prefer sentence-level or paragraph-level cleanup on high-risk passages.
   - Avoid touching formulas, citations, numbered headings, table titles, variable names, and technical labels unless they are clearly prose.

## Routing Decisions

### Route to `ddaigc` only

Use `ddaigc` alone when:

- the document is still in rounds 1-3
- the user asks to continue the next round
- record continuity matters more than style flourish
- the text is still obviously at the de-AIGC stage, not the final smoothing stage

### Route to `humanizer-zh` after `ddaigc`

Use `humanizer-zh` after `ddaigc` when:

- the Chinese text has already been through the required `ddaigc` rounds
- the user wants it to feel more like native Chinese writing
- the remaining problem is translation cadence, formulaic rhythm, or assembled-sounding prose

### Route to `humanizer` after `ddaigc`

Use `humanizer` after `ddaigc` when:

- there are English-heavy sections
- the user wants English paragraphs to sound less templated
- the Chinese round-tracked work is already complete and the English cleanup is the only remaining pass

## Hard Constraints

- Never skip `ddaigc` rounds.
- Never overwrite or ignore `ddaigc` record continuity.
- Never let humanization add facts, references, numbers, examples, or claims.
- Never let humanization flatten the original academic register into casual internet prose.
- Never run `humanizer-zh` and `humanizer` in parallel over the same paragraph.
- Never claim the full fusion was executed if only the current `ddaigc` round was completed.

## Output Pattern

When responding, be explicit about which stage the document is in:

- `Current stage`: `ddaigc round 1/2/3` or `post-ddaigc humanization`
- `This pass`: what was actually done now
- `Next safe pass`: the next legal step in the stack

Examples:

- `Current stage: ddaigc round 2. This pass only completes round 2. Next safe pass: ddaigc round 3.`
- `Current stage: post-ddaigc humanization. This pass uses humanizer-zh for final Chinese-native smoothing.`

## Practical Principle

Think of this stack as:

- `ddaigc` = compliance and de-template pipeline
- `humanizer-zh` = Chinese-native rhythm repair
- `humanizer` = English rhythm repair

The stack is sequential, not blended.
