# Resume Contract

This contract defines how any future session continues the workflow safely after compression or handoff.

## Source of truth order

Read in this strict order:

1. `state/RESUME.md`
2. `state/latest_run.json`
3. `runs/<timestamp>/import_report.md` from `latest_run.json.run_dir`
4. `runs/<timestamp>/import_results.json` from `latest_run.json.run_dir`

If `state/RESUME.md` and `state/latest_run.json` disagree, treat `state/latest_run.json` as authoritative and regenerate `state/RESUME.md` on next run.

## Required keys in `state/latest_run.json`

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

## Required sections in `state/RESUME.md`

- source file path
- target collection name/key
- requested and actual mode
- processed row progress
- key run counts
- stop reason
- blockers
- exact next command

## Handoff guardrails

- Do not reconstruct historical decisions from chat while state files exist.
- Do not claim Zotero write success unless `import_results.json` confirms imported rows.
- If blocked, keep `next_step` actionable and single-step.
- Keep resume text short and operational, not narrative.

## Recovery when state is missing or invalid

1. Run `python .\scripts\show_resume_state.py`.
2. Inspect newest run folder under `runs/`.
3. Recreate `state/latest_run.json` from `runs/<timestamp>/import_results.json`.
4. Recreate `state/RESUME.md` using `state/RESUME.template.md`.
