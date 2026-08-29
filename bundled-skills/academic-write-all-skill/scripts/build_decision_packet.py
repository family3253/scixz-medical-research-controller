from __future__ import annotations

import argparse
import csv
from pathlib import Path


def count_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return len(rows)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def summarize_gate(gate_path: Path) -> str:
    if not gate_path.exists():
        return "gate report missing"
    lines = [
        line.strip()
        for line in read_text(gate_path).splitlines()
        if line.strip().startswith("- [")
    ]
    return "; ".join(lines[:6]) if lines else "no explicit gate checks found"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a decision packet for proceed/refine/pivot debate."
    )
    parser.add_argument("project_dir")
    args = parser.parse_args()

    root = Path(args.project_dir).expanduser().resolve()
    candidate = root / "02_candidate_pool_and_screening" / "candidate_pool.csv"
    fulltext = root / "03_fulltext_acquisition_and_review" / "fulltext_screening.csv"
    evidence = root / "04_evidence_extraction" / "evidence_extraction.csv"
    gate = root / "08_revision_and_final_checks" / "gate_report.md"
    claim = root / "06_claim_mapping_and_outline" / "claim_mapping.md"
    manifest = root / "session_manifest.md"
    authenticity = root / "citation_authenticity_report.md"

    packet = root / "decision_packet.md"
    packet.write_text(
        "\n".join(
            [
                "# Debate Packet",
                "",
                "## Decision Context",
                f"- project: {root.name}",
                f"- current_stage: {('unknown' if not manifest.exists() else next((line.split(':', 1)[1].strip() for line in read_text(manifest).splitlines() if line.startswith('- current_stage:')), 'unknown'))}",
                "- target_output: draftable scholarly prose",
                "- current_direction: evidence-grounded writing workflow",
                "",
                "## Evidence Snapshot",
                f"- candidate_count: {count_rows(candidate)}",
                f"- fulltext_included_count: {count_rows(fulltext)}",
                f"- evidence_row_count: {count_rows(evidence)}",
                f"- gate_summary: {summarize_gate(gate)}",
                f"- authenticity_summary: {next((line.split(':', 1)[1].strip() for line in read_text(authenticity).splitlines() if line.startswith('- pivot_count:')), 'not available')}",
                "",
                "## Claims in Play",
                f"{read_text(claim).strip() or '- claim mapping missing'}",
                "",
                "## Debate Question",
                "Should the project PROCEED, REFINE, or PIVOT before writing?",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"[ok] wrote decision packet: {packet}")


if __name__ == "__main__":
    main()
