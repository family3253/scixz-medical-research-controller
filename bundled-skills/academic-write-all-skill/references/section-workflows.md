# Section Workflows

## Purpose
This file contains the heavy reference rules for drafting and revising academic manuscript sections.

## 1. Introduction Workflow

### Use when
- the paper topic is known but the narrative opening is weak
- the user has background notes, references, or partial methods/results
- the introduction needs to be rebuilt around a sharper gap

### Canonical structure
1. background anchor hook
2. literature turn and unresolved gap
3. contribution focus / purpose statement
4. structure roadmap
5. funnel QA

### Introduction Funnel Workflow

Treat introduction drafting as one integrated funnel, not a pile of adjacent microtasks.

Default order:

1. **Background anchor hook**
   - open with a concrete fact, policy shift, empirical pattern, or established scholarly tension
   - do not open with stale fillers such as `近年来`, `随着科技的发展`, `现如今`, or other generic time-transition cliches
   - prefer intellectual tension over emotional hype
   - if the user explicitly wants only the opening paragraph, return two options:
     - `选项A：事实/数据驱动型 Hook`
     - `选项B：理论悖论型 Hook`
   - target: within about 150 Chinese characters unless the user requests otherwise

2. **Literature turn and unresolved gap**
   - move from what the field already knows to what it still fails to explain
   - state the gap thematically, not as an author-by-author list
   - use precise gap verbs such as `忽视了`, `未能解释`, `仍然是碎片化的`, `尚未澄清`
   - if the user only supplies rough literature notes, synthesize the gap cautiously and mark unsupported claims with `[待核实文献]`
   - target: about 100 Chinese characters when the user wants a compact gap paragraph

3. **Contribution focus / purpose statement**
   - connect the study aim directly to the just-stated gap
   - default opening pattern when writing this paragraph directly:
     - `为了弥补这一研究空白，本研究旨在……`
   - refuse empty promises
   - name the concrete variables, method, dataset, population, or theoretical frame whenever visible
   - state why the study matters without inflating novelty

4. **Structure roadmap**
   - give the reader a fast-scanning roadmap of the remaining paper
   - focus on section order, not on re-describing findings
   - keep sentences short and purely structural
   - standard pattern:
     - `本文的其余部分结构如下：第二节……第三节……`

5. **Funnel QA**
   - check whether the assembled introduction actually narrows from macro context to exact study purpose
   - inspect transitions between background -> literature -> gap -> contribution -> structure
   - diagnose logical jumps, duplicated claims, stale filler, and residual machine-like padding
   - do not rewrite the whole introduction in this QA step unless the user explicitly asks for a rewrite after diagnosis
   - instead provide:
     - broken transition location
     - why the transition fails
     - 2-3 concrete bridging phrases or sentence-direction suggestions

### Hard rules
- every paragraph must have a distinct rhetorical job
- move from broad field to exact question
- avoid fake comprehensiveness (“many studies”, “numerous scholars”) without visible support
- do not spoil detailed results in the final paragraph
- if the venue is journal-specific, align with its tone and scope
- do not let hook-writing drift into sloganized scene-setting
- do not let gap-writing become an author roll call
- do not let purpose-writing claim importance without naming the actual method or analytic object
- do not let structure-roadmap paragraphs repeat findings or sell novelty
- do not let QA silently become a full rewrite pass

### Typical input bundle
- topic or working title
- target journal or discipline
- 3-8 core references or evidence summary
- one-sentence gap statement
- method and data summary
- innovation claim
- later-section outline if a structure roadmap is needed

### Native ownership vs specialist fallback

Keep `Introduction Workflow` as the primary owner when the user wants a full introduction or any contiguous subset of the funnel.

Use narrower specialist paths only when the user explicitly isolates one bottleneck:

- `literature-gap-dialogue-validator` for gap audit only
- `logic-skeleton-rewriter` for transition repair only
- `humanizer-zh` / `humanizer` for terminal anti-AI cleanup only

Do not split a normal introduction-writing request across several co-equal skills.

### Missing-info fallback
If references are incomplete:
- draft the structure anyway
- mark unsupported claims with `[待核实文献]`
- do not fabricate author-year citations

## 2. Methods Workflow

### Use when
- the user has data, figures, legends, analysis outputs, or procedure notes
- the user needs a methods section ready for manuscript insertion

### Canonical structure
1. study design
2. setting / cohort / corpus / sample source
3. data collection or experimental procedure
4. variables / materials / instruments / measures
5. preprocessing / quality control
6. statistical or analytic methods
7. ethics / approval / registration if relevant

