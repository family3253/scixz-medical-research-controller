import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "journal_selection.py"
SPEC = importlib.util.spec_from_file_location("scixz_journal_selection", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


PROFILE = {
    "direction_summary": "Clinical prediction model for antimicrobial resistance.",
    "research_object": "hospitalized adults",
    "research_question": "Can the model predict MDR infection?",
    "contribution_type": "external validation",
    "methods": ["machine learning"],
    "categories": [{"category1": "医学", "category2": "医学：研究与实验"}],
}


RECORD = {
    "name": "Example Journal",
    "issn": "1234-5678",
    "impact_factor": "4.2",
    "jcr_quartile": "Q2",
    "jcr_categories": [{"category": "MEDICINE", "quartile": "Q2"}],
    "cas_partition_2025": "3区",
    "cas_minor_categories": [{"category": "MEDICINE", "partition": "3区"}],
    "xinrui_partition_2026": "2区",
    "sci_type": "SCIE",
    "open_access": True,
    "oa_price": 2500,
    "warning": False,
    "speed": "平均审稿速度： 8 Weeks",
    "letpub_source_url": "https://letpub.com.cn/index.php?journalid=1&page=journalapp&view=detail",
    "letpub_retrieved_at": "2026-08-30T00:00:00Z",
    "scope_verified": True,
    "scope_source_url": "https://publisher.example/journal/scope",
    "scope_evidence": ["Accepts clinical prediction model validation studies."],
    "similar_works_count": 3,
    "query_coverage": 2,
    "publication_precedents": [{"title": "Comparable validation study", "year": 2025}],
    "fit_score": 28,
    "quality_score": 27,
    "risk_penalty": 0,
    "score": 28,
    "fit_confidence": "强",
    "tier": "推荐",
    "candidate_label": "中位候选",
    "fit_reasons": ["期刊官网 scope 已核验", "近年相似论文先例 3 篇 / 覆盖 2 组检索"],
    "quality_reasons": ["SCIE/SSCI 收录", "JCR Q2"],
    "risk_reasons": [],
    "data_notes": [],
    "_source_status": {
        "journal-index": {"status": "succeeded", "reason": "matching record"},
        "letpub": {"status": "succeeded", "reason": "journal detail"},
    },
}


def _artifact(tool):
    return {
        "tool": tool,
        "status": "succeeded",
        "query": "MDR infection machine learning external validation",
        "retrieved_at": "2026-08-30T00:00:00Z",
        "result_artifact": f"runs/{tool}.json",
        "summary": f"{tool} candidate discovery completed",
    }


def test_missing_mandatory_external_artifact_blocks_final_ranking():
    report = MODULE.build_report(PROFILE, [RECORD], {"jane": _artifact("jane")})

    assert report["decision_status"] == "BLOCKED"
    assert report["final_ranking"] == []
    assert report["blocking_requirements"] == ["ipubmed"]
    assert report["diagnostic_candidates"][0]["journal"] == "Example Journal"


def test_final_selection_card_has_rich_fields_and_non_predictive_score():
    report = MODULE.build_report(
        PROFILE,
        [RECORD],
        {"jane": _artifact("jane"), "ipubmed": _artifact("ipubmed")},
    )

    assert report["decision_status"] == "FINAL_EVIDENCE_RANKING"
    card = report["final_ranking"][0]
    assert card["rank"] == 1
    assert card["journal"] == "Example Journal"
    assert card["metrics"]["jcr_quartile"]["value"] == "Q2"
    assert card["metrics"]["cas_major_quartile_2025"]["value"] == "3区"
    assert card["metrics"]["xinrui_quartile_2026"]["value"] == "2区"
    assert card["metrics"]["letpub_review_speed"]["source_url"].startswith("https://letpub.com.cn/")
    assert card["metrics"]["data_completeness"]["percent"] == 100.0
    assert card["score"]["ranking_evidence_score"] == 28
    assert card["score"]["venue_context_score"] == 27
    assert "acceptance probability" in card["score"]["interpretation"]
    assert card["scope_and_precedent"]["official_scope_status"] == "verified"
    assert card["next_action"]


def test_external_artifact_requires_query_date_and_result_path():
    artifact = _artifact("jane")
    artifact.pop("result_artifact")

    validation = MODULE.validate_external_artifact("jane", artifact)

    assert validation["status"] == "invalid"
    assert "result_artifact" in validation["missing"]


def test_cli_runs_an_evidence_gated_report_from_artifacts(tmp_path):
    bundle_path = tmp_path / "bundle.json"
    jane_path = tmp_path / "jane.json"
    ipubmed_path = tmp_path / "ipubmed.json"
    output_path = tmp_path / "report.json"
    bundle_path.write_text(json.dumps({"profile": PROFILE, "results": [RECORD]}), encoding="utf-8")
    jane_path.write_text(json.dumps(_artifact("jane")), encoding="utf-8")
    ipubmed_path.write_text(json.dumps(_artifact("ipubmed")), encoding="utf-8")

    exit_code = MODULE.main(
        [
            "--bundle", str(bundle_path),
            "--jane-artifact", str(jane_path),
            "--ipubmed-artifact", str(ipubmed_path),
            "--output", str(output_path),
        ]
    )

    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert report["decision_status"] == "FINAL_EVIDENCE_RANKING"
    assert report["final_ranking"][0]["journal"] == "Example Journal"


def test_live_metric_enrichment_preserves_ranking_evidence():
    class Selector:
        @staticmethod
        def get_journal_metrics(name, **kwargs):
            assert name == "Example Journal"
            assert kwargs["source_mode"] == "full"
            return {
                "name": name,
                "speed": "平均审稿速度： 6 Weeks",
                "letpub_source_url": "https://letpub.com.cn/example",
                "_source_status": {"letpub": {"status": "succeeded", "reason": "detail"}},
            }

    bundle = MODULE.enrich_selection_metrics(Selector(), {"profile": PROFILE, "results": [RECORD]})

    enriched = bundle["results"][0]
    assert enriched["speed"] == "平均审稿速度： 6 Weeks"
    assert enriched["fit_score"] == 28
    assert bundle["metric_enrichment"][0]["status"] == "succeeded"


def test_runner_loads_the_bundled_sci_select_owner():
    selector = MODULE._load_sci_select()

    assert callable(selector.select_journals)
    assert callable(selector.get_journal_metrics)
