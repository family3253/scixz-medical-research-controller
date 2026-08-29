# Provider Adapter Examples

## Wanfang official API

1. Fill `wanfang_topic_api_config.json` with your `app_key` and `app_secret`.
2. Run:

```bash
python scripts/wanfang_topic_api_adapter.py "耐药菌" --output "02_candidate_pool_and_screening/candidate_pool.csv" --config "assets/templates/wanfang_topic_api_config.json" --type DEGREE --institution-filter "复旦大学"
```

## CNKI authorized browser workflow

1. Review `cnki_browser_workflow.json` and refine selectors for the current site layout.
2. Ensure the browser profile or login state already has the required authorization.
3. Run:

```bash
python scripts/cnki_browser_adapter.py --output "02_candidate_pool_and_screening/candidate_pool.csv" --query "多重耐药菌" --institution-filter "上海交通大学" --download-dir "downloads/cnki"
```

## CNKI DOI resolver route

Use this when you already have a DOI from another source and want a CNKI-aware resolution path without relying on a fragile search entry page.

```bash
python scripts/cnki_doi_adapter.py "10.7666/d.y1234567" --output "02_candidate_pool_and_screening/candidate_pool.csv"
```

## Cross-provider DOI acquisition route

Use this when the priority is to obtain an actual literature artifact no matter whether the DOI ultimately lands on CNKI, Wanfang, PMC, PubMed, or another provider.

```bash
python scripts/doi_acquisition_adapter.py "10.7666/d.y1234567" \
  --candidate-output "02_candidate_pool_and_screening/candidate_pool.csv" \
  --acquisition-output "03_fulltext_acquisition_and_review/fulltext_acquisition.csv" \
  --text-output "03_fulltext_acquisition_and_review/doi_10_7666_d_y1234567.txt"
```

Then classify quality and hand the artifacts into an AWAS project:

```bash
python scripts/classify_acquisition_artifact.py \
  --acquisition-csv "03_fulltext_acquisition_and_review/fulltext_acquisition.csv" \
  --text-file "03_fulltext_acquisition_and_review/doi_10_7666_d_y1234567.txt"

python scripts/handoff_acquisition_to_project.py \
  --project-dir "my-review-project" \
  --candidate-csv "02_candidate_pool_and_screening/candidate_pool.csv" \
  --acquisition-csv "03_fulltext_acquisition_and_review/fulltext_acquisition.csv" \
  --text-file "03_fulltext_acquisition_and_review/doi_10_7666_d_y1234567.txt"
```

## IPubMed authorized browser workflow

1. Review `ipubmed_browser_workflow.json` and add actions for your preferred export flow.
2. Ensure the browser profile already has the required login/session state.
3. Run:

```bash
python scripts/ipubmed_browser_adapter.py --output "02_candidate_pool_and_screening/candidate_pool.csv" --query "MDR-GNB" --download-dir "downloads/ipubmed"
```

## Generic browser workstation adapter

Use the generic adapter when a provider is only accessible through a browser workstation and you want to keep selectors in a JSON config rather than in Python code.

```bash
python scripts/browser_workstation_adapter.py --config "assets/templates/ipubmed_browser_workflow.json" --output "02_candidate_pool_and_screening/candidate_pool.csv" --query "MDR-GNB"
```

## Validation-only mode

Before running a browser adapter, inspect the rendered config:

```bash
python scripts/browser_workstation_adapter.py --config "assets/templates/cnki_browser_workflow.json" --output dummy.csv --query "耐药菌" --validate-only
```
