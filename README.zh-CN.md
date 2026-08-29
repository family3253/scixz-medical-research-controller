# SciXZ — Scientific eXpert Zone（科学研究专家区）

[English README](README.md)

SciXZ 是一个可移植的 Codex Skill，用于协调医学科研工作流。它作为中央控制器：先规范化用户请求，再审核候选路线，选择最小且足够的 Skill 集合，最后通过共识和验证门控输出。

控制器采用“三部门”流程：中书省负责拟定，门下省负责审核，尚书省负责执行；同时配合六个执行部，分离规划、专业分析、批评、共识和发布前核验。

## 仓库内容

- 可移植的 `scixz` 控制器与路由契约。
- 协作、角色、工作流、共识、评估和验证契约。
- 260 个去重后的配套 Skill，放在 [`bundled-skills/`](bundled-skills/)；其中包括本地独有 Skill，也包括本机 catalog 中已经安装的公开来源 Skill，方便他人复现。
- 可移植的运行时绑定示例；机器专属路径和私有状态不会纳入公开版本。
- 外部服务、专有读取器和上游仓库地址的完整说明：[`DOWNLOAD_GUIDE.md`](DOWNLOAD_GUIDE.md)。

## 快速开始

将本仓库安装为 `scixz` Skill，然后使用协调式科研请求调用：

```text
/scixz 审稿 manuscript.pdf
/scixz 设计 INSPIRE target-trial emulation
/scixz 分析 GEO 数据并设计验证方案
/scixz 选择适合的 SCI 期刊
/scixz 回复 reviewer comments
```

入口文件是 [`SKILL.md`](SKILL.md)。复杂任务会经过独立证据分析、批评审查、共识决策和最终验证；如果运行环境不支持原生子 Agent，会明确标记为顺序执行，而不会伪装成并行结果。

## 配套 Skill 与外部依赖

配套 Skill 位于 [`bundled-skills/`](bundled-skills/)，方便其他人发现并独立安装、替换和升级。本版本已经把本地独有 Skill 和本机 catalog 中存在的公开来源 Skill 一并打包。打包过程按 Skill 名去重，并排除了虚拟环境、依赖缓存、浏览器状态、凭据、稿件、数据集和其他私有运行产物。

打包不代表第三方组件自动改用本仓库顶层 MIT 许可证。单独再分发某个组件前，请检查组件自身的许可证文件或来源说明。详见 [`BUNDLED_SKILLS.md`](BUNDLED_SKILLS.md)、机器可读清单 [`registry/bundled_skill_manifest.json`](registry/bundled_skill_manifest.json)，以及可读完整表 [`BUNDLED_SKILL_MANIFEST.md`](BUNDLED_SKILL_MANIFEST.md)。

明确标注为 Proprietary 的 Skill（例如 `anthropics-*` 文档读取器）没有复制到公开仓库，需要使用其授权发行版本。JANE、iPubMed、ShowJCR 数据、JCR MCP 服务、Clarivate 访问、LetPub 网页和 EasyScholar API 凭据都属于外部来源/适配器，不是随仓库公开的密钥或服务。

## 依赖与下载说明

### 仓库内置

本仓库已经在 `bundled-skills/` 下包含 260 个顶层配套 Skill。全部安装：

```text
python scripts/install_bundled_skills.py
```

只安装或刷新部分 Skill：

```text
python scripts/install_bundled_skills.py find-journal sci-select --overwrite
```

如果运行环境不会自动发现嵌套包，请把相关子目录作为独立 Skill 安装。

### 已核实的公开 Skill 仓库

以下是本版本已核实、可直接访问的公开 Skill 仓库或 Skill 目录。只要本机 catalog 中存在，它们现在也已经随本仓库打包；保留链接是为了方便用户查看上游历史或直接从源仓库安装：

