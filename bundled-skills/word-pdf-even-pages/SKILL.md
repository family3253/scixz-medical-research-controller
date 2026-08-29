---
name: word-pdf-even-pages
description: Batch-convert Word .doc/.docx files to PDF with Microsoft Word, split large Word files whose tables represent individual records, reduce small overflow pages such as a third page containing only a 备注 row without changing font sizes, enforce even PDF page counts by deleting a truly blank last page or appending a blank page, validate outputs, and merge them. Use for print-ready student records, forms, dossiers, cards, or other Word batches where duplex printing requires every document to have an even number of pages.
---

# Word PDF Even Pages

Use the bundled scripts for deterministic processing. Work on copies and keep raw PDFs beside final PDFs.

## Workflow

For already separated Word files:

1. Copy source Word files into a workspace directory. Extract ZIP inputs first. Do not overwrite originals.
2. Run a conservative compaction pass only when a small overflow page should be pulled back.
3. Run `scripts/convert_word_to_pdf.ps1` on the accepted Word copies and all unchanged Word files.
4. Run `scripts/enforce_even_pages.py` on raw PDFs.
5. Inspect `odd_last_pages_contact_sheet.png`, especially every page classified as blank.
6. Run `scripts/merge_pdfs.py` only after per-file validation.

For large Word files where each person/record is one table:

1. Prefer `scripts/process_big_word_tables_even_pages.ps1`.
2. It splits every source table into a per-person legacy `.doc` to preserve compatibility-mode pagination.
3. It attempts direct `.doc` compaction only for split documents with exactly 3 pages.
4. Accepted compact PDFs replace the raw conversion; rejected files fall back to the raw PDF.
5. It enforces even pages per person and then merges the final per-person PDFs.

## Commands

```powershell
# Large Word files with one person/record per table.
pwsh -NoProfile -ExecutionPolicy Bypass `
  -File scripts\process_big_word_tables_even_pages.ps1 `
  -SourceDir "C:\work\source_docs" `
  -OutputRoot "C:\work\output" `
  -Python "python" `
  -MergedPdfName "student_cards_even_merged.pdf"

# Already separated Word files.
& scripts\compact_low_content_third_page.ps1 `
  -InputDir "C:\work\word" `
  -OutputRoot "C:\work\compact_attempt" `
  -MaxThirdPageChars 120

& scripts\convert_word_to_pdf.ps1 `
  -InputDir "C:\work\word" `
  -OutputDir "C:\work\pdf_raw"

python scripts\enforce_even_pages.py "C:\work\pdf_raw" "C:\work\pdf_even"

python scripts\merge_pdfs.py "C:\work\pdf_even" "C:\work\merged.pdf"
```

## Low-Content Third-Page Rules

For large legacy `.doc` student-card files, prefer `compact_one_compat_doc_direct.ps1` through the big-Word workflow. It keeps the split file as legacy `.doc` and attempts compaction only when the document has exactly 3 pages and normalized page-3 text is at most the configured threshold.

It tries these stages from least to most invasive and accepts the first 2-page result:

1. Compress empty rows on page 2 and the empty `备注` row.
2. Reduce the bottom margin in 6-point steps, never below 54 points.
3. Reduce the top margin in 6-point steps, never below 54 points.
4. As a final attempt, compress all completely empty rows before page 3.

Hard acceptance checks:

- The result has exactly 2 pages.
- Main-document text is exactly unchanged.
- Table, inline-image, floating-shape, and section counts are unchanged.
- Every Word font-size value is unchanged.
- Margins never go below 54 points.

Rejected files stay on the raw PDF path and later receive a blank page if still odd. Review the CSV and rendered PDFs before replacing raw conversions.

`compact_low_content_third_page.ps1` is still available for already separated batches where conversion to `.docx` is acceptable. Do not use it when `.docx` conversion changes pagination.

## Even-Page Rules

For an odd-page PDF:

- Delete the last page only when extracted text is empty and its rendered page has no visible ink.
- Otherwise append a blank page matching the last page size.

Always preserve a report, raw PDFs, final PDFs, and the odd-last-page contact sheet.

## Requirements

- Windows with Microsoft Word installed for `.doc` fidelity.
- Use `pwsh` for the orchestration scripts when paths contain Chinese or spaces. Old Windows PowerShell can hang on some Word COM compaction cases.
- Python with `pypdf` and Pillow.
- Poppler `pdftoppm` for visual blank-page detection.
