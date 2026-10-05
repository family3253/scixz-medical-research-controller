# DOCX Formatting

Work on a copy. `format_docx.py` applies only the normalized `actions` map in `journal_requirements.yaml`:

- `page_size`: `A4` or `LETTER`
- `margins_pt`: top/right/bottom/left
- `default_font_name`, `default_font_size_pt`
- `line_spacing`, `paragraph_spacing_after_pt`
- `line_numbers`, `page_numbers`

The script refuses to overwrite the input and compares body, footnote, and endnote text before and after. A mismatch deletes the output and blocks the pipeline. Page layout and numbering are formatting actions; changing text, numbers, table values, or scientific order is outside this script.

Inspect styles, tables, images, fields, headers/footers, comments, revisions, and metadata before editing. Render after every layout-sensitive change.
