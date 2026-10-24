# SciXZ DOCX formatting policy

## Purpose

Formatting is part of submission integrity. A Word file can contain correct text and still be unsuitable for submission when its font, size, line spacing, margins, heading hierarchy, or table layout drift across files. SciXZ therefore audits visible formatting separately from DOCX core metadata.

## Default manuscript profile

Unless the target journal gives a stricter or different rule, use this profile for manuscript text, title pages, cover letters, declarations, highlights, figure captions, and supplementary narrative text:

- Font: Times New Roman for Latin, Greek, and scientific text; preserve a journal-specific font only when the target guide explicitly requires it.
- Body size: 12 pt. A title may use 14 pt bold; headings may use 12 pt bold unless the target template specifies a hierarchy.
- Line spacing: double (2.0).
- Paragraph spacing: 0 pt before and 0 pt after.
- Page margins: at least 1 inch on all sides.
- Body alignment: justified or the target journal’s stated alignment; preserve first-line indents only when they are part of the manuscript’s existing paragraph design.
- Abstract and keywords: use the same body profile unless the target guide states otherwise.

## Table exception

Wide tables may use a documented exception:

- Table cells: Times New Roman 9 pt, single spacing, 0 pt before/after.
- Table-page margins may be reduced to 0.6 inch when the table cannot fit at 1 inch without illegible wrapping.
- Table captions and notes remain 12 pt with double spacing and 1-inch margins when possible.
- The exception must appear in the package audit and must be visually checked after conversion or upload.

Do not silently shrink the main manuscript to make a table fit. Use a separate table file, landscape section, supplementary table, or target-journal template when appropriate.

## Paragraph-level layout rules

Font and size checks alone miss most visible inconsistencies, because they read only the runs. The audit therefore also inspects paragraph properties and reports them as `layout:` findings. Treat every `layout:` finding as `MAJOR` unless the target journal's template documents the deviation.

- One indent rule per region. All prose paragraphs inside the main text (from the `1. Introduction` heading to `List of abbreviations` / `References`) share a single first-line indent; front matter, captions, table notes, references, and declarations follow one consistent rule of their own. A paragraph that is flush left among indented neighbours is a defect, not a style choice.
- Exact indent values. Do not mix `firstLine` and `firstLineChars` on the same paragraph: the rendered indent then depends on the font size. Do not leave values such as 482 twips beside 480.
- Headings. Left-aligned, not justified; no first-line indent; one size per document (12 pt bold unless the template defines a hierarchy); `keepNext` set so a heading cannot be orphaned at a page break.
- Explicit run properties. Every run carries `rFonts` (Times New Roman) and `sz`. A run that relies on `docDefaults` inherits the theme font, which is usually not Times New Roman, and the default size, which is usually 11 pt. A run holding only symbol glyphs (a checkbox, a tick) may use a symbol font.
- Blank lines. No two consecutive empty paragraphs between blocks. Leading vertical spacing before the first paragraph of a short form is permitted.
- Text hygiene. No leading whitespace inside a paragraph, no words glued together by a lost space, no missing space after a full stop, no paragraph opening with a lowercase word.
- Page geometry. All sections of one document use the same page size; a title page on A4 and a body on Letter is a defect. An all-landscape section carrying wide tables is a legitimate exception when the portrait and landscape sizes are the same sheet rotated.
- Tables. Cell alignment is consistent within a table; centred spanning labels are the only exception.

## Landscape table sections

A wide table is often moved into its own landscape section. The usual way of doing this - putting `sectPr` in the `pPr` of the table's last text paragraph - produces a blank page whenever that paragraph is the last thing the page can hold. The break paragraph must be laid out on some page, and if the text above it already reaches the bottom margin, that page is a new, empty one.

- Give the section break its own empty paragraph, placed after the text paragraph, and never attach `sectPr` to a paragraph that carries text. A 2.0 line-spaced empty paragraph still needs one line of room, so this alone does not guarantee the page survives.
- If the table plus its notes fill the page to the margin, prefer one landscape section holding every table, with an explicit `<w:br w:type="page"/>` before each table caption, over one section per table. Section breaks only have to be used where the page geometry changes.
- Verify by rendering, never by structure alone. Convert to PDF and list every page with three or fewer text blocks; a page holding only the footer is a blank page. Structure checks that count `sectPr` cannot see this defect.
- When a script relocates a `sectPr`, delete the now-stray `<w:pPr/>` left behind. Two `pPr` children in one paragraph is schema-invalid, and it later splits paragraphs at the wrong offset when the file is edited again.


## Audit procedure

Before accepting a DOCX package:

1. Audit every DOCX file, including title page, cover letter, declarations, table files, supplementary narrative files, and reviewer-facing attachments.
2. Record the effective font, size, line spacing, paragraph spacing, margins, alignment, and table-cell exception for each file.
3. Run `scripts/audit_docx_format.py` on the package directory. The paragraph-level checks run by default; `--no-layout` disables them for artifacts that are not manuscript-style documents.
4. Treat any unexpected font, size, margin, paragraph-spacing, or `layout:` finding as `MAJOR` until the author or target guide provides a documented exception.
5. Re-run the audit after any Word modification, conversion, or package rename. A tool that writes `word/document.xml` directly can leave runs without `rFonts`/`sz` or strip `docProps/core.xml`; re-audit both after every such write.
6. Keep the audit report beside the private package; do not put private manuscript paths, hashes, or reports into a public release.

## Verification boundary

A passing structural audit proves only that the inspected OOXML properties match the selected profile. It does not prove visual pagination, figure readability, table overflow, or the target portal’s final conversion. For those, render or open representative files and record a separate visual check.

## Target-journal precedence

The current target journal’s Instructions for Authors override this default profile. Record the journal rule, the affected file(s), the exception, and the verification evidence. Do not infer a journal-specific font or margin from a published PDF alone.

## Final upload-package hygiene

A final submission package is an upload set, not a working directory. Keep README files, audit JSON/TSV reports, manifests, scripts, backups, temporary exports, and package ZIP archives outside the final upload directory.

- The final upload directory may contain only journal-required manuscript, cover-letter, table, figure, disclosure, and supplementary files in accepted formats.
- Do not place `.md`, `.json`, `.tsv`, `.py`, `.ps1`, `.log`, `.bak`, `.tmp`, `.zip`, or `.rar` files in the final upload directory unless the target journal explicitly requests one of them.
- Run `scripts/audit_submission_package.py` before creating the final ZIP. The clean audit must pass, and the ZIP must be generated from the audited upload directory after the last modification.
- Keep formatting audits, metadata reports, manifests, preflight reports, and working backups in a separate private working directory.

## End-matter submission profile

When the author requests the conventional end-matter layout, place table 1, table 2, each table title/note, and the figure title/caption list after the references in the manuscript; upload image files separately. Keep separate table/caption files outside the clean upload set unless the target portal explicitly requires those file slots. If the portal marks separate table uploads as mandatory, follow the portal and retain the end-matter copy in the manuscript only when duplicate submission is accepted.
