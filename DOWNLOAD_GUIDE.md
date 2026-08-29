# SciXZ dependency download guide

This guide answers a practical question: after cloning this repository, which Skills must the user download separately?

## 1. Included in this repository

These four local-only Skills are already available under `bundled-skills/`:

- `revise`
- `find-journal`
- `deterministic-local-file-reading`
- `manage-refs`

No additional download is needed for these four. Install each subdirectory as an independent Skill if your runtime does not automatically discover nested packages.

## 2. Verified public Skills to download separately

The following public Skill repositories or Skill directories were verified for this release (checked 2026-08-29):

| Use case | Skill | Repository |
|---|---|---|
| Manuscript peer review | `nature-review-studio` | [mumdark/nature-review-studio/skill](https://github.com/mumdark/nature-review-studio/tree/main/skill) |
| Manuscript peer review | `academic-paper-reviewer` | [bystander563/academic-paper-reviewer-portable](https://github.com/bystander563/academic-paper-reviewer-portable) or [fbdeme/academic-paper-reviewer](https://github.com/fbdeme/academic-paper-reviewer) |
| Reporting-guideline audit | `check-reporting` | [Aperivue/check-reporting/skills/check-reporting](https://github.com/Aperivue/check-reporting/tree/main/skills/check-reporting) |
| Reference authenticity audit | `verify-refs` | [Aperivue/verify-refs/skills/verify-refs](https://github.com/Aperivue/verify-refs/tree/main/skills/verify-refs) |
| Submission-readiness preflight | `sci-manuscript-preflight` | [VivalavidaLu/sci-manuscript-preflight](https://github.com/VivalavidaLu/sci-manuscript-preflight/tree/master) |
| Manuscript drafting or broad revision | `academic-paper` | [Imbad0202/academic-research-skills/academic-paper](https://github.com/Imbad0202/academic-research-skills/tree/main/academic-paper) |
| Literature retrieval/synthesis | `research-lit` | [wanshuiyin/Auto-claude-code-research-in-sleep/skills/research-lit](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/tree/main/skills/research-lit) |
| Literature retrieval/synthesis | `deep-research` | [Imbad0202/academic-research-skills/deep-research](https://github.com/Imbad0202/academic-research-skills/tree/main/deep-research) |
| Known-journal lookup | `sci-select` | [keros68/sci-select](https://github.com/keros68/sci-select) |

## 2a. Catalog-dependent route Skills

No exact public GitHub Skill repository was verified for these route names in this release. Obtain them from the active Skill catalog or an authorized distribution: `search-lit`, `pubmed-database`, `analyze-stats`, `make-figures`, `academic-python-plotting`, `clean-data`, `deidentify`, `generate-codebook`, `version-dataset`, `calc-sample-size`, `sync-submission`, `venue-templates`, `paper-audit`, `bulk-rnaseq`, and `scanpy`.

## 3. Proprietary readers to obtain from their authorized source

For local Office files, install the reader matching the file type:

- `anthropics-docx` for DOCX/Word
- `anthropics-pdf` for PDF
- `anthropics-xlsx` for XLSX/CSV/tabular files
- `anthropics-pptx` for PowerPoint

These packages are not included because their source metadata marks them Proprietary. Do not mirror or redistribute them from this repository.

## 4. External services, not downloadable Skills

The journal-selection and citation-management routes require auditable JANE and iPubMed evidence branches. They are external services/adapters, not files to copy into this repository. Configure them at runtime and do not send unpublished manuscripts, PHI, restricted data, credentials, or API keys by default.

## 5. Installation patterns

For a public Skill repository, the generic `skills` installer supports:

```text
npx skills add <owner>/<repo> --list
npx skills add <owner>/<repo> --skill <skill-name> -g
```

For a Skill bundled in this repository, install from its directory:

```text
npx skills add ./bundled-skills/revise --skill revise -g
npx skills add ./bundled-skills/find-journal --skill find-journal -g
npx skills add ./bundled-skills/deterministic-local-file-reading --skill deterministic-local-file-reading -g
npx skills add ./bundled-skills/manage-refs --skill manage-refs -g
```

Recommended known-journal lookup stack:

```text
npx skills add keros68/sci-select --skill sci-select -g
git clone https://github.com/hitfyd/ShowJCR.git
git clone https://github.com/yosh3289/jcr_mcp.git
```

`ShowJCR` is a data/application repository rather than a Skill; `jcr_mcp` is an optional MCP server and does not replace `sci-select`.

If the installer does not recognize a nested package, copy that package directory into the runtime's configured Skills directory and keep the directory name equal to the Skill name. Resolve the destination from your runtime configuration; do not hard-code another machine's absolute path.

## 6. Minimal download sets by task

### Review and revise a DOCX manuscript

`scixz` + bundled `deterministic-local-file-reading` + proprietary `anthropics-docx` + public `nature-review-studio` or `academic-paper-reviewer` + public `check-reporting` + bundled `revise` + bundled `manage-refs` or public `verify-refs`.

### Select a journal

`scixz` + bundled `find-journal` + one manuscript-review/preflight Skill + the mandatory external JANE and iPubMed evidence branches.

### Perform a new statistical analysis

`scixz` + public `analyze-stats` + the relevant data-preparation and plotting Skills. Preserve analysis scripts, inputs, versions, and outputs in a private run directory.

### Work with GEO/RNA-seq or single-cell data

Add the domain Skill for the requested analysis (for example `bulk-rnaseq` or `scanpy`) together with `clean-data`, `deidentify`, and `version-dataset` when the data-governance route requires them.

---

# SciXZ 配套 Skill 下载说明

本文件专门说明：把仓库克隆下来之后，哪些 Skill 已经内置，哪些必须由使用者自行下载。

## 1. 仓库内置

以下 4 个本地独有 Skill 已放在 `bundled-skills/` 中：

- `revise`
- `find-journal`
- `deterministic-local-file-reading`
- `manage-refs`

这 4 个不需要再下载。如果运行环境不会自动发现嵌套目录，请把每个子目录作为独立 Skill 安装。

## 2. 需要自行下载的公开 Skill

已有公开来源、因此没有重复复制到本仓库的 Skill 包括：

| 用途 | 需要自行下载的 Skill |
|---|---|
| 稿件同行评审 | `nature-review-studio` 或 `academic-paper-reviewer` |
| 报告规范核查 | `check-reporting` |
| 参考文献真实性核查 | `verify-refs` |
| 投稿前预检 | `sci-manuscript-preflight` |
| 稿件撰写或大范围改写 | `academic-paper` |
| 文献检索/综合 | `research-lit`、`deep-research`、`search-lit` 或 `pubmed-database` |
| 统计分析 | `analyze-stats` |
| 图表制作 | `make-figures`、`academic-python-plotting` 或分析所需的绘图 Skill |
| 数据清洗与溯源 | `clean-data`、`deidentify`、`generate-codebook`，必要时加 `version-dataset` |
| 样本量规划 | `calc-sample-size` |
| 投稿打包 | `sync-submission`、`venue-templates`，必要时加 `paper-audit` |

公开仓库和版本会变化。请通过 Skill catalog 或源仓库的发行说明安装，不要直接复制未固定版本的本地缓存。

## 3. 需要从授权来源获取的专有读取器

处理本地 Office 文件时，按文件类型安装：

- `anthropics-docx`：DOCX/Word
- `anthropics-pdf`：PDF
- `anthropics-xlsx`：XLSX/CSV/表格
- `anthropics-pptx`：PowerPoint

这些包的源元数据标记为 Proprietary，因此没有放进公开仓库，也不应从本仓库镜像或再分发。

## 4. 外部服务，不是可下载 Skill

选刊和参考文献管理路线必须保留 JANE 与 iPubMed 的可审计证据分支。它们是运行时外部服务/适配器，不是复制到仓库的文件。默认不要向外部服务发送未发表稿件、PHI、受限数据、凭据或 API Key。

## 5. 安装方式

对于公开 Skill 仓库，通用 `skills` 安装器支持：

```text
npx skills add <owner>/<repo> --list
npx skills add <owner>/<repo> --skill <skill-name> -g
```

对于本仓库内置的 Skill，可从对应目录安装：

```text
npx skills add ./bundled-skills/revise --skill revise -g
npx skills add ./bundled-skills/find-journal --skill find-journal -g
npx skills add ./bundled-skills/deterministic-local-file-reading --skill deterministic-local-file-reading -g
npx skills add ./bundled-skills/manage-refs --skill manage-refs -g
```

推荐的“输入期刊名查全指标”组合：

```text
npx skills add keros68/sci-select --skill sci-select -g
git clone https://github.com/hitfyd/ShowJCR.git
git clone https://github.com/yosh3289/jcr_mcp.git
```

`ShowJCR` 是数据/应用仓库，不是 Skill；`jcr_mcp` 是可选 MCP 服务，不能替代 `sci-select`。

仓库自带实测运行器：

```text
python scripts/journal_lookup.py "Journal of Global Antimicrobial Resistance" --pretty
```

如果安装器无法识别嵌套包，就把相应目录复制到运行时配置的 Skills 目录，并保持目录名与 Skill 名一致。目标路径应从本机配置解析，不要硬编码其他机器的绝对路径。

## 6. 按任务准备最小下载集

### 已知期刊查询（输入期刊名 → 指标卡片）

以 [`sci-select`](https://github.com/keros68/sci-select) 作为主查询 Skill；加入 [`ShowJCR`](https://github.com/hitfyd/ShowJCR) 作为 JCR 2025、2025 中科院、2026 新锐分区和预警标记的数据源。也可以在本地设置 `EASY_SCHOLAR_SECRET_KEY`，启用 `bundled-skills/find-journal/scripts/easyscholar_lookup.py` 这个可选 API 适配器，补充 `sciif`、JCR/中科院升级版、新锐和预警字段。如果希望让 Codex 通过 MCP 直接调用数据库，可使用 [`jcr_mcp`](https://github.com/yosh3289/jcr_mcp)。LetPub 审稿速度由 `sci-select` 在线获取；页面受限时再用 [`agent-browser`](https://github.com/vercel-labs/agent-browser) 或 `chrome:control-chrome` 做浏览器回退。只有在还需要 scope 匹配和投稿梯队时，才加入内置 `find-journal`。

### 审阅并修回 DOCX 稿件

`scixz` + 内置 `deterministic-local-file-reading` + 专有 `anthropics-docx` + 公开 `nature-review-studio` 或 `academic-paper-reviewer` + 公开 `check-reporting` + 内置 `revise` + 内置 `manage-refs` 或公开 `verify-refs`。

### 选刊

`scixz` + 内置 `find-journal` + 一个审稿/投稿预检 Skill + 必需的 JANE 与 iPubMed 外部证据分支。

### 新增统计分析

`scixz` + 公开 `analyze-stats` + 所需的数据准备和绘图 Skill。分析脚本、输入、版本和输出应保存在私有运行目录。

### GEO/RNA-seq 或单细胞分析

按分析内容加装领域 Skill（例如 `bulk-rnaseq` 或 `scanpy`），并在数据治理路线需要时加入 `clean-data`、`deidentify` 和 `version-dataset`。
