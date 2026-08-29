from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the bundled IPubMed browser workflow through the generic workstation adapter."
    )
    parser.add_argument("--config", default="")
    parser.add_argument("--output", required=True)
    parser.add_argument("--query", default="")
    parser.add_argument("--institution-filter", default="")
    parser.add_argument("--download-dir", default="")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    config = (
        Path(args.config).expanduser().resolve()
        if args.config
        else script_dir.parent
        / "assets"
        / "templates"
        / "ipubmed_browser_workflow.json"
    )
    cmd = [
        sys.executable,
        str(script_dir / "browser_workstation_adapter.py"),
        "--config",
        str(config),
        "--output",
        args.output,
        "--query",
        args.query,
        "--institution-filter",
        args.institution_filter,
        "--database-source",
        "ipubmed-browser",
        "--source-provider",
        "ipubmed",
        "--access-mode",
        "authorized-browser",
    ]
    if args.download_dir:
        cmd.extend(["--download-dir", args.download_dir])
    if args.validate_only:
        cmd.append("--validate-only")
    raise SystemExit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
