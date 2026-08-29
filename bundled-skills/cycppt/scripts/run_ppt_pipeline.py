#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
PYTHON_EXE = sys.executable
PROMPT_BUILDER = SCRIPT_DIR / "01_build_slide_prompt_v20260504.py"
IMAGE_SCRIPT = SCRIPT_DIR / "run_gpt_image2_slide.py"
OCR_FALLBACK_SCRIPT = SCRIPT_DIR / "run_ocr_with_fallback.py"
CLEAN_INPUTS_SCRIPT = SCRIPT_DIR / "make_clean_inputs.py"
PPTX_SCRIPT = SCRIPT_DIR / "build_editable_pptx.py"
VALIDATE_SCRIPT = SCRIPT_DIR / "validate_outputs.py"


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def init_manifest(task_dir: Path, plan: dict[str, Any], provider_config_path: str | None) -> dict[str, Any]:
    deck = plan.get("deck", {})
    return {
        "task": {
            "id": task_dir.name,
            "created_at": iso_now(),
            "source_inputs": [],
            "target_slide_count": deck.get("total_slides", len(plan.get("slides", []))),
            "confirmed_by_user": True,
        },
        "providers": {
            "provider_config": provider_config_path,
        },
        "paths": {
            "task_dir": str(task_dir),
            "assets_dir": str(task_dir / "assets"),
            "slides_dir": str(task_dir / "slides"),
            "pptx_dir": str(task_dir / "pptx"),
            "ocr_dir": str(task_dir / "ocr"),
            "clean_inputs_dir": str(task_dir / "clean_inputs"),
            "clean_backgrounds_dir": str(task_dir / "clean_backgrounds"),
            "events_path": str(task_dir / "reports" / "orchestration_events.jsonl"),
            "image_only_pptx_out": str(task_dir / "pptx" / "final_image_only.pptx"),
            "editable_pptx_out": str(task_dir / "pptx" / "final_editable.pptx"),
        },
        "slides": [
            {
                "slide_id": slide["slide_id"],
                "status": "PENDING",
            }
            for slide in plan.get("slides", [])
        ],
        "events": [],
    }


def slide_record(manifest: dict[str, Any], slide_id: str) -> dict[str, Any]:
    for slide in manifest["slides"]:
        if slide["slide_id"] == slide_id:
            return slide
    raise KeyError(slide_id)


def write_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


def update_manifest(path: Path, manifest: dict[str, Any]) -> None:
    save_json(path, manifest)


def reference_images_for_slide(slide: dict[str, Any], slide_number: int, task_dir: Path) -> list[str]:
    refs: list[str] = []
    if slide_number >= 2:
        refs.append(str(task_dir / "slides" / "slide01.png"))
    if slide_number >= 3:
        refs.append(str(task_dir / "slides" / "slide02.png"))
    for asset in slide.get("assets", {}).get("required", []) or []:
        refs.append(str(asset))
    return refs


def run(cmd: list[str], *, timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONUTF8", "1")
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env=env,
    )


