---
name: deterministic-local-file-reading
description: Use when a request involves reading, opening, inspecting, extracting, OCRing, summarizing, or converting any local file by path, filename, attachment reference, download-folder reference, or workspace file reference, especially for .doc, .docx, .xls, .xlsx, .xlsm, .csv, .tsv, .ppt, .pptx, .pdf, image files, .txt, .md, or bibliographic exports such as .ris, .bib, .nbib, and .enw. Make sure to use this skill whenever local file opening needs to work on the first try instead of relying on ad hoc tool selection or retry loops.
---

# Deterministic Local File Reading

## Overview

Use this skill as the single intake router for local file-reading tasks. Its job is to stop trial-and-error file opening, lock onto one canonical path, and then hand the task to exactly one downstream skill or tool that can actually read that file type.

This skill is not the final reader. After using it, immediately route to the matching downstream skill or direct read tool.

## Core Rule

For local file-reading tasks, do not bounce between unrelated readers. Resolve path once, classify file type once, dispatch once.

## Path Resolution

### Resolution order

1. If the user gives an absolute path, use that exact path.
2. If the user gives a relative path, resolve it against the current workspace root.
3. If the user gives only a filename, search in this order:
   - current workspace recursively
   - the configured research workspace recursively
   - the configured downloads directory recursively
   - the configured documents directory recursively
4. If exactly one match is found, lock onto that absolute path for the rest of the task.
5. If multiple matches are found, ask one short disambiguation question with absolute candidate paths.
6. Do not re-resolve the same file to a different location later in the task.

### Path discipline

- Always restate the resolved absolute Windows path before opening a binary file.
- Never rely on `./input`, `./output`, or current working directory guesses when a concrete file path is needed.
- Never silently switch between workspace files and downloads files mid-task.

## Verified Dispatch Matrix

Only route to downstream skills or tools that are genuinely capable of reading the file type.

| File type | Primary route | Verified backup |
|---|---|---|
| `.txt`, `.md` | direct text read tool | none |
| `.ris`, `.bib`, `.nbib`, `.enw` | direct text read tool | metadata normalization / parser-backed conversion once the file is stably read |
| `.doc`, `.docx` | `anthropics-docx` | `markitdown` document conversion read |
| `.xls`, `.xlsx`, `.xlsm`, `.csv`, `.tsv` | `anthropics-xlsx` | raw workbook/dataframe read with `openpyxl` or `pandas` |
| `.ppt`, `.pptx` | `anthropics-pptx` | `markitdown` or `python-pptx` slide-text extraction |
| born-digital `.pdf` | `anthropics-pdf` | OCR only if the PDF reader returns little or no usable text |
| scanned/image-only `.pdf` | `ocr-document-processor` | `pdf-ocr-skill` if OCR quality is still poor |
| image files with text-extraction intent | `ocr-document-processor` | `pdf-ocr-skill` if OCR quality is still poor |
| image files with visual-inspection intent | visual/image read tool | none |

## Intent Split for Images and PDFs

### Use OCR when the user asks to:
- read text
- extract text
- OCR
- recognize text
- pull tables from a scan

### Use visual inspection when the user asks to:
- look at the image
- inspect layout
- describe the figure
- analyze a screenshot visually

For PDFs, start with `anthropics-pdf` unless the file is clearly scanned/image-only or the user explicitly asks for OCR.

## Failure Safeguards

Use safeguards once and only once. The point is recovery, not retry loops.

### Safeguard 1: Path failure
If the chosen path does not exist or is ambiguous, stop and resolve the path properly. Do not try another random folder first.

### Safeguard 2: Primary reader failure
If the primary route errors or returns clearly unusable output:
- Word files: try `markitdown` once if document conversion reading is still needed.
- Spreadsheet files: try one raw workbook/dataframe read path once.
- Presentation files: try `markitdown` or `python-pptx` once if text extraction is still needed.
- PDFs: move to OCR only if the PDF is consistent with a scan/image-only document or the PDF reader returned little or no usable text.
- Images for OCR: move from `ocr-document-processor` to `pdf-ocr-skill` once if quality is poor.

### Safeguard 3: Stop unrelated retries
Do not do things like:
- `.docx` -> plain text reader -> OCR -> PDF reader
- `.xlsx` -> markdown converter -> plain text reader -> random spreadsheet path
- `.pptx` -> OCR -> random office automation fallback
- `.pdf` -> OCR first when born-digital text is likely present
- route a reading task to a skill that does not actually read that file type

If the primary route and its documented backup both fail, report the exact failure and ask for one targeted clarification only if required.

## WPS Policy

WPS skills are not bare-file default readers. Use them only when:
- the user explicitly wants WPS-side opening or editing, or
- WPS application state has already been confirmed and the task is clearly application-driven rather than bare-file reading.

## Anti-Patterns

- Opening Office binaries with generic text readers first
- Polling the same file with multiple unrelated skills
- Re-searching for the same filename in different folders after already locking a resolved path
- Treating all PDFs as OCR tasks by default
- Using backup before the primary route has actually failed
- Asking the user to repeat a file path that was already successfully resolved
- Sending a local file-reading task to a downstream skill whose documented purpose is not file reading
- Using WPS skills as default bare-file readers when WPS application state has not been confirmed

## Quick Workflow

1. Detect that the task is about a local file.
2. Resolve the absolute path deterministically.
3. Identify the file extension and user intent.
4. Dispatch to one primary downstream skill or tool that is documented to read that file type.
5. If needed, use exactly one documented backup.
6. Stop after a successful read or a concrete failure.

## Examples

- `研究方案.docx` -> resolve absolute path -> `anthropics-docx`
- `height.xlsx` -> resolve absolute path -> `anthropics-xlsx`
- `陈烨超开题ppt.pptx` -> resolve absolute path -> `anthropics-pptx`
- `1开题报告_陈烨超.pdf` -> resolve absolute path -> `anthropics-pdf`
- `scan.png，帮我提取文字` -> resolve absolute path -> `ocr-document-processor`
- `陈烨超中期.md` -> resolve absolute path -> direct text read
- `references.ris` -> resolve absolute path -> direct text read -> bibliographic normalization workflow`r`n- `references.ris` -> resolve absolute path -> direct text read -> bibliographic normalization workflow

## Priority

When this skill applies, it should be used before any file-type-specific reading work begins. It is the intake router for local file access, not a competing reader.



