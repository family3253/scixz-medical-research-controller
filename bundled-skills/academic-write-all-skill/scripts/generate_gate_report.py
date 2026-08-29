from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import datetime
from pathlib import Path

from review_project_schema import PROJECT_DEFAULT_PATHS


def load_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_year(value: str) -> int | None:
    digits = "".join(ch for ch in (value or "") if ch.isdigit())
    if len(digits) < 4:
        return None
    year = int(digits[:4])
    return year if 1900 <= year <= 2100 else None


def truthy(value: str) -> bool:
    return (value or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
        "include",
        "included",
        "core",
    }


def status(ok: bool, label: str, detail: str) -> str:
    marker = "PASS" if ok else "FAIL"
    return f"- [{marker}] {label}: {detail}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a lightweight review-project gate report."
    )
    parser.add_argument("project_dir")
    args = parser.parse_args()

    root = Path(args.project_dir).expanduser().resolve()
    candidate_rows = load_rows(root / PROJECT_DEFAULT_PATHS["candidate_csv"])
    abstract_rows = load_rows(root / PROJECT_DEFAULT_PATHS["abstract_screen_csv"])
    fulltext_screen_rows = load_rows(
        root / PROJECT_DEFAULT_PATHS["fulltext_screen_csv"]
    )
    fulltext_review_rows = load_rows(
        root / PROJECT_DEFAULT_PATHS["fulltext_review_csv"]
    )
    evidence_rows = load_rows(root / PROJECT_DEFAULT_PATHS["evidence_csv"])

    unique_candidates = [
        r
        for r in candidate_rows
        if not (r.get("duplicate_status") or "").startswith("duplicate")
    ]
    abstract_included = [
        r for r in abstract_rows if truthy(r.get("enter_full_text_stage", ""))
    ]
    fulltext_included = [
        r for r in fulltext_screen_rows if truthy(r.get("included", ""))
    ]
    core_readings = [
        r for r in fulltext_review_rows if truthy(r.get("is_core_reading", ""))
    ]
    evidence_core = [
        r
        for r in evidence_rows
        if (
            r.get("manuscript_role", "").strip().lower() in {"core", "claim", "primary"}
        )
    ]

    current_year = datetime.now().year
    candidate_years = [parse_year(r.get("year", "")) for r in unique_candidates]
    valid_years = [y for y in candidate_years if y is not None]
    recent_ratio = None
    if valid_years:
        recent_ratio = sum(1 for y in valid_years if y >= current_year - 5) / len(
            valid_years
        )

    topic_counter = Counter(
        r.get("topic_tag", "").strip()
        for r in unique_candidates
        if r.get("topic_tag", "").strip()
    )

    lines = [
        "# Gate Report",
        "",
        f"Generated at: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Pipeline Counts",
        f"- Candidate pool rows: {len(candidate_rows)}",
        f"- Unique candidates: {len(unique_candidates)}",
        f"- Entered full-text stage: {len(abstract_included)}",
        f"- Full-text included: {len(fulltext_included)}",
        f"- Core readings: {len(core_readings)}",
        f"- Evidence extraction rows: {len(evidence_rows)}",
        f"- Core evidence rows: {len(evidence_core)}",
        "",
        "## Gate Checks",
        status(
            len(unique_candidates) >= 30,
            "Candidate coverage",
            f"need >= 30 unique candidates, got {len(unique_candidates)}",
        ),
        status(
            len(abstract_included) >= 10,
            "Full-text pipeline",
            f"need >= 10 records entering full-text stage, got {len(abstract_included)}",
        ),
        status(
            len(fulltext_included) >= 8,
            "Included full texts",
            f"need >= 8 included full texts, got {len(fulltext_included)}",
        ),
        status(
            len(evidence_rows) >= 8,
            "Evidence extraction",
            f"need >= 8 extracted evidence rows, got {len(evidence_rows)}",
        ),
    ]
    if recent_ratio is not None:
        lines.append(
            status(
                recent_ratio >= 0.35,
                "Recency ratio",
                f"need >= 35% within last 5 years, got {recent_ratio:.1%}",
            )
        )
    else:
        lines.append(
            "- [WARN] Recency ratio: could not compute from available year fields"
        )

    lines.extend(["", "## Topic Coverage"])
    if topic_counter:
        for topic, count in topic_counter.most_common():
            lines.append(f"- {topic}: {count}")
    else:
        lines.append("- No topic tags recorded yet")

    lines.extend(
        [
            "",
            "## Interpretation",
            "- This is a lightweight gate report, not a guarantee of review completeness.",
            "- If counts fail, narrow claims or continue retrieval/screening before drafting strong synthesis.",
            "- If topic coverage is lopsided, do not write balanced review sections as if coverage were even.",
        ]
    )

    output_path = root / PROJECT_DEFAULT_PATHS["gate_report_md"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    legacy_output = root / "08_revision_and_final_checks" / "gate_report.md"
    if legacy_output != output_path:
        legacy_output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[ok] wrote gate report: {output_path}")


if __name__ == "__main__":
    main()
