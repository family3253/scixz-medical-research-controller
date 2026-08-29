# academic-write-all-skill

## 概述 / Overview

`academic-write-all-skill` 是一个面向 OpenCode 和 OpenClaw 的学术写作编排型 skill。  
`academic-write-all-skill` is an academic writing orchestration skill for OpenCode and OpenClaw.

它的目标不是“直接把正文写出来”，而是先判断用户所处阶段、证据充分度和目标产物类型，再路由到更合适的学术工作流。  
Its goal is not to jump straight into prose generation, but to first identify the user's stage, evidence strength, and target artifact, then route to the most honest workflow.

它覆盖的核心场景包括：论文规划、章节写作、文献检索与筛选、综述项目分级、返修教练、投稿准备、预测模型综述，以及证据约束写作。对于系统综述、Meta分析和预测模型评估任务，它也会优先以 **multi-agent academic workflow coordinator** 的方式工作，而不是直接把正文一次性写完。  
Its core scope includes paper planning, section drafting, literature search and screening, review-project gating, revision coaching, submission preparation, prediction-model review, and evidence-aware writing. For systematic review, meta-analysis, and prediction-model appraisal tasks, it should also behave as a **multi-agent academic workflow coordinator** rather than a one-pass prose generator.

## 核心原则 / Core Principle

> 不要让修饰过的 prose 跑在已核实证据前面。  
> Do not let polished prose outrun verified evidence.

实际工作时，这个 skill 会优先回答三个问题：  
In practice, the skill tries to answer three questions first:

1. 用户当前处于哪个阶段？ / What stage is the user actually in?
2. 用户要产出什么学术对象？ / What type of academic artifact is needed?
3. 当前证据或材料是否足够支撑目标输出？ / Is the current evidence strong enough to support that output?

如果答案不够稳，它会优先选择更窄、更诚实的输出层级，而不是强行写成“完整论文”。  
If the answers are not strong enough, it will choose a narrower and more honest output level rather than pretending a full paper is ready.

## 主要能力 / Main Capability Areas

### 1. 论文生产工作流 / Paper-Production Workflows
适用于 article、thesis、chapter 等纸面产物。  
Use these when the task is article-, thesis-, or chapter-centric.

- 选题、开题、研究问题收束 / topic framing and proposal support
- 论文提纲、章节结构、段落任务拆分 / paper outlines, chapter structures, paragraph planning
- `Introduction`、`Methods`、`Results`、`Discussion`、`Abstract`、`Conclusion` 写作 / section drafting
- 学位论文与 chapter-based 写作 / thesis and dissertation workflows
- 摘要重写 / abstract rewriting
- 引用检查 / citation checks
- 格式转换意识 / format-convert awareness
- 审稿意见整理与修订路线图 / revision-coach mode
- 图表与后续编译约束对齐 / figure-and-compile-aware drafting

### 2. 综述项目工作流 / Review-Project Workflows
适用于 evidence map、review article、screening-heavy 任务。  
Use these when the task is review-corpus-centric.

- review 类型路由 / review-type routing
- 检索策略设计 / search strategy planning
- candidate pool 构建 / candidate-pool design
- 标题摘要筛选 / title and abstract screening
- 全文筛选与证据提取 / full-text screening and evidence extraction
- 多 agent 审稿/筛选/提取编排 / multi-agent orchestration for screening, extraction, and synthesis
- 提取优先的 review / meta 工作流 / extraction-first review and meta workflow
- 强化的 PDF 读取与补充材料提取 / stronger PDF reading and supplement-aware extraction
- claim-to-evidence 映射 / claim-to-evidence mapping
- prediction-model review 与 appraisal / prediction-model review and appraisal
- 内生的 TRIPOD-like / PROBAST-like / CHARMS-like 工作性评估框架 / native TRIPOD-like / PROBAST-like / CHARMS-like working appraisal frame
- 面向 prediction-model meta 的专项字段与审计强化 / strengthened extraction and appraisal for prediction-model meta
- 可直接落地的 split-aware prediction-model meta 提取模板 / direct split-aware prediction-model meta extraction template
- 证据不足时的输出降级 / honest downgrade when the corpus is weak

