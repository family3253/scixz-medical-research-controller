import csv
import json
import os
import sqlite3
from pathlib import Path

from scripts.refresh_journal_index import refresh_index
from scripts import journal_lookup


def test_refresh_index_downloads_showjcr_sources_and_builds_queryable_sqlite(tmp_path):
    def fake_download(url, destination, timeout=60):
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if url.endswith("FQBJCR2025-UTF8.csv"):
            rows = [
                ["Journal", "年份", "ISSN/EISSN", "大类", "大类分区", "小类1", "小类1分区"],
                ["Example Journal", "2025", "1234-5678/8765-4321", "医学", "3 [1/10]", "MEDICINE", "3 [1/100]"],
            ]
        elif url.endswith("JCR2025-UTF8.csv"):
            rows = [
                [
                    "Journal",
                    "ISSN",
                    "EISSN",
                    "Web of Science",
                    "IF(2025)",
                    "Category_1",
                    "IF Quartile(2025)_1",
                ],
                ["Example Journal", "1234-5678", "8765-4321", "SCIE", "4.2", "MEDICINE", "Q2"],
            ]
        else:
            rows = [
                ["Journal", "年份", "ISSN", "EISSN", "大类中文名", "大类新锐分区"],
                ["Example Journal", "2026", "1234-5678", "8765-4321", "医学", "2 区"],
            ]
        with destination.open("w", encoding="utf-8-sig", newline="") as handle:
            csv.writer(handle).writerows(rows)

    output = tmp_path / "sci_select_journals.sqlite"
    result = refresh_index(
        data_dir=tmp_path / "sources",
        output_path=output,
        downloader=fake_download,
    )

    assert result["journal_count"] == 1
    assert output.exists()
    assert result["source_status"]["jcr_2025"] == "downloaded"
    assert result["source_status"]["cas_2025"] == "downloaded"
    assert result["source_status"]["xinrui_2026"] == "downloaded"

    connection = sqlite3.connect(output)
    try:
        payload_json = connection.execute(
            "SELECT payload_json FROM journals WHERE normalized_title = ?",
            ("examplejournal",),
        ).fetchone()[0]
    finally:
        connection.close()
    payload = json.loads(payload_json)
    assert payload["jcr_quartile"] == "Q2"
    assert payload["cas_2025"] == "3区"
    assert payload["xuankan_2026"] == "2区"


def test_lookup_runner_auto_configures_refreshed_index_from_scixz_env(tmp_path, monkeypatch):
    index_path = tmp_path / "sci_select_journals.sqlite"
    index_path.write_bytes(b"sqlite-placeholder")
    monkeypatch.delenv("SCI_SELECT_JOURNAL_INDEX_DB", raising=False)
    monkeypatch.setenv("SCIXZ_JOURNAL_INDEX_DB", str(index_path))

    resolved = journal_lookup.configure_local_index()

    assert resolved == index_path
    assert os.environ["SCI_SELECT_JOURNAL_INDEX_DB"] == str(index_path)


def test_lookup_card_labels_showjcr_provenance_for_jcr_metrics():
    metrics = {
        "name": "Example Journal",
        "impact_factor": "4.2",
        "jcr_quartile": "Q2",
        "cas_partition_2025": "3区",
        "xinrui_partition_2026": "2区",
        "journal_index_provenance": {
            "jif_2025": "jcr_2025",
            "jcr_quartile": "jcr_2025",
            "cas_2025": "cas_2025",
            "xuankan_2026": "xinrui_2026",
        },
        "_source_status": {
            "journal-index": {"status": "succeeded", "reason": "matching local/static record"},
            "letpub": {"status": "skipped", "reason": "not queried"},
        },
    }

    card = journal_lookup.build_card(metrics, None)

    assert card["impact_factor"]["source"] == "sci-select/ShowJCR"
    assert card["jcr_quartile"]["source"] == "sci-select/ShowJCR"
    assert card["cas_major_quartile_2025"]["source"] == "sci-select/ShowJCR"
    assert card["xinrui_quartile_2026"]["source"] == "sci-select/ShowJCR"
