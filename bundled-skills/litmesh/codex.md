# LitMesh 学术文献技能（Codex 使用说明）

本目录是一个「免 API Key 的学术文献工具箱」，通过 `litmesh.mjs` 暴露 36 个工具，
直连免费公共 API（Semantic Scholar / PubMed / OpenAlex / arXiv / bioRxiv / medRxiv / DOI / 本地 auto_cite），无需任何密钥。

## 你（Codex）该如何使用

1. 若尚未安装依赖，先运行一次：`npm install`（仅 4 个轻量运行时依赖，约 1MB 级 + pdf-parse）。
2. 用 shell 调用 CLI 完成任务，范式如下：

```bash
node litmesh.mjs --list
node litmesh.mjs <tool_name> '<json_args>' [--render]
```

- 加 `--render` 时输出插件自带的 Markdown 渲染结果（适合给用户看）；不加则输出原始 JSON（适合二次处理）。
- 不确定参数时先跑 `node litmesh.mjs --schema <tool_name>` 拿到精确 JSON schema。

## 示例任务

```bash
# 统一跨平台检索（Semantic Scholar + PubMed + arXiv）
node litmesh.mjs search_papers '{"query":"graph neural network","sources":["semantic-scholar","pubmed","arxiv"],"max_results":5}' --render

# 生物医学文献（PubMed）
node litmesh.mjs search_pubmed '{"query":"CRNA anesthesia outcomes","max_results":3}' --render

# 语义学者（Semantic Scholar）
node litmesh.mjs search_semantic '{"query":"protein folding","max_results":3}' --render

# 自动引文：把正文里的论文提及标注出来，并生成 IEEE 参考文献 + BibTeX
node litmesh.mjs auto_cite '{"text":"<至少100字符、提及若干论文的句子>","style":"ieee"}'

# 引文脉络：某篇论文的参考文献与被引
node litmesh.mjs get_semantic_paper_detail '{"paper_id":"649def34f8be52c8b66281af98ae884c09aef38"}' --render
node litmesh.mjs get_semantic_references '{"paper_id":"649def34f8be52c8b66281af98ae884c09aef38","max_results":20}' --render
```

## 配置（仅环境变量，与 WorkBuddy / Claude Code 互不冲突）

- `LITMESH_MODE`：`direct`（默认，免 Key）| `proxy`（需 ai4scholar.net Key，本技能默认不含）。
- `LITMESH_TIMEOUT_MS`：单工具 HTTP 超时（如 `60000`），网络慢可调大。
- `SEMANTIC_SCHOLAR_API_KEY`：可选，仅提高 Semantic Scholar 限流额度。

## 重要约束

- 默认且只支持 `direct` 模式。不要尝试 `proxy` / `sci_draw` / 额度查询——它们需要外部计费 Key，不在本技能内。
- 所有调用都是真实网络请求，受公共 API 匿名限流影响；Semantic Scholar 偶发 `429` 时稍后重试即可，这不是缺陷。
- 本技能与 WorkBuddy / Claude Code 版本共用同一 `litmesh.mjs` 与 `lib/`，配置仅通过环境变量，三者互不冲突。
- 完整工具参数与可复现案例见 `references/api-cheatsheet.md` 与 `examples/cases.md`。
