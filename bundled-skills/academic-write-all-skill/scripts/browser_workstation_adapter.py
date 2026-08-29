from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from provider_adapter_common import (
    load_json,
    normalize_candidate_row,
    render_templates,
    write_candidate_rows,
)


def require_playwright():
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError as exc:
        raise SystemExit(
            "Playwright is required for browser_workstation_adapter.py. Install with: pip install playwright && playwright install"
        ) from exc
    return sync_playwright


def run_action(page, action: dict[str, Any], download_dir: Path | None) -> Path | None:
    action_type = action.get("type")
    selector = action.get("selector")
    locator = page.locator(selector).nth(action.get("nth", 0)) if selector else None
    if action_type == "goto":
        page.goto(
            action["url"], wait_until=action.get("wait_until", "domcontentloaded")
        )
        return None
    if action_type == "fill":
        if locator is None:
            raise SystemExit("fill action requires selector")
        locator.fill(action.get("value", ""))
        return None
    if action_type == "click":
        if locator is None:
            raise SystemExit("click action requires selector")
        locator.click()
        return None
    if action_type == "click_text":
        page.get_by_text(action["text"], exact=action.get("exact", False)).click()
        return None
    if action_type == "press":
        if locator is None:
            raise SystemExit("press action requires selector")
        locator.press(action["key"])
        return None
    if action_type == "wait_for_selector":
        if locator is None:
            raise SystemExit("wait_for_selector action requires selector")
        locator.wait_for(timeout=action.get("timeout", 30000))
        return None
    if action_type == "wait_for_timeout":
        page.wait_for_timeout(action.get("ms", 1000))
        return None
    if action_type == "download":
        if download_dir is None:
            raise SystemExit("download action requires --download-dir")
        download_dir.mkdir(parents=True, exist_ok=True)
        trigger = action.get("trigger", {})
        with page.expect_download() as download_info:
            run_action(page, trigger, download_dir)
        download = download_info.value
        target = download_dir / action.get("save_as", download.suggested_filename)
        download.save_as(str(target))
        return target
    raise SystemExit(f"Unsupported browser action type: {action_type}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run an authorized browser workstation workflow and normalize extracted rows."
    )
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--query", default="")
    parser.add_argument("--institution-filter", default="")
    parser.add_argument("--search-batch", default="")
    parser.add_argument("--database-source", default="browser-workstation")
    parser.add_argument("--source-provider", default="browser-workstation")
    parser.add_argument("--access-mode", default="authorized-browser")
    parser.add_argument("--download-dir", default="")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    config_path = Path(args.config).expanduser().resolve()
    raw_config = load_json(config_path)
    variables = {
        "query": args.query,
        "institution_filter": args.institution_filter,
        "today": datetime.now().strftime("%Y-%m-%d"),
    }
    config = render_templates(raw_config, variables)
    if args.validate_only:
        print(json.dumps(config, ensure_ascii=False, indent=2))
        return

    sync_playwright = require_playwright()
    search_batch = args.search_batch or datetime.now().strftime("browser-%Y%m%d-%H%M%S")
    retrieval_date = datetime.now().strftime("%Y-%m-%d")
    download_dir = (
        Path(args.download_dir).expanduser().resolve() if args.download_dir else None
    )

    extracted_rows: list[dict[str, Any]] = []
    download_artifacts: list[str] = []
    with sync_playwright() as playwright:
        browser_type = getattr(playwright, config.get("browser", "chromium"))
        launch_kwargs = {
            "headless": config.get("headless", False),
        }
        if config.get("channel"):
            launch_kwargs["channel"] = config["channel"]

        profile_dir = config.get("profile_dir")
        if profile_dir:
            context = browser_type.launch_persistent_context(
                profile_dir, accept_downloads=True, **launch_kwargs
            )
        else:
            browser = browser_type.launch(**launch_kwargs)
            context = browser.new_context(
                accept_downloads=True, storage_state=config.get("storage_state_path")
            )
        try:
            page = context.pages[0] if context.pages else context.new_page()
            for action in config.get("actions", []):
                download_path = run_action(page, action, download_dir)
                if download_path is not None:
                    download_artifacts.append(str(download_path))

            extract = config.get("extract", {})
            if extract.get("mode") == "evaluate":
                extracted_rows = page.evaluate(extract.get("script", "() => []"))
                if not isinstance(extracted_rows, list):
                    raise SystemExit(
                        "Browser extract script must return a list of row objects"
                    )
        finally:
            context.close()

    normalized = [
        normalize_candidate_row(
            row,
            {
                "search_batch": search_batch,
                "database_source": args.database_source,
                "source_provider": args.source_provider,
                "access_mode": args.access_mode,
                "retrieval_date": retrieval_date,
                "topic_tag": args.query,
                "institution_filter": args.institution_filter,
                "notes": "; ".join(
                    filter(None, [f"config={config_path.name}", *download_artifacts])
                ),
            },
        )
        for row in extracted_rows
        if isinstance(row, dict)
    ]

    output_path = Path(args.output).expanduser().resolve()
    write_candidate_rows(output_path, normalized)
    print(f"[ok] wrote {len(normalized)} normalized rows to {output_path}")
    if download_artifacts:
        print("[downloads]")
        for artifact in download_artifacts:
            print(f"- {artifact}")


if __name__ == "__main__":
    main()
