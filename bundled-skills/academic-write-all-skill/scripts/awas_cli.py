from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent


def run(module_script: str, *args: str) -> int:
    cmd = [sys.executable, str(SCRIPT_DIR / module_script), *args]
    return subprocess.call(cmd)


def cmd_bootstrap(_args: argparse.Namespace) -> int:
    bootstrap = SKILL_ROOT / "bootstrap_academic_write_all_skill_runtime.bat"
    return subprocess.call(["cmd", "/c", str(bootstrap)])


def cmd_ipubmed(args: argparse.Namespace) -> int:
    extra: list[str] = ["--output", args.output, "--query", args.query]
    if args.download_dir:
        extra.extend(["--download-dir", args.download_dir])
    if args.validate_only:
        extra.append("--validate-only")
    return run("ipubmed_browser_adapter.py", *extra)


def cmd_cnki(args: argparse.Namespace) -> int:
    extra: list[str] = ["--output", args.output, "--query", args.query]
    if args.institution_filter:
        extra.extend(["--institution-filter", args.institution_filter])
    if args.download_dir:
        extra.extend(["--download-dir", args.download_dir])
    if args.validate_only:
        extra.append("--validate-only")
    return run("cnki_browser_adapter.py", *extra)


def cmd_doi_flow(args: argparse.Namespace) -> int:
    candidate = args.candidate_output
    acquisition = args.acquisition_output
    text = args.text_output
    exit_code = run(
        "doi_acquisition_adapter.py",
        args.doi,
        "--candidate-output",
        candidate,
        "--acquisition-output",
        acquisition,
        "--text-output",
        text,
    )
    if exit_code != 0:
        return exit_code
    return run(
        "classify_acquisition_artifact.py",
        "--acquisition-csv",
        acquisition,
        "--text-file",
        text,
    )


def cmd_handoff(args: argparse.Namespace) -> int:
    return run(
        "handoff_acquisition_to_project.py",
        "--project-dir",
        args.project_dir,
        "--candidate-csv",
        args.candidate_csv,
        "--acquisition-csv",
        args.acquisition_csv,
        "--text-file",
        args.text_file,
    )


def cmd_project_init(args: argparse.Namespace) -> int:
    extra: list[str] = [args.project_dir]
    if args.force:
        extra.append("--force")
    return run("init_review_project.py", *extra)


def cmd_project_status(args: argparse.Namespace) -> int:
    return run("session_state_driver.py", args.project_dir)


def cmd_project_gate(args: argparse.Namespace) -> int:
    return run("generate_gate_report.py", args.project_dir)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Unified CLI for AWAS runtime workflows."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    bootstrap = subparsers.add_parser(
        "bootstrap", help="Create/update the isolated AWAS runtime."
    )
    bootstrap.set_defaults(func=cmd_bootstrap)

    ipubmed = subparsers.add_parser("ipubmed", help="Run the IPubMed browser workflow.")
    ipubmed.add_argument("--output", required=True)
    ipubmed.add_argument("--query", required=True)
    ipubmed.add_argument("--download-dir", default="")
    ipubmed.add_argument("--validate-only", action="store_true")
    ipubmed.set_defaults(func=cmd_ipubmed)

    cnki = subparsers.add_parser("cnki", help="Run the CNKI browser workflow.")
    cnki.add_argument("--output", required=True)
    cnki.add_argument("--query", required=True)
    cnki.add_argument("--institution-filter", default="")
    cnki.add_argument("--download-dir", default="")
    cnki.add_argument("--validate-only", action="store_true")
    cnki.set_defaults(func=cmd_cnki)

    doi_flow = subparsers.add_parser(
        "doi-flow", help="Run DOI acquisition + classification."
    )
    doi_flow.add_argument("doi")
    doi_flow.add_argument("--candidate-output", required=True)
    doi_flow.add_argument("--acquisition-output", required=True)
    doi_flow.add_argument("--text-output", required=True)
    doi_flow.set_defaults(func=cmd_doi_flow)

    handoff = subparsers.add_parser(
        "handoff", help="Attach acquisition artifacts into an AWAS project."
    )
    handoff.add_argument("--project-dir", required=True)
    handoff.add_argument("--candidate-csv", required=True)
    handoff.add_argument("--acquisition-csv", required=True)
    handoff.add_argument("--text-file", required=True)
    handoff.set_defaults(func=cmd_handoff)

    project_init = subparsers.add_parser(
        "project-init", help="Initialize an AWAS review/thesis project scaffold."
    )
    project_init.add_argument("project_dir")
    project_init.add_argument("--force", action="store_true")
    project_init.set_defaults(func=cmd_project_init)

    project_status = subparsers.add_parser(
        "project-status", help="Show current session state for an AWAS project."
    )
    project_status.add_argument("project_dir")
    project_status.set_defaults(func=cmd_project_status)

    project_gate = subparsers.add_parser(
        "project-gate", help="Generate gate report for an AWAS project."
    )
    project_gate.add_argument("project_dir")
    project_gate.set_defaults(func=cmd_project_gate)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
