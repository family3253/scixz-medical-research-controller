import importlib.util
import json
import sqlite3
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "bundled-skills"
    / "n8n-to-skill"
    / "scripts"
    / "extract_n8n_manifest.py"
)
SPEC = importlib.util.spec_from_file_location("scixz_n8n_manifest", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_json_manifest_redacts_parameters_and_reports_security_findings(tmp_path):
    workflow = {
        "name": "OCR to table",
        "nodes": [
            {
                "name": "OCR request",
                "type": "n8n-nodes-base.httpRequest",
                "parameters": {
                    "url": "https://example.org/v1/process?key=SENSITIVE_SENTINEL",
                    "prompt": "private prompt text that must not be copied",
                },
                "credentials": {"api": {"id": "credential-id"}},
            },
            {
                "name": "Run helper",
                "type": "n8n-nodes-base.executeCommand",
                "parameters": {"command": "python private_helper.py"},
            },
        ],
        "connections": {"OCR request": {"main": [[{"node": "Run helper"}]]}},
    }
    path = tmp_path / "workflow.json"
    path.write_text(json.dumps(workflow), encoding="utf-8")

    manifest = MODULE.extract_manifest(path)
    serialized = json.dumps(manifest, ensure_ascii=False)

    assert "SENSITIVE_SENTINEL" not in serialized
    assert "private prompt text" not in serialized
    assert manifest["workflows"][0]["node_count"] == 2
    assert manifest["workflows"][0]["external_hosts"] == ["example.org"]
    assert manifest["security_summary"]["credential_references"] == 1
    assert manifest["security_summary"]["credential_bearing_urls"] == 1
    assert manifest["security_summary"]["execute_command_nodes"] == 1


def test_sqlite_manifest_reads_workflow_graph_without_credentials_table(tmp_path):
    path = tmp_path / "database.sqlite"
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            "CREATE TABLE workflow_entity (id TEXT, name TEXT, active INTEGER, nodes TEXT, connections TEXT)"
        )
        connection.execute("CREATE TABLE credentials_entity (id TEXT, data TEXT)")
        nodes = [{"name": "PubMed", "type": "n8n-nodes-base.httpRequest", "parameters": {"url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"}}]
        connection.execute(
            "INSERT INTO workflow_entity VALUES (?, ?, ?, ?, ?)",
            ("wf-1", "PubMed review", 0, json.dumps(nodes), "{}"),
        )
        connection.execute(
            "INSERT INTO credentials_entity VALUES (?, ?)",
            ("cred-1", "SENSITIVE_SENTINEL"),
        )
        connection.commit()
    finally:
        connection.close()

    manifest = MODULE.extract_manifest(path)
    serialized = json.dumps(manifest, ensure_ascii=False)

    assert manifest["source_type"] == "n8n-sqlite"
    assert manifest["workflows"][0]["name"] == "PubMed review"
    assert manifest["workflows"][0]["external_hosts"] == ["eutils.ncbi.nlm.nih.gov"]
    assert "SENSITIVE_SENTINEL" not in serialized