### Hard rules
- never invent parameter values, dosages, sample sizes, catalog numbers, or software versions
- infer subsection headings from available evidence, but mark missing technical details explicitly
- separate what was done from why it was done
- keep method reproducibility higher than stylistic elegance
- if tables, figure legends, or analysis scripts reveal procedure details, use them carefully as evidence for wording, but do not infer hidden settings as fact

### Recommended placeholder style
- `[待补：样本量]`
- `[待补：试剂货号]`
- `[待核实：软件版本]`
- `[待补：伦理审批编号]`

## 3. Results Workflow

### Use when
- there are tables, figure legends, statistical outputs, key findings, or hypothesis results

### Canonical structure
- organize by hypothesis, figure order, model family, or research question
- start each block with the tested objective
- report key values faithfully
- reserve interpretation for the discussion unless a brief orienting sentence is unavoidable

### Hard rules
- no inflated language (“remarkable”, “groundbreaking”) unless user explicitly wants promotional tone
- keep statistical wording aligned with actual evidence
- if only summary findings are available, say so and avoid pretending to see the full raw output

### Figure / table driven writing protocol
When figures, legends, tables, or stats outputs are the main evidence source:
1. identify the organizing order: hypothesis, figure order, table order, or research question
2. extract only visible facts first: variable names, groups, directions, magnitudes, uncertainty markers, test labels, units
3. write one orienting sentence per block to tell the reader what comparison or test is being reported
4. report the result faithfully in prose without adding interpretation that belongs in Discussion
5. if a number, unit, sample size, p-value, CI, or subgroup label is not visible, mark `[待核实]` instead of guessing

### Recommended result sentence pattern
- orienting sentence: what was compared or tested
- primary finding sentence: the main direction / contrast / estimate
- secondary detail sentence: supporting statistics or subgroup details if visible
- figure/table anchor sentence: `As shown in Figure X` / `Table X summarizes ...` when appropriate

### Do / do not for result prose from artifacts
Do:
- follow figure/table order when that is the clearest narrative order
- convert legend language into readable prose while preserving meaning
- state contrasts explicitly (`higher than`, `lower than`, `no clear difference`, `mixed pattern`)
- distinguish descriptive results from inferential statistics

Do not:
- infer significance from a visual trend alone if the statistical test is not shown
- explain mechanisms here; move that to Discussion
- hide uncertainty, missing labels, or invisible denominators
- repeat every number in the table when the pattern can be summarized faithfully

## 4. Discussion Workflow

### Use when
- the results are already reasonably stable
- the user needs interpretation, literature comparison, limitations, and implications

### Canonical structure
1. restate study aim and core findings
2. interpret the main findings
3. compare with prior literature
4. explain consistencies or discrepancies
5. limitations and their consequences
6. implications and future work

### Common high-quality pattern
- finding -> interpretation -> literature anchor -> implication -> caution

### Hard rules
- discussion is not a second results section
- do not merely repeat figure-level descriptions
- do not overclaim causality if design is observational
- limitations should be honest but proportionate
- future work should be specific, not ceremonial

### Bridge from Results to Discussion
If Results were drafted from figures/tables, Discussion should:
- start from the already established result blocks rather than redescribing every panel
- explain meaning, comparison with literature, and implications
- explicitly distinguish visual pattern from supported inference

## 5. Abstract Workflow

### Use when
- the manuscript body or at least the core result logic is already known

### Canonical structure
1. problem / background
2. objective
3. methods
4. key findings
5. conclusion / significance

### Hard rules
- no new claims absent from the manuscript
- no fake citations in abstract
- if target journal has structured abstract rules, follow them
- keep results numerically anchored when appropriate

### Paper-production variants
Choose the narrowest useful abstract task:
- `abstract-first draft` — when the body logic is already stable enough to summarize
- `abstract rewrite` — when the manuscript exists but the abstract is weak, generic, or misaligned
- `bilingual abstract pair` — when Chinese + English abstracts must align conceptually without becoming mechanical translation

### Bilingual abstract rule
If the workflow is bilingual, preserve alignment of problem, objective, methods, findings, and conclusion across both language versions, but allow natural wording differences. Do not force literal sentence-by-sentence translation.

### Thesis abstract note
For a master's thesis or dissertation abstract, preserve the same logic but allow slightly more context-setting than in a journal abstract when institutional rules require it.

## 6. Thesis / Dissertation Chapter Workflow

### Use when
- the user is writing a master's thesis, dissertation, or chapter-based graduate manuscript
- the output needs chapter boundaries, wrapper text, or thesis-level transitions
- the user is converting papers, figures, or analysis outputs into a thesis chapter

### Typical chapter families
1. thesis introduction / background chapter
2. literature review chapter
3. methods chapter
4. findings / results chapter
5. general discussion chapter
6. conclusion / implications / future work chapter

