from __future__ import annotations

import argparse
import csv
import importlib
from pathlib import Path
from typing import Final, cast

schema_module = importlib.import_module(
    ".review_project_schema" if __package__ else "review_project_schema",
    package=__package__,
)
FULLTEXT_ACQUISITION_HEADERS: Final[list[str]] = cast(
    list[str], schema_module.FULLTEXT_ACQUISITION_HEADERS
)
PROJECT_DEFAULT_PATHS: Final[dict[str, str]] = cast(
    dict[str, str], schema_module.PROJECT_DEFAULT_PATHS
)


def load_single_row(path: Path, headers: list[str]) -> dict[str, str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            row = cast(dict[str, str], row)
            return {header: row.get(header, "") for header in headers}
    return {header: "" for header in headers}


def append_or_replace(path: Path, row: dict[str, str], key: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    headers = list(row.keys())
    if path.exists():
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames or headers
            for existing in reader:
                existing = cast(dict[str, str], existing)
                if existing.get(key) != row.get(key):
                    rows.append({field: existing.get(field, "") for field in headers})
    rows.append({field: row.get(field, "") for field in headers})
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        _ = writer.writeheader()
        _ = writer.writerows(rows)


def update_manifest(
    project_dir: Path, candidate_csv: Path, acquisition_csv: Path, text_file: Path
) -> None:
    manifest_path = project_dir / "session_manifest.md"
    lines = (
        manifest_path.read_text(encoding="utf-8").splitlines()
        if manifest_path.exists()
        else ["# Session Manifest", ""]
    )
    extra_note = f"- notes: latest_acquisition={acquisition_csv.relative_to(project_dir)}; latest_text={text_file.relative_to(project_dir)}"
    replaced = False
    for idx, line in enumerate(lines):
        if line.startswith("- current_stage:"):
            lines[idx] = "- current_stage: screening"
        if line.startswith("  - candidate_pool:"):
            lines[idx] = f"  - candidate_pool: {candidate_csv.relative_to(project_dir)}"
        if line.startswith("- notes:"):
            lines[idx] = extra_note
            replaced = True
    if not replaced:
        lines.append(extra_note)
    written = manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert written >= 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Attach acquisition artifacts to an AWAS project and move it into screening stage."
    )
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--candidate-csv", required=True)
    parser.add_argument("--acquisition-csv", required=True)
    parser.add_argument("--text-file", required=True)
    args = parser.parse_args()

    project_dir = Path(cast(str, args.project_dir)).expanduser().resolve()
    candidate_src = Path(cast(str, args.candidate_csv)).expanduser().resolve()
    acquisition_src = Path(cast(str, args.acquisition_csv)).expanduser().resolve()
    text_src = Path(cast(str, args.text_file)).expanduser().resolve()

    candidate_dst = project_dir / PROJECT_DEFAULT_PATHS["candidate_csv"]
    acquisition_dst = project_dir / PROJECT_DEFAULT_PATHS["fulltext_acquisition_csv"]
    text_dst = project_dir / "03_fulltext_acquisition_and_review" / text_src.name

    candidate_dst.parent.mkdir(parents=True, exist_ok=True)
    text_dst.parent.mkdir(parents=True, exist_ok=True)

    if candidate_src != candidate_dst:
        written = candidate_dst.write_text(
            candidate_src.read_text(encoding="utf-8-sig"), encoding="utf-8-sig"
        )
        assert written >= 0

    acquisition_row = load_single_row(acquisition_src, FULLTEXT_ACQUISITION_HEADERS)
    append_or_replace(acquisition_dst, acquisition_row, "citation_id")
    written = text_dst.write_text(
        text_src.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8"
    )
    assert written >= 0
    update_manifest(project_dir, candidate_dst, acquisition_dst, text_dst)

    print(f"[ok] candidate_pool -> {candidate_dst}")
    print(f"[ok] fulltext_acquisition -> {acquisition_dst}")
    print(f"[ok] text artifact -> {text_dst}")
    print(
        f"[ok] session manifest advanced to screening: {project_dir / 'session_manifest.md'}"
    )


if __name__ == "__main__":
    main()
