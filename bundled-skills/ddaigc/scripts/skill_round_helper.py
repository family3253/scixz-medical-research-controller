from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING, Callable, cast

if TYPE_CHECKING:
    from .aigc_records import get_workspace_root, load_records
    from .aigc_round_service import PROMPTS, normalize_path, relative_to_root, run_round
    from .docx_pipeline import read_docx_text
else:
    package_prefix = f"{__package__}." if __package__ else ""
    records_module = import_module(f"{package_prefix}aigc_records" or "aigc_records")
    round_module = import_module(f"{package_prefix}aigc_round_service" or "aigc_round_service")
    docx_module = import_module(f"{package_prefix}docx_pipeline" or "docx_pipeline")
    get_workspace_root = cast(Callable[[], Path], records_module.get_workspace_root)
    load_records = cast(Callable[[], dict[str, object]], records_module.load_records)
    PROMPTS = cast(dict[int, str], round_module.PROMPTS)
    normalize_path = cast(Callable[[Path], Path], round_module.normalize_path)
    relative_to_root = cast(Callable[[Path], str], round_module.relative_to_root)
    run_round = cast(Callable[..., dict[str, object]], round_module.run_round)
    read_docx_text = cast(Callable[[Path], str], docx_module.read_docx_text)

Transform = Callable[[str, str, int, str], str]
def get_intermediate_dir() -> Path:
    return get_workspace_root() / "finish" / "intermediate"


@dataclass
class RoundContext:
    doc_id: str
    round_number: int
    prompt_path: str
    source_path: Path
    input_text_path: Path
    output_text_path: Path
    manifest_path: Path
    source_kind: str
    extracted_from_docx: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "doc_id": self.doc_id,
            "round": self.round_number,
            "prompt_path": self.prompt_path,
            "source_path": str(self.source_path),
            "input_text_path": str(self.input_text_path),
            "output_text_path": str(self.output_text_path),
            "manifest_path": str(self.manifest_path),
            "source_kind": self.source_kind,
            "extracted_from_docx": self.extracted_from_docx,
        }


def detect_next_round(doc_id: str) -> int:
    rounds = _get_rounds(doc_id)
    completed = sorted(
        [
            round_value
            for round_item in rounds
            for round_value in [round_item.get("round")]
            if isinstance(round_value, int)
        ]
    )
    for expected in (1, 2, 3):
        if expected not in completed:
            return expected
    raise ValueError(f"Document already completed all 3 rounds: {doc_id}")


def build_round_context(source_path: Path | str, round_number: int | None = None) -> RoundContext:
    normalized_source = normalize_path(Path(source_path))
    doc_id = _build_doc_id(normalized_source)
    resolved_round = round_number or detect_next_round(doc_id)

    if resolved_round == 1:
        input_text_path, extracted_from_docx = ensure_skill_input_text(normalized_source)
    else:
        previous_round = resolved_round - 1
        input_text_path = _previous_round_output_path(doc_id, previous_round)
        extracted_from_docx = False

    stem = _doc_stem(doc_id)
    intermediate_dir = get_intermediate_dir()
    output_text_path = intermediate_dir / f"{stem}_round{resolved_round}.txt"
    manifest_path = intermediate_dir / f"{stem}_round{resolved_round}_manifest.json"

    return RoundContext(
        doc_id=doc_id,
        round_number=resolved_round,
        prompt_path=PROMPTS[resolved_round],
        source_path=normalized_source,
        input_text_path=input_text_path,
        output_text_path=output_text_path,
        manifest_path=manifest_path,
        source_kind=normalized_source.suffix.lower() or ".txt",
        extracted_from_docx=extracted_from_docx,
    )


def ensure_skill_input_text(source_path: Path | str) -> tuple[Path, bool]:
    normalized_source = normalize_path(Path(source_path))
    suffix = normalized_source.suffix.lower()

    if suffix == ".txt":
        return normalized_source, False

    if suffix == ".docx":
        intermediate_dir = get_intermediate_dir()
        intermediate_dir.mkdir(parents=True, exist_ok=True)
        extracted_path = intermediate_dir / f"{normalized_source.stem}_extracted.txt"
        extracted_path.write_text(read_docx_text(normalized_source), encoding="utf-8")
        return extracted_path, True

    raise ValueError(f"Unsupported input type for skill mode: {normalized_source}")


def run_skill_round(source_path: Path | str, transform: Transform, round_number: int | None = None) -> dict[str, object]:
    context = build_round_context(source_path, round_number=round_number)
    result = run_round(
        doc_id=context.doc_id,
        round_number=context.round_number,
        input_path=context.input_text_path,
        output_path=context.output_text_path,
        manifest_path=context.manifest_path,
        transform=transform,
    )
    result["skill_context"] = context.to_dict()
    return result


def dump_round_plan(source_path: Path | str, round_number: int | None = None) -> str:
    context = build_round_context(source_path, round_number=round_number)
    return json.dumps(context.to_dict(), ensure_ascii=False, indent=2)


def _build_doc_id(source_path: Path) -> str:
    return relative_to_root(source_path)


def _doc_stem(doc_id: str) -> str:
    return Path(doc_id).stem


def _get_rounds(doc_id: str) -> list[dict[str, object]]:
    records = load_records()
    entry = records.get(doc_id, {})
    rounds = entry.get("rounds", []) if isinstance(entry, dict) else []
    return [round_item for round_item in rounds if isinstance(round_item, dict)]


def _previous_round_output_path(doc_id: str, round_number: int) -> Path:
    rounds = _get_rounds(doc_id)
    for round_item in rounds:
        if round_item.get("round") == round_number:
            output_path = round_item.get("output_path")
            if not isinstance(output_path, str) or not output_path.strip():
                break
            return normalize_path(Path(output_path))
    raise ValueError(f"Round {round_number} output not found for document: {doc_id}")
