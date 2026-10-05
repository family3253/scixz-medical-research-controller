"""DOCX metadata policy helpers for SciXZ-generated Word artifacts."""
from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

DEFAULT_DOCX_AUTHOR = "chenyechao"


def set_docx_author(document, author: str = DEFAULT_DOCX_AUTHOR):
    """Set the required Word core author and last-modified-by metadata."""
    document.core_properties.author = author
    document.core_properties.last_modified_by = author
    return document


def read_docx_author(path: str | Path) -> tuple[str, str]:
    """Read creator and last-modified-by values from a DOCX file."""
    with ZipFile(path) as archive:
        root = ET.fromstring(archive.read("docProps/core.xml"))
    ns = {
        "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
        "dc": "http://purl.org/dc/elements/1.1/",
    }
    creator = root.find("dc:creator", ns)
    modified = root.find("cp:lastModifiedBy", ns)
    return (
        creator.text if creator is not None and creator.text else "",
        modified.text if modified is not None and modified.text else "",
    )


def assert_docx_author(path: str | Path, author: str = DEFAULT_DOCX_AUTHOR) -> None:
    creator, modified = read_docx_author(path)
    if creator != author or modified != author:
        raise ValueError(
            f"DOCX metadata must be author={author!r}, last_modified_by={author!r}; "
            f"got author={creator!r}, last_modified_by={modified!r}: {path}"
        )