### 3. 多代理综述与 Meta 编排 / Multi-Agent Review and Meta Orchestration
适用于 systematic review、meta-analysis、prediction-model review、方法学审计、证据链尚未稳定的 thesis chapter 任务。  
Use these when the task needs staged evidence work before trustworthy drafting.

- retrieval → screening → extraction → appraisal / audit → decision loop → writing 的阶段化流程
- companion agents 的默认分工（retrieval orchestrator, screening analyst, evidence extractor, authenticity auditor, writing coordinator）
- 双评+仲裁的默认机制（提取与评分均优先 2 个 agent 独立执行，冲突时第 3 个 agent 仲裁）
- 对外部 workflow 模式的受控吸收，如 MetaScreener、ASReview、LatteReview、paperfetcher、metafor 风格边界
- 优先使用结构化 artifacts、审计表、claim-evidence 矩阵，而不是直接依赖会话记忆

### 3A. 本地课程资产桥接 / Local Course-Asset Bridging
适用于用户提到相关统计/建模知识点时，skill 主动去本地课程库与专题代码库里寻找现成 workflow，而不要求用户显式说出目录路径。  
Use this when the user mentions relevant statistics or modeling topics and the skill should proactively check the local teaching/code library for reusable workflows, even without explicit path instructions.

- 把本地课程目录当作 method library，而不是普通附件 / treat local course folders as a method library, not just generic attachments
- 相关知识点出现就主动匹配本地课程资产 / proactively match local course assets when relevant knowledge points appear
- 先按主题匹配章节，再找对应代码 / route by method family, then locate the matching code
- 代码优先于课件命名猜测 / executable code outranks slide-title inference
- 抽取最小可复用 workflow：输入要求、关键函数、步骤顺序、输出形式 / extract the minimum reusable workflow unit
- 适合处理 `F:\e\实战\ppt`、`F:\e\实战\code` 这类“课件 + temp_code + 方法学文献”联动型本地知识库 / especially useful for local course libraries with paired slides and `temp_code` directories

### 4. 后期微操作 / Late-Stage Operations
适用于已有稿件的局部改写或投稿前工作。  
Use these when the draft already exists and the job is narrower.

- 润色与重写 / polishing and rewriting
- 翻译 / translation
- 降 AI 味 / anti-AI-tone cleanup
- response package / reviewer response materials
- response matrix / response matrices
- 重审检查 / re-review checks
- 选刊与 desk-reject 风险判断 / journal-fit triage
- 投稿前检查 / pre-submission review

### 5. 谨慎自我更新 / Guarded Self-Update
当当前 native 能力不够时，它不会硬写，而是走一条受控的能力补位路径。  
When native coverage is insufficient, it does not bluff. It follows a guarded capability-gap path.

- 先查本仓库自带 references / consult bundled references first
- 再借用更强的本地 skill 逻辑 / then borrow stronger local skill logic
- 必要时谨慎学习 GitHub 或官方实现模式 / cautiously learn from GitHub or official patterns only when needed
- 明确标注借用来源，且不能绕过 integrity gates / explicitly label borrowed logic and never bypass integrity gates

## 为什么需要它 / Why This Skill Exists

很多学术写作助手会在这些地方失误：  
Many academic writing assistants fail in predictable ways:

- 过早进入正文写作 / drafting full prose too early
- 编造类似引用的内容 / inventing citation-like content
- 夸大 novelty、结论或确定性 / overstating novelty or certainty
- 把综述当普通章节写 / treating a review as a normal section task
- 把修订教练当成正文写作 / confusing revision planning with drafting
- 无视证据是否足够支撑目标输出 / ignoring whether the evidence base is strong enough

`academic-write-all-skill` 通过显式阶段划分、证据门槛和诚信约束来减少这些失败模式。  
`academic-write-all-skill` reduces these failure modes through explicit stage routing, evidence gates, and integrity constraints.

## 设计哲学 / Skill Design Philosophy

仓库采用分层结构：  
The repository uses a layered structure:

