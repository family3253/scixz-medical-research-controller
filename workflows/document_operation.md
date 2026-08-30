# Document-operation workflow

## Entry and scope

Use for deterministic local reading, extraction, conversion, rendering, and verification of PDF/DOCX/XLSX/PPTX/TXT/Markdown files. It does not perform scientific interpretation unless a second approved workflow is issued.

## Inputs

Require exact path or deterministic filename resolution, user intent (read, extract, convert, inspect layout), file type, and desired output.

## Route

Controller → 户部 resolves and fingerprints the path → one file-type reader is selected. Use `deterministic-local-file-reading` first, then `anthropics-pdf`, `anthropics-docx`, `anthropics-xlsx`, `anthropics-pptx`, OCR, or direct text reading as appropriate.

## Outputs

Extracted text/table/metadata, converted file, layout inspection, or a verified error report. Preserve absolute paths and output counts.

For batch OCR or image-to-table requests, issue a second data-preparation ticket after successful reading. Use `image-to-table-qa` to retain one source identifier per row, preserve units/flags/raw uncertainty, validate a stable schema, and produce a human-review queue. OCR text is an extraction candidate, not verified clinical data.

## Verification

Check file existence, reader success, text sufficiency, page/sheet/slide counts, output paths, and whether OCR or a fallback was actually required. For structured extraction, reconcile source count to row count, reject duplicate source IDs, retain unreadable cells, and verify CSV/XLSX column consistency.

## Failure/fallback

Use one documented backup only after the primary reader fails. Stop after both documented routes fail; do not bounce through unrelated readers or silently change the user's intent.
