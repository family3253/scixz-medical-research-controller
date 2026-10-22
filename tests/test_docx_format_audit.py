from pathlib import Path
import importlib.util
from docx import Document
from docx.shared import Inches, Pt

SCRIPT=Path(__file__).resolve().parents[1]/'scripts'/'audit_docx_format.py'
spec=importlib.util.spec_from_file_location('audit_docx_format',SCRIPT)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def make_doc(path, good=True):
    d=Document()
    sec=d.sections[0]
    for attr in ('top_margin','bottom_margin','left_margin','right_margin'):
        setattr(sec,attr,Inches(1 if good else 0.5))
    s=d.styles['Normal']; s.font.name='Times New Roman'; s.font.size=Pt(12); s.paragraph_format.line_spacing=2; s.paragraph_format.space_before=Pt(0); s.paragraph_format.space_after=Pt(0)
    p=d.add_paragraph('Body paragraph')
    if good:
        p.runs[0].font.name='Times New Roman'; p.runs[0].font.size=Pt(12)
    else:
        p.runs[0].font.name='Calibri'; p.runs[0].font.size=Pt(11)
    d.save(path)

def test_good_manuscript_docx_passes(tmp_path):
    p=tmp_path/'good.docx'; make_doc(p,True)
    result=mod.audit_file(p)
    assert result['status']=='PASS'
    assert result['findings']==[]

def test_bad_manuscript_docx_fails(tmp_path):
    p=tmp_path/'bad.docx'; make_doc(p,False)
    result=mod.audit_file(p)
    assert result['status']=='FAIL'
    assert any('margin' in x for x in result['findings'])
    assert any('font=' in x or 'font_size=' in x for x in result['findings'])
