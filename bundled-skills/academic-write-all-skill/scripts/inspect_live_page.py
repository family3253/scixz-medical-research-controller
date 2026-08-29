from __future__ import annotations

import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect a live page and dump interactive selectors."
    )
    parser.add_argument("url")
    parser.add_argument("--output", required=True)
    parser.add_argument("--wait-ms", type=int, default=5000)
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=args.headless)
        context = browser.new_context()
        page = context.new_page()
        page.goto(args.url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(args.wait_ms)
        data = page.evaluate(
            r"""
            () => {
              const text = (node) => (node.innerText || node.textContent || '').replace(/\s+/g, ' ').trim();
              const pick = (selector, limit = 40) => Array.from(document.querySelectorAll(selector)).slice(0, limit).map((node, idx) => ({
                index: idx,
                tag: node.tagName,
                id: node.id || '',
                classes: Array.from(node.classList || []),
                name: node.getAttribute('name') || '',
                role: node.getAttribute('role') || '',
                type: node.getAttribute('type') || '',
                href: node.getAttribute('href') || '',
                value: node.value || '',
                placeholder: node.getAttribute('placeholder') || '',
                ariaLabel: node.getAttribute('aria-label') || '',
                text: text(node).slice(0, 300),
              }));
              return {
                title: document.title,
                url: location.href,
                buttons: pick('button, [role="button"], input[type="button"], input[type="submit"]'),
                inputs: pick('input, textarea, select'),
                links: pick('a'),
                tables: pick('table, [role="table"]', 20),
                textBlocks: pick('h1, h2, h3, h4, p, li, label, span', 120),
              };
            }
            """
        )
        output_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        browser.close()


if __name__ == "__main__":
    main()
