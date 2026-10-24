from __future__ import annotations
import argparse, json, re, zipfile
from collections import Counter
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET
from docx import Document
from docx.shared import Inches

FONT='Times New Roman'
NS='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
W='{'+NS+'}'

# Unnumbered headings that must still be recognised as headings.
KNOWN_HEADINGS = {
    'Abstract','Key Messages','References','List of abbreviations','Abbreviations',
    'Declarations','Additional files','Tables and Figure Captions','Figure Captions',
    'Consent for publication','Availability of data and materials',
    "Authors' contributions",'Acknowledgements','Acknowledgments','Conflict of Interest',
    'Conflicts of Interest','Funding Source','Funding','Ethical Approval',
}


def _doc_paras(path):
    """Return (records, page_sizes, default_size, findings) read straight from the XML.

    records: list of dicts with text, in_table, bold, first_line, first_line_chars,
    jc, keep_next, line, sizes, missing_size, missing_font, bad_font
    """
    findings = []
    with zipfile.ZipFile(path) as z:
        doc = ET.fromstring(z.read('word/document.xml'))
        try:
            styles = ET.fromstring(z.read('word/styles.xml'))
        except KeyError:
            styles = None

    default_size = None
    if styles is not None:
        dd = styles.find(W+'docDefaults')
        if dd is not None:
            n = dd.find(W+'rPrDefault/'+W+'rPr/'+W+'sz')
            if n is not None:
                default_size = n.get(W+'val')

    table_para_ids = set()
    for tbl in doc.iter(W+'tbl'):
        for pe in tbl.iter(W+'p'):
            table_para_ids.add(id(pe))

    page_sizes = []
    for sp in doc.iter(W+'sectPr'):
        pg = sp.find(W+'pgSz')
        if pg is not None:
            page_sizes.append((pg.get(W+'w'), pg.get(W+'h')))

    records = []
    for pe in doc.iter(W+'p'):
        ppr = pe.find(W+'pPr')
        text = ''.join(t.text or '' for t in pe.iter(W+'t'))
        bold = any(r.find(W+'rPr/'+W+'b') is not None for r in pe.iter(W+'r'))
        ind = ppr.find(W+'ind') if ppr is not None else None
        sp = ppr.find(W+'spacing') if ppr is not None else None
        jc = ppr.find(W+'jc') if ppr is not None else None
        sizes, missing_size, missing_font, bad_font = [], 0, 0, 0
        for r in pe.iter(W+'r'):
            if not ''.join(t.text or '' for t in r.iter(W+'t')).strip():
                continue
            rpr = r.find(W+'rPr')
            sz = rpr.find(W+'sz') if rpr is not None else None
            rf = rpr.find(W+'rFonts') if rpr is not None else None
            if sz is None:
                missing_size += 1
            else:
                sizes.append(sz.get(W+'val'))
            if rf is None:
                missing_font += 1
            else:
                name = rf.get(W+'ascii') or rf.get(W+'asciiTheme')
                rtext = ''.join(t.text or '' for t in r.iter(W+'t'))
                # a run holding only symbol glyphs (e.g. a checkbox) may use a symbol font
                if name and name != FONT and re.search(r'[A-Za-z0-9]', rtext):
                    bad_font += 1
        records.append({
            'text': text, 'in_table': id(pe) in table_para_ids, 'bold': bold,
            'first_line': ind.get(W+'firstLine') if ind is not None else None,
            'first_line_chars': ind.get(W+'firstLineChars') if ind is not None else None,
            'jc': jc.get(W+'val') if jc is not None else None,
            'keep_next': ppr is not None and ppr.find(W+'keepNext') is not None,
            'line': sp.get(W+'line') if sp is not None else None,
            'sizes': sizes, 'missing_size': missing_size,
            'missing_font': missing_font, 'bad_font': bad_font,
        })
    return records, page_sizes, default_size, findings


def _is_heading(rec):
    if not rec['bold'] or rec['in_table']:
        return False
    t = rec['text'].strip()
    if not t or len(t) > 95:
        return False
    if re.match(r'^\d+(?:\.\d+)*\.?\s', t):
        return True
    if t in KNOWN_HEADINGS:
        return True
    return t.startswith('Declaration of generative AI')


