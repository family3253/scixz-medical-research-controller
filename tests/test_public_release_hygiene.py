import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_public_bundle_excludes_runtime_caches_and_private_artifact_names():
    forbidden_directory_names = {"cache", "browser-state", "node_modules", ".venv"}
    forbidden_file_suffixes = {".token", ".key", ".pem", ".p12"}
    forbidden_name_fragments = (
        "paperreview-state",
        "paperreview-artifact",
        "provider-review",
        "final-review",
    )

    tracked = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=ROOT, text=False
    ).decode("utf-8").split("\0")
    violations = []
    for relative_name in tracked:
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
