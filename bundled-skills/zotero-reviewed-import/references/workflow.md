# Workflow

## Goal

Turn a reviewed bibliography source into:

- real Zotero items when write credentials are available
- otherwise a deterministic import bundle plus a resume state

## First read contract

Before any new run, read:

1. `state/RESUME.md`
2. `state/latest_run.json`
3. `references/resume_contract.md`

## Engine selection

### `auto`

- use `hybrid` only if both `ZOTERO_API_KEY` and `ZOTERO_LIBRARY_ID` are present
- if credentials are missing, run a non-writing local POST probe and record the exact rejection reason
- otherwise fall back to `prepare`

### `hybrid`

- reads the local Zotero library for duplicate checks
- writes via Zotero Web API
- can target a collection key such as `UDC49MTG`

### `prepare`

- no Zotero write attempt
- still emits importable `.bib` and detailed JSON/Markdown logs
- updates resume state with the exact blocker and next step

## Resume contract

`state/latest_run.json` must include:

- `status`
- `mode_requested`
- `mode_used`
- `input_path`
- `collection_name`
- `collection_key`
- `run_dir`
- `counts`
- `next_step`
- `blockers`

`state/RESUME.md` must stay short and operational:

- what source file was used
- what collection is targeted
- what succeeded
- what is blocked
- the next exact command to run

Use `state/RESUME.template.md` when regenerating this file.

Use `python .\scripts\show_resume_state.py` as the first diagnostic command.

Each resumable run should also keep `runs/<timestamp>/checkpoint.json` so `--run-dir` can continue from the last processed row without replaying finished rows.

## Current Zotero collection

For the current machine, the known `cpu` collection is:

- name: `cpu`
- key: `UDC49MTG`

Treat that as the default until the user says otherwise.