### Core rules
- a thesis chapter must have a clear chapter job, not just copied paper prose
- explain cross-chapter transitions explicitly
- allow broader context in introduction and discussion chapters than most journals would
- keep findings/results chapters evidence-led and non-interpretive where required by the discipline
- if the thesis is article-based, add wrapper text that explains what each paper/chapter contributes to the whole thesis argument

### Common thesis mistake patterns
- repeating the same background in every chapter
- copying a journal article into a thesis without wrapper transitions
- merging findings and discussion unintentionally because the thesis chapter feels long
- forgetting thesis-specific front matter, summary, or general conclusion requirements

### Thesis-level general discussion / conclusion synthesis
Use when the thesis has multiple result chapters, multiple studies, or article-based components that must be synthesized at the thesis level.

#### Core job
- do not merely concatenate per-chapter discussions
- synthesize what the whole thesis now shows that no single chapter shows alone
- restate the overarching research problem and answer it at thesis scale
- explain how chapters/studies connect, reinforce, qualify, or contradict one another

#### Recommended order
1. restate the overall thesis question / objective
2. synthesize the cross-chapter findings in 3-6 thesis-level claims
3. show how each claim is supported by one or more chapters / studies / figures / tables
4. explain theoretical, methodological, or practical implications at thesis scale
5. discuss thesis-level limitations, including boundaries shared across chapters
6. end with future work or application directions grounded in the synthesized evidence

#### Hard rules
- avoid chapter-by-chapter summary fatigue
- do not introduce new evidence absent from earlier chapters
- distinguish thesis-level synthesis from per-study interpretation
- acknowledge contradictions across chapters instead of smoothing them over
- keep implications proportional to the total evidence base, not the strongest single chapter

#### Useful output artifact
Before drafting, it is often useful to create a `chapter-to-thesis synthesis table` with:
- chapter / study
- its main finding
- what larger thesis claim it supports
- any limitation or contradiction it introduces
- where it should appear in the general discussion or conclusion

## 6A. China Pharmaceutical University Thesis / Dissertation Notes

Use this sublayer when the user explicitly names China Pharmaceutical University, Chinese school template constraints, or local CPU thesis requirement files.

### Local authority order

If local source files conflict, use this priority:

1. `<PRIVATE_WORKSPACE>\参考\论文格式.doc`
2. official CPU graduate-thesis requirement documents and school-issued template files
3. generic AWAS thesis defaults

### Stable local constraints already visible

- CPU thesis packages should be treated as having stronger front-matter requirements than ordinary paper-like drafts
- common components include: cover, originality statement, copyright authorization, contents, Chinese abstract, English abstract, optional abbreviation list, main text, references, publication list during degree period, acknowledgements
- CPU thesis body should default to simplified Chinese except for school-allowed English components
- abstract formatting, pagination split, and chapter-body sequencing should be checked against the local CPU source files before output is presented as compliant
- local CPU rules may prioritize thesis-specific reference and layout conventions over journal-style habits
- when local CPU files disagree, `<PRIVATE_WORKSPACE>\参考\论文格式.doc` is the controlling authority
- the current local project should default to the **CPU professional-master's route**, not the 同等学历 route, unless the user explicitly says otherwise
- the current local evidence set shows that CPU's professional-master and 同等学历 template routes should not be silently merged at the cover/front-matter level

### Writing implication

- when drafting CPU thesis content, prefer chapter-role clarity and school-format compliance over journal-like compactness
- when converting a CPU thesis into a paper, explicitly treat that as a second-stage conversion, not as the native thesis mode
- for CPU 专硕 tasks, keep the professional-master template and official requirement logic aligned first, and treat 同等学历 templates only as subordinate references when the user is actually in that track

## 6. Title / Keywords / Highlights Workflow

### Title rules
- specific and searchable
- reflect topic and contribution
- avoid hype words unless standard in the field
- avoid claiming more than the study shows

### Keyword rules
- balance precision and discoverability
- prefer field-standard terms
- include method/population/context when they materially define the paper

### Highlights rules
- each highlight should capture one contribution or finding
- avoid full-sentence fluff
- maintain factual traceability to the manuscript body

## 7. Review-Article Workflow

### Use when
- the user is writing a narrative review, scoping review, evidence map, umbrella review, or theory review

### Key decision points
- what review type is this?
- is the output evidence-mapping or strong-claim synthesis?
- how reproducible must the search and screening process be?
- what framework best organizes the body: time, topic, method, application, dispute, mechanism?

### Strong recommendation
For review writing, do not start from prose. Start from:
1. type of review
2. search and inclusion logic
3. framework selection
4. evidence grouping
5. claim-to-evidence map
