# Optional external review tools

## PaperReview.ai

`PaperReview.ai` is an optional external, browser-mediated supplementary review branch for
English manuscripts. It is not a Skill, it has no documented SciXZ API integration, and SciXZ
must never upload a manuscript automatically.

The provider's current public page says that it accepts a PDF and email address, analyzes the
first 15 pages, supports English only, bases recommendations primarily on arXiv papers, and may
make mistakes. Treat all returned text as an `external-signal`, not as a verified review finding.

### Authorized use boundary

1. Freeze and fingerprint the local manuscript before any external action.
2. Obtain explicit current authorization to upload that specific PDF. Do not upload PHI,
   restricted data, reviewer-confidential material, or an unpublished manuscript by default.
3. Run `scripts/paperreview_adapter.py --prepare` locally. It creates a redacted upload manifest;
   it never opens a browser, uploads a file, or stores an email address.
4. The user performs any browser upload. Record only the local input fingerprint, date, language,
   pages actually reviewed, and a local result/export path.
5. Run `scripts/paperreview_adapter.py --validate-artifact` after the result is saved.
6. Convert the provider output into atomic issues with manuscript locations, evidence, severity,
   and an independent disposition. Unverifiable findings remain unresolved.

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
