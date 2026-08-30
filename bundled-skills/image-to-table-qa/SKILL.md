---
name: image-to-table-qa
description: Use when users need to batch-convert report images, scanned forms, laboratory screenshots, or OCR text into a structured CSV/XLSX-style table while preserving one source identifier per row, units and abnormal flags, unreadable/low-confidence cells, schema validation, and a human-review queue. Use for auditable image-to-table extraction, not generic visual description.
---

# Image-to-table QA

Convert images to structured rows without letting a fluent OCR result masquerade as verified data.

## Route

1. Resolve and inventory every source image. Never overwrite the originals.
2. If the material may contain PHI or identifiers, run de-identification/privacy review before any
   external OCR or model call.
3. OCR one source at a time with `ocr-document-processor`, `pdf-ocr-skill`, or another approved
   reader. Preserve the source filename, raw OCR output, and extraction status.
4. Pilot a small sample to establish the target schema. Prefer a user-supplied schema; otherwise
   infer a union schema and present it for review before a large batch.
5. Represent each field as a value plus optional `unit`, `flag`, `confidence`, `status`, and `raw`.
   Do not discard abnormal arrows or uncertainty; store them separately.
6. Normalize with the bundled deterministic script:

```text
python scripts/build_table.py extracted_records.json --csv output.csv --qa output.qa.json
```

7. Review all unreadable, low-confidence, structurally invalid, or duplicate-source records against
   the original images before downstream analysis.

Read `references/schema.md` for the exchange format.

## Verification

- one unique `_source_file` per row;
- stable column order and equal row width;
- units and high/low flags preserved separately from numeric values;
- unreadable values remain blank with review status, not guessed;
- OCR confidence is not treated as truth probability;
- row count reconciles with source-image count;
- CSV/JSON encoding and output paths are verified;
- no image, raw OCR text, or sensitive value is sent externally without authorization.

## Failure/fallback

If OCR is unavailable, return an image inventory and schema template. If source images are too
blurred, mark the cells/source `needs-review`; do not reconstruct values from neighboring rows. If
the reports use incompatible schemas, split them into homogeneous batches instead of forcing a
misleading universal table.

