from __future__ import annotations

import json
from pathlib import Path


def _print_path_status(path: Path) -> None:
    if path.exists():
        print(f"[ok] {path}")
    else:
        print(f"[missing] {path}")


def _print_read_order(root: Path) -> None:
    print("# Read First")
    for rel in [
        "state/RESUME.md",
        "state/latest_run.json",
        "references/resume_contract.md",
        "references/workflow.md",
    ]:
        _print_path_status(root / rel)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    state_dir = root / "state"
    latest = state_dir / "latest_run.json"
    resume = state_dir / "RESUME.md"

    _print_read_order(root)
    print()

    if latest.exists():
        try:
            payload = json.loads(latest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print("# Latest Run")
            print(f"state/latest_run.json is invalid JSON: {exc}")
            print("Next: fix latest_run.json or regenerate from newest runs/<timestamp>/import_results.json")
            return

        print("# Latest Run")
        print(f"status: {payload.get('status', 'unknown')}")
        print(f"mode_requested: {payload.get('mode_requested', 'unknown')}")
        print(f"mode_used: {payload.get('mode_used', 'unknown')}")
        print(f"input_path: {payload.get('input_path', '')}")
        print(f"collection: {payload.get('collection_name', '')} ({payload.get('collection_key', '')})")
        print(f"run_dir: {payload.get('run_dir', '')}")
        counts = payload.get("counts", {})
        if counts:
            print(
                "processed_rows: "
                f"{counts.get('processed_rows', 'unknown')}/{counts.get('total_rows', 'unknown')}"
            )
        print(f"next_step: {payload.get('next_step', '')}")
        blockers = payload.get("blockers", [])
        print(f"blockers: {len(blockers)}")
        for blocker in blockers:
            print(f"- {blocker}")

        run_dir_value = payload.get("run_dir", "")
        if run_dir_value:
            run_dir = Path(run_dir_value)
            print()
            print("# Run Artifacts")
            _print_path_status(run_dir / "import_results.json")
            _print_path_status(run_dir / "import_report.md")
            _print_path_status(run_dir / "verified_from_review.bib")
        return

    if resume.exists():
        print("# Resume Markdown")
        print(resume.read_text(encoding="utf-8"))
        return

    print("# Resume State")
    print("No resume state found.")
    print("Next: run import/verification script to create state files.")


if __name__ == "__main__":
    main()
