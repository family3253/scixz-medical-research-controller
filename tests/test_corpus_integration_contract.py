import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "verify_corpus_integration.py"
SPEC = importlib.util.spec_from_file_location("scixz_corpus_verify", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_every_assessed_source_has_concrete_existing_owner():
    result = MODULE.verify(ROOT)

    assert result["sources"] == 14
    assert result["integrations"] == result["sources"]
    assert result["owners"] >= result["sources"]


def test_verifier_rejects_a_source_without_an_integration(tmp_path):
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry" / "prompt_corpus_sources.json").write_text(
        json.dumps({"sources": [{"id": "unmapped"}]}), encoding="utf-8"
    )
    (tmp_path / "registry" / "corpus_integration_contract.json").write_text(
        json.dumps({"integrations": []}), encoding="utf-8"
    )

    with pytest.raises(ValueError, match=r"missing=\['unmapped'\]"):
        MODULE.verify(tmp_path)


def test_verifier_resolves_a_companion_skill_in_the_installed_layout(tmp_path):
    (tmp_path / "registry").mkdir()
    companion = tmp_path.parent / "companion" / "SKILL.md"
    companion.parent.mkdir()
    companion.write_text("---\nname: companion\n---\n", encoding="utf-8")
    (tmp_path / "registry" / "prompt_corpus_sources.json").write_text(
        json.dumps({"sources": [{"id": "source"}]}), encoding="utf-8"
    )
    (tmp_path / "registry" / "corpus_integration_contract.json").write_text(
        json.dumps(
            {
                "integrations": [
                    {
                        "source": "source",
                        "outcome": "new-skill",
                        "capabilities": ["test"],
                        "owners": ["bundled-skills/companion/SKILL.md"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    assert MODULE.verify(tmp_path)["owners"] == 1