- `SKILL.md`：轻量级核心路由层 / lightweight routing layer
- `references/`：重规则与深工作流说明 / heavy rules and deeper workflows
- `scripts/`：可复用检索、项目与辅助脚本 / reusable project and retrieval helpers
- `assets/templates/`：结构化模板与表格 / structured templates and tables
- `evals/`：行为回归提示集 / behavior-regression prompt set

能力增长也遵循受控顺序：  
Capability growth is treated as a managed process:

1. 本地 references 优先 / bundled references first
2. 本地 specialist skills 其次 / local specialist skills second
3. 外部学习最后 / external learning third

## 仓库结构 / Repository Layout

```text
academic-write-all-skill/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── RELEASE_NOTES.md
├── evals/
├── requirements-cycwrite.txt
├── bootstrap_academic_write_all_skill_runtime.bat
├── academic-write-all-skill.bat
├── references/
├── scripts/
└── assets/templates/
```

## 关键文件 / Important Files

### 核心 skill / Core Skill
- `SKILL.md`
  - 主路由逻辑 / main routing logic
  - 触发覆盖 / trigger coverage
  - 分阶段选择 / stage-aware workflow selection
  - 证据与完整性约束 / integrity rules
  - 默认子工作流映射 / default subworkflow mapping

- `references/local-academic-routing-matrix.md`
  - 本地学术场景的 canonical 路由矩阵 / canonical local-academic routing matrix
  - primary owner / allowed downstream / forbidden parallel paths
  - AWAS 与 OMO agent 边界 / AWAS vs OMO boundaries
  - superpowers 过程层要求 / required superpowers process layer

- `references/china-pharmaceutical-university-thesis.md`
  - 中国药科大学学位论文专用约束 / CPU thesis-specific constraints
  - 本地权威来源优先级 / local authority order
  - 专硕默认偏置 / professional-master default bias
  - thesis 与 paper 转换边界 / thesis-to-paper stage boundary

### 回归测试提示 / Evals
- `evals/evals.json`
  - live routing 回归提示 / reusable live routing prompts
  - 包含：outline-only、revision-coach、review downgrade、guarded self-update、prediction-model review、external fallback 测试  
  - includes outline-only, revision-coach, review downgrade, guarded self-update, prediction-model review, and external fallback tests

### 专项模板 / Scenario Templates
- `assets/templates/cpu-professional-master-thesis-checklist.md`
  - 中国药科大学专硕论文检查清单 / CPU professional-master thesis compliance checklist
  - 覆盖：authority order、盲审包 vs 归档包、AI承诺书、页码、图表、参考文献、thesis-to-paper 边界

### 参考规则 / Reference Guides
- `references/literature-search-and-screening.md`
  - 检索、筛选、提取、引用治理 / search, screening, extraction, citation governance
- `references/section-workflows.md`
  - 章节写作硬规则 / section-specific drafting rules
- `references/review-routing-and-gates.md`
  - review 类型与证据门槛 / review routing and evidence gates
- `references/review-and-submission.md`
  - 投稿、返修、submission package / submission and revision workflows
- `references/prediction-model-review.md`
  - 预测模型综述与 appraisal / prediction-model review and appraisal workflow
  - 内生工作性评估框架 + 外部 TRIPOD / TRIPOD+AI / PROBAST / PROBAST+AI / CHARMS-style 借用规则
- `references/quality-and-integrity.md`
  - 抗幻觉与证据纪律 / anti-hallucination and evidence discipline
- `references/microtasks-and-operations.md`
  - 高频微任务 / high-frequency microtasks
- `references/local-course-asset-bridge.md`
  - 本地课程资料与专题代码库的吸收式复用规则 / absorption rules for local course assets and reusable method code libraries

### 脚本 / Scripts
- `scripts/awas_cli.py`
  - runtime helper 的统一 CLI 入口 / unified CLI entrypoint for runtime helpers
- `scripts/init_review_project.py`
  - 初始化 review 项目骨架 / initialize a review-writing project scaffold
