#!/usr/bin/env python3
"""Crop an original Figure/Table region from a PDF and write provenance metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import fitz  # PyMuPDF
except ImportError as exc:  # pragma: no cover - exercised only on missing dependency
    raise SystemExit("PyMuPDF is required: pip install pymupdf") from exc


def parse_rect(value: str) -> fitz.Rect:
    try:
        numbers = [float(part.strip()) for part in value.split(",")]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--rect must be x0,y0,x1,y1 in PDF points") from exc
    if len(numbers) != 4:
        raise argparse.ArgumentTypeError("--rect must contain four comma-separated values")
    rect = fitz.Rect(*numbers)
    if rect.is_empty or rect.is_infinite or rect.width <= 0 or rect.height <= 0:
        raise argparse.ArgumentTypeError("--rect must describe a non-empty rectangle")
    return rect


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def extract_evidence(
    pdf_path: Path,
    page_number: int,
    rect: fitz.Rect,
    kind: str,
    label: str,
    out_path: Path,
    dpi: int = 300,
    citation: str = "",
) -> dict[str, Any]:
    pdf_path = pdf_path.expanduser().resolve()
    out_path = out_path.expanduser().resolve()
    if page_number < 1:
        raise ValueError("--page is 1-based and must be >= 1")
    if dpi < 72:
        raise ValueError("--dpi must be >= 72")
    if out_path.suffix.casefold() != ".png":
        raise ValueError("--out must use a .png extension")

    with fitz.open(pdf_path) as document:
        if page_number > document.page_count:
            raise ValueError(f"PDF has {document.page_count} pages; requested page {page_number}")
        page = document.load_page(page_number - 1)
        clipped = rect & page.rect
        if clipped.is_empty or clipped.width <= 0 or clipped.height <= 0:
            raise ValueError("--rect does not overlap the requested PDF page")
        scale = dpi / 72.0
        pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=clipped, alpha=False)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        pixmap.save(out_path)

    metadata = {
        "schema_version": 1,
        "asset_id": out_path.stem,
        "label": label,
        "source_pdf": str(pdf_path),
        "source_page": page_number,
        "source_region": {
            "x0": round(clipped.x0, 3),
            "y0": round(clipped.y0, 3),
            "x1": round(clipped.x1, 3),
            "y1": round(clipped.y1, 3),
            "unit": "pdf_points",
        },
        "kind": kind,
        "evidence_mode": "original",
        "render_policy": "reconstruct_allowed" if kind == "table" else "original_preferred",
        "output_path": str(out_path),
        "citation": citation or f"{pdf_path.name}, p.{page_number}, {label}",
        "dpi": dpi,
        "pixel_size": [pixmap.width, pixmap.height],
        "allowed_transformations": ["proportional_scale", "crop_blank_margins", "external_annotation"],
        "forbidden_transformations": ["ai_redraw", "data_change", "legend_change", "aspect_ratio_change"],
    }
    metadata_path = out_path.with_suffix(".json")
    write_json(metadata_path, metadata)
    return {"image": str(out_path), "metadata": str(metadata_path), "asset": metadata}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--page", required=True, type=int, help="1-based PDF page number")
    parser.add_argument("--rect", required=True, type=parse_rect, help="x0,y0,x1,y1 in PDF points")
    parser.add_argument("--kind", required=True, choices=["figure", "table"])
    parser.add_argument("--label", required=True)
    parser.add_argument("--out", required=True, help="Output PNG path")
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--citation", default="")
    args = parser.parse_args()
    try:
        payload = extract_evidence(
            Path(args.pdf), args.page, args.rect, args.kind, args.label, Path(args.out), args.dpi, args.citation
        )
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({"passed": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"passed": True, **payload}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
