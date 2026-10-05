from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

from common import require_file


def find_soffice() -> str | None:
    candidates = [os.environ.get("LIBREOFFICE_BIN"), shutil.which("soffice"), shutil.which("libreoffice"), shutil.which("lowriter")]
    candidates += [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]
    return next((item for item in candidates if item and Path(item).exists()), None)


def render_images(pdf: Path, output_dir: Path) -> list[str]:
    try:
        import fitz
        document = fitz.open(pdf)
        paths = []
        for index, page in enumerate(document, 1):
            pixmap = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
            target = output_dir / f"page-{index:03d}.png"
            pixmap.save(target)
            paths.append(str(target))
        return paths
    except ImportError:
        converter = shutil.which("pdftoppm")
        if not converter:
            raise RuntimeError("PyMuPDF or pdftoppm is required to render PDF pages")
        prefix = output_dir / "page"
        subprocess.run([converter, "-png", str(pdf), str(prefix)], check=True, capture_output=True)
        return [str(path) for path in sorted(output_dir.glob("page-*.png"))]


def main() -> int:
    parser = argparse.ArgumentParser(description="Render DOCX to PDF and page images for visual QA")
    parser.add_argument("docx", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    source = require_file(args.docx, "DOCX")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    soffice = find_soffice()
    if not soffice:
        result = {"status": "blocked", "reason": "LibreOffice/soffice was not found", "docx": str(source)}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2
    run = subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(args.output_dir), str(source)], text=True, capture_output=True)
    pdf = args.output_dir / f"{source.stem}.pdf"
    if run.returncode != 0 or not pdf.exists():
        result = {"status": "blocked", "reason": run.stderr or run.stdout or "DOCX to PDF conversion failed", "docx": str(source)}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2
    try:
        pages = render_images(pdf, args.output_dir)
    except RuntimeError as exc:
        result = {"status": "blocked", "reason": str(exc), "pdf": str(pdf)}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2
    result = {"status": "rendered", "pdf": str(pdf), "pages": pages, "page_count": len(pages)}
    (args.output_dir / "render.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
