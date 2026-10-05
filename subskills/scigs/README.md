# Formatting Journal Submissions

An executable DOCX-first skill for moving an existing manuscript to a named journal without silently rewriting scientific content.

## Integrated design

- `Journal Submission From Package`: package intake, source-of-truth metadata, official requirements, blinded/non-blinded variants, pre-submit stop.
- `JournalManuscript`: family baseline, journal-specific overlay, profile/evidence distinction, layout-aware validation.
- Academic manuscript utilities: Crossref metadata and conservative reference conversion, while preserving dynamic citation-manager fields.

The implementation adds deterministic scripts for requirements evidence, DOCX formatting, DOI metadata, reference auditing, anonymity scanning, asset inventory, rendering, packaging, and final status.

## Quick start

```powershell
python -m pip install -r requirements.txt
python scripts/fetch_official_requirements.py `
  --url https://journal.example.org/instructions `
  --output journal_requirements.yaml `
  --journal "Example Journal" `
  --article-type "Original Article"
# Review the YAML and set only confirmed actions/verification values.
python scripts/prepare_submission.py `
  --manuscript manuscript.docx `
  --requirements journal_requirements.yaml `
  --output-dir submission-output `
  --term "Author Name" `
  --term "Institution Name"
```

The pipeline never claims `READY` when official evidence, rendering, reference integrity, or anonymity checks remain unresolved.
