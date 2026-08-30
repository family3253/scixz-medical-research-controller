# Optional external review tools

## PaperReview.ai

`PaperReview.ai` is an optional external supplementary review branch for English manuscripts. It
is not a Skill. SciXZ provides a guarded automation adapter based on the provider's public
front-end flow; it is disabled unless the user explicitly authorizes that exact upload.

The provider's current public page says that it accepts a PDF and email address, analyzes the
first 15 pages, supports English only, bases recommendations primarily on arXiv papers, and may
make mistakes. Treat all returned text as an `external-signal`, not as a verified review finding.

### Authorized use boundary

1. Freeze and fingerprint the local manuscript before any external action.
2. Obtain explicit current authorization to upload that specific PDF. Do not upload PHI,
   restricted data, reviewer-confidential material, or an unpublished manuscript by default.
3. Set `PAPERREVIEW_EMAIL` only in the current local environment. It is never accepted on the
   command line, logged, or written to the state/result files.
4. Run the authorized submit command below. It follows the provider's public presigned-upload
   flow, stores the returned access token only in the user-selected private state file, and never
   prints the token.
5. Poll or fetch the result. It saves a raw provider result and a redacted artifact in a directory
   outside the repository; no browser cookie, email, or token enters the result artifact.
6. Build the bounded synthesis package. The SciXZ reviewer reads the frozen manuscript and this
   package, independently verifies issues, and produces the bilingual final-review JSON.
7. Render the verified final-review JSON into Chinese and English Word files.
8. Convert the provider output into atomic issues with manuscript locations, evidence, severity,
   and an independent disposition. Unverifiable findings remain unresolved.

### Automated commands

All paths below must be outside the Git repository because state, returned review text, and access
tokens can be sensitive unpublished-work artifacts.

```text
$env:PAPERREVIEW_EMAIL = "your-email@example.edu"
python scripts/paperreview_automation.py submit --manuscript manuscript.pdf --venue Other --state C:\private-runs\paperreview-state.json --authorized-upload
python scripts/paperreview_automation.py poll --state C:\private-runs\paperreview-state.json --result C:\private-runs\provider-review.json --artifact C:\private-runs\paperreview-artifact.json --attempts 24 --interval-seconds 900
python scripts/build_paperreview_synthesis_bundle.py --manuscript manuscript.pdf --artifact C:\private-runs\paperreview-artifact.json --provider-review C:\private-runs\provider-review.json --output C:\private-runs\scixz-synthesis-input.json
```

The final synthesis step is intentionally a SciXZ reviewer task rather than an automatic text
merge: a deterministic program cannot substantively verify a medical/statistical critique without
the manuscript evidence. The reviewer writes a validated bilingual `final-review.json` using
[`templates/paperreview_final_review_bilingual.json`](../templates/paperreview_final_review_bilingual.json)
as the structural template, then:

```text
python scripts/render_final_review_docx.py --input C:\private-runs\final-review.json --output-dir C:\private-runs\final-review-docx
```

This produces `scixz_final_review_zh.docx` and `scixz_final_review_en.docx`.

### Routing rule

Use the provider only as an optional additional critique perspective after local deterministic
intake. `academic-paper-reviewer` or `nature-review-studio` remains the primary review owner;
`check-reporting` and `statistical-analysis` retain their domain checks. Never let an external
review alone determine an editorial recommendation, a claim of error, or a manuscript revision.

### Artifact schema

```json
{
  "tool": "paperreview-ai",
  "status": "completed",
  "input_fingerprint": "sha256:...",
  "submitted_at": "2026-08-30T12:00:00+08:00",
  "result_artifact": "local/path/to/saved-review.md",
  "language": "English",
  "pages_reviewed": 15
}
```

The user email, provider account state, uploaded PDF copy, browser cookies, and provider-side
URLs are not stored in SciXZ run artifacts or committed to the repository.
