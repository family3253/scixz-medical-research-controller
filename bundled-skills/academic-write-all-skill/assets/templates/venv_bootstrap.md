# academic-write-all-skill isolated runtime bootstrap

## Create / refresh the dedicated virtual environment

```bash
bootstrap_academic_write_all_skill_runtime.bat
```

Or just call the top-level launcher once and let it self-bootstrap:

```bash
academic-write-all-skill.bat --help
```

Equivalent manual steps:

```bash
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements-cycwrite.txt
.venv\Scripts\python -m playwright install chromium
```

## Unified CLI entrypoint

```bash
.venv\Scripts\python scripts\awas_cli.py --help
```

Top-level launcher equivalent:

```bash
cycwrite.bat --help
```

## Run adapters inside the isolated runtime

### Validate IPubMed workflow

```bash
academic-write-all-skill.bat ipubmed --output D:\下载\academic_write_all_skill_live_ipubmed_run.csv --query MDR-GNB --validate-only
```

### Run DOI acquisition workflow

```bash
academic-write-all-skill.bat doi-flow 10.7666/d.y1234567 --candidate-output D:\下载\academic_write_all_skill_doi_candidate.csv --acquisition-output D:\下载\academic_write_all_skill_doi_acquisition.csv --text-output D:\下载\academic_write_all_skill_doi_text.txt
academic-write-all-skill.bat handoff --project-dir D:\下载\academic_write_all_skill_handoff_project --candidate-csv D:\下载\academic_write_all_skill_doi_candidate.csv --acquisition-csv D:\下载\academic_write_all_skill_doi_acquisition.csv --text-file D:\下载\academic_write_all_skill_doi_text.txt
```

## Project lifecycle shortcuts

```bash
academic-write-all-skill.bat project-init D:\下载\academic_write_all_skill_project --force
academic-write-all-skill.bat project-status D:\下载\academic_write_all_skill_project
academic-write-all-skill.bat project-gate D:\下载\academic_write_all_skill_project
```

## Notes

- Keep browser adapters in the isolated runtime to avoid conflicts with MCP/server dependencies in the global environment.
- `httpx==0.27.2` is pinned here to avoid the `mcp-server-fetch` incompatibility seen in the global interpreter.
