from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "anti_baibai_awas_pipeline.py"
)
SPEC = importlib.util.spec_from_file_location("anti_baibai_awas_pipeline", SCRIPT_PATH)
assert SPEC and SPEC.loader
pipeline = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pipeline)


def test_process_segment_runs_initial_baibai_and_reprocesses_until_below_threshold() -> None:
    risks = [0.72, 0.43]
    calls: list[tuple[str, str, int]] = []

    def fake_baibai(text: str, filename: str, rounds: int) -> tuple[str, list[str]]:
        calls.append((text, filename, rounds))
        return f"{text}|pass{len(calls)}", [filename]

    def fake_anti(text: str) -> tuple[float, list[str]]:
        return risks.pop(0), [f"risk for {text}"]

    record = pipeline.process_segment_until_threshold(
        index=1,
        segment="原始段落",
        run_id="demo",
        threshold=0.5,
        rounds=2,
        max_reprocess_attempts=3,
        baibai_runner=fake_baibai,
        anti_detector=fake_anti,
    )

    assert len(calls) == 2
    assert calls[0] == ("原始段落", "demo_seg001_pass00.txt", 2)
    assert calls[1] == ("原始段落|pass1", "demo_seg001_pass01.txt", 2)
    assert record.selected is True
    assert record.processed_text == "原始段落|pass1|pass2"
    assert record.risk_history == [0.72, 0.43]
    assert record.final_risk == 0.43
    assert record.unresolved_high_risk is False


def test_process_segment_keeps_low_risk_after_initial_baibai_pass() -> None:
    calls: list[tuple[str, str, int]] = []

    def fake_baibai(text: str, filename: str, rounds: int) -> tuple[str, list[str]]:
        calls.append((text, filename, rounds))
        return f"{text}|pass{len(calls)}", [filename]

    def fake_anti(text: str) -> tuple[float, list[str]]:
        return 0.22, ["low risk"]

    record = pipeline.process_segment_until_threshold(
        index=2,
        segment="低风险段落",
        run_id="demo",
        threshold=0.5,
        rounds=2,
        max_reprocess_attempts=3,
        baibai_runner=fake_baibai,
        anti_detector=fake_anti,
    )

    assert len(calls) == 1
    assert record.selected is False
    assert record.processed_text == "低风险段落|pass1"
    assert record.risk_history == [0.22]
    assert record.final_risk == 0.22

