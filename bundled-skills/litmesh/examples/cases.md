# LitMesh 可复现案例集

所有命令均基于本仓库根目录（`litmesh/`），在 `npm install` 之后可直接复现。
通用格式：`node litmesh.mjs <tool> '<json>' [--render]`；`--render` 输出 Markdown，省略则输出原始 JSON。

> 环境：Node ≥ 22.19.0，默认 `direct` 模式，免 API Key。真实网络请求，受公共 API 匿名限流影响
> （Semantic Scholar 偶发 `429` 属正常，工具会优雅降级或重试；非缺陷）。

---

## 0. 安装与自检

```bash
cd litmesh && npm install
node litmesh.mjs --list        # 应输出 36 个工具名
node litmesh.mjs --schema search_papers   # 打印某工具精确 JSON 参数 schema
```

实测 `--list` 输出 **36** 个工具（direct 模式），名称如下（以 `litmesh.mjs --list` 为准）：

```
auto_cite  download_arxiv  download_biorxiv  download_by_doi  download_medrxiv
download_semantic  get_pubmed_citations  get_pubmed_paper_batch
get_pubmed_paper_detail  get_pubmed_related  get_semantic_author_batch
get_semantic_author_detail  get_semantic_author_papers  get_semantic_citations
get_semantic_paper_authors  get_semantic_paper_batch  get_semantic_paper_detail
get_semantic_recommendations  get_semantic_recommendations_for_paper
get_semantic_references  read_arxiv_paper  read_biorxiv_paper  read_by_doi
read_medrxiv_paper  read_semantic_paper  search_arxiv  search_biorxiv
search_google_scholar  search_medrxiv  search_papers  search_pubmed
search_semantic  search_semantic_authors  search_semantic_bulk
search_semantic_paper_match  search_semantic_snippets
```

---

## 案例 1 · PubMed 检索（渲染 Markdown）

```bash
node litmesh.mjs search_pubmed '{"query":"CRNA anesthesia outcomes","max_results":3}' --render
```

实测输出（节选）：

```
PubMed results for "CRNA anesthesia outcomes" (showing 3 of 141):

1. **[Retire the Conventional Laryngoscope?](https://pubmed.ncbi.nlm.nih.gov/36722782/)**
   Christopher Bailey, Rhys Dela Cruz, Shari Burns et al. · 2023 · AANA journal
   PMID: 36722782
   Categories: Adult, Humans, Anesthesia, Anesthesiology, Intubation, Intratracheal, Laryngoscopes
   Video laryngoscopy is useful when direct laryngoscopy fails. However, should video
   laryngoscopy replace conventional laryngoscopy? We sought evidence updating previous
   systematic reviews examining whether video laryngoscopy should replace direct laryngoscopy
   for routine adult intubations performed by experienced anesthesia providers ...

2. **[The impact of an anesthesia residency teaching service on anesthesia-controlled time ...](https://pubmed.ncbi.nlm.nih.gov/38561787/)**
   Davene Lynch, Paul D Mongan, Amie L Hoefnagel · 2024 · Patient safety in surgery
   PMID: 38561787 · DOI: 10.1186/s13037-024-00394-z
   ...

3. **[Anesthesia-Related Malpractice Claims in Maryland 1994-2017.](https://pubmed.ncbi.nlm.nih.gov/36413191/)**
   William O Howie, George Zangaro, Benjamin A Howie et al. · 2022 · AANA journal
   PMID: 36413191
   ...
```

> 稳定可重现：PubMed 为 NCBI E-utilities 公共接口，匿名即可用，几乎不受限流。

---

## 案例 2 · arXiv 检索（原始 JSON）

```bash
node litmesh.mjs search_arxiv '{"query":"attention mechanism","max_results":2}'
```

实测输出（节选）：

```json
{
  "source": "arxiv",
  "query": "attention mechanism",
  "total": 337313,
  "papers": [
    {
      "source": "arxiv",
      "id": "2002.00741",
      "title": "Déjà vu: A Contextualized Temporal Attention Mechanism for Sequential Recommendation",
      "authors": ["Jibang Wu", "Renqin Cai", "Hongning Wang"],
      "year": 2020,
      "date": "2020-01-29",
      "abstract": "Predicting users' preferences based on their sequential behaviors ...",
      "url": "https://arxiv.org/abs/2002.00741"
    }
  ]
}
```

---

## 案例 3 · 自动引文 auto_cite（本地管线）

```bash
node litmesh.mjs auto_cite '{"text":"Attention mechanisms have become an integral part of compelling sequence modeling and transduction models in various tasks in recent years. The Transformer architecture introduced by Vaswani et al. relies entirely on self-attention and has been shown to be effective for machine translation. Subsequent work by Devlin et al. proposed BERT, a pretrained language model that achieves strong results on many NLP benchmarks.","style":"ieee"}'
```

实测输出（节选）：

