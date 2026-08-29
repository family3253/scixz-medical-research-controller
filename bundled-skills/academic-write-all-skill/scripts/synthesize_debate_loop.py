from __future__ import annotations

import argparse
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def has_failures(text: str) -> bool:
    return "[FAIL]" in text


def parse_auth_counts(text: str) -> tuple[int, int]:
    refine = 0
    pivot = 0
    for line in text.splitlines():
        if line.startswith("- refine_count:"):
            try:
                refine = int(line.split(":", 1)[1].strip())
            except ValueError:
                pass
        if line.startswith("- pivot_count:"):
            try:
                pivot = int(line.split(":", 1)[1].strip())
            except ValueError:
                pass
    return refine, pivot


def parse_gate_failures(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith("- [FAIL]")
    ]


def parse_auth_decisions(text: str) -> dict[str, list[str]]:
    result = {"PROCEED": [], "REFINE": [], "PIVOT": []}
    for line in text.splitlines():
        stripped = line.strip()
        if (
            not stripped.startswith("|")
            or "Citation ID" in stripped
            or "---" in stripped
        ):
            continue
        parts = [part.strip() for part in stripped.strip("|").split("|")]
        if len(parts) < 6:
            continue
        citation_id = parts[0]
        decision = parts[5].upper()
        if decision in result:
            result[decision].append(citation_id)
    return result


def write(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Materialize proceed/refine/pivot stance files and synthesize a decision record."
    )
    parser.add_argument("project_dir")
    args = parser.parse_args()

    root = Path(args.project_dir).expanduser().resolve()
    packet = read_text(root / "decision_packet.md")
    gate = read_text(root / "08_revision_and_final_checks" / "gate_report.md")
    authenticity = read_text(root / "citation_authenticity_report.md")

    refine_count, pivot_count = parse_auth_counts(authenticity)
    fail_gate = has_failures(gate)
    gate_failures = parse_gate_failures(gate)
    auth_decisions = parse_auth_decisions(authenticity)

    proceed_case = root / "proceed_case.md"
    refine_case = root / "refine_case.md"
    pivot_case = root / "pivot_case.md"
    decision_record = root / "decision_record.md"

    write(
        proceed_case,
        f"""# Proceed Case

- source_packet: decision_packet.md
- source_gate_report: 08_revision_and_final_checks/gate_report.md
- source_authenticity_report: citation_authenticity_report.md

- recommendation: PROCEED
- strongest_support:
  - artifact chain is complete enough to demonstrate the workflow
  - current citations are authentic enough for demo-scale writing: {", ".join(auth_decisions["PROCEED"]) or "none"}
- allowed_claim_scope:
  - workflow demonstration
  - evidence-grounded writing system framing
- residual_risks:
  - corpus size is too small for submission-grade synthesis
  - failed gate checks remain: {"; ".join(gate_failures) if gate_failures else "none"}
""",
    )

    write(
        refine_case,
        f"""# Refine Case

- source_packet: decision_packet.md
- source_gate_report: 08_revision_and_final_checks/gate_report.md
- source_authenticity_report: citation_authenticity_report.md

- recommendation: REFINE
- blocking_weaknesses:
  - gate report still contains failed coverage thresholds: {"yes" if fail_gate else "no"}
  - specific failed checks: {"; ".join(gate_failures) if gate_failures else "none"}
  - authenticity refine count: {refine_count}
- minimum_upgrades_needed:
  - expand candidate pool and full-text coverage
  - increase extracted evidence rows
  - rerun gate and authenticity checks
- why_not_pivot:
  - current direction is coherent; the main problem is insufficiency, not structural invalidity
""",
    )

    write(
        pivot_case,
        f"""# Pivot Case

- source_packet: decision_packet.md
- source_gate_report: 08_revision_and_final_checks/gate_report.md
- source_authenticity_report: citation_authenticity_report.md

- recommendation: PIVOT
- strongest_counterargument:
  - if the user insists on strong literature-backed claims immediately, the current corpus is too weak
- critical_issues:
  - authenticity pivot count: {pivot_count}
  - citations at pivot risk: {", ".join(auth_decisions["PIVOT"]) or "none"}
  - failed gate thresholds: {"; ".join(gate_failures) if gate_failures else "none"}
- alternative_direction:
  - downgrade the output to workflow demonstration only, or re-scope to a narrower pilot note
""",
    )

    if pivot_count > 0:
        final_decision = "PIVOT"
        blocks_handoff = "yes"
        rationale = "At least one citation authenticity result requires pivot; the current claim structure should be changed before writing proceeds."
    elif fail_gate or refine_count > 0:
        final_decision = "REFINE"
        blocks_handoff = "yes"
        rationale = "The direction is coherent, but gate or authenticity checks show the project is not yet safe for strong handoff."
    else:
        final_decision = "PROCEED"
        blocks_handoff = "no"
        rationale = (
            "Gate and authenticity checks are strong enough for current writing scope."
        )

    write(
        decision_record,
        f"""# Decision Record

- source_packet: decision_packet.md
- source_gate_report: 08_revision_and_final_checks/gate_report.md
- source_authenticity_report: citation_authenticity_report.md
- source_stance_files: proceed_case.md, refine_case.md, pivot_case.md

- final_decision: {final_decision}
- confidence: high
- rationale: {rationale}
- consensus_points:
  - the artifact-driven workflow is operational
  - the current decision is grounded in gate and authenticity artifacts
  - proceed-eligible citations: {", ".join(auth_decisions["PROCEED"]) or "none"}
- disagreement_points:
  - proceed remains acceptable only for a narrow demo scope if refine conditions are ignored
  - failed gate checks still argue against strong handoff: {"; ".join(gate_failures) if gate_failures else "none"}
- required_next_actions:
  - review proceed_case.md
  - review refine_case.md
  - review pivot_case.md
  - follow the chosen path before handoff
- blocks_handoff: {blocks_handoff}
""",
    )

    print(f"[ok] wrote stance files and decision record in {root}")


if __name__ == "__main__":
    main()