- `scripts/import_and_dedupe_candidates.py`
  - candidate pool 规范化与去重 / normalize and dedupe candidate pools
- `scripts/generate_gate_report.py`
  - 生成 gate report / compute gate status
- `scripts/session_state_driver.py`
  - 项目阶段检查 / inspect staged project readiness
- `scripts/citation_authenticity_sentinel.py`
  - 引用真实性检查 / citation-authenticity checks
- `scripts/smoke_test.py`
  - 仓库级 smoke test / repository-level smoke test

### 模板 / Templates
- `assets/templates/*.csv`
  - candidate pool、screening、evidence extraction、prediction-model appraisal 表格  
  - candidate pool, screening, evidence extraction, and prediction-model appraisal tables
- `assets/templates/*.md`
  - outline、claim map、decision packet、gate checklist、prediction-model appraisal checklist 等  
  - outlines, claim maps, decision packets, gate checklists, prediction-model appraisal checklists, and review artifacts
- `assets/templates/*.json`
  - browser workflow 示例与 provider config  
  - browser workflow examples and provider configs

## 最近整合的能力 / Recently Integrated Capabilities

当前版本吸收了来自以下来源的能力模式：  
This version absorbs capability families from:

- `academic-write-all-skill` / AWAS
- 早期 paper / review 技能族 / earlier paper and review skills
- 旧项目 `academic-write`
- `MetaScreener`
- `ASReview`
- `LatteReview`
- `paperfetcher`
- `metafor`-style meta-analysis workflow boundaries
- local course-library bridging patterns for paired teaching PDFs and reusable `temp_code` directories

### 强化后的方向 / What Became Stronger
- 更强的 outline-first 路由 / stronger outline-first routing
- abstract-only / abstract rewrite / citation-check / format-convert
- revision-coach
- review output-level gating
- corpus-first review logic
- prediction-model review / appraisal
- more native prediction-model appraisal with TRIPOD-like / PROBAST-like / CHARMS-like built-in structure
- research lifecycle routing
- guarded self-update
- explicit multi-agent orchestration for systematic review and meta-analysis
- extraction-first behavior for review and meta-analysis tasks
- stronger PDF-first reading, layout-aware extraction, and OCR escalation for review corpora
- stronger prediction-model meta extraction and validation-aware appraisal
- direct reusable template for split-aware prediction-model meta extraction
- stronger guideline-backed distinction between development, internal validation/testing, and external validation/testing
- stronger separation between extraction, appraisal, synthesis, and prose
- clearer code-aware fallback logic for review automation and meta-analysis support

因此它现在不只是“写作路由器”，而是一个更完整的 academic workflow router。  
It is no longer just a writing router, but a broader academic workflow router.

## 安装 / Installation

### OpenCode 一键安装 / One-Command Install for OpenCode

项目级安装 / Project-scoped install:

```bash
npx skills add family3253/academic-write-all-skill -a opencode
```

全局安装 / Global install:

```bash
npx skills add family3253/academic-write-all-skill -a opencode -g
```

### OpenClaw 一键安装 / One-Command Install for OpenClaw

项目级安装 / Project-scoped install:

```bash
npx skills add family3253/academic-write-all-skill -a openclaw
```

全局安装 / Global install:

```bash
npx skills add family3253/academic-write-all-skill -a openclaw -g
```

### 兼容旧安装器写法 / Fallback for Older Installer Name

```bash
npx add-skill family3253/academic-write-all-skill --agent opencode
```

典型安装位置 / Typical install targets:
- OpenCode project: `.agents/skills/`
- OpenCode global: `~/.config/opencode/skills/`
- OpenClaw project: `skills/`
- OpenClaw global: `~/.openclaw/skills/`

## Runtime 辅助环境 / Runtime Helper Setup

### 方式 1：Windows 脚本 / Option 1: Windows Scripts

如果你希望启用本地 runtime helper，可运行：  
If you want local runtime helpers, run:

```bat
bootstrap_academic_write_all_skill_runtime.bat
```

