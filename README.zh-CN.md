# SciXZ — Scientific eXpert Zone（科学研究专家区）

[English README](README.md)

SciXZ 是一个可移植的 Codex Skill，用于协调医学科研工作流。它作为中央控制器：先规范化用户请求，再审核候选路线，选择最小且足够的 Skill 集合，最后通过共识和验证门控输出。

控制器采用“三部门”流程：中书省负责拟定，门下省负责审核，尚书省负责执行；同时配合六个执行部，分离规划、专业分析、批评、共识和发布前核验。

## 仓库内容

- 可移植的 `scixz` 控制器与路由契约。
- 协作、角色、工作流、共识、评估和验证契约。
- 一组本地独有、难以从外部发现的配套 Skill：`revise`、`find-journal`、`deterministic-local-file-reading` 和 `manage-refs`，详见 [`BUNDLED_SKILLS.md`](BUNDLED_SKILLS.md)。
- 可移植的运行时绑定示例；机器专属路径和私有状态不会纳入公开版本。
- 需要自行下载的 Skill 完整清单：[`DOWNLOAD_GUIDE.md`](DOWNLOAD_GUIDE.md)。

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

本地独有的配套 Skill 位于 [`bundled-skills/`](bundled-skills/)，方便其他人发现并独立安装、替换和升级。它们不会被顶层 MIT 许可证自动重新授权；各组件的来源和许可说明见 [`BUNDLED_SKILLS.md`](BUNDLED_SKILLS.md)。

已有公开 GitHub 来源的 Skill 只作为依赖引用，不重复复制。明确标注为 Proprietary 的 Skill（例如 `anthropics-*` 文档读取器）没有复制到公开仓库，需要使用其权威发行版本。JANE 和 iPubMed 是外部证据适配器，不是随仓库分发的 Skill。

## 依赖与下载说明

### 仓库内置

以下本地独有的配套 Skill 已经放在 `bundled-skills/` 中：

- `revise`
- `find-journal`
- `deterministic-local-file-reading`
- `manage-refs`

这 4 个不需要再下载。如果运行环境不会自动发现嵌套目录，请把每个子目录作为独立 Skill 安装。

### 需要自行下载的公开 Skill

已有公开来源、因此没有重复复制到本仓库的 Skill 包括：

| 用途 | 需要自行下载 |
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

对于本仓库内置的 Skill，可从对应目录安装：

```text
npx skills add ./bundled-skills/revise --skill revise -g
npx skills add ./bundled-skills/find-journal --skill find-journal -g
npx skills add ./bundled-skills/deterministic-local-file-reading --skill deterministic-local-file-reading -g
npx skills add ./bundled-skills/manage-refs --skill manage-refs -g
```

如果安装器无法识别嵌套包，就把相应目录复制到运行时配置的 Skills 目录，并保持目录名与 Skill 名一致。目标路径应从本机配置解析，不要硬编码其他机器的绝对路径。

### 按任务准备最小下载集

**审阅并修回 DOCX 稿件**

`scixz` + 内置 `deterministic-local-file-reading` + 专有 `anthropics-docx` + 公开 `nature-review-studio` 或 `academic-paper-reviewer` + 公开 `check-reporting` + 内置 `revise` + 内置 `manage-refs` 或公开 `verify-refs`。

**选刊**

`scixz` + 内置 `find-journal` + 一个审稿/投稿预检 Skill + 必需的 JANE 与 iPubMed 外部证据分支。

**新增统计分析**

`scixz` + 公开 `analyze-stats` + 所需的数据准备和绘图 Skill。分析脚本、输入、版本和输出应保存在私有运行目录。

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

SciXZ 控制器和仓库自有文档采用 MIT License。配套 Skill 保留 [`BUNDLED_SKILLS.md`](BUNDLED_SKILLS.md) 中记录的来源与许可说明；单独再分发某个组件前，请先核对其许可条件。
