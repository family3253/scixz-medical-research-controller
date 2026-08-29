from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "scripts" / "awas_cli.py"
SMOKE_DIR = ROOT / "smoke-project"


def run(*args: str) -> None:
    cmd = [sys.executable, *args]
    print(f"[run] {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=ROOT)


def main() -> int:
    shutil.rmtree(SMOKE_DIR, ignore_errors=True)
    try:
        run("-m", "compileall", "scripts")
        run(str(CLI), "--help")
        run(str(CLI), "project-init", str(SMOKE_DIR), "--force")
        run(str(CLI), "project-status", str(SMOKE_DIR))
        run(str(CLI), "project-gate", str(SMOKE_DIR))
    finally:
        shutil.rmtree(SMOKE_DIR, ignore_errors=True)
    print("[ok] academic-write-all-skill smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