该脚本会：  
This script will:
- 创建 `.venv` / create `.venv`
- 升级 `pip` / upgrade `pip`
- 安装 `requirements-cycwrite.txt` / install `requirements-cycwrite.txt`
- 安装 Playwright Chromium / install Playwright Chromium

之后可用：  
Then use:

```bat
academic-write-all-skill.bat <command> [...args]
```

### 方式 2：手动 Python 安装 / Option 2: Manual Python Setup

```bash
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements-cycwrite.txt
.venv\Scripts\python -m playwright install chromium
```

## CLI 用法 / CLI Usage

runtime CLI 位于 `scripts/awas_cli.py`。
The runtime CLI is implemented in `scripts/awas_cli.py`.

### 查看帮助 / Show Help

```bash
python scripts/awas_cli.py --help
```

### 可用命令 / Available Commands
- `bootstrap`
- `ipubmed`
- `cnki`
- `doi-flow`
- `handoff`
- `project-init`
- `project-status`
- `project-gate`

### 示例 / Examples

初始化 review 项目 / Initialize a review project scaffold:

```bash
python scripts/awas_cli.py project-init my-review-project
```

生成 gate report / Generate a gate report:

```bash
python scripts/awas_cli.py project-gate my-review-project
```

查看项目状态 / Inspect project status:

```bash
python scripts/awas_cli.py project-status my-review-project
```

运行 DOI acquisition flow / Run DOI acquisition flow:

```bash
python scripts/awas_cli.py doi-flow 10.1000/example-doi \
  --candidate-output candidate_pool.csv \
  --acquisition-output fulltext_acquisition.csv \
  --text-output artifact.txt
```

## 实际使用方式 / How To Use The Skill In Practice

典型提示词 / Typical prompts:

- `我有研究结果，但还不知道论文怎么搭结构。请先帮我列一个论文提纲，不要直接写正文。`
- `我收到一堆审稿意见，很乱。先别帮我写回复信，先帮我整理成修订路线图和 response matrix 骨架。`
- `我想写一篇投稿级综述，但我现在只有十几篇文献和一个很粗的主题。你先判断应该写到什么层级。`
- `帮我检查这篇稿子的引用有没有明显问题。`
- `帮我把摘要重写得更贴合正文，不要新增事实。`
- `帮我做预测模型综述。`

它的正确反应并不总是“直接写正文”，很多时候第一步应该是：  
The correct response is not always to draft immediately. Often the right first move is to:

- 稳定提纲 / stabilize the outline
- 降级输出层级 / downgrade the output level
- 请求缺失证据 / request missing evidence
- 构建修订路线图 / build a revision roadmap
- 生成 claim-to-evidence matrix / produce a claim-to-evidence matrix
- 进入 prediction-model appraisal 结构 / enter prediction-model appraisal structure

## 测试 / Testing

### Live Routing Evals

仓库内的 `evals/evals.json` 保存了一组 harness-level 回归提示，包括：  
`evals/evals.json` stores harness-level regression prompts, including:

- outline-only routing
- revision-coach routing
- review-output downgrade routing
- guarded self-update / capability-gap handling
- prediction-model review and external-standard fallback tests

这些提示可用于未来重复跑行为回归。  
These prompts can be reused for future behavior regression runs.

### 本仓库已重跑的检查 / What Was Re-Tested

已执行的推荐检查 / Recommended checks executed:

```bash
python -m compileall scripts
python scripts/awas_cli.py --help
python scripts/awas_cli.py project-init tmp-project --force
python scripts/awas_cli.py project-status tmp-project
python scripts/awas_cli.py project-gate tmp-project
python scripts/smoke_test.py
```

这些检查验证了：  
These checks validate:

- Python 脚本语法 / Python syntax for bundled scripts
- CLI parser integrity
- project scaffold initialization
- session state inspection
- gate report generation
- smoke-test repeatability

### Skill 行为测试状态 / Skill-Behavior Testing Status

需要区分两层测试：  
There is an important distinction between two layers:

1. 仓库/runtime 测试 / repository/runtime tests
2. assistant harness 内的 live skill-routing 测试 / live skill-routing tests inside the assistant harness

