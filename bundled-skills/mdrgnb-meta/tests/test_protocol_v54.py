from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; SCRIPTS=ROOT/"scripts"; sys.path.insert(0,str(SCRIPTS))
from qa_semantic_key_v1 import validate as validate_semkey
from qa_eligibility_consistency_v1 import validate as validate_eligibility
from qa_pool_consistency_v1 import validate as validate_pool
from qa_source_identity_v1 import validate as validate_identity
from qa_full40_coverage_v1 import validate as validate_coverage
from migrate_v53_to_v54 import ELIGIBILITY_HEADER, ELIGIBILITY_LEGACY_23, UNIT_HEADER, UNIT_PILOT_32, migrate_batch
from migrate_semkey_crosswalk_v54 import migrate as migrate_crosswalk

FIX=ROOT/"tests"/"fixtures"


class ProtocolV54Tests(unittest.TestCase):
    def test_semkey_and_crosswalk_pass(self):
        r=validate_semkey(FIX/"semkey/alignment_pass.tsv",FIX/"semkey/crosswalk_pass.tsv",1)
        self.assertTrue(r["pass"],r)

    def test_semkey_unescaped_fails(self):
        r=validate_semkey(FIX/"semkey/alignment_bad_unescaped.tsv",None,1)
        self.assertFalse(r["pass"])

    def test_semkey_explicit_coarse_to_fine_split_passes(self):
        r=validate_semkey(FIX/"semkey/alignment_split_pass.tsv",FIX/"semkey/crosswalk_split_pass.tsv",1)
        self.assertTrue(r["pass"],r)

    def test_semkey_legacy_duplicate_source_remains_blocking_in_compat_mode(self):
        with tempfile.TemporaryDirectory() as td:
            cross=Path(td)/"cross.tsv"
            lines=(FIX/"semkey/crosswalk_pass.tsv").read_text(encoding="utf-8").splitlines()
            legacy_header="\t".join(lines[0].split("\t")[:18])
            legacy_rows=["\t".join(line.split("\t")[:18]) for line in lines[1:]]
            cells=legacy_rows[1].split("\t"); cells[0]="X-3"
            cross.write_text("\n".join([legacy_header]+legacy_rows+["\t".join(cells)])+"\n",encoding="utf-8")
            r=validate_semkey(FIX/"semkey/alignment_pass.tsv",cross,1,compat_v53=True)
            self.assertFalse(r["pass"],r)
            self.assertTrue(any("source entity maps" in e for e in r["errors"]))

    def test_semkey_crosswalk_migration_accepts_clean_and_refuses_reused_source(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"clean.tsv"
            r=migrate_crosswalk(FIX/"semkey/alignment_pass.tsv",FIX/"semkey/crosswalk_pass.tsv",out)
            self.assertTrue(r["pass"],r)
            lines=(FIX/"semkey/crosswalk_pass.tsv").read_text(encoding="utf-8").splitlines()
            cells=lines[2].split("\t"); cells[0]="X-DUP"
            bad=Path(td)/"bad.tsv"; bad.write_text("\n".join(lines+["\t".join(cells)])+"\n",encoding="utf-8")
            blocked=migrate_crosswalk(FIX/"semkey/alignment_pass.tsv",bad,Path(td)/"blocked.tsv")
            self.assertFalse(blocked["pass"]); self.assertEqual(blocked["status"],"REQUIRES_FACTUAL_CROSSWALK_REPAIR")

    def test_branch_eligibility_and_report_aggregation(self):
        r=validate_eligibility(FIX/"eligibility/branch_pass.tsv","branch")
        self.assertTrue(r["pass"],r)
        self.assertEqual(r["counts"]["derived_report_status"]["RPT-001"],"INCLUDE_DIAGNOSTIC_BRANCH_ONLY")
        self.assertEqual(r["counts"]["derived_report_status"]["RPT-002"],"EXCLUDE_ALL_BRANCHES")
        self.assertEqual(r["counts"]["derived_report_status"]["RPT-003"],"PENDING_PROTOCOL_ADJUDICATION")

    def test_v54_branch_timing_cases(self):
        r=validate_eligibility(FIX/"eligibility/branch_v54_cases.tsv","branch")
        self.assertTrue(r["pass"],r)
        status=r["counts"]["branch_status"]
        self.assertEqual(status["INCLUDE_DIAGNOSTIC_CURRENT_STATE"],6)
        self.assertEqual(status["EXCLUDE_PROGNOSTIC_FUTURE_EVENT"],2)
        self.assertEqual(status["EXCLUDE_KNOWN_CURRENT_ORGANISM_INPUT_AT_T0"],2)
        self.assertEqual(status["EXCLUDE_ORGANISM_RESTRICTED_COHORT"],1)
        self.assertEqual(status["PENDING_FINAL_MODEL_SPECIFICATION"],1)
        self.assertEqual(r["counts"]["derived_report_status"]["RPT-BR3"],"INCLUDE_DIAGNOSTIC_BRANCH_ONLY")
        self.assertEqual(r["counts"]["derived_report_status"]["RPT-BR4"],"INCLUDE_DIAGNOSTIC_BRANCH_ONLY")

    def test_pool_pass_and_pending_rejected(self):
        r=validate_pool(FIX/"pools/audit_40_pass.tsv",FIX/"pools/synthesis_pass.tsv",
                        FIX/"eligibility/branch_pass.tsv",FIX/"pools/source_index_40_pass.tsv","unused",40)
        self.assertTrue(r["pass"],r)
        with tempfile.TemporaryDirectory() as td:
            bad=Path(td)/"bad.tsv"; text=(FIX/"pools/synthesis_pass.tsv").read_text(encoding="utf-8")
            bad.write_text(text.replace("ELIG-OPT","ELIG-PENDING"),encoding="utf-8")
            r=validate_pool(FIX/"pools/audit_40_pass.tsv",bad,FIX/"eligibility/branch_pass.tsv",
                            FIX/"pools/source_index_40_pass.tsv","unused",40)
            self.assertFalse(r["pass"])

    def test_pool_requires_exactly_40_audit_reports(self):
        with tempfile.TemporaryDirectory() as td:
            bad=Path(td)/"audit.tsv"; lines=(FIX/"pools/audit_40_pass.tsv").read_text(encoding="utf-8").splitlines()
            bad.write_text("\n".join(lines[:-1])+"\n",encoding="utf-8")
            r=validate_pool(bad,FIX/"pools/synthesis_pass.tsv",FIX/"eligibility/branch_pass.tsv",
                            FIX/"pools/source_index_40_pass.tsv","unused",40)
            self.assertFalse(r["pass"])
            self.assertTrue(any("exactly 40" in e for e in r["errors"]))

    def test_source_identity_reorder_stable(self):
        p=FIX/"pools/source_index_40_pass.tsv"; r=validate_identity(p,"unused",40,40,False); self.assertTrue(r["pass"],r)
        with tempfile.TemporaryDirectory() as td:
            lines=p.read_text(encoding="utf-8").splitlines(); q=Path(td)/"reordered.tsv"
            q.write_text("\n".join([lines[0]]+list(reversed(lines[1:])))+"\n",encoding="utf-8")
            rr=validate_identity(q,"unused",40,40,False); self.assertTrue(rr["pass"],rr)
            self.assertEqual(r["counts"],rr["counts"])

    def test_migration_preserves_cells_and_unifies_headers(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); inputs=[]
            for idx in range(2):
                d=root/f"in{idx}"; d.mkdir(); inputs.append(d)
                elig={k:"NR" for k in ELIGIBILITY_LEGACY_23}; elig.update({"assessment_id":f"E{idx}","report_id":f"R{idx}","study_id":f"S{idx}","outcome_id":f"O{idx}","model_id":f"M{idx}","target_present_at_t0_01":"1","organism_unknown_at_t0_01":"1","organism_restricted_cohort_01":"0","future_event_target_01":"0","diagnostic_vs_prognostic_final":"DIAGNOSTIC_CURRENT","eligibility_status":"INCLUDE","adjudication_status":"FINAL_ADJUDICATED","evidence_id":f"EV{idx}"})
                unit={k:"NR" for k in UNIT_PILOT_32}; unit.update({"unit_id":f"U{idx}","report_id":f"R{idx}","study_id":f"S{idx}","cohort_id":f"C{idx}","outcome_id":f"O{idx}","model_id":f"M{idx}","dataset_id":f"D{idx}"})
                for name,header,row in (("eligibility_t0.tsv",ELIGIBILITY_LEGACY_23,elig),("unit_inventory.tsv",UNIT_PILOT_32,unit)):
                    with (d/name).open("w",encoding="utf-8",newline="") as h: w=csv.DictWriter(h,fieldnames=header,delimiter="\t");w.writeheader();w.writerow(row)
            outs=[]
            for d in inputs:
                out=root/"out"/d.name; result=migrate_batch(d,out); self.assertTrue(result["unit"]["all_source_cells_preserved"]); self.assertTrue(result["eligibility"]["all_source_cells_preserved"]); outs.append(out)
            cov=validate_coverage(outs,2,True); self.assertTrue(cov["pass"],cov)
            self.assertEqual(cov["details"]["in0"]["eligibility_t0.tsv"]["header"],ELIGIBILITY_HEADER)
            self.assertEqual(cov["details"]["in0"]["unit_inventory.tsv"]["header"],UNIT_HEADER)
            with (outs[0]/"eligibility_t0.tsv").open(encoding="utf-8",newline="") as h:
                migrated_elig=list(csv.DictReader(h,delimiter="\t"))[0]
            self.assertEqual(migrated_elig["branch_label_raw"],"NOT_CAPTURED")
            self.assertEqual(migrated_elig["parent_model_id"],"NA_STRUCTURAL")

    def test_migration_does_not_pick_an_arbitrary_cohort_or_collapse_performance_list(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source=root/"in"; source.mkdir()
            elig={k:"NR" for k in ELIGIBILITY_LEGACY_23}; elig.update({"assessment_id":"E1","report_id":"R1","study_id":"S1","outcome_id":"O1","model_id":"M1","target_present_at_t0_01":"1","organism_unknown_at_t0_01":"1","organism_restricted_cohort_01":"0","future_event_target_01":"0","diagnostic_vs_prognostic_final":"DIAGNOSTIC_CURRENT","eligibility_status":"INCLUDE","adjudication_status":"FINAL_ADJUDICATED","evidence_id":"EV1"})
            rows=[]
            for cohort,unit in [("C1","U1"),("C2","U2")]:
                row={k:"NR" for k in UNIT_PILOT_32}; row.update({"unit_id":unit,"report_id":"R1","study_id":"S1","cohort_id":cohort,"outcome_id":"O1","model_id":"M1","dataset_id":f"D{unit}","performance_ids":"P1|P2"}); rows.append(row)
            for name,header,rows_to_write in (("eligibility_t0.tsv",ELIGIBILITY_LEGACY_23,[elig]),("unit_inventory.tsv",UNIT_PILOT_32,rows)):
                with (source/name).open("w",encoding="utf-8",newline="") as h: w=csv.DictWriter(h,fieldnames=header,delimiter="\t");w.writeheader();w.writerows(rows_to_write)
            out=root/"out"; result=migrate_batch(source,out); self.assertTrue(result["unit"]["all_source_cells_preserved"])
            with (out/"eligibility_t0.tsv").open(encoding="utf-8",newline="") as h: migrated=list(csv.DictReader(h,delimiter="\t"))
            self.assertEqual(migrated[0]["cohort_id"],"MULTIPLE_COHORTS_REQUIRES_SCOPE_SPLIT:C1|C2")
            self.assertEqual(migrated[0]["migration_status"],"MIGRATED_REQUIRES_SCOPE_EXPANSION")
            with (out/"unit_inventory.tsv").open(encoding="utf-8",newline="") as h: units=list(csv.DictReader(h,delimiter="\t"))
            self.assertTrue(all(u["performance_id"]=="UNCLEAR" for u in units))


if __name__=="__main__": unittest.main()
