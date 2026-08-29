#!/usr/bin/env python3
"""Aggregate the final read-only first-15 staging acceptance gates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from protocol_v54 import read_tsv, write_json


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--validation",type=Path,required=True)
    p.add_argument("--batch02-crosswalk",type=Path,required=True)
    p.add_argument("--batch02-source-coverage",type=Path,required=True); p.add_argument("--out",type=Path)
    a=p.parse_args(); v=a.validation
    strict={name:load(v/f"strict_semkey_{name}_final.json") for name in (
        "pilot_granularity_adjudication_v5_3","batch02_adjudication_v1","batch03_adjudication_v1")}
    eligibility={name:load(v/f"eligibility_migrated_{name}_final.json") for name in strict}
    coverage=load(v/"qa_first15_migrated_coverage_final.json")
    identity=load(v/"source_identity_final.json")
    regression=load(v/"candidate_regression_final.json")
    frozen=load(v/"forward_compat_first15_expected_fail_v2.json")
    source_coverage=load(a.batch02_source_coverage)
    _,rows=read_tsv(a.batch02_crosswalk)
    removed_metrics=sum(r.get("entity_type")=="performance" and r.get("mapping_decision")=="REMOVED_INELIGIBLE_ENTITY" for r in rows)
    gates={
        "candidate_regression":regression.get("pass") is True,
        "strict_semkey_pilot":strict["pilot_granularity_adjudication_v5_3"].get("pass") is True,
        "strict_semkey_batch02_overlay":strict["batch02_adjudication_v1"].get("pass") is True,
        "strict_semkey_batch03":strict["batch03_adjudication_v1"].get("pass") is True,
        "migrated_first15_coverage":coverage.get("pass") is True and coverage.get("counts",{}).get("reports")==15,
        "migrated_eligibility_all_batches":all(x.get("pass") is True for x in eligibility.values()),
        "source_identity_41_to_40":identity.get("pass") is True and identity.get("counts",{}).get("source_records")==41 and identity.get("counts",{}).get("reports")==40,
        "frozen_source_integrity":frozen.get("source_and_frozen_integrity_pass") is True,
        "batch02_source_entity_coverage":source_coverage.get("pass") is True,
        "transparent_removed_metric_count_32":removed_metrics==32,
    }
    payload={
        "protocol":"FIRST15_RELEASE_ACCEPTANCE_V54","pass":all(gates.values()),"release_state":"RELEASABLE" if all(gates.values()) else "NOT_READY_TO_PUBLISH",
        "gates":gates,"counts":{"reports":15,"strict_alignment_entities":sum(x["counts"]["alignment_rows"] for x in strict.values()),
        "strict_crosswalk_rows":sum(x["counts"]["crosswalk_rows"] for x in strict.values()),"batch02_removed_ineligible_performance_metrics":removed_metrics},
        "schema_coverage_limitation":"32 secondary G-mean/Kappa/MCC source performance rows remain auditable as REMOVED_INELIGIBLE_ENTITY because the frozen v5.3 final fact schema has no corresponding final performance entities; promote only after explicit schema expansion.",
        "warnings":identity.get("warnings",[]),
    }
    write_json(payload,a.out); return 0 if payload["pass"] else 1


if __name__=="__main__": raise SystemExit(main())
