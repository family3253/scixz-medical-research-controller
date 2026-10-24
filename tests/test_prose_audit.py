from pathlib import Path
import importlib.util

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'audit_prose.py'
spec = importlib.util.spec_from_file_location('audit_prose', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLEAN = """# Abstract
Aims: To estimate the burden of carbapenem-resistant infection.
Results: Deaths fell from 15,300 to 15,086 (95% UI 11,390-18,783) and the rate halved.
Conclusions: Burden shifted toward older adults.

# 1. Introduction
Carbapenems are reserved agents.

# 4.1 Limitations
Estimates are model-based and carry substantial uncertainty.

# 5. Conclusions
Deaths are projected to reach 14,399 by 2030.
"""

DEFENSIVE = """# Abstract
Results: Concordance was high, although the ranking diverged only modestly overall.
Conclusions: Unfortunately the estimates cannot identify causal effects.

# 5. Conclusions
The approach may potentially suggest that results could possibly differ.
"""

CHINESE = """# 摘要
结果：本文仅在两个数据集上做了初步尝试，只能提供有限参考。
"""


def test_clean_text_passes(tmp_path):
    p = tmp_path / 'clean.md'
    p.write_text(CLEAN, encoding='utf-8')
    result = mod.audit(p)
    assert result['status'] == 'PASS'
    assert result['counts']['P1'] == 0


def test_defensive_abstract_blocks_delivery(tmp_path):
    p = tmp_path / 'defensive.md'
    p.write_text(DEFENSIVE, encoding='utf-8')
    result = mod.audit(p)
    assert result['status'] == 'FAIL'
    rules = {f['rule'] for f in result['findings'] if f['severity'] == 'P1'}
    assert 'self_weakening' in rules
    assert 'apology' in rules
    assert all(f['section'] in ('abstract', 'conclusions') for f in result['findings']
               if f['severity'] == 'P1')


def test_caveat_in_abstract_is_blocking(tmp_path):
    p = tmp_path / 'caveat.md'
    p.write_text('# Abstract\nResults: The estimate is uncertain and should be interpreted with caution.\n',
                 encoding='utf-8')
    result = mod.audit(p)
    hits = [f for f in result['findings'] if f['rule'] == 'caveat_in_high_impact']
    assert hits and hits[0]['severity'] == 'P1'


def test_limitations_are_not_high_impact(tmp_path):
    p = tmp_path / 'lim.md'
    p.write_text(CLEAN, encoding='utf-8')
    result = mod.audit(p)
    assert not any(f['rule'] == 'caveat_in_high_impact' for f in result['findings'])


def test_stacked_hedges_are_flagged(tmp_path):
    p = tmp_path / 'hedge.md'
    p.write_text(DEFENSIVE, encoding='utf-8')
    result = mod.audit(p)
    assert any(f['rule'] == 'stacked_hedge' for f in result['findings'])


def test_chinese_rules_can_be_disabled(tmp_path):
    p = tmp_path / 'zh.md'
    p.write_text(CHINESE, encoding='utf-8')
    assert any(f['rule'] == 'zh_defensive' for f in mod.audit(p)['findings'])
    assert not any(f['rule'] == 'zh_defensive' for f in mod.audit(p, include_zh=False)['findings'])


def test_abstract_without_number_is_blocking(tmp_path):
    p = tmp_path / 'noheadline.md'
    p.write_text('# Abstract\nAims: To describe the burden.\nConclusions: The burden is large.\n', encoding='utf-8')
    result = mod.audit(p)
    assert any(f['rule'] == 'abstract_without_headline' for f in result['findings'])
    assert result['status'] == 'FAIL'
