# LitMesh · 免 Key 学术文献技能（WorkBuddy / Claude Code / Codex 通用）

> **LitMesh** = **Lit**erature **Mesh**：把多个学术数据库的检索与引用能力聚合成「一张网」，
> 用**一个免 API Key 的命令行工具箱**统一调用。**直连免费公共 API，开箱即用，无需任何密钥。**

---

## 这是什么

LitMesh 把 36 个学术工具打包成一个环境无关的 Node CLI（`litmesh.mjs` + 编译好的 `lib/`）：

- **多源聚合（Mesh）**：Semantic Scholar、PubMed、OpenAlex（Google Scholar）、arXiv、bioRxiv / medRxiv、DOI 全文，以及统一跨平台检索 `search_papers`。
- **自动引文**：`auto_cite` 在本地完成「断句 → 真实检索 → IEEE 参考文献 + BibTeX」全流程，零外部依赖。
- **免密钥**：默认 `direct` 模式直连免费公共 API，**不需要任何 API Key** 即可使用全部 36 个工具。
- **一次编写，三处运行**：同一份核心，WorkBuddy / Claude Code / Codex 各自用一份说明文件接入；配置**只走环境变量，三者互不冲突、可各自自定义**。

### 参考资料与致谢

LitMesh 是一个**独立项目**，在设计实现上参考了学术检索相关的公开资料与开源项目（如 [`dsh-ai4scholar`](https://github.com/literaf/ai4scholar-plugin-dsh)，MIT License）。
其核心定位为「免 API Key 服务是安装前提」——默认 `direct` 模式直连免费公共 API，提供 36 个学术检索与引文工具。
本仓库保留所参考项目的 MIT 版权声明（见 `LICENSE`）。

---

## 目录结构

```
litmesh/
├── litmesh.mjs              # 核心适配器：按工具名调用，输出 JSON 或 --render Markdown
├── lib/                     # 编译好的运行时（已剥离 dsh 专用 UI 半侧，免 TS 工具链即可运行）
├── src/                     # 清理后的 TypeScript 源码（供学习/审计；非运行必需）
├── SKILL.md                 # WorkBuddy / Claude Code 共用技能文件（含 agent_created: true）
├── codex.md                 # Codex 专用指令文件
├── references/
│   └── api-cheatsheet.md    # 36 个工具的精确参数速查
├── examples/
│   └── cases.md             # 可复现案例集（命令 + 真实输出）
├── package.json             # 运行时依赖（4 个轻量包 + pdf-parse）
├── LICENSE                  # MIT（保留所参考项目版权声明）
└── .gitignore
```

---

## 快速开始（三环境安装）

**前置条件**：Node.js ≥ 22.19.0（WorkBuddy 自带 managed Node 22.22.2；Claude Code / Codex 用系统 Node 即可）。

### 0. 安装运行时依赖（三环境通用的一步）

进入技能目录后只需一次：

```bash
cd litmesh
npm install      # 安装 @deepseek-ai/* (4 个轻量包) + pdf-parse
```

### 1. WorkBuddy

```bash
cp -r "$(pwd)" "$HOME/.workbuddy/skills/litmesh"
cd "$HOME/.workbuddy/skills/litmesh" && npm install
```

之后在 WorkBuddy 对话中直接描述需求即可，例如：「用 LitMesh 检索最近关于 graph neural network 的 PubMed 论文」。
WorkBuddy 会加载 `SKILL.md` 并按需调用 `node litmesh.mjs ...`。

### 2. Claude Code

```bash
cp -r "$(pwd)" "$HOME/.claude/skills/litmesh"
cd "$HOME/.claude/skills/litmesh" && npm install
```

在 Claude Code 会话中描述文献需求，它会读取 `~/.claude/skills/litmesh/SKILL.md` 并运行 `node litmesh.mjs ...`。
（Claude Code 复用与 WorkBuddy 相同的 `SKILL.md` 格式。）

### 3. Codex

在本仓库根目录（`litmesh/`）运行 `codex` 即可；Codex 会读取 `codex.md` 作为项目指令：

```bash
cd litmesh
npm install
codex          # 用自然语言提出文献任务，Codex 运行 node litmesh.mjs ...
```

---

## 配置（仅环境变量，三环境互不冲突、可各自自定义）

| 变量 | 取值 | 说明 |
| --- | --- | --- |
| `LITMESH_MODE` | `direct`（默认）\| `proxy` | 本技能固定用 `direct`（免 Key）。设 `proxy` 需 `ai4scholar.net` Key，不在范围内。 |
| `LITMESH_TIMEOUT_MS` | 毫秒（可选） | 单工具 HTTP 超时（默认 30000）；网络慢可调大，如 `60000`。已接入 `requestTimeoutMs`。 |
| `SEMANTIC_SCHOLAR_API_KEY` | 可选 | 仅提高 Semantic Scholar 匿名限流额度；不设也能用。 |

三个环境可分别设置这些变量（例如在各自 shell profile / `.env` 中），彼此不共享、不覆盖。

---

## 使用教程

```bash
# 1) 列出全部 36 个工具
node litmesh.mjs --list

# 2) 查看某工具精确 JSON 参数 schema（便于复现，无需查源码）
node litmesh.mjs --schema search_papers

# 3) 统一跨平台检索 + Markdown 渲染
node litmesh.mjs search_papers '{"query":"graph neural network","sources":["semantic-scholar","pubmed","arxiv"],"max_results":5}' --render
# 注：若 Semantic Scholar 返回 429 限流，search_papers 会优雅降级（保留其它来源结果并附 warning），不影响使用。

# 4) 生物医学文献（PubMed）
node litmesh.mjs search_pubmed '{"query":"CRNA anesthesia outcomes","max_results":3}' --render

# 5) 自动引文：标注正文提及 + 生成 IEEE 参考文献 + BibTeX
node litmesh.mjs auto_cite '{"text":"Attention mechanisms have become an integral part of compelling sequence modeling and transduction models in various tasks in recent years. The Transformer architecture introduced by Vaswani et al. relies entirely on self-attention and has been shown to be effective for machine translation. Subsequent work by Devlin et al. proposed BERT, a pretrained language model that achieves strong results on many NLP benchmarks.","style":"ieee"}'

# 6) 全文抽取（arXiv）
node litmesh.mjs read_arxiv_paper '{"paper_id":"2106.15524","max_chars":4000}' --render
```

输出两种模式：
- **默认 JSON**：机器可读，便于脚本二次处理。
- **`--render`**：插件自带的 Markdown 渲染（标题、作者、摘要、引用脉络），适合直接给人看。

---

## 可复现案例

完整命令与**真实运行输出**见 [`examples/cases.md`](examples/cases.md)。所有案例均可在「`npm install` 后直接复现」：
`search_pubmed`、`search_arxiv`、`auto_cite`、`read_arxiv_paper` 等已实测成功；Semantic Scholar 偶发 `429` 属匿名限流，重试即恢复（非缺陷）。

---

## 工具总览（36 个，direct 模式）

**统一检索**：`search_papers`

**PubMed**：`search_pubmed` / `get_pubmed_paper_detail` / `get_pubmed_paper_batch` / `get_pubmed_citations` / `get_pubmed_related`

**Semantic Scholar**：`search_semantic` / `get_semantic_paper_detail` / `get_semantic_paper_batch` / `get_semantic_references` / `get_semantic_citations` / `get_semantic_author_papers` / `get_semantic_author_detail` / `get_semantic_author_batch` / `search_semantic_authors` / `search_semantic_bulk` / `search_semantic_paper_match` / `search_semantic_snippets` / `get_semantic_paper_authors` / `get_semantic_recommendations` / `get_semantic_recommendations_for_paper` / `read_semantic_paper` / `download_semantic`

**arXiv**：`search_arxiv` / `download_arxiv` / `read_arxiv_paper`

**bioRxiv**：`search_biorxiv` / `download_biorxiv` / `read_biorxiv_paper`

**medRxiv**：`search_medrxiv` / `download_medrxiv` / `read_medrxiv_paper`

**Google Scholar（经 OpenAlex）**：`search_google_scholar`

**DOI 全文**：`read_by_doi` / `download_by_doi`

**自动引文**：`auto_cite`

完整参数见 [`references/api-cheatsheet.md`](references/api-cheatsheet.md)。

---

## 常见问题

- **Semantic Scholar 返回 429？** 匿名公共 API 有限流，稍后重试或更换网络即可；设置 `SEMANTIC_SCHOLAR_API_KEY` 可显著提升额度。这不是缺陷。
- **arXiv 偶发超时？** 公共 API 瞬时抖动，重试即可。
- **需要 `sci_draw` / 额度查询？** 那是参考项目中 `proxy` 计费能力，需 `ai4scholar.net` Key，**不在 LitMesh 内**。
- **Node 版本不够？** 需 ≥ 22.19.0；WorkBuddy 自带 managed Node 已满足。

---

## License

MIT —— 保留所参考项目 [`dsh-ai4scholar`](https://github.com/literaf/ai4scholar-plugin-dsh) 版权声明，详见 `LICENSE`。
