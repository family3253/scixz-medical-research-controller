#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from protocol_v54 import read_tsv, write_json


def validate(batch_dirs:list[Path],expected_reports:int|None,require_identical_headers:bool=True)->dict:
    errors=[]; warnings=[]; details={}; report_union=set(); reference={}
    for d in batch_dirs:
        details[d.name]={}
        for table in ("eligibility_t0.tsv","unit_inventory.tsv"):
            p=d/table
            if not p.exists(): errors.append(f"{d.name}: missing {table}"); continue
            h,r=read_tsv(p); reports={x.get("report_id","") for x in r if x.get("report_id","")}; report_union|=reports
            details[d.name][table]={"columns":len(h),"header":h,"rows":len(r),"reports":len(reports)}
            if table not in reference: reference[table]=h
            elif require_identical_headers and h!=reference[table]: errors.append(f"{d.name}: {table} header differs from first batch")
            if any("" in (x.get("report_id",""),x.get("study_id","")) for x in r): errors.append(f"{d.name}: {table} blank report/study")
    if expected_reports is not None and len(report_union)!=expected_reports: errors.append(f"expected {expected_reports} reports, observed {len(report_union)}")
    return {"protocol":"FULL40_COVERAGE_V1/v5.4","pass":not errors,"errors":errors,"warnings":warnings,"counts":{"batches":len(batch_dirs),"reports":len(report_union)},"details":details}


def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("batch_dir",type=Path,nargs="+"); p.add_argument("--expected-reports",type=int); p.add_argument("--allow-header-drift",action="store_true"); p.add_argument("--out",type=Path)
    a=p.parse_args(); result=validate(a.batch_dir,a.expected_reports,not a.allow_header_drift); write_json(result,a.out); return 0 if result["pass"] else 1


if __name__=="__main__": raise SystemExit(main())
