#!/usr/bin/env python3
"""Audit prose for defensive writing and press-release structure violations.

Two rule sets are enforced together:

1. Anti-defensive writing (claim-forward prose): unnecessary disclaimers,
   self-weakening quantifiers, apology framing, reflexive contrast, stacked
   hedges, pre-emptive explanations, and caveats placed in high-impact
   positions.
2. Press-release principle: no process chronology, no self-verdicts, no
   unwinnable contests, and every results block must carry a quantified claim.

The script is a detector, not a rewriter. It reports the sentence, the section,
a severity, and the repair move to apply. Deleting the sentence is always the
first option; narrowing the claim, switching the evaluation dimension,
explaining a trade-off, or reorganising the section come after it.

Usage:
    python audit_prose.py manuscript.docx
    python audit_prose.py manuscript.docx --json --out prose.json
    python audit_prose.py draft.md --min-severity P2
    python audit_prose.py manuscript.docx --include-zh
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

# --------------------------------------------------------------------------- sections
# Order matters: specific numbered sections before the generic numbered pattern.
HEAD_PATTERNS = [
    (r'^abstract$', 'abstract'),
    (r'^摘要$', 'abstract'),
    (r'^key messages?$', 'key_messages'),
    (r'^关键消息$', 'key_messages'),
    (r'^highlights?$', 'key_messages'),
    (r'^\d+(\.\d+)?\.?\s*limitations?', 'limitations'),
    (r'^(?:局限性|研究局限)$', 'limitations'),
    (r'^\d+\.?\s*introduction', 'introduction'),
    (r'^引言$', 'introduction'),
    (r'^\d+\.?\s*methods?', 'methods'),
    (r'^(?:方法|研究方法)$', 'methods'),
    (r'^\d+\.?\s*results?', 'results'),
    (r'^结果$', 'results'),
    (r'^\d+\.?\s*discussion', 'discussion'),
    (r'^讨论$', 'discussion'),
    (r'^\d+\.?\s*conclusions?', 'conclusions'),
    (r'^结论$', 'conclusions'),
    (r'^\d+(\.\d+)?\.?\s', 'methods_or_results'),
    (r'^(references?|bibliography)$', 'references'),
    (r'^(?:参考文献|文献)$', 'references'),
    (r'^declarations?$', 'declarations'),
    (r'^(list of abbreviations|abbreviations)$', 'back_matter'),
    (r'^(additional files|tables and figure captions|figure captions|supplementary.*)$', 'back_matter'),
]

# Sections where a caveat costs the most: the reader who stops after the
# abstract must not be told the finding is small, mechanical, or unsafe.
HIGH_IMPACT = {'abstract', 'conclusions', 'key_messages'}
MID = {'introduction', 'discussion', 'results'}
ALLOWED = {'limitations', 'methods', 'references', 'declarations', 'back_matter'}

# --------------------------------------------------------------------------- rules
# (id, severity, regex, action)
RULES = [
    # ---- disclaimers: telling the reader what the paper does NOT do
    ('disclaimer', 'P1',
     r'\b(?:does not|do not|did not) (?:claim|attempt|address|seek to|purport|intend)\b',
     'Delete. State what the analysis does; the reader does not need the negative.'),
    ('disclaimer', 'P1',
     r'\bshould not be (?:read|interpreted|taken|construed) as\b',
     'Delete, or convert to a positive scope statement ("the estimates cover ...").'),
    ('disclaimer', 'P1',
     r'\bis not (?:a|an|intended to be|meant to be) (?:substitute|causal|estimate of|measure of)\b',
     'Delete unless the contrast defines the metric itself; if it does, keep it once, in Methods.'),
    ('disclaimer', 'P2',
     r'\b(?:no attempt (?:is|was) made|outside the scope of this (?:paper|study))\b',
     'Delete. Scope is shown by what the paper reports, not by what it declines.'),
    ('disclaimer', 'P2',
     r'\b(?:it should be noted|it is worth noting|it is important to note|to be clear|note that)\b',
     'Delete the frame and keep the fact, if the fact carries information.'),
    ('disclaimer', 'P2',
     r'\b(?:of course|certainly|admittedly|arguably)\b',
     'Delete. These add tone, not content.'),

    # ---- self-weakening quantifiers on the paper's own result
    ('self_weakening', 'P1',
     r'\bonly (?:modestly|slightly|marginally|partially|weakly|partly)\b',
     'Report the magnitude. "Only modestly" contradicts the number that follows it.'),
    ('self_weakening', 'P1',
     r'\b(?:merely|just a|nothing more than)\b',
     'Delete the minimiser; state the quantity.'),
    ('self_weakening', 'P2',
     r'\b(?:limited improvement|modest improvement|marginal gain|small gain)\b',
     'Give the delta and let the reader judge whether it is small.'),
    ('self_weakening', 'P2',
     r'\b(?:preliminary|exploratory|tentative) (?:analysis|result|finding|evidence|comparison)\b',
     'Remove the label unless the design is genuinely exploratory; if it is, say what it can support.'),
    ('self_weakening', 'P2',
     r'\b(?:for reference only|for illustrative purposes only)\b',
     'Delete. Either the result is used in the argument or it is not reported.'),
    ('self_weakening', 'P2',
     r'\b(?:preliminary|exploratory|tentative)\b',
     'Remove the label unless the design is genuinely exploratory; if it is, say what it can support.'),
    ('self_weakening', 'P2',
     r'\b(?:imprecise|noisy|unstable|fragile)\b',
     'Report the interval or the estimate; an adjective is not a result.'),
    ('self_verdict', 'P2',
     r'\b(?:none|neither) of (?:these|the|our) [a-z ]{0,30}(?:identif|establish|support|allow)',
     'Delete. It withdraws the paper\'s own framework at the point where the reader expects the payoff.'),

    # ---- apology framing
    ('apology', 'P1', r'\bunfortunately\b',
     'Delete. A finding is not a misfortune; report it and its condition.'),
    ('apology', 'P2', r'\b(?:we regret|regrettably|sadly)\b', 'Delete.'),

    # ---- self-verdict outside Limitations
    ('self_verdict', 'P1',
     r'\b(?:reveals?|exposes?|highlights?) (?:the )?(?:limitations?|weakness(?:es)?)\b',
     'Delete outside Limitations. One local observation is not a verdict on the method.'),
    ('self_verdict', 'P2',
     r'\b(?:suffers? from|is hampered by|is constrained by)\b',
     'Replace with the specific condition ("the estimates cover 36 locations").'),

    # ---- unwinnable contest
    ('contest_lost', 'P1',
     r'\b(?:lags? behind|falls? short of|inferior to|is worse than|still below|underperforms?)\b',
     'Do not stage a contest you lose. Re-choose the dimension or the comparator, then name the game you win.'),
    ('contest_lost', 'P2',
     r'\b(?:fails? to (?:capture|account for|reproduce|match))\b',
     'Narrow the claim to what the design does, or state the trade-off explicitly.'),

    # ---- reflexive contrast
    ('reflexive_contrast', 'P3',
     r'\brather than\b',
     'Keep when the contrast is the argument (e.g. "interpreted descriptively rather than causally"); '
     'delete when it only pre-empts a misreading.'),
    ('reflexive_contrast', 'P3',
     r'\binstead of\b',
     'Keep when the alternative is a real competitor; delete when it is a straw man.'),
    ('reflexive_contrast', 'P2',
     r'\bnot (?:merely |simply )?[a-z][^.;]{2,45}? but (?:also )?[a-z]',
     'Reflexive "not X but Y". State Y; mention X only if the contrast carries information.'),

    # ---- pre-emptive explanation of an apparent inconsistency
    ('preemptive', 'P2',
     r'\b(?:which is why|this is (?:why|because)|that is why)\b',
     'Replace with two parallel facts and let the reader draw the link.'),
    ('preemptive', 'P2',
     r'\b(?:expected|implied|driven) by construction\b',
     'If the result follows mechanically from the definition, say so once in Methods, not as a result caveat.'),
    ('preemptive', 'P2',
     r'\bpartly structural\b',
     'Delete. If the concordance is structural, the structural explanation belongs in Methods.'),

    # ---- explicit weakness verbs
    ('cannot', 'P2',
     r'\bcannot (?:identify|establish|separate|exclude|determine|distinguish|resolve|be excluded)\b',
     'Prefer a positive statement of what the design does estimate; keep "cannot" only where it changes the interpretation.'),
    ('cannot', 'P3',
     r'\b(?:may|might|could) not be (?:generalisable|generalizable|representative)\b',
     'State the scope instead: which populations the estimate covers.'),

    # ---- process chronology (press-release rule 2)
    ('process', 'P1',
     r'\b(?:we|the authors) (?:first|initially|then|next|subsequently) (?:tried|attempted|considered|explored)\b',
     'Delete. Keep the final standing logic, not the order of attempts.'),
    ('process', 'P2',
     r'\b(?:in|at) an earlier (?:version|draft|stage)\b',
     'Delete. The reader is buying the finished product, not the lab log.'),
    ('process', 'P2',
     r'\bwas (?:later |subsequently )?(?:replaced|superseded|abandoned) by\b',
     'Delete the abandoned route unless it changes the interpretation.'),

    # ---- Chinese equivalents
    ('zh_defensive', 'P1',
     r'(?:(?<!不)仅|只是|仅限于|仅能|只能)[^。；]{0,20}(?:初步|有限|参考|尝试)',
     '删除自贬限定，直接说明研究做了什么、覆盖什么范围。'),
    ('zh_defensive', 'P1', r'遗憾的是', '删除。'),
    ('zh_defensive', 'P2',
     r'(?:仍有(?:很大|较大)?提升空间|不足之处|有待(?:进一步)?(?:研究|完善|验证))',
     '改为具体信息：缺哪个条件、影响哪条结论。'),
    ('zh_defensive', 'P2',
     r'(?:众所周知|需要注意的是|不难看出|显而易见)',
     '删除套语，直接给事实。'),
    ('zh_defensive', 'P2', r'(?:无法|难以)(?:识别|区分|排除|确定)', '改为正向陈述：该设计估计了什么。'),
]

HEDGES = r'\b(?:may|might|could|possibly|potentially|perhaps|arguably|seemingly|appears? to|suggests? that|likely|somewhat|relatively)\b'
CAVEAT = (r'\b(?:limitation|caveat|caution|uncertain|uncertainty|imprecise|wide interval|'
          r'underpowered|not powered|conservative estimate|should be interpreted)\b')

COMPILED = [(rid, sev, re.compile(pat, re.I), act) for rid, sev, pat, act in RULES]
HEDGE_RE = re.compile(HEDGES, re.I)
CAVEAT_RE = re.compile(CAVEAT, re.I)
SENT_SPLIT = re.compile(r'(?<=[.;:!?。！？；])\s*(?=[A-Z(\[\u4e00-\u9fff])')


# --------------------------------------------------------------------------- input
def read_docx(path: Path):
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml').decode('utf-8')
    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml)
    out = []
    for p in root.iter(W + 'p'):
        text = ''.join(t.text or '' for t in p.iter(W + 't')).strip()
        bold = any(r.find(W + 'rPr/' + W + 'b') is not None for r in p.iter(W + 'r'))
        out.append((text, bold))
    return out


def read_text(path: Path):
    raw = path.read_text(encoding='utf-8')
    out = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        bold = line.startswith('#')
        out.append((line.lstrip('#').strip(), bold))
    return out


def section_of(text: str, bold: bool, current: str):
    """Return (new_section, is_heading)."""
    t = text.strip().lower().rstrip(':')
    if not t or len(t) > 90:
        return current, False
    for pat, name in HEAD_PATTERNS:
        if re.match(pat, t):
            if name == 'methods_or_results':
                # numbered subsection: keep the parent section
                return current, True
            return name, True
    return current, False


def severity_for(section: str, base: str):
    """Raise severity when the sentence sits in a high-impact position."""
    order = ['P3', 'P2', 'P1']
    sev = base
    if section in HIGH_IMPACT and sev == 'P2':
        sev = 'P1'
    elif section in ALLOWED and sev == 'P1' and section == 'limitations':
        sev = 'P2'
    return sev


# --------------------------------------------------------------------------- audit
def audit(path: Path, min_sev='P3', include_zh=True):
    rows = read_docx(path) if path.suffix.lower() == '.docx' else read_text(path)
    findings = []
    section = 'front_matter'
    stats = {'sentences': 0, 'words': 0, 'sections': []}
    abstract_parts = []

    for idx, (text, bold) in enumerate(rows):
        if not text:
            continue
        new_sec, is_head = section_of(text, bold, section)
        if is_head:
            if new_sec != section:
                stats['sections'].append(new_sec)
            section = new_sec
            continue
        if section in ('references', 'declarations', 'back_matter'):
            continue
        if section == 'abstract':
            abstract_parts.append(text)

        for sent in SENT_SPLIT.split(text):
            sent = sent.strip()
            if len(sent.split()) < 4 and len(sent) < 12:
                continue
            stats['sentences'] += 1
            stats['words'] += len(sent.split())

            for rid, base_sev, rx, action in COMPILED:
                if rid == 'zh_defensive' and not include_zh:
                    continue
                m = rx.search(sent)
                if not m:
                    continue
                findings.append({
                    'rule': rid,
                    'severity': severity_for(section, base_sev),
                    'section': section,
                    'paragraph': idx,
                    'match': m.group(0),
                    'sentence': sent[:300],
                    'action': action,
                })

            # stacked hedges: two or more in one sentence
            hedges = HEDGE_RE.findall(sent)
            if len(hedges) >= 2:
                findings.append({
                    'rule': 'stacked_hedge',
                    'severity': severity_for(section, 'P2'),
                    'section': section,
                    'paragraph': idx,
                    'match': ', '.join(sorted(set(h.lower() for h in hedges))),
                    'sentence': sent[:300],
                    'action': 'Keep at most one hedge; if the uncertainty is real, name its source.',
                })

            # caveat sentence in a high-impact position
            if section in HIGH_IMPACT and CAVEAT_RE.search(sent):
                findings.append({
                    'rule': 'caveat_in_high_impact',
                    'severity': 'P1',
                    'section': section,
                    'paragraph': idx,
                    'match': CAVEAT_RE.search(sent).group(0),
                    'sentence': sent[:300],
                    'action': 'Move the caveat to Methods or Limitations; keep the headline clean.',
                })

        # press-release: a results block with no number carries no claim
        if section == 'results' and len(text.split()) > 40 and not re.search(r'\d', text):
            findings.append({
                'rule': 'result_without_number',
                'severity': 'P3',
                'section': section,
                'paragraph': idx,
                'match': '',
                'sentence': text[:300],
                'action': 'Give the estimate this block exists to report, or move it to the Discussion.',
            })

    # abstract must open the press conference with a quantified result
    abs_text = ' '.join(abstract_parts)
    if abs_text and not re.search(r'\d', abs_text):
        findings.append({
            'rule': 'abstract_without_headline',
            'severity': 'P1',
            'section': 'abstract',
            'paragraph': -1,
            'match': '',
            'sentence': '',
            'action': 'The abstract carries no number. State the strongest result with its estimate.',
        })

    order = {'P1': 0, 'P2': 1, 'P3': 2}
    findings = [f for f in findings if order[f['severity']] <= order[min_sev]]
    findings.sort(key=lambda f: (order[f['severity']], f['paragraph']))

    counts = {s: sum(1 for f in findings if f['severity'] == s) for s in ('P1', 'P2', 'P3')}
    return {
        'path': str(path),
        'status': 'FAIL' if counts['P1'] else ('WARN' if counts['P2'] else 'PASS'),
        'counts': counts,
        'stats': stats,
        'findings': findings,
    }


def main():
    ap = argparse.ArgumentParser(description='Audit prose for defensive writing and press-release violations.')
    ap.add_argument('path')
    ap.add_argument('--out', default='')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--min-severity', default='P3', choices=['P1', 'P2', 'P3'])
    ap.add_argument('--no-zh', action='store_true', help='skip Chinese pattern rules')
    args = ap.parse_args()

    root = Path(args.path)
    files = [root] if root.is_file() else sorted(
        p for p in root.rglob('*') if p.suffix.lower() in ('.docx', '.txt', '.md'))
    results = [audit(p, args.min_severity, not args.no_zh) for p in files]
    payload = {
        'policy': 'prose-anti-defensive-v1',
        'files': results,
        'status': 'FAIL' if any(r['status'] == 'FAIL' for r in results)
                  else ('WARN' if any(r['status'] == 'WARN' for r in results) else 'PASS'),
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text + '\n', encoding='utf-8')
        print('wrote=%s;status=%s;files=%d' % (args.out, payload['status'], len(files)))
    else:
        print(text if args.json else _summary(payload))
    return 0 if payload['status'] != 'FAIL' else 2


def _summary(payload):
    lines = []
    for r in payload['files']:
        c = r['counts']
        lines.append('%s  %s  P1=%d P2=%d P3=%d' % (r['status'], r['path'], c['P1'], c['P2'], c['P3']))
        for f in r['findings']:
            lines.append('  [%s] %-24s %-13s %r' % (f['severity'], f['rule'], f['section'], f['match'][:40]))
            lines.append('        %s' % f['sentence'][:150])
            lines.append('        -> %s' % f['action'])
    lines.append('OVERALL: %s' % payload['status'])
    return '\n'.join(lines)


if __name__ == '__main__':
    sys.exit(main())
