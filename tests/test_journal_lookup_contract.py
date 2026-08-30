import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "journal_lookup.py"
SPEC = importlib.util.spec_from_file_location("scixz_journal_lookup", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_known_journal_card_exposes_letpub_provenance():
    metrics = {
        "name": "Example Journal",
        "issn": "1234-5678",
        "speed": "平均审稿速度： 8 Weeks",
        "letpub_source_url": "https://letpub.com.cn/index.php?journalid=123&page=journalapp&view=detail",
        "letpub_retrieved_at": "2026-08-30T00:00:00Z",
        "_source_status": {"letpub": {"status": "succeeded", "reason": "usable journal detail"}},
    }

    card = MODULE.build_card(metrics, None)

    assert card["letpub_review_speed"]["value"] == "平均审稿速度： 8 Weeks"
    assert card["letpub_review_speed"]["source_url"].startswith("https://letpub.com.cn/")
    assert card["letpub_review_speed"]["retrieved_at"] == "2026-08-30T00:00:00Z"
