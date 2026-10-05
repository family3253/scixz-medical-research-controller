from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import yaml


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected a YAML mapping: {path}")
    return data


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def iter_docx_xml(path: Path):
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if name.endswith(".xml") or name.endswith(".rels"):
                yield name, archive.read(name)


def xml_text(path: Path) -> str:
    chunks: list[str] = []
    for _, raw in iter_docx_xml(path):
        try:
            root = ET.fromstring(raw)
        except ET.ParseError:
            continue
        for element in root.iter():
            if element.text and (element.tag.endswith("}t") or element.tag.endswith("}instrText")):
                chunks.append(element.text)
    return "\n".join(chunks)


def content_digest(path: Path) -> str:
    chunks: list[str] = []
    for name, raw in iter_docx_xml(path):
        if name not in {"word/document.xml", "word/footnotes.xml", "word/endnotes.xml"}:
            continue
        try:
            root = ET.fromstring(raw)
        except ET.ParseError:
            continue
        for element in root.iter():
            if element.text and element.tag.endswith("}t"):
                chunks.append(element.text)
    normalized = re.sub(r"\s+", " ", "\n".join(chunks)).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def package_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def has_dynamic_fields(path: Path) -> bool:
    for name, raw in iter_docx_xml(path):
        if not name.startswith("word/"):
            continue
        text = raw.decode("utf-8", errors="ignore")
        if "w:fldChar" in text or "ADDIN ZOTERO" in text or "ADDIN Mendeley" in text:
            return True
    return False


def require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        raise FileNotFoundError(f"{label} does not exist: {path}")
    return path
