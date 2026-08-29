from __future__ import annotations

import json
from pathlib import Path


PLOTCASE_CONTENT = Path(
    r"<USER_HOME>\Downloads\PlotCase-win-x64-1.0.3\PlotCase-win-x64-1.0.3\resources\app.asar.unpacked\content"
)


def pick_data_file(example_dir: Path) -> Path | None:
    data_dir = example_dir / "data"
    if not data_dir.exists() or not data_dir.is_dir():
        return None
    files = sorted(
        [path for path in data_dir.iterdir() if path.is_file()],
        key=lambda p: p.name.lower(),
    )
    return files[0] if files else None


def build_index(content_root: Path) -> list[dict]:
    items: list[dict] = []
    if not content_root.exists():
        raise FileNotFoundError(f"PlotCase content directory not found: {content_root}")

    for category_dir in sorted(
        [path for path in content_root.iterdir() if path.is_dir()],
        key=lambda p: p.name.lower(),
    ):
        for example_dir in sorted(
            [path for path in category_dir.iterdir() if path.is_dir()],
            key=lambda p: p.name.lower(),
        ):
            sample = pick_data_file(example_dir)
            if sample is None:
                continue

            title = example_dir.name
            category = category_dir.name
            item_id = f"{category}-{title}".replace(" ", "-").replace("/", "-")
            items.append(
                {
                    "id": item_id,
                    "title": title,
                    "category": category,
                    "keywords": [category, title],
                    "tags": [category],
                    "summary": f"PlotCase bundled example under {category}: {title}",
                    "example_path": sample.as_posix(),
                }
            )

    return items


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    root = script_dir.parent
    output_path = root / "assets" / "examples" / "examples.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    items = build_index(PLOTCASE_CONTENT)
    output_path.write_text(
        json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Generated {len(items)} PlotCase example entries at {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
