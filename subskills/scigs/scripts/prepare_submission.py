from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml

from common import load_yaml, package_sha256, require_file


ROOT = Path(__file__).resolve().parent


def run(name: str, *args, check: bool = False):
    return subprocess.run([sys.executable, str(ROOT / name), *map(str, args)], text=True, capture_output=True, check=check)


def parse_stdout_json(proc):
    text = proc.stdout.strip()
    candidates = [text]
    if "{" in text and "}" in text:
        candidates.append(text[text.find("{"):text.rfind("}") + 1])
    for candidate in candidates:
        try:
            result = json.loads(candidate)
            if isinstance(result, (dict, list)):
                return result
        except json.JSONDecodeError:
            continue
    return {"status": "blocked", "reason": proc.stderr or proc.stdout}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the content-locked journal submission preparation pipeline")
    parser.add_argument("--manuscript", type=Path, required=True)
    parser.add_argument("--requirements", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--term", action="append", default=[])
    parser.add_argument("--blinded", action="store_true")
    parser.add_argument("--reference-metadata", type=Path)
    parser.add_argument("--title-page", type=Path)
    parser.add_argument("--figures-dir", type=Path)
    parser.add_argument("--supplements-dir", type=Path)
    parser.add_argument("--skip-render", action="store_true")
    args = parser.parse_args()

    manuscript = require_file(args.manuscript, "Manuscript")
    requirements = load_yaml(args.requirements)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    working = args.output_dir / "working"
    working.mkdir(exist_ok=True)
    formatted = working / "manuscript-formatted.docx"
    format_log = working / "formatting.json"
    format_proc = run("format_docx.py", manuscript, formatted, "--requirements", args.requirements, "--change-log", format_log)
    format_result = json.loads(format_log.read_text(encoding="utf-8")) if format_log.exists() else parse_stdout_json(format_proc)
    final_docx = formatted

    reference_result = {"status": "not_requested"}
    if args.reference_metadata:
        reference_docx = working / "manuscript-references-formatted.docx"
        reference_proc = run("reference_style.py", formatted, reference_docx, "--metadata", args.reference_metadata, "--style", (requirements.get("actions") or {}).get("reference_style") or "vancouver")
        reference_result = parse_stdout_json(reference_proc)
        if reference_docx.exists() and reference_proc.returncode == 0:
            final_docx = reference_docx
    elif (requirements.get("actions") or {}).get("reference_style"):
        reference_result = {"status": "manual_action_required", "reason": "No reference metadata supplied"}

    if args.blinded:
        blinded = working / "manuscript-blinded.docx"
        anonymize_args = ["anonymize_docx.py", final_docx, blinded]
        for term in args.term:
            anonymize_args += ["--term", term]
        anonymize_proc = run(*anonymize_args)
        anonymize_result = parse_stdout_json(anonymize_proc)
        if blinded.exists() and anonymize_proc.returncode == 0:
            final_docx = blinded
    else:
        anonymize_result = {"status": "not_requested"}

    scan_path = working / "anonymity.json"
    scan_proc = run("anonymity_scan.py", final_docx, *sum((["--term", term] for term in args.term), []))
    scan_result = parse_stdout_json(scan_proc)

    audit_path = working / "reference-audit.json"
    audit_proc = run("reference_audit.py", final_docx, "--output", audit_path)
    audit_result = json.loads(audit_path.read_text(encoding="utf-8")) if audit_path.exists() else parse_stdout_json(audit_proc)

    assets_path = working / "assets.json"
    asset_args = ["asset_inventory.py", "--manuscript", final_docx, "--output", assets_path]
    if args.figures_dir:
        asset_args += ["--figures-dir", args.figures_dir]
    if args.supplements_dir:
        asset_args += ["--supplements-dir", args.supplements_dir]
    asset_proc = run(*asset_args)
    assets_result = json.loads(assets_path.read_text(encoding="utf-8")) if assets_path.exists() else parse_stdout_json(asset_proc)

    render_result = {"status": "blocked", "reason": "render skipped"}
    if not args.skip_render:
        render_proc = run("render_docx.py", final_docx, "--output-dir", working / "render")
        render_result = parse_stdout_json(render_proc)

    unverified = requirements.get("unverified_items") or []
    conflicts = requirements.get("conflicts") or []
    blockers = []
    if format_result.get("status") != "applied":
        blockers.append("DOCX formatting did not pass content-preservation check")
    if unverified:
        blockers.append(f"{len(unverified)} requirement(s) remain unverified")
    if conflicts:
        blockers.append("requirements conflicts remain unresolved")
    if audit_result.get("status") == "blocked":
        blockers.append("citation-to-bibliography audit has missing entries")
    if render_result.get("status") != "rendered":
        blockers.append("final DOCX was not rendered and visually inspected")
    if args.blinded and scan_result.get("risk") == "high":
        blockers.append("blinded output still contains high-risk identity findings")

    manual_actions = {
        reference_result.get("status"),
        audit_result.get("status"),
    }
    status = "BLOCKED" if blockers else ("READY_WITH_MANUAL_ACTIONS" if "manual_action_required" in manual_actions else "READY")
    change_log = args.output_dir / "FORMAT_CHANGE_LOG.md"
    change_log.write_text(
        "\n".join([
            "# FORMAT CHANGE LOG",
            "",
            f"- Checked: {date.today().isoformat()}",
            f"- Source manuscript: `{manuscript}`",
            f"- Final DOCX: `{final_docx}`",
            f"- Review model: `{requirements.get('review_model', 'unverified')}`",
            f"- Requirements file: `{args.requirements}`",
            "",
            "## Evidence",
            f"- Format actions: `{format_result.get('status')}`",
            f"- Reference conversion: `{reference_result.get('status')}`",
            f"- Anonymity scan: `{scan_result.get('risk', scan_result.get('status'))}`",
            f"- Reference audit: `{audit_result.get('status')}`",
            f"- Figure/table/supplement inventory: `{assets_result.get('manuscript', 'not available')}`",
            f"- Render: `{render_result.get('status')}`",
            "",
            "## Content integrity",
            f"- Format content preserved: `{format_result.get('content_preserved')}`",
            f"- Source SHA-256: `{package_sha256(manuscript)}`",
            "",
            "## Blockers / manual actions",
            *([f"- {item}" for item in blockers] or ["- None recorded by the automated gates."]),
            "",
            "## Status",
            f"`{status}`",
            "",
        ]),
        encoding="utf-8",
    )

    package_dir = args.output_dir / "submission-package"
    package_args = ["package_submission.py", "--destination", package_dir, "--manuscript", final_docx, "--requirements", args.requirements, "--change-log", change_log]
    if args.title_page:
        package_args += ["--title-page", args.title_page]
    if args.figures_dir:
        package_args += ["--figures-dir", args.figures_dir]
    if args.supplements_dir:
        package_args += ["--supplements-dir", args.supplements_dir]
    run(*package_args)

    result = {
        "status": status,
        "output_dir": str(args.output_dir),
        "final_docx": str(final_docx),
        "change_log": str(change_log),
        "submission_package": str(package_dir),
        "blockers": blockers,
    }
    (args.output_dir / "submission-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if status == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
