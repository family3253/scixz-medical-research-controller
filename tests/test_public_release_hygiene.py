import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _tracked_files():
    if (ROOT / ".git").exists():
        return subprocess.check_output(
            ["git", "ls-files", "-z"], cwd=ROOT, text=False
        ).decode("utf-8").split("\0")
    generated_directories = {".pytest_cache", "__pycache__", ".mypy_cache"}
    return [
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in ROOT.rglob("*")
        if path.is_file() and not any(part in generated_directories for part in path.parts)
    ]


def test_public_bundle_excludes_runtime_caches_and_private_artifact_names():
    forbidden_directory_names = {
        "cache",
        "browser-state",
        "node_modules",
        ".venv",
        "private-runs",
        "manuscript-runs",
        "journal-selection-runs",
        "selection-runs",
    }
    forbidden_file_suffixes = {".token", ".key", ".pem", ".p12"}
    forbidden_name_fragments = (
        "paperreview-state",
        "paperreview-artifact",
        "provider-review",
        "final-review",
        "selection-report",
        "journal-selection",
        "fingerprint",
        "paperreview" + "-synthesis",
        "parallel" + "-review-fusion",
        "repeat" + "-audit",
    )

    violations = []
    for relative_name in _tracked_files():
        if not relative_name:
            continue
        path = ROOT / relative_name
        if any(part in forbidden_directory_names for part in path.parts):
            violations.append(relative_name)
        lower_name = path.name.lower()
        if path.suffix.lower() in forbidden_file_suffixes:
            violations.append(relative_name)
        if any(fragment in lower_name for fragment in forbidden_name_fragments):
            violations.append(relative_name)

    assert violations == []


def test_public_bundle_contains_no_local_manuscript_or_run_paths():
    """Keep real manuscript locations and generated run records off the mirror."""
    forbidden_fragments = (
        "Sc" + "iXZ" + "-" + "PaperReview" + "-" + "Runs",
        "for" + "ward" + "-" + "test-v",
        "Paper" + "Review" + "-" + "Runs",
        "priv" + "ate" + "-" + "manuscript",
    )
    text_suffixes = {".md", ".json", ".py", ".txt", ".yaml", ".yml", ".toml", ".sh", ".ps1"}
    violations = []
    for relative_name in _tracked_files():
        if not relative_name or Path(relative_name).suffix.lower() not in text_suffixes:
            continue
        path = ROOT / relative_name
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for fragment in forbidden_fragments:
            if fragment.lower() in text.lower():
                violations.append(f"{relative_name}: {fragment}")
    assert violations == []


def test_public_bundle_does_not_track_real_manuscript_fingerprint_literals():
    """Only placeholders and generic hashing logic belong in the public mirror."""
    text_suffixes = {".md", ".json", ".py", ".txt", ".yaml", ".yml", ".toml", ".sh", ".ps1"}
    suspicious = []
    for relative_name in _tracked_files():
        if not relative_name or Path(relative_name).suffix.lower() not in text_suffixes:
            continue
        path = ROOT / relative_name
        text = path.read_text(encoding="utf-8", errors="ignore")
        # A real manuscript digest is never a fixture, template, or source literal.
        for line_number, line in enumerate(text.splitlines(), 1):
            lowered = line.lower()
            if "sha256:" not in lowered:
                continue
            if any(marker in lowered for marker in ("sha256:test", "sha256:paper", "sha256:fictional", "replace-with", "hashlib.sha256", "sha256-or-stable-version", "sha256:...")):
                continue
            if any(char * 8 in lowered for char in "0123456789abcdef"):
                suspicious.append(f"{relative_name}:{line_number}")
    assert suspicious == []
