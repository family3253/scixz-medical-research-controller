---
name: paper-by-paper-prediction-review
description: >-
  Use when the user wants to process prediction-model papers one by one with a
  strict evidence workflow: first decide which model units to retain, then
  extract from original PDF/DOCX plus supplements, run dual extraction and dual
  scoring when possible, resolve every field as filled or explicitly
  未记录/无数据/不适用, and only close a paper after evidence and scoring are
  genuinely settled. Make sure to use this whenever the user is building or
  repairing a paper collection table, reconciling model units, closing papers
  sequentially, or asks for a prediction-model review pipeline that must not
  rely on vague summaries.
---

# paper-by-paper-prediction-review

## Overview

This skill captures a paper-by-paper evidence workflow for prediction-model review projects.

Its core idea is simple:

1. **the user chooses retained model units**
2. **the assistant extracts from source files first**
3. **dual extraction / dual scoring happen when infrastructure allows**
4. **all fields must be resolved before closure**
5. **Excel is a display layer, not the only source of truth**

Use this skill when the user is curating a structured evidence base paper by paper and wants strict control over retention, scoring, missingness, and closure.

## When To Use

Use this skill whenever the user says or implies any of the following:

- “逐篇处理 / 一篇一篇核对”
- “先让我决定保留哪些模型”
- “做数据收集表 / extraction workbook / collection workbook”
- “把 missing 字段标成未记录 / 无数据 / 不适用”
- “双提取 / 双评分 / 仲裁”
- “不要直接信底板，要先读原文和补充材料”
- “先收口前面的 paper，再开下一篇”
- “traditional vs machine learning”
- “prediction model review / risk score review / nomogram review”

## Canonical Ordering Rule

Use the bracketed number in the original source filename as the canonical paper order.

Examples:
- `[1]...pdf`
- `[2078]...pdf`
- `[7151]...pdf`

Do not silently switch to another numbering system.

## Source Hierarchy

Always follow this evidence order:

1. original PDF / DOCX / thesis file
2. supplementary PDF / DOCX / ZIP contents
3. existing extraction workbook rows
4. staged JSON summaries / provenance files

The workbook is never the only truth source.

## Project-Specific Working Paths

When this skill is used in the current MDR-GNB project, default to these paths unless the user explicitly overrides them:

- **primary collection workbook to fill**:
  - `D:\下载\MDR_GNB_detailed_data_collection_with_scoring_v2.xlsx`
- **original source folder**:
  - `<PRIVATE_PROJECT_WORKSPACE>\python\pdf_downloads2\纳入`
- **supplement folder**:
  - `<PRIVATE_PROJECT_WORKSPACE>\python\pdf_downloads2\纳入\补充材料`
- **working display / queue workbook**:
  - `<PRIVATE_PROJECT_WORKSPACE>\MDR_master_collection_split_aware.xlsx`
- **stable JSON staging directory**:
  - `<PRIVATE_PROJECT_WORKSPACE>`

For this project, the preferred human-facing collection target is the workbook under `D:\下载\...`, while JSON files remain the stability layer during heavy processing.

Before extracting a new paper in this project, inspect the target workbook structure first so the extraction follows the collection schema rather than improvising a new one.

## Front-Loop Rule

The user decides retained model units.

For each paper:
1. identify all distinct model units
2. list model name, model type, outcome, dataset structure, and key performance
3. let the user choose which units to retain
4. only then proceed to extraction and scoring

Do not finalize model retention without the user’s decision.

## Model-Selection Rules

### Traditional vs machine learning

- **Traditional model** = non-ML algorithm model
  - logistic regression
  - score / nomogram
  - classical decision rule
- **Machine learning model** = RF / GBM / XGBoost / SVM / neural network / similar ML pipeline models

### Main-model rule

If a paper explicitly identifies a main / final / best / selected model, prefer it.
If not, present the candidate models clearly and let the user decide.

### Comparator rule

When the user wants traditional-vs-ML comparison, retain:
- one traditional model
- one ML model

unless the user explicitly wants a wider menu.

### Validation subtype rule

- same hospital, different time period = **temporal external validation**
- different hospitals / centers = **geographic external validation**
- simple split / bootstrap / cross-validation = **internal validation**

Keep these distinctions explicit in the collection sheets.

### Scope rule for this MDR-GNB project

