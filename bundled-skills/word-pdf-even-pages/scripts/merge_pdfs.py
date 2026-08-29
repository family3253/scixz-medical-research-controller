from __future__ import annotations

import argparse
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_pdf", type=Path)
    args = parser.parse_args()

    input_dir = args.input_dir.resolve()
    output_pdf = args.output_pdf.resolve()
    files = sorted(input_dir.glob("*.pdf"), key=lambda path: path.name)
    if not files:
        raise FileNotFoundError(f"No PDF files found in {input_dir}")

    writer = PdfWriter()
    source_pages = 0
    for pdf_path in files:
        reader = PdfReader(str(pdf_path))
        source_pages += len(reader.pages)
        writer.append(str(pdf_path))

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    writer.write(str(output_pdf))
    merged_pages = len(PdfReader(str(output_pdf)).pages)
    if merged_pages != source_pages:
        raise RuntimeError(
            f"Page mismatch: sources={source_pages}, merged={merged_pages}"
        )

    print(
        f"Merged {len(files)} PDFs and {merged_pages} pages into {output_pdf}"
    )


if __name__ == "__main__":
    main()