| 用途 | Skill | 仓库地址 |
|---|---|---|
| 稿件同行评审 | `nature-review-studio` | [mumdark/nature-review-studio/skill](https://github.com/mumdark/nature-review-studio/tree/main/skill) |
| 稿件同行评审 | `academic-paper-reviewer` | [bystander563/academic-paper-reviewer-portable](https://github.com/bystander563/academic-paper-reviewer-portable)（Codex 便携版）或 [fbdeme/academic-paper-reviewer](https://github.com/fbdeme/academic-paper-reviewer) |
| 报告规范核查 | `check-reporting` | [Aperivue/check-reporting/skills/check-reporting](https://github.com/Aperivue/check-reporting/tree/main/skills/check-reporting) |
| 参考文献真实性核查 | `verify-refs` | [Aperivue/verify-refs/skills/verify-refs](https://github.com/Aperivue/verify-refs/tree/main/skills/verify-refs) |
| 投稿前预检 | `sci-manuscript-preflight` | [VivalavidaLu/sci-manuscript-preflight](https://github.com/VivalavidaLu/sci-manuscript-preflight/tree/master) |
| 稿件撰写或大范围改写 | `academic-paper` | [Imbad0202/academic-research-skills/academic-paper](https://github.com/Imbad0202/academic-research-skills/tree/main/academic-paper) |
| 文献检索/综合 | `research-lit` | [wanshuiyin/Auto-claude-code-research-in-sleep/skills/research-lit](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/tree/main/skills/research-lit) |
| 文献检索/综合 | `deep-research` | [Imbad0202/academic-research-skills/deep-research](https://github.com/Imbad0202/academic-research-skills/tree/main/deep-research) |
| 已知期刊查询 | `sci-select` | [keros68/sci-select](https://github.com/keros68/sci-select) |

公开仓库和版本会变化。严格复现时优先使用本仓库内置版本；升级时先与上游仓库比对，再替换本地 Skill。

### 依赖 Skill catalog 的路线

以下名称存在于本地 Skill catalog，但本版本没有为它们确认到可直接对应的公开 GitHub Skill 仓库。因此请从当前 catalog 或有授权的发行源获取：`search-lit`、`pubmed-database`、`analyze-stats`、`make-figures`、`academic-python-plotting`、`clean-data`、`deidentify`、`generate-codebook`、`version-dataset`、`calc-sample-size`、`sync-submission`、`venue-templates`、`paper-audit`、`bulk-rnaseq` 和 `scanpy`。

### 需要从授权来源获取的专有读取器

处理本地 Office 文件时，按文件类型安装：

- `anthropics-docx`：DOCX/Word
- `anthropics-pdf`：PDF
- `anthropics-xlsx`：XLSX/CSV/表格
- `anthropics-pptx`：PowerPoint

这些包的源元数据标记为 Proprietary，因此没有放进公开仓库，也不应从本仓库镜像或再分发。

### 外部服务，不是可下载 Skill

选刊和参考文献管理路线必须保留 JANE 与 iPubMed 的可审计证据分支。它们是运行时外部服务/适配器，不是复制到仓库的文件。默认不要向外部服务发送未发表稿件、PHI、受限数据、凭据或 API Key。

### 安装方式

对于公开 Skill 仓库，通用 `skills` 安装器支持：

```text
npx skills add <owner>/<repo> --list
npx skills add <owner>/<repo> --skill <skill-name> -g
```

对于本仓库内置的全部 Skill：

```text
python scripts/install_bundled_skills.py
```

对于单个本仓库内置 Skill：

```text
npx skills add ./bundled-skills/find-journal --skill find-journal -g
```

推荐的“输入期刊名查全指标”组合安装方式：

```text
npx skills add keros68/sci-select --skill sci-select -g
git clone https://github.com/hitfyd/ShowJCR.git
git clone https://github.com/yosh3289/jcr_mcp.git
```

其中 `ShowJCR` 是数据/应用仓库，不是 Skill；`jcr_mcp` 是可选 MCP 服务，不能替代 `sci-select` 的查询与格式化层。

如果安装器无法识别嵌套包，就把相应目录复制到运行时配置的 Skills 目录，并保持目录名与 Skill 名一致。目标路径应从本机配置解析，不要硬编码其他机器的绝对路径。

### 按任务准备最小下载集

**已知期刊查询（输入期刊名 → 指标卡片）**

以 [`sci-select`](https://github.com/keros68/sci-select) 作为主查询 Skill；加入 [`ShowJCR 数据仓库`](https://github.com/hitfyd/ShowJCR) 作为 JCR 2025、2025 中科院、2026 新锐分区和预警标记的本地/静态数据源。也可以在本地设置 `EASY_SCHOLAR_SECRET_KEY`，启用 `bundled-skills/find-journal/scripts/easyscholar_lookup.py` 这个可选 API 适配器，补充 `sciif`、JCR/中科院升级版、新锐和预警字段。如果希望让 Codex 通过 MCP 直接调用数据库，可使用封装 ShowJCR 数据的 [`jcr_mcp`](https://github.com/yosh3289/jcr_mcp)。LetPub 审稿速度由 `sci-select` 在线获取；页面受限时再用 [`agent-browser`](https://github.com/vercel-labs/agent-browser) 或 `chrome:control-chrome` 做浏览器回退。当前 JIF/JCR/收录状态仍应通过 Clarivate 或机构权限复核。只有在还需要 scope 匹配和投稿梯队时，才加入仓库内置的 `find-journal`；对单个期刊精确查询不要与 [`journal-recommender`](https://github.com/zero565656/journal-recommender) 重复运行。

预期输出字段：规范期刊名/ISSN、IF/JIF 及版本年份、按学科分类的 JCR Q 区、2025 中科院大类/小类分区、2026 新锐分区、带页面网址和日期的 LetPub 审稿速度、收录状态、OA/APC、预警状态及 `_source_status`。缺失或冲突字段必须保留并明确标注。

实现提示：`jcr_mcp` 当前提供的是通用期刊搜索/分区接口，不能单独替代字段级来源追踪。若要稳定返回分开的 JCR/CAS/新锐列，建议使用 `sci-select` 配合 ShowJCR 的 CSV/SQLite 数据，或扩展 MCP 返回结构；LetPub 审稿速度仍需实时页面/浏览器核验。

运行仓库自带的实测流程：

```text
python scripts/journal_lookup.py "Journal of Global Antimicrobial Resistance" --pretty
```

该运行器会加载已安装的 `sci-select`，调用本地索引和 LetPub；如果配置了 `EASY_SCHOLAR_SECRET_KEY`，再合并 EasyScholar。未配置时不会发送 EasyScholar 请求，并会明确保留字段状态。

**审阅并修回 DOCX 稿件**

`scixz` + 内置 `deterministic-local-file-reading` + 专有 `anthropics-docx` + 公开 `nature-review-studio` 或 `academic-paper-reviewer` + 公开 `check-reporting` + 内置 `revise` + 内置 `manage-refs` 或公开 `verify-refs`。

**选刊**

`scixz` + 内置 `find-journal` + 一个审稿/投稿预检 Skill + 必需的 JANE 与 iPubMed 外部证据分支。

**新增统计分析**

`scixz` + 由 catalog 提供的 `analyze-stats` + 所需的数据准备和绘图 Skill。分析脚本、输入、版本和输出应保存在私有运行目录。

**GEO/RNA-seq 或单细胞分析**

按分析内容加装领域 Skill（例如 `bulk-rnaseq` 或 `scanpy`），并在数据治理路线需要时加入 `clean-data`、`deidentify` 和 `version-dataset`。

## 常用稿件路线

审稿、修回、选刊和参考文献质控通常按以下顺序组合：

1. `deterministic-local-file-reading` 加对应文件类型读取器。
2. 使用公开的审稿 Skill，如 `nature-review-studio` 或 `academic-paper-reviewer`。
3. 使用公开的报告规范/投稿预检 Skill，如 `check-reporting` 或 `sci-manuscript-preflight`。
4. 使用仓库内的本地独有 `revise` 生成逐条回复和修订任务。
5. 引用修改后使用仓库内的 `manage-refs` 或公开的 `verify-refs`。
6. 使用仓库内的本地独有 `find-journal`，并保留 JANE 与 iPubMed 的可审计证据分支。

各路线的简要依赖矩阵见 [`DEPENDENCIES.md`](DEPENDENCIES.md)。[`DOWNLOAD_GUIDE.md`](DOWNLOAD_GUIDE.md) 作为同一套安装说明的独立版本保留，方便只查安装步骤的使用者。

## 安全与公开边界

SciXZ 用于科研规划和评价，不用于自主诊疗、处方、患者管理或伦理审批。除非另行请求治理类产物，临床相关输出应保持研究用途。

本版本不包含稿件、患者级数据、提取工作簿、私有期刊画像、本地审计日志、API Key、Token、浏览器状态或机器专属绑定注册表。默认不要把未发表稿件、PHI、受限数据、凭据或 API Key 发送给外部适配器。

## 设计原则

- 优先复用已有 Skill，避免重复建设。
- 在共识前保持独立证据分支分离。
- 区分关联、预测和因果。
- 显式呈现不确定性、缺失证据和路线限制。
- 维护时优先归档，避免永久删除。

## 许可证

SciXZ 控制器和仓库自有文档采用 MIT License。配套 Skill 保留 [`BUNDLED_SKILLS.md`](BUNDLED_SKILLS.md) 与 [`BUNDLED_SKILL_MANIFEST.md`](BUNDLED_SKILL_MANIFEST.md) 中记录的来源与许可说明；单独再分发某个组件前，请先核对其许可条件。
