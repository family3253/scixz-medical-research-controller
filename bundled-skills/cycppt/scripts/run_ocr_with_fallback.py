#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
LOCAL_OCR_SCRIPT = SCRIPT_DIR / "run_ocr_slide.py"
PPOCR_API_SCRIPT = SCRIPT_DIR / "run_ppocrv5_api_slide.py"
BAIDU_CLOUD_OCR_SCRIPT = SCRIPT_DIR / "run_baidu_cloud_ocr_slide.py"


def load_json(path: str) -> dict:
    return json.loads(Path(path).expanduser().read_text(encoding="utf-8"))


def ocr_provider_candidates(config: dict) -> list[dict]:
    providers = config.get("ocr_providers")
    if isinstance(providers, list) and providers:
        return [entry for entry in providers if isinstance(entry, dict)]
    provider = config.get("ocr_provider")
    return [provider] if isinstance(provider, dict) else []


def candidate_label(provider: dict) -> str:
    return provider.get("kind", "unknown")


def run_candidate(
    provider: dict,
    *,
    image: str,
    ocr_json: str,
    annotation: str,
    raw_dir: str | None,
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    kind = provider.get("kind")

    if kind == "local_paddleocr_v5":
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tmp:
            json.dump({"ocr_provider": provider}, tmp, ensure_ascii=False, indent=2)
            tmp_path = tmp.name
        try:
            cmd = [
                sys.executable,
                str(LOCAL_OCR_SCRIPT),
                "--image", image,
                "--ocr-json", ocr_json,
                "--annotation", annotation,
                "--provider-config", tmp_path,
            ]
            return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=timeout, env=env)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    if kind == "paddle_ocr_v5_api":
        token_env = provider.get("api_key_env", "AISTUDIO_OCR_TOKEN")
        if token_env in os.environ:
            env[token_env] = os.environ[token_env]
        cmd = [
            sys.executable,
            str(PPOCR_API_SCRIPT),
            "--image", image,
            "--ocr-json", ocr_json,
            "--annotation", annotation,
            "--job-url", provider.get("job_url", "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs"),
            "--model", provider.get("model", "PP-OCRv5"),
            "--poll-interval", str(provider.get("poll_interval_seconds", 5)),
            "--timeout", str(timeout),
        ]
        if raw_dir:
            cmd.extend(["--raw-dir", raw_dir])
        return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=timeout, env=env)

    if kind == "baidu_cloud_ocr":
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tmp:
            json.dump({"ocr_provider": provider}, tmp, ensure_ascii=False, indent=2)
            tmp_path = tmp.name
        try:
            cmd = [
                sys.executable,
                str(BAIDU_CLOUD_OCR_SCRIPT),
                "--image", image,
                "--ocr-json", ocr_json,
                "--annotation", annotation,
                "--provider-config", tmp_path,
                "--timeout", str(timeout),
            ]
            return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=timeout, env=env)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    raise SystemExit(f"Unsupported OCR provider kind for fallback wrapper: {kind}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run OCR with provider fallback. Tries configured OCR providers in order until one succeeds.")
    parser.add_argument("--image", required=True)
    parser.add_argument("--ocr-json", required=True)
    parser.add_argument("--annotation", required=True)
    parser.add_argument("--provider-config", required=True, help="JSON config containing ocr_provider or ocr_providers")
    parser.add_argument("--raw-dir", help="Optional raw-dir for API-based OCR candidates")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    config = load_json(args.provider_config)
    candidates = ocr_provider_candidates(config)
    if not candidates:
        raise SystemExit("No OCR provider candidates found in provider config.")

    failures: list[str] = []
    for index, provider in enumerate(candidates, start=1):
        candidate_raw_dir = None
        if args.raw_dir:
            candidate_raw_dir = str(Path(args.raw_dir) / f"{index:02d}_{candidate_label(provider)}")
        result = run_candidate(
            provider,
            image=args.image,
            ocr_json=args.ocr_json,
            annotation=args.annotation,
            raw_dir=candidate_raw_dir,
            timeout=args.timeout,
        )
        if result.returncode == 0:
            if result.stdout:
                print(result.stdout.strip())
            return
        message = result.stderr.strip() or result.stdout.strip() or f"return code {result.returncode}"
        failures.append(f"{candidate_label(provider)} -> {message}")
        if index < len(candidates):
            print(
                f"OCR provider candidate {index}/{len(candidates)} failed: {candidate_label(provider)}. Trying next candidate.",
                file=sys.stderr,
            )

    raise SystemExit("All OCR provider candidates failed:\n" + "\n".join(failures))


if __name__ == "__main__":
    main()
