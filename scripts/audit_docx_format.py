from __future__ import annotations
import argparse, json, re
from pathlib import Path
from typing import Any
from docx import Document
from docx.shared import Inches

FONT='Times New Roman'
NS='http://schemas.openxmlformats.org/wordprocessingml/2006/main'

def pt(v): return None if v is None else round(v.pt,2)
def inches(v): return None if v is None else round(v.inches,3)

def style_effective_para(para):
    style=para.style
    return style.paragraph_format

def effective_font(run, para):
    name=run.font.name or getattr(para.style.font,'name',None)
    size=pt(run.font.size) or pt(getattr(para.style.font,'size',None))
    return name,size

def expected_profile(path: Path, table_exception: bool=True):
    n=path.name.lower()
    return 'table' if table_exception and n.startswith('table_') else 'text'

def audit_file(path: Path, margin_min: float=1.0, table_exception=True):
    findings=[]; counts={'body_paragraphs':0,'table_paragraphs':0,'runs':0,'table_runs':0}
    try: doc=Document(path)
    except Exception as exc:
        return {'path':str(path),'status':'FAIL','findings':[f'cannot_parse:{exc}'],'counts':counts}
    profile=expected_profile(path,table_exception)
    for si,sec in enumerate(doc.sections):
        vals={'top':inches(sec.top_margin),'bottom':inches(sec.bottom_margin),'left':inches(sec.left_margin),'right':inches(sec.right_margin)}
        required=0.6 if profile=='table' else margin_min
        for k,v in vals.items():
            if v is None or v < required:
                findings.append(f'section_{si}_margin_{k}={v};expected>={required}')
    def check_para(para, in_table=False, para_index=-1):
        counts['table_paragraphs' if in_table else 'body_paragraphs']+=1
        fmt=para.paragraph_format
        pf=style_effective_para(para)
        line=fmt.line_spacing if fmt.line_spacing is not None else pf.line_spacing
        before=pt(fmt.space_before) if fmt.space_before is not None else pt(pf.space_before)
        after=pt(fmt.space_after) if fmt.space_after is not None else pt(pf.space_after)
        expected_line=1.0 if in_table else 2.0
        if line is not None:
            line_num=float(line) if not hasattr(line,'pt') else float(line.pt)
            if abs(line_num-expected_line)>0.05:
                findings.append(f'paragraph_line_spacing={line_num};expected={expected_line};text={para.text[:60]}')
        if before not in (None,0): findings.append(f'paragraph_space_before={before};text={para.text[:60]}')
        if after not in (None,0): findings.append(f'paragraph_space_after={after};text={para.text[:60]}')
        for run in para.runs:
            counts['table_runs' if in_table else 'runs']+=1
            name,size=effective_font(run,para)
            title_exception=(not in_table and para_index==0 and path.name in {'Title_Page_Annals_of_Medicine.docx','Manuscript_Annals_of_Medicine_With_Author_Details.docx','Supplementary_Figures_Annals_of_Medicine.docx'})
            expected_size=9.0 if in_table else (14.0 if para.style.name=='Title' or title_exception else 12.0)
            if name and name != FONT: findings.append(f'font={name};expected={FONT};text={run.text[:60]}')
            if size is not None and abs(size-expected_size)>0.1:
                findings.append(f'font_size={size};expected={expected_size};text={run.text[:60]}')
    for idx,para in enumerate(doc.paragraphs): check_para(para,False,idx)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for idx,para in enumerate(cell.paragraphs): check_para(para,True,idx)
    status='PASS' if not findings else ('WARN' if profile=='table' and all('margin' in x or 'font_size=9.0' in x for x in findings) else 'FAIL')
    return {'path':str(path),'status':status,'profile':profile,'margins':[{"top":inches(s.top_margin),"bottom":inches(s.bottom_margin),"left":inches(s.left_margin),"right":inches(s.right_margin)} for s in doc.sections],'counts':counts,'findings':findings[:200]}

def main():
    ap=argparse.ArgumentParser(description='Audit SciXZ DOCX font, size, spacing, margins, and table exceptions.')
    ap.add_argument('path')
    ap.add_argument('--out',default='')
    ap.add_argument('--json',action='store_true')
    ap.add_argument('--margin-min',type=float,default=1.0)
    ap.add_argument('--no-table-exception',action='store_true')
    args=ap.parse_args()
    root=Path(args.path)
    files=[root] if root.is_file() else sorted(root.rglob('*.docx'))
    results=[audit_file(p,args.margin_min,not args.no_table_exception) for p in files]
    payload={'policy':'default-manuscript-v1','files':results,'status':'PASS' if all(r['status']!='FAIL' for r in results) else 'FAIL'}
    text=json.dumps(payload,ensure_ascii=False,indent=2)
    if args.out: Path(args.out).write_text(text+'\n',encoding='utf-8')
    print(text if args.json or not args.out else f'wrote={args.out};status={payload["status"]};files={len(files)}')
    return 0 if payload['status']=='PASS' else 2
if __name__=='__main__': raise SystemExit(main())



