# SciXZ prose policy: claim-forward writing

This policy merges two rule sets that were previously maintained outside SciXZ:

- **Set A — anti-defensive writing.** Remove caveats, disclaimers, hedges, apology framing, and self-limiting statements that do not improve accuracy.
- **Set B — the press-release principle.** A paper is a press conference, not a project summary, lab log, or self-audit.

They converge on one instruction: advance the claim directly, and let necessary precision appear once, in the section where it belongs.

Both are enforced by `scripts/audit_prose.py`, which reports the sentence, its section, a severity, and the repair move.

## The priority ladder

When material is unfavorable, work down this list and stop at the first move that resolves it:

1. **Delete** — if the sentence adds no evidence, scope, logic, or reader guidance.
2. **Narrow the claim** — cut the claim back to what the design supports.
3. **Switch the evaluation dimension** — report the metric, scenario, or comparator this work actually wins.
4. **Explain as a trade-off** — state the cost and the benefit side by side.
5. **Reorganise** — give the material the section where it carries weight, and take it out of the headline.
6. **Redefine the story** — only when the finding changes the paper's thesis.

State a weakness plainly only when it is unavoidable and truly affects the core conclusion.

## What to keep

A limitation is necessary when it affects:

- the validity of the claim;
- the interpretation of the evidence;
- the scope of application;
- the research design;
- the reader's ability to use the result correctly.

Write a necessary limitation **once**, in Methods, Discussion, or Limitations. Do not scatter it through the abstract, the introduction, contribution paragraphs, topic sentences, or the conclusion.

Methodological qualifiers that define the design are not defensive and must survive:

- "interpreted descriptively rather than causally" (an age–period–cohort model cannot do otherwise);
- "a predefined geographic grouping rather than a World Bank income classification" (a scope statement, in Limitations);
- "a normative welfare valuation rather than observed expenditure" (the definition of the metric itself);
- "for welfare valuation only" (states what a data source was used for).

## Detection checklist

Run through this list before accepting a draft, a revision, or a response letter:

1. unnecessary disclaimers;
2. repeated statements of what the text does not claim;
3. stacked hedges in one sentence;
4. caveats in high-impact positions (abstract, key messages, conclusion);
5. a paragraph that opens with a limitation;
6. negative framing where positive framing carries the same information;
7. explanations added only to prevent a hypothetical misreading;
8. self-undermining contribution statements;
9. reflexive "not X but Y", "rather than", "instead of";
10. redundant "however", "nevertheless", "although";
11. process chronology (what was tried, what was replaced);
12. a self-verdict drawn from one local observation;
13. an unwinnable contest staged against a better-suited comparator;
14. a result block that reports no number.

## Position rules

| Section | A caveat is |
|---|---|
| Abstract, Key Messages, Conclusions | a defect unless it changes the meaning of the headline number |
| Introduction | allowed only as the gap the paper fills |
| Results | allowed only where it bounds that specific estimate |
| Discussion | allowed as interpretation, once |
| Methods, Limitations | the correct place; keep it factual and specific |

## Repair moves

1. **Classify the sentence.** Is it a disclaimer, a scope condition, a real limitation, a conceptual contrast, an evidence-based qualification, or a redundant clarification?
2. **Delete disclaimers** that add no evidence, scope, logic, or guidance.
3. **Convert a defensive limitation into positive scope.** "The analysis focuses on urban governance cases from 2015 to 2023" replaces "We do not claim these cases are representative".
4. **Replace hedging with precision.** If uncertainty is real, name its source: "the design does not estimate population-level effects".
5. **Rebuild the paragraph around the main point**: topic sentence first, one job per paragraph, no repeated caveats, no apology framing.

## Patterns

### English

| Discouraged | Preferred |
|---|---|
| This paper does not claim that… | This paper examines… |
| This should not be taken to mean… | (delete; state what it does mean) |
| The goal is not X but Y. | The goal is Y. |
| Although this study has limitations… | (delete from abstract; keep in Limitations) |
| It is worth noting that… | (delete the frame, keep the fact) |
| These results may potentially suggest that X could possibly be associated with Y. | X is associated with Y in this analysis. |
| Absolute concordance is therefore expected by construction. | (delete; if structural, say it once in Methods) |
| Only modestly higher than the baseline. | Higher by 0.4 percentage points. |

Do not mechanically delete "may", "suggests", or "under these conditions". Decide from the evidence.

### Chinese

| 应避免 | 推荐 |
|---|---|
| 本文仅在两个数据集上做了初步尝试，只能提供有限参考 | 本文在两个数据集上评估该方法 |
| 遗憾的是，结果仍不理想 | 直接给结果与条件 |
| 需要指出的是 | 删除套语，直接陈述 |
| 仍有很大提升空间 | 具体说明缺哪个条件、影响哪条结论 |
| 众所周知 | 删除 |

Keep “初步”“可能”“提示” when the evidence warrants them. Do not add “显著” or “全面领先” merely to sound stronger.

## Press-release structure

- **Abstract**: important problem → gap in existing work → what this paper provides → strongest result with its estimate. Never open with implementation detail or process.
- **Introduction**: end on what the paper does, not on what it declines to do.
- **Each Results block** must carry a duty — prove effectiveness, prove the mechanism, prove scenario value, or rule out an alternative explanation — and must report the number that discharges it.
- **Conclusion**: reinforce the takeaway. No sudden self-negation in the final paragraph.
- **No process chronology.** Keep the final standing logic: why the problem matters → why existing methods fall short → what this paper provides → how the evidence supports it.

## How the script maps to this policy

`scripts/audit_prose.py` emits one finding per match:

| Rule id | Meaning | Default severity |
|---|---|---|
| `disclaimer` | what the paper does not claim, do, or intend | P1 |
| `self_weakening` | minimisers and labels applied to the paper's own result | P1 |
| `apology` | regret framing | P1 |
| `self_verdict` | a local observation turned into a verdict on the method | P1 |
| `contest_lost` | a comparison the paper cannot win | P1 |
| `reflexive_contrast` | "rather than" / "instead of" / "not X but Y" | P3 |
| `preemptive` | explaining away an apparent inconsistency | P2 |
| `cannot` | explicit inability verbs | P2 |
| `process` | chronology of attempts | P1 |
| `stacked_hedge` | two or more hedges in one sentence | P2 |
| `caveat_in_high_impact` | a caveat sentence in abstract, key messages, or conclusion | P1 |
| `result_without_number` | a Results block with no estimate | P3 |
| `abstract_without_headline` | an abstract with no quantified result | P1 |
| `zh_defensive` | Chinese self-deprecation, admonitory tone, hedging | P1–P2 |

Severity is raised when the sentence sits in a high-impact section and lowered inside Limitations.

## Verification boundary

The script is a detector, not a rewriter. Sentence-level matching cannot decide whether a contrast carries information or whether a hedge is warranted by the design. Every `P1` must be read in context before it is acted on; `P3` findings are informational and are expected to remain in a finished manuscript (for example, "interpreted descriptively rather than causally" in Methods).

A passing run proves only that the listed patterns are absent. It does not prove that the paper has a clear headline, that every Results block carries a duty, or that the conclusion reinforces the takeaway. Those require reading the abstract, the introduction, and the conclusion as a reader would.
