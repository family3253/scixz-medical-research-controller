#!/usr/bin/env python3
"""Build a scored, evidence-gated SciXZ journal-selection deliverable."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


MANDATORY_TOOLS = ("jane", "ipubmed")


def _value(value: Any) -> Any:
    return value if value not in (None, "", [], {}) else None


def _source_status(record: Dict[str, Any], source: str) -> Dict[str, str]:
    status = (record.get("_source_status") or {}).get(source)
    if isinstance(status, dict):
        return {"status": str(status.get("status", "unknown")), "reason": str(status.get("reason", ""))}
    return {"status": "not_available", "reason": "source status was not supplied"}


def validate_external_artifact(tool: str, artifact: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate the minimum auditable record needed for a mandatory external branch."""
    if not isinstance(artifact, dict):
        return {"tool": tool, "status": "missing", "missing": ["artifact"]}
    if artifact.get("tool") not in (None, tool):
        return {"tool": tool, "status": "invalid", "missing": ["matching tool"]}
    aliases = {
        "query": ("query", "query_url"),
        "retrieved_at": ("retrieved_at", "query_date"),
        "result_artifact": ("result_artifact", "result_path", "export_path"),
    }
    missing = [label for label, keys in aliases.items() if not any(artifact.get(key) for key in keys)]
    if str(artifact.get("status", "")).lower() != "succeeded":
        missing.append("status=succeeded")
    if missing:
        return {"tool": tool, "status": "invalid", "missing": missing}
    return {
        "tool": tool,
        "status": "succeeded",
        "query": artifact.get("query") or artifact.get("query_url"),
        "retrieved_at": artifact.get("retrieved_at") or artifact.get("query_date"),
        "result_artifact": artifact.get("result_artifact") or artifact.get("result_path") or artifact.get("export_path"),
        "summary": str(artifact.get("summary", "")),
    }


