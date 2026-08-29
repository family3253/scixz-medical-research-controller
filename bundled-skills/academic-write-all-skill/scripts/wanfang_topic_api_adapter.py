from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

from provider_adapter_common import normalize_candidate_row, write_candidate_rows


DEFAULT_ENDPOINT = "https://api.wanfangdata.com.cn/topic_read/paper"


def compute_signature(secret: str, body: str) -> str:
    return hmac.new(
        secret.encode("utf-8"), body.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def post_json(
    url: str, payload: dict[str, object], headers: dict[str, str]
) -> dict[str, object]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    request.add_header("Content-Type", "application/json; charset=utf-8")
    for key, value in headers.items():
        if value:
            request.add_header(key, value)
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def load_config(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Query Wanfang topic API and normalize degree-paper results."
    )
    parser.add_argument("keyword")
    parser.add_argument("--output", required=True)
    parser.add_argument("--config")
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument(
        "--type", default="DEGREE", choices=["HIGH", "NEW", "DEGREE", "REVIEW"]
    )
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--database-source", default="wanfang-topic-api")
    parser.add_argument("--source-provider", default="wanfang")
    parser.add_argument("--access-mode", default="official-api")
    parser.add_argument("--search-batch", default="")
    parser.add_argument("--institution-filter", default="")
    parser.add_argument("--app-key", default="")
    parser.add_argument("--app-secret", default="")
    parser.add_argument("--ca-version", default="1")
    parser.add_argument(
        "--header", action="append", default=[], help="Extra header as Key=Value"
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config = load_config(
        Path(args.config).expanduser().resolve() if args.config else None
    )
    app_key = args.app_key or config.get("app_key", "")
    app_secret = args.app_secret or config.get("app_secret", "")
    retrieval_date = datetime.now().strftime("%Y-%m-%d")
    search_batch = args.search_batch or datetime.now().strftime("wanfang-%Y%m%d-%H%M%S")

    payload = {
        "keyword": args.keyword,
        "page": args.page,
        "type": args.type,
    }
    body = json.dumps(payload, ensure_ascii=False)
    headers = {
        "X-Ca-Version": config.get("ca_version", args.ca_version),
        "X-Ca-AppKey": app_key,
    }
    if app_secret:
        headers["X-Ca-Signature"] = compute_signature(app_secret, body)
    for header in args.header:
        if "=" in header:
            key, value = header.split("=", 1)
            headers[key.strip()] = value.strip()

    if args.dry_run:
        print(
            json.dumps(
                {"endpoint": args.endpoint, "payload": payload, "headers": headers},
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    try:
        response = post_json(args.endpoint, payload, headers)
    except urllib.error.HTTPError as exc:
        raise SystemExit(
            f"HTTP error from Wanfang API: {exc.code} {exc.reason}"
        ) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Network error from Wanfang API: {exc.reason}") from exc

    page_info = response.get("pageInfo", {}) if isinstance(response, dict) else {}
    raw_rows = page_info.get("pageDatas", []) if isinstance(page_info, dict) else []
    normalized = []
    for item in raw_rows:
        if not isinstance(item, dict):
            continue
        paper = (
            item.get("periodical") if isinstance(item.get("periodical"), dict) else item
        )
        normalized.append(
            normalize_candidate_row(
                paper,
                {
                    "search_batch": search_batch,
                    "database_source": args.database_source,
                    "source_provider": args.source_provider,
                    "access_mode": args.access_mode,
                    "retrieval_date": retrieval_date,
                    "topic_tag": args.keyword,
                    "institution_filter": args.institution_filter,
                    "notes": f"wanfang_type={args.type}",
                },
            )
        )

    output_path = Path(args.output).expanduser().resolve()
    write_candidate_rows(output_path, normalized)
    print(f"[ok] wrote {len(normalized)} normalized rows to {output_path}")


if __name__ == "__main__":
    main()
