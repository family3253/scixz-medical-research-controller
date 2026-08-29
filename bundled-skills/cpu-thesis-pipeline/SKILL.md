---
name: cpu-thesis-pipeline
description: Use when the user wants an end-to-end China Pharmaceutical University thesis workflow that combines local AntiAIGC review, baibaiAIGC multi-round academic prose processing, and AWAS-style final thesis scoring, especially when they provide a manuscript file and ask for splitting, review, revision, merge, and final assessment. Treat mentions of cpu-thesis-pipeline as referring to this skill.
---

# CPU Thesis Pipeline

## Purpose

Use this skill to orchestrate a local academic manuscript workflow across three layers:

- `AntiAIGC` diagnoses template-like academic prose and provides segment-level risk signals.
- `baibaiAIGC` performs controlled multi-round academic prose processing and keeps intermediate files.
- `AWAS` governs final academic integrity review, China Pharmaceutical University thesis scoring, and human-review priorities.

The workflow is for academic quality control and template-expression risk review. Do not use it as an automated detector-evasion loop or as a promise that any commercial AIGC detector will return a lower score.

## Required Local Projects

Expected default locations:

- `<PRIVATE_THESIS_WORKSPACE>\AntiAIGC`
- `<PRIVATE_THESIS_WORKSPACE>\baibaiAIGC`

Expected default services:

- `AntiAIGC` backend: `http://127.0.0.1:8000`
- `baibaiAIGC` backend: `http://127.0.0.1:18765`

Before running the pipeline, verify both backends are reachable:

```powershell
$env:SystemRoot='C:\Windows'
$env:windir='C:\Windows'
Invoke-WebRequest http://127.0.0.1:8000/api/providers -UseBasicParsing
Invoke-WebRequest http://127.0.0.1:18765/api/model-config -UseBasicParsing
```

If either service is down, start it from its project directory before proceeding.

## Core Workflow

1. Resolve the manuscript file path deterministically. If the file is local `.docx`, `.txt`, or `.md`, use the local file-reading intake rules first.
2. Split the manuscript into semantic segments, preferring chapter and paragraph boundaries over fixed character counts.
3. Send each segment to `AntiAIGC` `/api/detect`.
4. Select only segments above the risk threshold for baibai processing unless the user explicitly asks to process every segment.
5. Send selected segments to `baibaiAIGC` as temporary text files and run one or two rounds.
6. Re-send processed segments to `AntiAIGC` for review.
7. Merge processed and untouched segments into a revised candidate manuscript.
8. Produce an AWAS review packet and then do a human-facing final review:
   - China Pharmaceutical University thesis fit
   - chapter logic
   - method/result/discussion evidence alignment
   - terminology, abbreviations, data, citations
   - table/figure/statistical expression
   - language clarity and remaining template-like expression

## Script Entry

Use the bundled script for the first automated pass:

```powershell
$env:SystemRoot='C:\Windows'
$env:windir='C:\Windows'
& '<PRIVATE_THESIS_WORKSPACE>\baibaiAIGC\.venv\Scripts\python.exe' `
  '<USER_HOME>\.cc-switch\skills\anti-baibai-awas-pipeline\scripts\anti_baibai_awas_pipeline.py' `
  'F:\absolute\path\to\manuscript.docx' `
  --threshold 0.58 `
  --rounds 2
```

Useful options:

- `--all`: process every segment, not only segments above threshold.
- `--limit N`: process at most `N` selected segments for a smoke test.
- `--output-root PATH`: change the output directory.
- `--anti-api URL`: override AntiAIGC backend URL.
- `--baibai-api URL`: override baibaiAIGC backend URL.

Default output root:

```text
<PRIVATE_THESIS_WORKSPACE>\pipeline_outputs
```

Each run writes:

- `original.txt`
- `merged_revised.txt`
- `merged_revised.docx` when `python-docx` is available
- `pipeline_report.json`
- `awas_review_packet.md`

## Operating Rules

- Never overwrite the original manuscript.
- Keep all intermediate outputs traceable.
- Do not automatically keep iterating until a score changes.
- Treat `AntiAIGC` risk scores as heuristic signals, not as final academic quality judgments.
- Prefer processing only high-risk prose sections such as introduction, literature review, and discussion.
- Be conservative with methods, results, tables, figure captions, numerical claims, citations, and terminology-heavy passages.
- After the script finishes, read `awas_review_packet.md` and `merged_revised.txt` before giving final AWAS-style feedback.

## Final Response Pattern

After running the workflow, report:

- resolved input file
- output directory
- number of segments
- number processed
- initial vs final risk summary
- paths to merged manuscript and AWAS packet
- whether any stages failed
- next manual-review priorities
