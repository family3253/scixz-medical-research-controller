from __future__ import annotations

import argparse
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def contains_failures(gate_text: str) -> bool:
    return "[FAIL]" in gate_text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check consistency before AWAS handoff."
    )
    parser.add_argument("project_dir")
    args = parser.parse_args()

    root = Path(args.project_dir).expanduser().resolve()
    gate_path = root / "08_revision_and_final_checks" / "gate_report.md"
    deliverables_path = root / "deliverables_manifest.md"
    manifest_path = root / "session_manifest.md"
    decision_path = root / "decision_record.md"
    authenticity_path = root / "citation_authenticity_report.md"

    gate_text = read_text(gate_path)
    deliverables_text = read_text(deliverables_path)
    manifest_text = read_text(manifest_path)
    decision_text = read_text(decision_path)
    authenticity_text = read_text(authenticity_path)

    warnings = []
    blocks = []
    if "blocks_handoff: yes" in decision_text:
        blocks.append("decision_record.md explicitly blocks handoff")
    if contains_failures(gate_text) and "ready_for_handoff: yes" in deliverables_text:
        blocks.append(
            "deliverables manifest claims handoff readiness while gate report still contains FAIL items"
        )
    if "current_stage: complete" in manifest_text and contains_failures(gate_text):
        warnings.append("project reached complete stage despite failed gate thresholds")
    if (
        "draft_sections:" in manifest_text
        and "draft_sections: " in manifest_text
        and "07_draft/draft_sections.md" not in manifest_text
        and (root / "07_draft" / "draft_sections.md").exists()
    ):
        warnings.append("session manifest does not record existing draft_sections path")
    if not decision_text.strip():
        warnings.append("decision_record.md is missing or empty")
    if not authenticity_text.strip():
        warnings.append("citation_authenticity_report.md is missing or empty")
    if (
        "|" in authenticity_text
        and "| PIVOT |" in authenticity_text
        and "ready_for_handoff: yes" in deliverables_text
    ):
        blocks.append(
            "deliverables manifest claims handoff readiness while citation authenticity report still contains PIVOT entries"
        )
    if (
        "|" in authenticity_text
        and "| REFINE |" in authenticity_text
        and "ready_for_handoff: yes" in deliverables_text
    ):
        warnings.append(
            "citation authenticity report still contains REFINE entries while handoff is marked ready"
        )

    status = "blocked" if blocks else "warn" if warnings else "pass"
    report = root / "sentinel_watch_report.md"
    lines = [
        "# Sentinel Watch Report",
        "",
        f"- status: {status}",
        "- blocking_inconsistencies:",
    ]
    lines.extend([f"  - {item}" for item in blocks] or ["  -"])
    lines.append("- warnings:")
    lines.extend([f"  - {item}" for item in warnings] or ["  -"])
    lines.append("- required_fixes:")
    required = blocks + warnings
    lines.extend([f"  - {item}" for item in required] or ["  -"])
    lines.append(f"- handoff_allowed: {'no' if blocks else 'yes'}")
    lines.append("")
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"[ok] wrote sentinel watch report: {report}")


if __name__ == "__main__":
    main()
