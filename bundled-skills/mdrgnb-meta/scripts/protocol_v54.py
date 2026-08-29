#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path
from urllib.parse import quote, unquote

MISSING = {
    "NA_STRUCTURAL", "NR_SOURCE", "NOT_CALCULABLE", "NOT_RUN", "NOT_CAPTURED",
    "UNCLEAR", "PENDING_REVIEW", "SOURCE_NOT_ACCESSIBLE", "CONFLICT",
    # Read-only compatibility for frozen v5.3/v5.4 artifacts; v5.6 fact QA forbids these.
    "NA", "NR", "NOT_ACCESSIBLE",
}
TRUE = {"1", "TRUE", "YES", "Y"}
FALSE = {"0", "FALSE", "NO", "N"}
SEMKEY_COMMON = ("v", "entity", "report", "study")
SEMKEY_SUFFIX = {
    "study": ("project",),
    "cohort": ("source", "site_time", "sampling"),
    "dataset": ("cohort", "role", "population", "axis"),
    "outcome": ("target", "t0", "reference", "case_control"),
    "model": ("family", "algorithm", "predictors", "version"),
    "performance": ("model", "outcome", "dataset", "population", "metric", "subgroup", "timepoint"),
    "threshold": ("performance", "threshold", "selection"),
    "calibration": ("performance", "metric"),
    "predictor": ("model", "construct", "window", "unit", "coding", "coefficient"),
}
MAPPING_DECISIONS = {
    "ONE_TO_ONE", "MERGED_TO_FINAL", "SPLIT_TO_FINAL", "REMOVED_DUPLICATE",
    "REMOVED_INELIGIBLE_ENTITY", "ADDED_BY_ADJUDICATION",
}
RELATION_BASIS_CODES = {
    "IDENTITY", "SOURCE_COARSE_TO_FINER", "SOURCE_CATEGORY_GROUP_TO_LEVELS",
    "SOURCE_COMPOSITE_TO_COMPONENTS", "MULTIPLE_SOURCE_TO_ONE_FINAL",
    "SOURCE_REMOVAL", "ADJUDICATOR_ADDITION",
}


def norm(value: str | None) -> str:
    return (value or "").strip().upper()


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def write_json(payload: dict, out: Path | None) -> None:
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if out:
        out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


def encode_component(value: str) -> str:
    # urllib's safe default retains '/', which is allowed; the contract only reserves these three.
    return quote(value, safe="/:._-", encoding="utf-8").replace("%7c", "%7C").replace("%3d", "%3D")


def parse_semkey(value: str, compat_v53: bool = False) -> tuple[list[str], dict[str, str], list[str]]:
    errors: list[str] = []
    parts = value.split("|")
    names: list[str] = []
    values: dict[str, str] = {}
    for part in parts:
        if part.count("=") != 1:
            errors.append(f"component must contain exactly one '=': {part!r}")
            continue
        name, raw = part.split("=", 1)
        if not name or not raw:
            errors.append(f"empty name/value: {part!r}")
            continue
        if name in values:
            errors.append(f"duplicate field: {name}")
            continue
        if "|" in raw or "=" in raw:
            errors.append(f"unescaped reserved character in {name}")
        if "%" in raw:
            import re
            for m in re.finditer("%", raw):
                triplet = raw[m.start():m.start()+3]
                if len(triplet) != 3 or any(c not in "0123456789ABCDEF" for c in triplet[1:]):
                    if not compat_v53:
                        errors.append(f"noncanonical percent escape in {name}: {triplet!r}")
        names.append(name)
        values[name] = unquote(raw, encoding="utf-8", errors="strict")
    return names, values, errors
