#!/usr/bin/env python3
"""Extract a sanitized, read-only manifest from n8n JSON or SQLite."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List
from urllib.parse import parse_qsl, urlsplit


CREDENTIAL_QUERY_KEYS = {
    "key",
    "api_key",
    "apikey",
    "token",
    "access_token",
    "secret",
    "secretkey",
}
SECRET_PATTERNS = {
    "google-api-key": re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    "openai-style-key": re.compile(r"\bsk-[0-9A-Za-z_-]{16,}"),
    "generic-bearer": re.compile(r"(?i)\bbearer\s+[0-9A-Za-z._-]{16,}"),
}


def _strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def _urls(value: Any) -> Iterable[str]:
    for text in _strings(value):
        for match in re.finditer(r"https?://[^\s\"'<>]+", text):
            yield match.group(0)


def _node_category(node_type: str) -> str:
    lowered = node_type.lower()
    if "trigger" in lowered or "webhook" in lowered:
        return "trigger"
    if "executecommand" in lowered:
        return "command"
    if "http" in lowered or "request" in lowered:
        return "external-adapter"
    if "agent" in lowered or "lmchat" in lowered or "language" in lowered:
        return "reasoning-adapter"
    if any(token in lowered for token in ("readwritefile", "extractfromfile", "converttofile")):
        return "file-io"
    if any(token in lowered for token in ("code", "merge", "split", "loop", "filter", "if")):
        return "transform"
    if any(token in lowered for token in ("email", "push", "telegram", "slack", "feishu")):
        return "external-side-effect"
    return "other"


def _edge_count(connections: Any) -> int:
    if not isinstance(connections, dict):
        return 0
    count = 0
    for source in connections.values():
        if not isinstance(source, dict):
            continue
        for branches in source.values():
            if not isinstance(branches, list):
                continue
            for branch in branches:
                if isinstance(branch, list):
                    count += sum(1 for item in branch if isinstance(item, dict) and item.get("node"))
    return count


def _capability_tags(nodes: List[Dict[str, Any]]) -> List[str]:
    text = " ".join(_strings(nodes)).lower()
    rules = {
        "ocr-table": ("ocr", "columns", "rows"),
        "literature-retrieval": ("pubmed", "esearch", "efetch"),
        "review-writing": ("review", "综述", "combined_summary"),
        "citation-processing": ("citation", "reference", "参考文献", "renumber"),
        "journal-enrichment": ("issn", "jcr", "impact factor", "影响因子"),
        "document-export": ("csv", "xlsx", "docx", "converttofile"),
        "notification": ("email", "push", "telegram", "wxpusher"),
    }
    return sorted(label for label, terms in rules.items() if any(term in text for term in terms))


def _sanitize_workflow(record: Dict[str, Any]) -> Dict[str, Any]:
    raw_nodes = record.get("nodes") if isinstance(record.get("nodes"), list) else []
    nodes: List[Dict[str, Any]] = []
    hosts = set()
    credential_refs = 0
    credential_urls = 0
    execute_commands = 0
    embedded_secret_types = set()

    for raw in raw_nodes:
        if not isinstance(raw, dict):
            continue
        node_type = str(raw.get("type", ""))
        node_hosts = set()
        node_credential_urls = 0
        for url in _urls(raw.get("parameters", {})):
            parsed = urlsplit(url)
            if parsed.hostname:
                node_hosts.add(parsed.hostname)
                hosts.add(parsed.hostname)
            if any(key.lower() in CREDENTIAL_QUERY_KEYS for key, _ in parse_qsl(parsed.query)):
                node_credential_urls += 1
        credential_urls += node_credential_urls
        has_credentials = bool(raw.get("credentials"))
        if has_credentials:
            credential_refs += 1
        is_command = "executecommand" in node_type.lower()
        if is_command:
            execute_commands += 1
        parameter_text = " ".join(_strings(raw.get("parameters", {})))
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(parameter_text):
                embedded_secret_types.add(label)
        nodes.append(
            {
                "name": str(raw.get("name", "")),
                "type": node_type,
                "category": _node_category(node_type),
                "has_credentials": has_credentials,
                "has_prompt_or_text_body": any(
                    token in str(key).lower()
                    for key in (raw.get("parameters") or {})
                    for token in ("prompt", "text", "body", "message")
                ),
                "external_hosts": sorted(node_hosts),
                "credential_bearing_urls": node_credential_urls,
                "execute_command": is_command,
            }
        )

    return {
        "id": str(record.get("id", "")),
        "name": str(record.get("name", "")),
        "active": bool(record.get("active", False)),
        "node_count": len(nodes),
        "edge_count": _edge_count(record.get("connections")),
        "nodes": nodes,
        "external_hosts": sorted(hosts),
        "capability_tags": _capability_tags(raw_nodes),
        "security": {
            "credential_references": credential_refs,
            "credential_bearing_urls": credential_urls,
            "execute_command_nodes": execute_commands,
            "embedded_secret_types": sorted(embedded_secret_types),
        },
    }


def _json_workflows(path: Path) -> List[Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(payload, dict) and isinstance(payload.get("nodes"), list):
        return [payload]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict) and isinstance(item.get("nodes"), list)]
    if isinstance(payload, dict) and isinstance(payload.get("workflows"), list):
        return [item for item in payload["workflows"] if isinstance(item, dict)]
    raise ValueError("No n8n workflow nodes found in JSON")


def _sqlite_workflows(path: Path) -> List[Dict[str, Any]]:
    connection = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    try:
        tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        if "workflow_entity" not in tables:
            raise ValueError("n8n workflow_entity table not found")
        columns = [row[1] for row in connection.execute('PRAGMA table_info("workflow_entity")')]
        selected = [key for key in ("id", "name", "active", "nodes", "connections") if key in columns]
        if "nodes" not in selected:
            raise ValueError("workflow_entity.nodes column not found")
        rows = []
        for values in connection.execute(f'SELECT {", ".join(selected)} FROM "workflow_entity"'):
            row = dict(zip(selected, values))
            for key in ("nodes", "connections"):
                if isinstance(row.get(key), str):
                    try:
                        row[key] = json.loads(row[key])
                    except json.JSONDecodeError:
                        row[key] = [] if key == "nodes" else {}
            rows.append(row)
        return rows
    finally:
        connection.close()


def extract_manifest(path: Path | str) -> Dict[str, Any]:
    source = Path(path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.suffix.lower() == ".json":
        source_type = "n8n-json"
        records = _json_workflows(source)
    elif source.suffix.lower() in {".sqlite", ".db"}:
        source_type = "n8n-sqlite"
        records = _sqlite_workflows(source)
    else:
        raise ValueError("Supported inputs are .json, .sqlite, and .db")
    workflows = [_sanitize_workflow(record) for record in records]
    security = {
        key: sum(int(workflow["security"][key]) for workflow in workflows)
        for key in ("credential_references", "credential_bearing_urls", "execute_command_nodes")
    }
    security["embedded_secret_types"] = sorted(
        {
            label
            for workflow in workflows
            for label in workflow["security"]["embedded_secret_types"]
        }
    )
    return {
        "source_name": source.name,
        "source_type": source_type,
        "workflow_count": len(workflows),
        "workflows": workflows,
        "security_summary": security,
        "redaction": "Parameters, prompt bodies, command bodies, URL queries, and credential values are excluded.",
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract a sanitized manifest from n8n JSON or SQLite.")
    parser.add_argument("input")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)
    try:
        manifest = extract_manifest(args.input)
    except Exception as exc:
        parser.exit(1, f"n8n manifest extraction failed: {exc}\n")
    print(json.dumps(manifest, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

