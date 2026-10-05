# SciXZ Word author metadata policy

## Required metadata

Every `.docx` artifact produced or modified through SciXZ must contain:

- `docProps/core.xml/cp:creator = chenyechao`
- `docProps/core.xml/cp:lastModifiedBy = chenyechao`

This is document metadata only. It must not change the visible author list, blinded manuscript content, corresponding-author fields, acknowledgements, or submission identity.

## Scope

Apply to reviewer reports, reviewer responses, proposals, formatted manuscripts, submission packages, patent/disclosure Word files, Word conversions, and supplemental Word outputs. If a route produces multiple Word files, verify every file.

## Verification

Use:

```powershell
python C:\Users\chenyechao\.codex\skills\scixz\scripts\verify_docx_author.py <file1.docx> <file2.docx>
```

A route cannot be reported complete when the metadata check fails or cannot run. Mark it `DEGRADED_ROUTE` or `BLOCKED` and preserve the output for repair.