仓库级测试可本地执行；assistant-level 测试依赖模型和环境。  
Repository-level tests are executable locally; assistant-level tests depend on model and environment health.

当前已成功验证的 live routing 包括：  
The following live routing behaviors have been successfully verified:

- outline-only behavior
- revision-coach behavior
- review-output downgrade behavior
- guarded self-update behavior
- prediction-model review mode
- adversarial external fallback with explicit TRIPOD / PROBAST / CHARMS labeling

## 已知限制 / Known Limitations

- 本仓库不保证运行时一定能访问外部文献源。  
  This repository does not guarantee runtime access to external literature sources.
- 浏览器辅助流程依赖真实 session、权限和环境健康。  
  Browser-assisted workflows still depend on real sessions, permissions, and environment health.
- 它很擅长路由和证据约束，但不会凭空把弱证据变成可投稿稿件。  
  It is strong at routing and evidence discipline, but it does not magically make weak evidence publication-ready.
- review-grade 工作仍然依赖真实 corpus 质量、screening 纪律和证据完整性。  
  Review-grade work still depends on actual corpus quality, screening discipline, and evidence completeness.
- prediction-model appraisal 现在已经更内生，但最严格的方法学审查在 AI/ML 模型场景下仍可能依赖显式外部 fallback（如 TRIPOD+AI / PROBAST+AI）。  
  Prediction-model appraisal is now more native, but the strictest methodology review in AI/ML settings may still depend on explicit external fallback such as TRIPOD+AI or PROBAST+AI.

## 安全与完整性规则 / Safety and Integrity Rules

`academic-write-all-skill` 在这些方面是刻意保守的：  
`academic-write-all-skill` is intentionally conservative in these areas:

- 不伪造引用 / no fabricated references
- 不编造统计结果 / no invented statistics
- 不做无证据 novelty claim / no unsupported novelty claims
- 不假装 journal-fit 很确定 / no fake journal-fit certainty
- 不把弱 corpus 说成 submission-grade / no pretending a weak corpus is submission-grade
- 不把借来的能力伪装成本地原生能力 / no presenting borrowed capability as native
- 没有 artifact 就不假装已获得全文 / no claiming full-text access unless the artifact is present

如果证据不完整，正确输出应该是降级的、带占位的、可追溯的结果。  
If evidence is incomplete, the correct output should be downgraded, placeholder-bearing, and traceable.

## 开发说明 / Development Notes

### 仓库根目录中故意不包含的内容 / What Is Intentionally Excluded

- `.venv/`
- `__pycache__/`
- `*.pyc`

这些都是运行时产物，不是源码。  
These are runtime artifacts, not source.

### Git 发布说明 / Git Publishing Note

GitHub 上的公开仓库是从一个干净的 workspace 副本推上去的，所以远端内容优先反映源码与模板，而不是本地环境噪声。  
The public GitHub repository was prepared from a clean workspace copy, so the remote reflects source and templates rather than local environment noise.

## 后续建议 / Recommended Next Steps

如果继续演进，最值的方向是：  
If you continue evolving this skill, the highest-value next steps are:

1. 更明确记录 CNKI / Wanfang / browser workflow 的 provider prerequisites  
   Document provider-specific prerequisites for CNKI / Wanfang / browser workflows more explicitly
2. 补 sample review-project 目录用于端到端演示  
   Add sample review-project directories for end-to-end dry runs
3. 为 `evals/evals.json` 增加量化评分  
   Add quantitative grading around `evals/evals.json`
4. 继续把 prediction-model appraisal 做得更内生  
   Continue making prediction-model appraisal more native
5. 把 multi-agent review / meta pipeline 做成更标准的可复用模板与 eval  
   Add stronger reusable templates and evals for multi-agent review and meta-analysis pipelines
6. 把本地课程库桥接进一步模板化，让 `chapter -> code -> adapted workflow` 的吸收过程更标准  
   Standardize the local course-library bridge so `chapter -> code -> adapted workflow` becomes a reusable routing pattern

## 仓库地址 / Repository

- `https://github.com/family3253/academic-write-all-skill`
