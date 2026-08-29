# PDF and Image Reading Playbook

## Purpose

This playbook makes PDF and image reading operational rather than aspirational.
Use it when review, meta-analysis, thesis drafting, or prediction-model appraisal depends on information that lives in:

- article PDFs
- supplementary PDFs
- appendix PDFs
- scanned pages
- figure panels
- image-based tables
- screenshots pasted from papers or portals

The goal is not merely to `see` the file.
The goal is to extract evidence in a way that remains traceable and reusable downstream.

## Core Rule

For evidence-heavy work, reading quality follows this ladder:

1. file triage
2. extraction path choice
3. targeted extraction
4. page-level verification
5. structured handoff into extraction tables

If a value cannot survive that ladder, it is not yet strong enough for confident prose.

## 1. File Triage

Before reading, classify the file into one of these buckets:

### A. Text PDF
- selectable text exists
- standard extraction usually works
- still verify tables and figure captions separately if they matter

### B. Layout-heavy PDF
- multi-column text
- dense tables
- appendix-style formatting
- figure-caption-heavy pages

### C. Supplement-heavy PDF
- critical details live in supplementary tables or appendices
- common for prediction models: formulae, coefficients, thresholds, hyperparameters, calibration, subgroup performance, extra validation results

### D. Scan / image PDF
- pages behave like images
- OCR is required

### E. Mixed PDF
- some pages are selectable text
- some tables / figures / supplements are image-like
- requires combined extraction and OCR

## 2. Extraction Path Choice

Choose the strongest honest path:

- text PDF -> text extraction first
- layout-heavy PDF -> layout-aware and table-aware extraction
- supplement-heavy PDF -> separate supplement extraction, not merged blindly into main text
- scan / image PDF -> OCR-first workflow
- mixed PDF -> text extraction plus targeted OCR for hard pages or regions

Do not use quick visual inspection as the final evidence source for exact metrics, thresholds, or model details.

## 3. Targeted Extraction Workflow

### Minimal general workflow
1. count pages and inspect document type
2. extract body text
3. identify pages with tables / figures / supplements
4. re-extract those pages specifically
5. record page-level provenance for anything that enters an evidence table

### Table-heavy workflow
1. isolate the relevant table page(s)
2. extract table content separately from body text
3. normalize rows / columns into the extraction table
4. verify that units, subgroup labels, and time windows were preserved

### Figure-heavy workflow
1. identify whether the figure contains text, plotted metrics, or only qualitative trends
2. if the figure caption contains the usable evidence, extract caption text and preserve page reference
3. if the plotted value itself is required but not numerically visible, mark it as not directly extractable rather than guessing

### Supplement-heavy workflow
1. treat main article and supplement as separate sources in the reading stage
2. extract supplement-only metrics separately
3. preserve provenance such as `main article` vs `supplementary PDF`
4. merge only after provenance has been recorded in the structured extraction table

## 4. OCR Escalation Rules

Escalate to OCR when:

- the PDF has no selectable text
- tables are image-based
- appendix pages are scanned
- screenshots or pasted figures contain the only visible metric labels
- text extraction produces empty or obviously broken content

OCR output is provisional until checked against the image region or page source.

## 5. Prediction-Model Review / Meta Bias

Prediction-model papers often hide the most important extraction targets outside the narrative body.

Check these locations before calling a field `not reported`:

- supplementary tables
- model formula appendix
- coefficient tables
- calibration figure captions
- decision-curve appendices
- extended methods sections
- online supplement PDFs

Common hidden targets:
- training / validation / test split details
- hyperparameter tuning dataset role
- external validation implementation details
- recalibration or model updating details
- confidence intervals around performance metrics
- subgroup performance results

## 6. Page-Level Verification Rule

For every value likely to enter a review table or meta extraction register, preserve at least one provenance field such as:

- page number
- table number
- figure number
- appendix label
- caption reference

If the value came from a supplement, preserve that explicitly.

Examples:
- `main PDF p.7 Table 2`
- `supplement PDF p.3 Appendix Table S4`
- `main PDF p.12 Figure 3 caption`

## 7. What Counts as Verified

Treat a value as verified only when:

- it was extracted from a reproducible path
- the wording or number can be tied back to a page-level source
- the metric meaning is clear enough to place in the right field

Treat a value as provisional when:

- OCR confidence is weak
- the page is image-heavy and the extracted text is noisy
- the metric appears only as a plotted point with no numeric label
- the wording is ambiguous (`validation cohort`, `test cohort`) and the underlying split is unclear

## 8. Handoff Into Structured Extraction

Do not stop at extracted notes.
Move extracted evidence into the appropriate structured artifact:

- `evidence_extraction.csv`
- `prediction_model_evidence_matrix.csv`
- split-aware prediction-model meta extraction table
- appraisal checklist or audit register

The handoff should preserve provenance rather than discarding it.

## 9. Safe Language

Preferred phrases:
- `The value was extracted from the supplementary PDF and should be interpreted with that provenance in mind.`
- `The split label is reported as 'validation cohort' in the paper; external status should not be assumed without further clarification.`
- `The calibration result appears only in the figure caption and has been preserved with page-level trace-back.`
- `The appendix contains additional validation results not visible in the main text.`

Avoid:
- `not reported` before checking supplements
- `external validation` when the paper only says `test cohort`
- exact numeric claims sourced only from a quick-look image summary
