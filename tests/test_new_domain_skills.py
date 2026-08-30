import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _module(relative):
    spec = importlib.util.spec_from_file_location(relative.stem, relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_statistical_plan_skill_is_runnable_and_blocks_missing_sensitivity_plan():
    module = _module(ROOT / "bundled-skills" / "statistical-analysis" / "scripts" / "validate_analysis_plan.py")
    result = module.validate({"analysis_unit": "participant", "outcome": "binary", "estimand": "risk difference", "design": "cohort", "objective": "causal", "primary_analysis": "regression", "assumptions": ["positivity"], "missing_data_plan": "multiple imputation", "sensitivity_analyses": ["complete case"], "multiplicity_plan": "FDR", "reproducibility": {"seed": 42}})
    blocked = module.validate({"analysis_unit": "participant"})

    assert result["status"] == "READY_FOR_EXECUTION"
    assert blocked["status"] == "BLOCKED"


def test_multiomics_skill_is_runnable_and_requires_matching_and_provenance():
    module = _module(ROOT / "bundled-skills" / "multiomics-analysis" / "scripts" / "validate_multiomics_plan.py")
    plan = {"question": "association", "modalities": ["RNA", "protein"], "analysis_unit": "participant", "sample_matching": {"matched": True}, "provenance": {"verified": True}, "batch": "recorded", "missingness_plan": "pre-specified", "integration_objective": "exploratory", "validation_design": "independent cohort", "claim_level": "associational", "leakage_control": "fold-local preprocessing"}
    result = module.validate(plan)
    plan["sample_matching"] = {"matched": False}

    assert result["status"] == "READY_FOR_EXECUTION"
    assert module.validate(plan)["status"] == "BLOCKED"


def test_repository_authored_domain_skills_are_in_the_public_bundle_manifest():
    manifest = json.loads((ROOT / "registry" / "bundled_skill_manifest.json").read_text(encoding="utf-8"))
    names = {item["name"] for item in manifest["skills"]}

    assert {"statistical-analysis", "multiomics-analysis"} <= names
    bundle_skills = [path for path in (ROOT / "bundled-skills").iterdir() if (path / "SKILL.md").is_file()]
    assert manifest["counts"]["bundledTopLevelSkills"] == len(bundle_skills)
