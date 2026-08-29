#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from protocol_v54 import read_tsv, write_json
from qa_eligibility_consistency_v1 import validate as validate_eligibility
from qa_semantic_key_v1 import validate as validate_semkey
from qa_source_identity_v1 import read_index, validate as validate_identity


def sha256(path:Path)->str:
    h=hashlib.sha256();
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()


def verify_manifest(package:Path)->dict:
    p=package/"manifest_sha256.json"; errors=[]
    if not p.exists(): return {"pass":False,"errors":["missing manifest_sha256.json"]}
    manifest=json.loads(p.read_text(encoding="utf-8"))
    for rel,wanted in manifest.items():
        # v5.3 manifests stored a bare hash; v5.4 frozen packages store a
        # provenance object with sha256/bytes/status. Validate either without
        # weakening hash checking.
        expected = wanted.get("sha256") if isinstance(wanted, dict) else wanted
        if expected is None:
            errors.append(f"invalid manifest entry {rel}")
            continue
        f=package/rel
        if not f.exists():errors.append(f"missing {rel}")
        elif sha256(f).lower()!=str(expected).lower():errors.append(f"hash mismatch {rel}")
    return {"pass":not errors,"errors":errors,"files":len(manifest)}


def validate(workbook:Path,packages:list[Path],expected_reports:int)->dict:
    identity=validate_identity(workbook,"01_Source_Report_Index",41,40,True,True)
    _,index_rows=read_index(workbook,"01_Source_Report_Index"); index_map={(r["report_id"],r["study_id"]) for r in index_rows}
    details=[]; seen=set(); errors=[]; warnings=[]
    for package in packages:
        _,erows=read_tsv(package/"eligibility_t0.tsv"); pairs={(r.get("report_id",""),r.get("study_id","")) for r in erows}; seen|=pairs
        missing=sorted(pairs-index_map)
        if missing:errors.append(f"{package.name}: identities absent from source index {missing}")
        sem=validate_semkey(package/"granularity_alignment.tsv",package/"semantic_key_crosswalk.tsv",len({x[0] for x in pairs}),True)
        elig=validate_eligibility(package/"eligibility_t0.tsv","final")
        frozen=verify_manifest(package)
        details.append({"package":str(package),"reports":len(pairs),"source_identity_match":not missing,
                        "frozen_hashes":frozen,"semantic_compat":sem,"eligibility_compat":elig})
    if len({x[0] for x in seen})!=expected_reports:errors.append(f"expected {expected_reports} package reports, observed {len({x[0] for x in seen})}")
    if not identity["pass"]:errors.extend(identity["errors"])
    strict=not errors and all(d["frozen_hashes"]["pass"] and d["semantic_compat"]["pass"] and d["eligibility_compat"]["pass"] for d in details)
    semantic_blockers=sum(len(d["semantic_compat"]["errors"]) for d in details)
    eligibility_blockers=sum(len(d["eligibility_compat"]["errors"]) for d in details)
    return {"protocol":"FORWARD_COMPAT_V54_FIRST10","strict_pass":strict,
            "source_and_frozen_integrity_pass":not errors and all(d["frozen_hashes"]["pass"] for d in details),
            "eligibility_compat_pass":eligibility_blockers==0,"semantic_compat_pass":semantic_blockers==0,
            "pass":strict,"errors":errors,"warnings":warnings+identity["warnings"],
            "counts":{"reports":len({x[0] for x in seen}),"semantic_blockers":semantic_blockers,"eligibility_blockers":eligibility_blockers},
            "source_identity":identity,"packages":details}


def main()->int:
    p=argparse.ArgumentParser();p.add_argument("--workbook",type=Path,required=True);p.add_argument("--package",type=Path,action="append",required=True);p.add_argument("--expected-reports",type=int,default=10);p.add_argument("--out",type=Path)
    a=p.parse_args();result=validate(a.workbook,a.package,a.expected_reports);write_json(result,a.out);return 0 if result["pass"] else 1


if __name__=="__main__":raise SystemExit(main())
