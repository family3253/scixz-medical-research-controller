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

## 常用稿件路线

审稿、修回、选刊和参考文献质控通常按以下顺序组合：

1. `deterministic-local-file-reading` 加对应文件类型读取器。
2. 使用公开的审稿 Skill，如 `nature-review-studio` 或 `academic-paper-reviewer`。
3. 使用公开的报告规范/投稿预检 Skill，如 `check-reporting` 或 `sci-manuscript-preflight`。
4. 使用仓库内的本地独有 `revise` 生成逐条回复和修订任务。
5. 引用修改后使用仓库内的 `manage-refs` 或公开的 `verify-refs`。
6. 使用仓库内的本地独有 `find-journal`，并保留 JANE 与 iPubMed 的可审计证据分支。

各路线的依赖和运行时说明见 [`DEPENDENCIES.md`](DEPENDENCIES.md)。

如果是在新机器上部署 SciXZ，建议先阅读 [`DOWNLOAD_GUIDE.md`](DOWNLOAD_GUIDE.md)，其中区分了仓库内置的本地 Skill、需要自行下载的公开 Skill、专有读取器以及 JANE/iPubMed 外部适配器。

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
