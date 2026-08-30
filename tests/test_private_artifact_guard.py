import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts" / "private_artifact_guard.py"
SPEC = importlib.util.spec_from_file_location("scixz_private_artifact_guard", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_private_artifact_guard_allows_external_directory(tmp_path):
    output = MODULE.ensure_private_output_path(tmp_path / "artifact.json", ROOT)
    assert output == (tmp_path / "artifact.json").resolve()


def test_private_artifact_guard_blocks_source_tree_output():
    with pytest.raises(ValueError, match="outside the checkout"):
        MODULE.ensure_private_output_path(ROOT / "artifact.json", ROOT)