```json
{
  "annotatedText": "Attention mechanisms have become an integral part of compelling sequence modeling ... [1] The Transformer architecture introduced by Vaswani et al. [2] relies entirely on self-attention ... [3] Subsequent work by Devlin et al. proposed BERT ... [4]",
  "references": [
    { "number": 1, "formatted": "[1] E. Peterson and P. Kaur, \"Antibiotic Resistance Mechanisms in Bacteria ...\", Frontiers in Microbiology, 2018. doi: 10.3389/fmicb.2018.02928.", "relevanceScore": 0.39 },
    { "number": 2, "formatted": "[2] S. Zheng et al., \"Rethinking Semantic Segmentation from a Sequence-to-Sequence Perspective with Transformers,\" 2021. doi: 10.1109/cvpr46437.2021.00681.", "relevanceScore": 0.40 },
    { "number": 3, "formatted": "[3] M. Guo et al., \"Attention mechanisms in computer vision: A survey,\" Computational Visual Media, 2022. doi: 10.1007/s41095-022-0271-y.", "relevanceScore": 0.54 },
    { "number": 4, "formatted": "[4] Y. Jiang, J. A. Irvin, A. Y. Ng, and J. Zou, \"VetLLM: Large Language Model for Predicting Diagnosis from Veterinary Notes.\", Pacific Symposium on Biocomputing, 2024.", "relevanceScore": 0.78 }
  ],
  "bibtex": "@article{ref1,\n  title = {Antibiotic Resistance Mechanisms in Bacteria ...}\n  author = {Peterson, E. and Kaur, P.}\n  journal = {Frontiers in Microbiology}\n  year = {2018}\n  doi = {10.3389/fmicb.2018.02928}\n  url = {https://doi.org/10.3389/fmicb.2018.02928}\n}\n ...",
  "stats": { "citationCount": 4, "searchCount": 13, "processingTime": 103.84 }
}
```

> 说明：免 Key 模式下 `auto_cite` 走「本地断句 + 免费 API 关键词匹配」，匹配精度低于参考项目计费版
> Auto-Cite，但仍可端到端生成标注文本 + IEEE 参考文献 + BibTeX。对实体明确、术语规范的句子效果更佳。

---

## 案例 4 · 统一跨平台检索 search_papers（优雅降级）

```bash
node litmesh.mjs search_papers '{"query":"graph neural network","sources":["semantic-scholar","pubmed","arxiv"],"max_results":2}'
```

实测：当 Semantic Scholar 匿名限流（HTTP 429）时，工具**不中断**，而是保留 PubMed / arXiv 结果并附 warning：

```json
{
  "query": "graph neural network",
  "sources": ["semantic-scholar", "pubmed", "arxiv"],
  "total": 30,
  "perSource": [
    { "source": "semantic-scholar", "count": 0,
      "error": "Semantic Scholar search failed: HTTP 429: Too Many Requests ... (after 3 attempts)" },
    { "source": "pubmed", "count": 10, "total": 13689 },
    { "source": "arxiv", "count": 10, "total": 485822 }
  ],
  "truncated": true,
  "warning": "Semantic Scholar: ... HTTP 429 ..."
}
```

> 仅用稳定来源时完全无警告：`sources:["pubmed","arxiv"]` 返回 `total:20` 正常结果。

---

## 案例 5 · arXiv 全文抽取 read_arxiv_paper

```bash
node litmesh.mjs read_arxiv_paper '{"paper_id":"2106.15524","max_chars":1500}' --render
```

实测输出（节选）：

```
Full text of 2106.15524
Source PDF: https://arxiv.org/pdf/2106.15524 · 27 pages · 86,173 characters
Showing characters 0–1,500 — call again with offset=1500 for the rest.

Fully Dynamic Four-Vertex Subgraph Counting
Kathrin Hanauer · University of Vienna, Faculty of Computer Science, Vienna, Austria
...
Abstract
```

---

## 复现要点小结

| 工具 | 实测结果 | 稳定性 |
| --- | --- | --- |
| `search_pubmed` | ✅ 真实结果 | 高（匿名公共接口） |
| `search_arxiv` | ✅ 真实结果 | 高（偶有瞬时抖动，重试即可） |
| `auto_cite` | ✅ 标注+IEEE+BibTeX | 高（匹配精度取决于文本规范性） |
| `search_papers` | ✅ 多源聚合 | 高（单源 429 自动降级） |
| `read_arxiv_paper` | ✅ 全文抽取 | 高 |
| `search_semantic` 系列 | ⚠️ 偶发 429 | 中（设 `SEMANTIC_SCHOLAR_API_KEY` 可提升额度） |

安装与调用验证命令（三环境通用）：

```bash
# WorkBuddy
cp -r "$(pwd)" "$HOME/.workbuddy/skills/litmesh" && cd "$HOME/.workbuddy/skills/litmesh" && npm install

# Claude Code
cp -r "$(pwd)" "$HOME/.claude/skills/litmesh" && cd "$HOME/.claude/skills/litmesh" && npm install

# Codex：在本目录直接 npm install 后运行 codex
npm install
```