def ensure_prompt(task_dir: Path, plan_path: Path, slide_id: str, slide_number: int) -> Path:
    prompt_path = task_dir / "prompts" / f"{slide_id}_prompt.txt"
    if prompt_path.exists():
        return prompt_path
    result = run(
        [
            PYTHON_EXE,
            str(PROMPT_BUILDER),
            "--plan", str(plan_path),
            "--slide-id", slide_id,
            "--slide-number", str(slide_number),
            "--out", str(prompt_path),
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return prompt_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Lightweight PPT pipeline runner that orchestrates the existing scripts and records manifest/events.")
    parser.add_argument("--task-dir", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--provider-config", required=True)
    parser.add_argument("--timeout-image", type=int, default=1800)
    parser.add_argument("--timeout-ocr", type=int, default=300)
    parser.add_argument("--graphic-mode", choices=["off", "small-icons"], default="off")
    args = parser.parse_args()

    task_dir = Path(args.task_dir).expanduser().resolve()
    task_dir.mkdir(parents=True, exist_ok=True)
    for name in ["assets", "slides", "plans", "prompts", "pptx", "ocr", "clean_inputs", "clean_backgrounds", "logs", "reports"]:
        (task_dir / name).mkdir(parents=True, exist_ok=True)

    plan_path = Path(args.plan).expanduser().resolve()
    plan = load_json(plan_path)
    manifest = init_manifest(task_dir, plan, args.provider_config)
    manifest_path = task_dir / "reports" / "task_manifest.json"
    events_path = task_dir / "reports" / "orchestration_events.jsonl"
    update_manifest(manifest_path, manifest)

    write_event(events_path, {"ts": iso_now(), "event": "PROGRESS_UPDATE", "message": "任务规划：正在准备任务目录、素材清单、manifest 和 ppt_plan.json。"})

    slides = plan.get("slides", [])
    total = len(slides)

    for index, slide in enumerate(slides, start=1):
        slide_id = slide["slide_id"]
        actual_slide_number = int(slide.get("slide_number", index))
        slide_rec = slide_record(manifest, slide_id)
        prompt_path = ensure_prompt(task_dir, plan_path, slide_id, actual_slide_number)
        image_out = task_dir / "slides" / f"{slide_id}.png"
        if not image_out.exists():
            slide_rec["status"] = "IMAGE_GENERATING"
            update_manifest(manifest_path, manifest)
            write_event(events_path, {"ts": iso_now(), "slide_id": slide_id, "event": "IMAGE_GENERATING", "progress": f"{index-1}/{total}"})
            cmd = [
                PYTHON_EXE,
                str(IMAGE_SCRIPT),
                "--provider-config", args.provider_config,
                "--workflow-phase", "first_pass" if actual_slide_number == 1 else "followup",
                "--prompt-file", str(prompt_path),
                "--out", str(image_out),
                "--retries", "5",
            ]
            for ref in reference_images_for_slide(slide, actual_slide_number, task_dir):
                cmd.extend(["--image", ref])
            result = run(cmd, timeout=args.timeout_image)
            if result.returncode != 0:
                slide_rec["status"] = "FAILED_IMAGE"
                slide_rec["error"] = result.stderr or result.stdout
                update_manifest(manifest_path, manifest)
                raise SystemExit(result.stderr or result.stdout)
            write_event(events_path, {"ts": iso_now(), "slide_id": slide_id, "event": "IMAGE_READY", "path": str(image_out), "progress": f"{index}/{total}"})
        else:
            write_event(events_path, {"ts": iso_now(), "slide_id": slide_id, "event": "IMAGE_READY_SKIPPED", "path": str(image_out)})

        slide_rec["status"] = "IMAGE_READY"
        slide_rec["image"] = str(image_out)

        ocr_json = task_dir / "ocr" / f"{slide_id}_ocr.json"
        ocr_annotation = task_dir / "ocr" / f"{slide_id}_ocr_annotation.png"
        if not (ocr_json.exists() and ocr_annotation.exists()):
            ocr_cmd = [
                PYTHON_EXE,
                str(OCR_FALLBACK_SCRIPT),
                "--image", str(image_out),
                "--ocr-json", str(ocr_json),
                "--annotation", str(ocr_annotation),
                "--provider-config", args.provider_config,
                "--raw-dir", str(task_dir / "logs" / f"ocr_fallback_{slide_id}"),
            ]
            ocr_result = run(ocr_cmd, timeout=args.timeout_ocr)
            if ocr_result.returncode != 0:
                slide_rec["status"] = "FAILED_OCR"
                slide_rec["error"] = ocr_result.stderr or ocr_result.stdout
                update_manifest(manifest_path, manifest)
                raise SystemExit(ocr_result.stderr or ocr_result.stdout)
            write_event(events_path, {"ts": iso_now(), "slide_id": slide_id, "event": "OCR_READY", "path": str(ocr_json)})
        else:
            write_event(events_path, {"ts": iso_now(), "slide_id": slide_id, "event": "OCR_READY_SKIPPED", "path": str(ocr_json)})
        slide_rec["ocr_json"] = str(ocr_json)
        slide_rec["status"] = "OCR_READY"

        text_items_path = task_dir / "clean_inputs" / f"{slide_id}_all_ocr_text_items.json"
        graphic_items_path = task_dir / "clean_inputs" / f"{slide_id}_all_graphic_items.json"
        clean_inputs_cmd = [
            PYTHON_EXE,
            str(CLEAN_INPUTS_SCRIPT),
            "--image", str(image_out),
            "--ocr-json", str(ocr_json),
            "--out-dir", str(task_dir / "clean_inputs"),
            "--prompt-dir", str(task_dir / "prompts"),
            "--slide-id", slide_id,
            "--graphic-mode", args.graphic_mode,
        ]
        if not (text_items_path.exists() and graphic_items_path.exists()):
            clean_inputs_result = run(clean_inputs_cmd)
            if clean_inputs_result.returncode != 0:
                slide_rec["status"] = "FAILED_CLEAN_INPUTS"
                slide_rec["error"] = clean_inputs_result.stderr or clean_inputs_result.stdout
                update_manifest(manifest_path, manifest)
                raise SystemExit(clean_inputs_result.stderr or clean_inputs_result.stdout)
            write_event(events_path, {"ts": iso_now(), "slide_id": slide_id, "event": "CLEAN_INPUTS_READY"})
        else:
            write_event(events_path, {"ts": iso_now(), "slide_id": slide_id, "event": "CLEAN_INPUTS_READY_SKIPPED"})
        slide_rec["status"] = "CLEAN_INPUTS_READY"

        clean_prompt = task_dir / "prompts" / f"{slide_id}_clean_prompt.txt"
        binary_mask = task_dir / "clean_inputs" / f"{slide_id}_all_ocr_delete_binary_mask.png"
        clean_out = task_dir / "clean_backgrounds" / f"{slide_id}_clean_background.png"
        if not clean_out.exists():
            clean_cmd = [
                PYTHON_EXE,
                str(IMAGE_SCRIPT),
                "--provider-config", args.provider_config,
                "--workflow-phase", "followup",
                "--prompt-file", str(clean_prompt),
                "--image", str(image_out),
                "--image", str(ocr_annotation),
                "--image", str(binary_mask),
                "--out", str(clean_out),
                "--retries", "5",
            ]
            clean_result = run(clean_cmd, timeout=args.timeout_image)
            if clean_result.returncode != 0:
                slide_rec["status"] = "FAILED_CLEAN_BACKGROUND"
                slide_rec["error"] = clean_result.stderr or clean_result.stdout
                update_manifest(manifest_path, manifest)
                raise SystemExit(clean_result.stderr or clean_result.stdout)
            write_event(events_path, {"ts": iso_now(), "slide_id": slide_id, "event": "CLEAN_BACKGROUND_READY", "path": str(clean_out)})
        else:
            write_event(events_path, {"ts": iso_now(), "slide_id": slide_id, "event": "CLEAN_BACKGROUND_READY_SKIPPED", "path": str(clean_out)})
        slide_rec["clean_background"] = str(clean_out)
        slide_rec["text_items"] = str(text_items_path)
        slide_rec["graphic_items"] = str(graphic_items_path)
        slide_rec["status"] = "PPTX_READY_FOR_AGGREGATION"
        update_manifest(manifest_path, manifest)

    image_only_out = task_dir / "pptx" / "final_image_only.pptx"
    editable_out = task_dir / "pptx" / "final_editable.pptx"
    run([
        PYTHON_EXE,
        str(PPTX_SCRIPT),
        "--mode", "image-only",
        "--image-dir", str(task_dir / "slides"),
        "--manifest", str(plan_path),
        "--out", str(image_only_out),
    ])
    run([
        PYTHON_EXE,
        str(PPTX_SCRIPT),
        "--mode", "editable",
        "--ocr-dir", str(task_dir / "ocr"),
        "--clean-dir", str(task_dir / "clean_backgrounds"),
        "--source-image-dir", str(task_dir / "slides"),
        "--text-items-dir", str(task_dir / "clean_inputs"),
        "--graphic-items-dir", str(task_dir / "clean_inputs"),
        "--manifest", str(plan_path),
        "--out", str(editable_out),
    ])
    validate_out = task_dir / "reports" / "validate_outputs.json"
    run([
        PYTHON_EXE,
        str(VALIDATE_SCRIPT),
        "--manifest", str(plan_path),
        "--slides-dir", str(task_dir / "slides"),
        "--ocr-dir", str(task_dir / "ocr"),
        "--clean-dir", str(task_dir / "clean_backgrounds"),
        "--pptx", str(editable_out),
        "--report", str(validate_out),
    ])
    write_event(events_path, {"ts": iso_now(), "event": "VALIDATING_OUTPUTS", "message": "验证输出完成。"})
    manifest["paths"]["image_only_pptx_out"] = str(image_only_out)
    manifest["paths"]["editable_pptx_out"] = str(editable_out)
    update_manifest(manifest_path, manifest)
    print(json.dumps({"status": "success", "task_dir": str(task_dir), "manifest": str(manifest_path), "events": str(events_path), "image_only_pptx": str(image_only_out), "editable_pptx": str(editable_out), "validate_report": str(validate_out)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