def _metric_fields(record: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    letpub = _source_status(record, "letpub")
    journal_index = _source_status(record, "journal-index")
    metrics = {
        "impact_factor": {"value": _value(record.get("impact_factor")), "year": record.get("if_year"), "jcr_release_year": record.get("jcr_release_year"), "data_year": record.get("jcr_data_year"), "source_status": journal_index},
        "jcr_quartile": {"value": _value(record.get("jcr_quartile")), "categories": record.get("jcr_categories") or [], "source_status": journal_index},
        "cas_major_quartile_2025": {"value": _value(record.get("cas_partition_2025")), "source_status": journal_index},
        "cas_minor_quartile_2025": {"value": record.get("cas_minor_categories") or [], "source_status": journal_index},
        "xinrui_quartile_2026": {"value": _value(record.get("xinrui_partition_2026")), "source_status": journal_index},
        "coverage": {"value": _value(record.get("sci_type")), "source_status": journal_index},
        "oa_apc": {"open_access": _value(record.get("open_access")), "apc_usd": _value(record.get("oa_price")), "source_status": letpub},
        "letpub_review_speed": {"value": _value(record.get("speed")), "source_url": _value(record.get("letpub_source_url")), "retrieved_at": _value(record.get("letpub_retrieved_at")), "source_status": letpub},
        "warning": {"value": _value(record.get("warning")), "source_status": journal_index},
    }
    def present_field(field: Dict[str, Any]) -> bool:
        return any(
            value not in (None, "", [], {})
            for key, value in field.items()
            if key != "source_status"
        )

    present = sum(present_field(metrics[key]) for key in metrics)
    metrics["data_completeness"] = {"present_fields": present, "total_fields": 9, "percent": round(present * 100 / 9, 1)}
    return metrics


def _scope_and_precedent(record: Dict[str, Any]) -> Dict[str, Any]:
    verified = bool(record.get("scope_verified"))
    checked = bool(record.get("scope_checked"))
    return {
        "official_scope_status": "verified" if verified else ("read_unresolved" if checked else "not_verified"),
        "official_scope_url": _value(record.get("scope_source_url")),
        "scope_evidence": record.get("scope_evidence") or [],
        "recent_precedent_count": int(record.get("similar_works_count", 0) or 0),
        "query_coverage": int(record.get("query_coverage", 0) or 0),
        "precedents": record.get("publication_precedents") or [],
    }


def _next_action(card: Dict[str, Any]) -> str:
    scope = card["scope_and_precedent"]
    completeness = card["metrics"]["data_completeness"]["percent"]
    if scope["official_scope_status"] != "verified":
        return "Read and record the official aims, scope, and accepted article type before selecting this journal."
    if completeness < 70:
        return "Verify missing current policy, APC, coverage, or review-speed fields before choosing submission order."
    return "Run journal-specific preflight against current author guidelines and article-type requirements."


def _candidate_card(record: Dict[str, Any], rank: int) -> Dict[str, Any]:
    card = {
        "rank": rank,
        "journal": record.get("name", ""),
        "issn": _value(record.get("issn")),
        "candidate_status": record.get("candidate_label") or record.get("tier") or "needs-review",
        "fit_confidence": record.get("fit_confidence", "weak"),
        "score": {
            "ranking_evidence_score": int(record.get("score", 0) or 0),
            "scope_and_precedent_score": int(record.get("fit_score", 0) or 0),
            "risk_penalty": int(record.get("risk_penalty", 0) or 0),
            "venue_context_score": int(record.get("quality_score", 0) or 0),
            "interpretation": "Ranking evidence score for candidate ordering; it is not an acceptance probability or a manuscript-quality score.",
        },
        "scope_and_precedent": _scope_and_precedent(record),
        "metrics": _metric_fields(record),
        "fit_reasons": record.get("fit_reasons") or [],
        "venue_context": record.get("quality_reasons") or [],
        "risks": record.get("risk_reasons") or [],
        "data_notes": record.get("data_notes") or [],
        "source_status": record.get("_source_status") or {},
    }
    card["next_action"] = _next_action(card)
    return card


def build_report(profile: Dict[str, Any], ranked_records: Iterable[Dict[str, Any]], external_artifacts: Dict[str, Any]) -> Dict[str, Any]:
    """Build a publication-decision aid from already ranked candidate records."""
    external = {tool: validate_external_artifact(tool, external_artifacts.get(tool)) for tool in MANDATORY_TOOLS}
    blocked = [tool for tool, result in external.items() if result["status"] != "succeeded"]
    ordered = sorted((dict(record) for record in ranked_records), key=lambda record: (-int(record.get("score", 0) or 0), -int(record.get("fit_score", 0) or 0), str(record.get("name", "")).lower()))
    cards = [_candidate_card(record, index) for index, record in enumerate(ordered, 1)]
    return {
        "decision_status": "BLOCKED" if blocked else "FINAL_EVIDENCE_RANKING",
        "selection_basis": "Scope and recent publication precedents rank before venue metrics. Scores are decision-aid evidence, not acceptance predictions.",
        "manuscript_fingerprint": {key: profile.get(key) for key in ("direction_summary", "research_object", "research_question", "contribution_type", "methods", "categories", "exclusions")},
        "mandatory_external_evidence": external,
        "blocking_requirements": blocked,
        "final_ranking": [] if blocked else cards,
        "diagnostic_candidates": cards,
        "submission_readiness_boundary": {
            "desk_screening": "Requires current scope, article-type, and guideline verification.",
            "peer_review": "Not inferred from journal rank, metrics, or similarity evidence.",
            "acceptance_probability": "Not estimated without journal/article-type-specific independent calibration data.",
        },
    }


def _candidate_sci_select_roots() -> Iterable[Path]:
    root = Path(__file__).resolve().parents[1]
    yield root / "bundled-skills" / "sci-select"
    # A locally installed SciXZ and sci-select are sibling Skills.
    yield root.parent / "sci-select"
    codex_home = Path.home() / ".codex" / "skills"
    yield codex_home / "sci-select"
    yield Path.home() / ".agents" / "skills" / "sci-select"


def _load_sci_select():
    for root in _candidate_sci_select_roots():
        if not (root / "scripts" / "select_journals.py").is_file():
            continue
        sys.path.insert(0, str(root))
        try:
            for name in list(sys.modules):
                if name == "scripts" or name.startswith("scripts."):
                    del sys.modules[name]
            return importlib.import_module("scripts.select_journals")
        finally:
            sys.path.pop(0)
    raise RuntimeError("sci-select was not found; install the bundled or local companion Skill")


def _load_json(path: str) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected an object in {path}")
    return payload


def enrich_selection_metrics(selector: Any, bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Refresh candidate cards through sci-select's full known-journal lookup path."""
    result = dict(bundle)
    enriched = []
    outcomes = []
    preserve = {
        "_candidate", "similar_works_count", "query_coverage", "literature_evidence_score",
        "publication_precedents", "scope_verified", "scope_checked", "scope_match",
        "scope_source_url", "scope_evidence", "fit_score", "quality_score", "risk_penalty",
        "score", "fit_reasons", "quality_reasons", "risk_reasons", "fit_confidence", "tier",
        "candidate_label", "submission_band", "data_notes", "metrics_line", "data_status",
    }
    for record in bundle["results"]:
        current = dict(record)
        name = str(current.get("name", "")).strip()
        if not name:
            enriched.append(current)
            outcomes.append({"journal": "", "status": "skipped", "reason": "missing journal name"})
            continue
        try:
            fresh = selector.get_journal_metrics(
                name,
                issn=current.get("issn", ""),
                use_cache=False,
                source_mode="full",
            )
            for key, value in fresh.items():
                if value not in (None, "", [], {}):
                    current[key] = value
            for key in preserve:
                if record.get(key) not in (None, "", [], {}):
                    current[key] = record[key]
            outcomes.append({"journal": name, "status": "succeeded"})
        except Exception as exc:
            outcomes.append({"journal": name, "status": "partial", "reason": str(exc)})
        enriched.append(current)
    result["results"] = enriched
    result["metric_enrichment"] = outcomes
    return result


def _bundle_from_args(args: argparse.Namespace) -> Dict[str, Any]:
    if args.bundle:
        bundle = _load_json(args.bundle)
        if not isinstance(bundle.get("profile"), dict) or not isinstance(bundle.get("results"), list):
            raise ValueError("bundle requires profile object and results array")
        return bundle
    text = args.text or (Path(args.text_file).read_text(encoding="utf-8") if args.text_file else "")
    if not text:
        raise ValueError("Supply --text, --text-file, or --bundle")
    selector = _load_sci_select()
    bundle = selector.select_journals(text, max_candidates=args.max_candidates, request_delay=args.request_delay)
    return bundle if args.skip_live_enrichment else enrich_selection_metrics(selector, bundle)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run the SciXZ evidence-gated journal-selection report.")
    parser.add_argument("--text", default="")
    parser.add_argument("--text-file", default="")
    parser.add_argument("--bundle", default="", help="Precomputed sci-select bundle for deterministic reruns.")
    parser.add_argument("--jane-artifact", default="")
    parser.add_argument("--ipubmed-artifact", default="")
    parser.add_argument("--output", default="")
    parser.add_argument("--max-candidates", type=int, default=8)
    parser.add_argument("--request-delay", type=float, default=1.0)
    parser.add_argument("--skip-live-enrichment", action="store_true", help="Do not refresh selected candidate metrics through the full sci-select lookup path.")
    parser.add_argument("--allow-diagnostic", action="store_true")
    args = parser.parse_args(argv)
    try:
        bundle = _bundle_from_args(args)
        artifacts = {"jane": _load_json(args.jane_artifact) if args.jane_artifact else None, "ipubmed": _load_json(args.ipubmed_artifact) if args.ipubmed_artifact else None}
        report = build_report(bundle["profile"], bundle["results"], artifacts)
    except Exception as exc:
        parser.exit(1, f"journal selection failed: {exc}\n")
    serialized = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(serialized + "\n", encoding="utf-8")
    print(serialized)
    return 0 if report["decision_status"] != "BLOCKED" or args.allow_diagnostic else 2


if __name__ == "__main__":
    raise SystemExit(main())
