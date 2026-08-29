#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path

import requests
from PIL import Image, ImageDraw

DEFAULT_TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
DEFAULT_OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate"


def load_provider_config(path: str | None) -> dict:
    if not path:
        return {}
    config_path = Path(path).expanduser()
    if not config_path.exists():
        raise SystemExit(f"Provider config not found: {config_path}")
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return data.get("ocr_provider", data)


def fetch_access_token(*, api_key: str, secret_key: str, token_url: str, timeout: int) -> str:
    response = requests.post(
        token_url,
        params={
            "grant_type": "client_credentials",
            "client_id": api_key,
            "client_secret": secret_key,
        },
        timeout=(20, timeout),
    )
    response.raise_for_status()
    payload = response.json()
    token = payload.get("access_token")
    if not token:
        raise RuntimeError(f"Baidu cloud token response did not contain access_token: {payload}")
    return token


def bbox_from_location(location: dict) -> list[float]:
    left = float(location["left"])
    top = float(location["top"])
    width = float(location["width"])
    height = float(location["height"])
    return [left, top, left + max(width, 0), top + max(height, 0)]


def poly_from_vertexes(vertexes: list[dict] | None, location: dict) -> list[list[float]]:
    if vertexes:
        return [[float(point["x"]), float(point["y"])] for point in vertexes]
    x1, y1, x2, y2 = bbox_from_location(location)
    return [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]


def normalize_result(payload: dict) -> list[dict]:
    items = []
    for entry in payload.get("words_result", []) or []:
        text = str(entry.get("words", "")).strip()
        location = entry.get("location")
        if not text or not location:
            continue
        prob = entry.get("probability", {}) or {}
        score = float(prob.get("average", 1.0))
        vertexes = entry.get("vertexes_location") or entry.get("min_finegrained_vertexes_location")
        bbox = bbox_from_location(location)
        poly = poly_from_vertexes(vertexes, location)
        items.append({
            "text": text,
            "score": score,
            "poly": poly,
            "bbox": bbox,
        })
    return items


def annotate(image_path: Path, items: list[dict], out_path: Path) -> None:
    im = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(im)
    for i, item in enumerate(items, 1):
        x1, y1, x2, y2 = item["bbox"]
        color = "green" if item["score"] >= 0.72 else "red"
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3 if color == "green" else 2)
        draw.text((x1, max(0, y1 - 14)), str(i), fill=color)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    im.save(out_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Baidu cloud OCR on one slide image and emit the same OCR JSON contract as other OCR providers.")
    parser.add_argument("--image", required=True)
    parser.add_argument("--ocr-json", required=True)
    parser.add_argument("--annotation", required=True)
    parser.add_argument("--provider-config", help="JSON config containing baidu_cloud_ocr credentials and optional OCR settings")
    parser.add_argument("--api-key-env", help="Environment variable name containing the Baidu OCR API Key")
    parser.add_argument("--secret-key-env", help="Environment variable name containing the Baidu OCR Secret Key")
    parser.add_argument("--api-key", help="Direct API key value; prefer env vars or provider config")
    parser.add_argument("--secret-key", help="Direct secret key value; prefer env vars or provider config")
    parser.add_argument("--ocr-url", default=DEFAULT_OCR_URL)
    parser.add_argument("--token-url", default=DEFAULT_TOKEN_URL)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    provider = load_provider_config(args.provider_config)
    api_key_env = args.api_key_env or provider.get("api_key_env") or "BAIDU_OCR_API_KEY"
    secret_key_env = args.secret_key_env or provider.get("secret_key_env") or "BAIDU_OCR_SECRET_KEY"
    api_key = args.api_key or provider.get("api_key") or os.environ.get(api_key_env)
    secret_key = args.secret_key or provider.get("secret_key") or os.environ.get(secret_key_env)
    if not api_key or not secret_key:
        raise SystemExit(f"Missing Baidu OCR credentials. Set {api_key_env} and {secret_key_env}, or pass --api-key/--secret-key.")

    image_path = Path(args.image).expanduser()
    if not image_path.exists():
        raise SystemExit(f"Image not found: {image_path}")
    access_token = fetch_access_token(
        api_key=api_key,
        secret_key=secret_key,
        token_url=provider.get("token_url", args.token_url),
        timeout=args.timeout,
    )
    image_b64 = base64.b64encode(image_path.read_bytes()).decode("ascii")
    response = requests.post(
        f"{provider.get('ocr_url', args.ocr_url)}?access_token={access_token}",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "image": image_b64,
            "language_type": provider.get("language_type", "CHN_ENG"),
            "detect_direction": str(provider.get("detect_direction", True)).lower(),
            "paragraph": str(provider.get("paragraph", False)).lower(),
            "probability": str(provider.get("probability", True)).lower(),
            "vertexes_location": str(provider.get("vertexes_location", True)).lower(),
        },
        timeout=(20, args.timeout),
    )
    response.raise_for_status()
    payload = response.json()
    items = normalize_result(payload)

    ocr_json = Path(args.ocr_json)
    annotation = Path(args.annotation)
    ocr_json.parent.mkdir(parents=True, exist_ok=True)
    ocr_json.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    annotate(image_path, items, annotation)
    print(json.dumps({"image": str(image_path), "ocr_json": str(ocr_json), "annotation": str(annotation), "items": len(items)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
