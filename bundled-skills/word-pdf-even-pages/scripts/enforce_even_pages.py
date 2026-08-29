from __future__ import annotations

import argparse
import csv
import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter


def find_pdftoppm(explicit: str | None) -> str:
    candidates = [
        explicit,
        shutil.which("pdftoppm"),
        r"D:\software\CTEX\MiKTeX\miktex\bin\x64\pdftoppm.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    raise FileNotFoundError("pdftoppm was not found")


def render_page(
    pdftoppm: str, pdf_path: Path, page_number: int, output_dir: Path
) -> Path:
    prefix = output_dir / f"{pdf_path.stem}_page_{page_number}"
    subprocess.run(
        [
            pdftoppm,
            "-f",
            str(page_number),
            "-l",
            str(page_number),
            "-r",
            "100",
            "-png",
            "-singlefile",
            str(pdf_path),
            str(prefix),
        ],
        check=True,
        capture_output=True,
    )
    return prefix.with_suffix(".png")


def inspect_render(image_path: Path) -> dict[str, float | int | bool]:
    with Image.open(image_path) as source:
        grayscale = source.convert("L")
        histogram = grayscale.histogram()
        total_pixels = grayscale.width * grayscale.height
        dark_pixels = sum(histogram[:245])
        very_dark_pixels = sum(histogram[:210])
        width, height = grayscale.size

    threshold = max(100, math.ceil(total_pixels * 0.00002))
    return {
        "width_px": width,
        "height_px": height,
        "dark_pixels": dark_pixels,
        "very_dark_pixels": very_dark_pixels,
        "dark_ratio": dark_pixels / total_pixels,
        "pixel_threshold": threshold,
        "has_visible_content": dark_pixels > threshold or very_dark_pixels > 40,
    }


def copy_metadata(reader: PdfReader, writer: PdfWriter) -> None:
    if reader.metadata:
        metadata = {
            str(key): str(value)
            for key, value in reader.metadata.items()
            if value is not None
        }
        if metadata:
            writer.add_metadata(metadata)


def write_removed_last(reader: PdfReader, destination: Path) -> None:
    writer = PdfWriter()
    for page in reader.pages[:-1]:
        writer.add_page(page)
    copy_metadata(reader, writer)
    with destination.open("wb") as output:
        writer.write(output)


def write_added_blank(reader: PdfReader, destination: Path) -> None:
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    last_page = reader.pages[-1]
    writer.add_blank_page(
        width=float(last_page.mediabox.width),
        height=float(last_page.mediabox.height),
    )
    copy_metadata(reader, writer)
    with destination.open("wb") as output:
        writer.write(output)


def label_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in [
        Path(r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\simhei.ttf"),
        Path(r"C:\Windows\Fonts\arial.ttf"),
    ]:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def make_contact_sheet(items: list[dict[str, object]], output_path: Path) -> None:
    if not items:
        return

    columns, cell_width, image_height, label_height = 4, 330, 430, 70
    rows = math.ceil(len(items) / columns)
    sheet = Image.new(
        "RGB",
        (columns * cell_width, rows * (image_height + label_height)),
        "white",
    )
    draw = ImageDraw.Draw(sheet)
    font = label_font(18)

    for index, item in enumerate(items):
        row, column = divmod(index, columns)
        x = column * cell_width
        y = row * (image_height + label_height)
        with Image.open(Path(str(item["render_path"]))) as source:
            preview = source.convert("RGB")
            preview.thumbnail((cell_width - 20, image_height - 20))
            sheet.paste(
                preview,
                (
                    x + (cell_width - preview.width) // 2,
                    y + (image_height - preview.height) // 2,
                ),
            )
        label = (
            f"{item['filename']}\n"
            f"p={item['original_pages']} {item['action']} "
            f"ink={float(item['dark_ratio']):.6f}"
        )
        draw.multiline_text((x + 8, y + image_height + 4), label, fill="black", font=font)
        draw.rectangle(
            [x, y, x + cell_width - 1, y + image_height + label_height - 1],
            outline="#b0b0b0",
            width=1,
        )

    sheet.save(output_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--pdftoppm")
    args = parser.parse_args()

    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir.parent / "page_processing_report.csv"
    contact_path = output_dir.parent / "odd_last_pages_contact_sheet.png"
    render_dir = output_dir.parent / "odd_last_page_renders"
    render_dir.mkdir(exist_ok=True)
    pdftoppm = find_pdftoppm(args.pdftoppm)
    pdf_paths = sorted(input_dir.glob("*.pdf"), key=lambda path: path.name)
    if not pdf_paths:
        raise FileNotFoundError(f"No PDF files found in {input_dir}")

    rows: list[dict[str, object]] = []
    odd_items: list[dict[str, object]] = []

    with tempfile.TemporaryDirectory(prefix="even_pages_") as temp_name:
        temp_dir = Path(temp_name)
        for index, pdf_path in enumerate(pdf_paths, start=1):
            reader = PdfReader(str(pdf_path))
            original_pages = len(reader.pages)
            destination = output_dir / pdf_path.name
            row: dict[str, object] = {
                "filename": pdf_path.name,
                "original_pages": original_pages,
                "last_page_text_chars": "",
                "dark_pixels": "",
                "very_dark_pixels": "",
                "dark_ratio": "",
                "pixel_threshold": "",
                "action": "kept_even",
                "final_pages": original_pages,
            }

            if original_pages % 2 == 0:
                shutil.copy2(pdf_path, destination)
            else:
                text = (reader.pages[-1].extract_text() or "").strip()
                render_path = render_page(pdftoppm, pdf_path, original_pages, temp_dir)
                stats = inspect_render(render_path)
                has_content = bool(text) or bool(stats["has_visible_content"])
                row.update(
                    {
                        "last_page_text_chars": len(text),
                        "dark_pixels": stats["dark_pixels"],
                        "very_dark_pixels": stats["very_dark_pixels"],
                        "dark_ratio": stats["dark_ratio"],
                        "pixel_threshold": stats["pixel_threshold"],
                    }
                )

                if has_content:
                    write_added_blank(reader, destination)
                    row["action"] = "added_blank_page"
                    row["final_pages"] = original_pages + 1
                else:
                    write_removed_last(reader, destination)
                    row["action"] = "removed_blank_last_page"
                    row["final_pages"] = original_pages - 1

                persisted = render_dir / render_path.name
                shutil.copy2(render_path, persisted)
                odd_items.append({**row, "render_path": persisted})

            rows.append(row)
            print(
                f"[{index}/{len(pdf_paths)}] {pdf_path.name}: "
                f"{original_pages} -> {row['final_pages']} ({row['action']})"
            )

    fieldnames = list(rows[0].keys())
    with report_path.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    make_contact_sheet(odd_items, contact_path)
    invalid = [row for row in rows if int(row["final_pages"]) % 2]
    if invalid:
        raise RuntimeError(f"{len(invalid)} output PDF(s) still have odd page counts")

    print(f"Processed {len(rows)} PDFs into {output_dir}")


if __name__ == "__main__":
    main()

