---
name: zotero-reviewed-import
description: Use when the user wants a reviewed bibliography spreadsheet or bibliography list turned into verified Zotero-ready items, especially for workflows like “参考文献审核 -> 真实文献 -> 导入 Zotero cpu 集合 -> 继续写作”, and when the work must remain resumable after context compression via a saved resume state.
---

# Zotero Reviewed Import

This skill turns reviewed bibliography sources into deterministic Zotero import results, with resume-first handoff guarantees.

## Mandatory resume-first behavior

Before any action, read these files in order:

1. `state/RESUME.md`
2. `state/latest_run.json`
3. `references/resume_contract.md`
4. `references/workflow.md`

If `state/RESUME.md` or `state/latest_run.json` is missing, run:

```powershell
python .\scripts\show_resume_state.py
```

Do not reconstruct task history from chat when state files exist.

## Workflow intent

Use this skill for:

1. read a reviewed bibliography source
2. keep only rows already marked as real / verified
3. prepare or execute Zotero import
4. update resumable state so a later compressed session can continue safely

## When to use

- the user gives `.xlsx`, `.txt`, `.md`, or `.docx` bibliography material
- the user mentions `cpu` Zotero collection
- the user wants “核对真实文献后导入 Zotero”
- the user wants Markdown, Word, and WPS-compatible downstream writing
- the user wants the workflow to survive context compression or handoff

## Commands by stage

Verification:

```powershell
python .\scripts\verify_references.py --input <file>
```

Reviewed spreadsheet import/prep:

```powershell
python .\scripts\import_reviewed_xlsx_to_zotero.py --input <xlsx>
```

Incremental resume:

```powershell
python .\scripts\import_reviewed_xlsx_to_zotero.py --input <xlsx> --run-dir <runs/timestamp> --max-rows 20
```

Resume inspection:

```powershell
python .\scripts\show_resume_state.py
```

## Current import contract

The spreadsheet import script expects a sheet like the current audit workbook:

- `状态`
- `DOI/URL`
- `参考文献文本(前120字)`
- `审核说明`

Rows with status starting with `✓` are treated as verified candidates.

## Write mode rules

- Prefer `auto` mode. It upgrades to `hybrid` only when Zotero Web API credentials are present.
- In `auto`, the script performs a non-writing local API probe and records the exact failure when local POST writes are unsupported.
- If the machine is local-only and has no `ZOTERO_API_KEY`, do not pretend write succeeded.
- In local-only mode, still produce:
  - `verified_from_review.bib`
  - `import_results.json`
  - `import_report.md`
  - updated resume state

## Resume discipline

Every run must leave:

- `state/latest_run.json`
- `state/RESUME.md`
- one timestamped folder under `runs/`
- `runs/<timestamp>/checkpoint.json`

Compression/handoff rule: future sessions continue from those files first, then inspect run artifacts.

## Handoff minimum checklist

Before handing to another session/agent, confirm:

- `python .\scripts\show_resume_state.py` runs without crash
- `state/latest_run.json` has `next_step` and `run_dir`
- `state/RESUME.md` includes source, collection, actual mode, blockers, next command
- run folder contains `import_results.json` and `import_report.md`

## References

Read these when needed:

- `references/resume_contract.md` for strict resume/handoff contract
- `references/workflow.md` for engine-selection and import behavior