def layout_findings(path: Path):
    """Paragraph-level layout consistency checks.

    Catches the defects that font/size auditing alone misses: first-line indent
    drift (a paragraph flush left among indented neighbours), ambiguous
    character-unit indents, headings that are justified or can be orphaned at a
    page break, runs that fall back to the theme font or default size, leading
    whitespace, doubled blank lines, mixed page sizes, mixed table-cell
    alignment, and words glued together by a lost space.
    """
    try:
        records, page_sizes, default_size, _ = _doc_paras(path)
    except Exception as exc:
        return ['layout:cannot_parse:%s' % exc]

    out = []
    miss = sum(r['missing_size'] for r in records)
    if miss:
        out.append('layout:runs_without_explicit_size=%d' % miss)
        if default_size is not None and default_size != '24':
            out.append('layout:docdefault_size=%s;expected=24 (11 pt) so the %d runs '
                       'without an explicit size render 11 pt' % (default_size, miss))
    mf = sum(r['missing_font'] for r in records)
    if mf:
        out.append('layout:runs_without_rFonts=%d (falls back to the theme font)' % mf)
    bf = sum(r['bad_font'] for r in records)
    if bf:
        out.append('layout:runs_with_non_TNR_font=%d' % bf)

    # --- main-text indent uniformity
    texts = [r['text'].strip() for r in records]
    try:
        start = next((i for i, t in enumerate(texts) if t == '1. Introduction'), None)
        if start is None:
            start = next(i for i, t in enumerate(texts)
                         if re.match(r'^1\.\s', t) and _is_heading(records[i]))
        end = next(i for i, t in enumerate(texts)
                   if i > start and re.match(r'^(List of abbreviations|Abbreviations|References)\b', t))
    except StopIteration:
        start = end = None
    if start is not None:
        span = [r for r in records[start:end]
                if r['text'].strip() and not r['in_table'] and not _is_heading(r)]
        vals = Counter(r['first_line'] for r in span)
        if len(vals) > 1:
            modal = vals.most_common(1)[0][0]
            for r in span:
                if r['first_line'] != modal:
                    out.append('layout:first_line_indent=%s;modal=%s;text=%s'
                               % (r['first_line'], modal, r['text'].strip()[:60]))

    for r in records:
        if r['in_table']:
            continue
        if r['first_line'] and r['first_line_chars'] not in (None, '0'):
            out.append('layout:ambiguous_indent=firstLine %s + firstLineChars %s;text=%s'
                       % (r['first_line'], r['first_line_chars'], r['text'].strip()[:60]))
        elif r['first_line'] and int(r['first_line']) % 10:
            out.append('layout:odd_indent=%s;text=%s' % (r['first_line'], r['text'].strip()[:60]))

    # --- headings
    heads = [r for r in records if _is_heading(r)]
    if heads:
        for r in heads:
            if r['jc'] == 'both':
                out.append('layout:heading_justified;text=%s' % r['text'].strip()[:60])
            if not r['keep_next']:
                out.append('layout:heading_without_keepNext;text=%s' % r['text'].strip()[:60])
            if r['first_line'] not in (None, '0'):
                out.append('layout:heading_indented=%s;text=%s' % (r['first_line'], r['text'].strip()[:60]))
        sizes = {s for r in heads for s in r['sizes']}
        if len(sizes) > 1:
            out.append('layout:heading_size_mixed=%s' % ','.join(sorted(sizes)))

    # --- text hygiene
    blanks = 0
    seen_text = False
    for r in records:
        t = r['text']
        if not t.strip():
            blanks += 1
            continue
        if blanks >= 2 and seen_text:
            out.append('layout:consecutive_blank_paragraphs=%d;before=%s' % (blanks, t.strip()[:50]))
        blanks = 0
        seen_text = True
        if t[0] in ' \t\u3000':
            out.append('layout:leading_whitespace;text=%r' % t[:50])
        for m in re.finditer(r'\b[a-z]{2,}(?:[A-Z][a-z]{2,})+', t):
            out.append('layout:run_together=%s;text=%s' % (m.group(0), t[max(0, m.start()-30):m.end()+30]))
        for m in re.finditer(r'[a-z\)][.,;][A-Z][a-z]', t):
            out.append('layout:missing_space_after_punctuation;text=%s'
                       % t[max(0, m.start()-30):m.end()+30])
        if re.match(r'^[a-z]{3,}\s', t) and len(t) > 40:
            out.append('layout:lowercase_sentence_start;text=%s' % t[:60])

    # --- page geometry
    if len(set(page_sizes)) > 1:
        out.append('layout:page_size_mismatch=%s' % sorted(set(page_sizes)))

    # --- table cell alignment
    with zipfile.ZipFile(path) as z:
        doc = ET.fromstring(z.read('word/document.xml'))
    for ti, tbl in enumerate(doc.iter(W+'tbl')):
        vals = Counter()
        for pe in tbl.iter(W+'p'):
            jc = pe.find(W+'pPr/'+W+'jc')
            v = jc.get(W+'val') if jc is not None else 'none'
            if v != 'center':
                vals[v] += 1
        if len(vals) > 1:
            out.append('layout:table_%d_alignment_mixed=%s' % (ti + 1, dict(vals)))

    return out


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

def audit_file(path: Path, margin_min: float=1.0, table_exception=True, layout=True):
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
    if layout and profile=='text':
        findings.extend(layout_findings(path))
    status='PASS' if not findings else ('WARN' if profile=='table' and all('margin' in x or 'font_size=9.0' in x for x in findings) else 'FAIL')
    return {'path':str(path),'status':status,'profile':profile,'margins':[{"top":inches(s.top_margin),"bottom":inches(s.bottom_margin),"left":inches(s.left_margin),"right":inches(s.right_margin)} for s in doc.sections],'counts':counts,'findings':findings[:200]}

def main():
    ap=argparse.ArgumentParser(description='Audit SciXZ DOCX font, size, spacing, margins, and table exceptions.')
    ap.add_argument('path')
    ap.add_argument('--out',default='')
    ap.add_argument('--json',action='store_true')
    ap.add_argument('--margin-min',type=float,default=1.0)
    ap.add_argument('--no-table-exception',action='store_true')
    ap.add_argument('--no-layout',action='store_true',help='skip paragraph-level layout checks')
    args=ap.parse_args()
    root=Path(args.path)
    files=[root] if root.is_file() else sorted(root.rglob('*.docx'))
    results=[audit_file(p,args.margin_min,not args.no_table_exception,not args.no_layout) for p in files]
    payload={'policy':'default-manuscript-v1','files':results,'status':'PASS' if all(r['status']!='FAIL' for r in results) else 'FAIL'}
    text=json.dumps(payload,ensure_ascii=False,indent=2)
    if args.out: Path(args.out).write_text(text+'\n',encoding='utf-8')
    print(text if args.json or not args.out else f'wrote={args.out};status={payload["status"]};files={len(files)}')
    return 0 if payload['status']=='PASS' else 2
if __name__=='__main__': raise SystemExit(main())



