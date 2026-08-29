from __future__ import annotations

import argparse
import csv
import importlib
from pathlib import Path
from typing import Final, cast

FULLTEXT_ACQUISITION_HEADERS: Final[list[str]] = cast(
    list[str],
    importlib.import_module(
        ".review_project_schema" if __package__ else "review_project_schema",
        package=__package__,
    ).FULLTEXT_ACQUISITION_HEADERS,
)


QUALITY_RULES: Final[list[tuple[str, list[str], str]]] = [
    (
        "login-wall",
        ["登录", "注册", "institution login", "绑定机构", "扫码"],
        "metadata-only",
    ),
    (
        "navigation-page",
        ["首页", "客服", "网站地图", "公众号", "浏览器版本过低"],
        "metadata-only",
    ),
    ("abstract-page", ["摘要", "abstract"], "partial"),
    (
        "fulltext-like",
        ["方法", "结果", "discussion", "introduction", "references"],
        "likely-fulltext",
    ),
]


def classify_text(text: str) -> tuple[str, str]:
    lowered = text.lower()
    for label, hints, acquisition_status in QUALITY_RULES:
        if any(hint.lower() in lowered for hint in hints):
            return label, acquisition_status if len(text) > 500 else "metadata-only"
    return ("unknown", "acquired" if len(text) > 500 else "metadata-only")


def read_acquisition_row(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            row = cast(dict[str, str], row)
            return {
                header: row.get(header, "") for header in FULLTEXT_ACQUISITION_HEADERS
            }
    return {header: "" for header in FULLTEXT_ACQUISITION_HEADERS}


def write_acquisition_row(path: Path, row: dict[str, str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FULLTEXT_ACQUISITION_HEADERS)
        _ = writer.writeheader()
        _ = writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Classify extracted acquisition text into quality/access buckets."
    )
    parser.add_argument("--acquisition-csv", required=True)
    parser.add_argument("--text-file", required=True)
    args = parser.parse_args()

    acquisition_csv = cast(str, args.acquisition_csv)
    text_file = cast(str, args.text_file)
    acquisition_path = Path(acquisition_csv).expanduser().resolve()
    text_path = Path(text_file).expanduser().resolve()
    text = (
        text_path.read_text(encoding="utf-8", errors="ignore")
        if text_path.exists()
        else ""
    )

    row = read_acquisition_row(acquisition_path)
    quality_label, acquisition_status = classify_text(text)
    row["acquisition_status"] = acquisition_status
    row["readable"] = "yes" if text else ""
    row["is_complete_full_text"] = (
        "yes" if quality_label == "fulltext-like" and len(text) > 2000 else ""
    )
    row["has_abstract"] = (
        "yes"
        if "摘要" in text or "abstract" in text.lower()
        else row.get("has_abstract", "")
    )
    row["access_notes"] = "; ".join(
        filter(None, [row.get("access_notes", ""), f"quality_label={quality_label}"])
    )
    if quality_label == "login-wall":
        row["paywalled"] = "yes"

    write_acquisition_row(acquisition_path, row)
    print(f"[ok] classified acquisition as {quality_label}: {acquisition_path}")


if __name__ == "__main__":
    main()