The default inclusion scope is:
- **MDR-GNB**
- accepted narrower organism/end-point subsets that still belong to the MDR-GNB family, such as relevant CRE / CPE / CR-GNB / ESBL-E style subgroups when the user confirms they belong in scope

Do not silently retain broader or adjacent targets just because they co-occur in the same paper.
Examples that need explicit caution:
- overly broad CRO / CR-GNB groupings
- VRE / MRSA or other non-GNB targets
- prognosis-only sections that are not prediction-model units

When a paper mixes in-scope and out-of-scope outcomes, keep only the in-scope units in the primary collection workbook and explain exclusions explicitly.

See `references/model-selection-and-validation.md`.

## Required Workflow

### Phase 1: Per-paper model menu

For the current paper, produce a menu that includes:
- model/unit name
- model type
- exact outcome
- organism / resistance scope
- setting / department
- dataset or split structure
- key available performance

### Phase 2: Extraction

Preferred pattern:
- extractor A
- extractor B
- adjudicator if needed

If the environment blocks parallel descendants, use a source-based foreground fallback.
Do not pretend dual extraction happened if it did not.

Before extracting, learn the sheet structure and key headers of the target collection workbook `D:\下载\MDR_GNB_detailed_data_collection_with_scoring_v2.xlsx`. Extraction should populate the workbook’s existing logic, not invent a new schema on the fly.

### Phase 3: Scoring

Preferred pattern:
- TRIPOD scorer A + B
- PROBAST scorer A + B
- adjudicator if needed

If a scorer fails:
- retry it
- do not count failure as evidence
- if retry remains blocked, record explicit source-based fallback provenance instead of pretending the scorer existed

### Phase 4: Field-completion discipline

Every tracked field must end as one of:
- filled
- 未记录
- 无数据
- 不适用

No paper can be closed while any tracked field remains pending.

### Phase 5: Closure

Only close a paper when:
- retained models are fixed
- source extraction is complete enough for all tracked fields
- scoring is truly written back to `TRIPOD_WIDE` / `PROBAST_DEV_WIDE` / `PROBAST_EVAL_WIDE`, **or** a source-based fallback is explicitly documented for the missing scorer path
- all pending fields are resolved
- stable final files are written

See `references/closure-and-writeback.md`.

## Collection Workbook Shape

Default collection-friendly workbook structure:

- `Study_Detail`
- `Outcome_Definition`
- `Dataset_Splits`
- `Model_Selected`
- `Performance_Selected`
- `Method_Flags_01`
- `Validation_Subtype_Audit`
- `TRIPOD_WIDE`
- `PROBAST_DEV_WIDE`
- `PROBAST_EVAL_WIDE`
- `Paper_Status`

This mirrors the user’s preferred workflow better than summary-only sheets.

For the current project, the preferred collection workbook already exists and should be treated as the primary collection target:

- `D:\下载\MDR_GNB_detailed_data_collection_with_scoring_v2.xlsx`

The expected core sheets are:

- `Paper_Tracking_文献追踪`
- `Study_Detail_研究层`
- `Outcome_Definition_结局层`
- `Dataset_Splits_数据集层`
- `Model_Selected_模型层`
- `Performance_Selected_性能层`
- `Method_Flags_01`
- `Validation_Subtype_Audit`
- `TRIPOD_AI_评分` or equivalent wide scoring sheet
- `PROBAST_AI_开发`
- `PROBAST_AI_验证`

If a parallel working workbook exists, use it only as a staging/display helper. The target workbook to keep filling for the user remains the one under `D:\下载\...`.

## Stable Storage Rule

Use JSON / CSV as the stable staging layer when Excel becomes fragile under repeated writes.

Recommended paper-level files:
- `paperX_model_choice.json`
- `paperX_stage_snapshot.json`
- `paperX_final_summary.json`
- `paperX_scoring_provenance.json`

Excel remains the human-facing collection / display layer.

## Thesis-Specific Rule

For thesis sources:
- do not assume the whole thesis is one prediction-model paper
- isolate the exact retained section(s)
- distinguish prediction-model evidence from prognosis / descriptive / microbiology background sections

## Output Discipline

When presenting a model menu to the user, always include:
- what the model is
- what outcome it predicts
- what dataset structure supports it
- whether it is traditional or ML
- what the best available performance is
- what you recommend and why

When reporting progress after the user has decided the model set, do not ask whether to continue. Continue automatically.

## References

- `references/model-selection-and-validation.md`
- `references/closure-and-writeback.md`
