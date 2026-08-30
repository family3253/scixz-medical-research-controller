"""Guard manuscript-derived outputs from entering the SciXZ source tree."""

from __future__ import annotations

from pathlib import Path
from typing import Optional


def ensure_private_output_path(path: Path, source_root: Optional[Path] = None) -> Path:
    """Return a resolved output path unless it is inside the source checkout."""
    destination = Path(path).expanduser().resolve()
    root = (source_root or Path(__file__).resolve().parents[1]).expanduser().resolve()
    try:
        destination.relative_to(root)
    except ValueError:
        return destination
    raise ValueError(
        "Refusing to write a manuscript-derived artifact inside the SciXZ source tree; "
        "choose a private output directory outside the checkout"
    )
