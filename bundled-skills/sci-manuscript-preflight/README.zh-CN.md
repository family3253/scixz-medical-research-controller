# SCI 论文投稿前预检 Skill

[English](README.md)

这是一个可移植的 agent skill，用于 SCI、生物医学和生物信息学论文在投稿或返修前的质量控制预检。

当前版本：`v0.2.2`。

它借鉴 arXiv-style preflight check 的思路，但面向期刊论文场景：检查 AI 写作残留、参考文献真实性、claim-to-citation 支撑关系、图表一致性、图像/源数据/统计完整性、确定性表格与源数据放行门、报告规范和投稿风险。

## 它检查什么

- AI 起草残留、遗留的 agent 指令、占位符、Markdown/LaTeX 残留
- 幻觉文献、伪造文献、无法解析文献、DOI/PMID/题名/作者/年份不匹配
- 过度 claim、未被引用直接支撑的 claim、临床或机制性越界表述
- 图、表、补充材料、caption、缩写、统计标注和编号一致性
- 图像、源数据和统计完整性风险，包括疑似重复 panel、源数据缺口、定量结果不匹配、方法-结果-图注矛盾
- 确定性表格异常信号、解析覆盖、源文件哈希、误报解释、独立复算和投稿放行状态
- 方法、统计、伦理、数据可用性、报告指南缺口
- 目标期刊投稿或返修前 readiness

## 设计借鉴

`v0.2.0` 将 [wooly99/geng-academic-fraud-detector](https://github.com/wooly99/geng-academic-fraud-detector) 的图像来源、图像组装、统计一致性和方法矛盾维度，转化为非指控式的作者侧投稿前质量控制。

`v0.2.2` 吸收了 [zixixr/paperconan](https://github.com/zixixr/paperconan) 的确定性数值信号、解析失败显式化、证据定位、误报 profile、复核状态与科学影响分离、对抗式复核等设计。本地包装器仅接受兼容的 `0.8.x` 输出，并对账预期文件与扫描器实际报告的文件和 Sheet。本仓库没有复制 paperconan 源代码；它仍是遵循自身许可证和版本周期的外部依赖。

## 仓库内容

- `SKILL.md` - skill 主说明
- `scripts/preflight_static_scan.py` - 静态扫描 AI 残留、占位符、Markdown/LaTeX 残留和高风险投稿措辞
- `scripts/reference_audit.py` - DOI 解析以及标题/首位作者/年份/期刊元数据一致性核查
- `scripts/table_integrity_gate.py` - 冻结源数据清单、调用/解析 paperconan 并生成保守的放行结果
- `references/checklist.md` - 人工投稿前检查清单
- `references/table_source_data_gate.md` - 表格/源数据放行门、误报复核、对账和放行标准
- `templates/preflight_report.md` - 结构化预检报告模板
- `examples/example-preflight-report.md` - 投稿前 QC 报告示例
- `tests/` - 静态扫描、参考文献核查和表格放行门的离线回归测试

## 下载

克隆仓库：

```bash
git clone https://github.com/VivalavidaLu/sci-manuscript-preflight.git
cd sci-manuscript-preflight
```

或者从 GitHub 下载 ZIP：

1. 打开 <https://github.com/VivalavidaLu/sci-manuscript-preflight>
2. 点击 **Code**
3. 点击 **Download ZIP**
4. 解压文件夹

请保留完整文件夹。这个 skill 不只是一个 `SKILL.md`，还依赖 `scripts/`、`references/`、`templates/` 和 `examples/`。

## 安装

这个仓库是一个可移植 agent skill。它不只适用于 Claude Code，也可以在 Codex、Antigravity、Cursor、GitHub Copilot、Trae，以及其他能读取本地 instruction 文件的 coding agent 中使用。

### Claude Code

全局安装：

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/VivalavidaLu/sci-manuscript-preflight.git ~/.claude/skills/sci-manuscript-preflight
```

只安装到当前项目：

```bash
mkdir -p .claude/skills
git clone https://github.com/VivalavidaLu/sci-manuscript-preflight.git .claude/skills/sci-manuscript-preflight
```

然后对 Claude Code 说：

```text
Use the sci-manuscript-preflight skill to check this manuscript folder before submission.
```

### Codex

全局安装：

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/VivalavidaLu/sci-manuscript-preflight.git ~/.codex/skills/sci-manuscript-preflight
```

然后对 Codex 说：

```text
Use the sci-manuscript-preflight skill to check this manuscript folder for AI residue, reference problems, claim-citation mismatch, figure/data/statistical integrity issues, and submission risks.
```

### Antigravity

Antigravity 可以把这个仓库作为本地 instruction/skill 文件夹使用。把仓库克隆到工作区内一个稳定目录，然后在 agent instructions 中引用 `SKILL.md`。

```bash
git clone https://github.com/VivalavidaLu/sci-manuscript-preflight.git tools/sci-manuscript-preflight
```

建议添加这样的 agent instruction：

```text
When I ask for manuscript preflight, follow tools/sci-manuscript-preflight/SKILL.md and use its scripts, references, templates, and examples when relevant.
```

### Cursor

把仓库克隆到项目中：

```bash
git clone https://github.com/VivalavidaLu/sci-manuscript-preflight.git .cursor/skills/sci-manuscript-preflight
```

然后添加 project rule 或 instruction：

```text
For manuscript pre-submission checks, follow .cursor/skills/sci-manuscript-preflight/SKILL.md. Treat the whole folder as the skill package.
```

### GitHub Copilot

把仓库克隆到项目中，或放到一个共享本地工具目录：

```bash
git clone https://github.com/VivalavidaLu/sci-manuscript-preflight.git .github/copilot/skills/sci-manuscript-preflight
```

然后在 Copilot instructions 中引用：

```text
For SCI/biomedical manuscript preflight tasks, follow .github/copilot/skills/sci-manuscript-preflight/SKILL.md and use the included scripts and templates when applicable.
```

### Trae

把仓库克隆到项目中：

```bash
git clone https://github.com/VivalavidaLu/sci-manuscript-preflight.git .trae/skills/sci-manuscript-preflight
```

然后添加 Trae project rule 或 agent instruction：

```text
When reviewing a manuscript for submission readiness, follow .trae/skills/sci-manuscript-preflight/SKILL.md and keep the report structured by severity.
```

## 基本使用

对你的 agent 说：

```text
Use the sci-manuscript-preflight skill to check this manuscript folder for AI residue, hallucinated references, claim-citation mismatch, figure/table numbering issues, figure/data/statistical integrity issues, and SCI submission risks.
```

推荐提供的输入包括：

- 论文主文：`.docx`、`.pdf`、`.tex` 或 `.md`
- 参考文献文件：`.bib`、`.ris`、`.nbib`、`.xml`、`.enl` 或 `.txt`
- 图片、源数据和补充材料文件夹
- Cover letter
- 目标期刊 instructions
- Reviewer checklist 或 response-to-reviewers 草稿

如果你只提供一个文件，agent 应该执行可行的部分预检，并明确列出缺失输入。

## 兼容性与依赖

- CI 覆盖 Python `3.10`–`3.12`。
- 静态扫描核心仅使用 Python 标准库；提取 `.docx` 可选用 `python-docx>=1.1`，提取 PDF 可选用 `PyMuPDF>=1.24`。
- 参考文献实时核查需要访问 Crossref；离线测试使用固定的合成元数据。
- 表格放行门支持 `paperconan[all]>=0.8,<0.9`。schema 或版本不兼容时必须阻断，直到重新验证兼容性。

仓库不会自动安装依赖。修改共享 Python 环境前应先取得同意。

## 直接运行辅助脚本

静态残留扫描：

```bash
python scripts/preflight_static_scan.py path/to/manuscript_folder --out static_scan.tsv
```

参考文献 DOI/Crossref 核查：

```bash
python scripts/reference_audit.py path/to/references.bib --out reference_audit.tsv
```

表格与源数据完整性放行门：

```bash
python -m pip install "paperconan[all]>=0.8,<0.9"
python scripts/table_integrity_gate.py --input-dir path/to/source_data --out preflight/table_gate --profile review
```

也可以直接解析已有扫描结果：

```bash
python scripts/table_integrity_gate.py --scan-json path/to/scan.json --out preflight/table_gate
```

包装器会输出源文件清单、`gate.json`、`findings.tsv` 和 `gate_report.md`。向共享环境安装 paperconan 前应先取得用户同意；如果扫描器不可用，必须报告 `NOT_ASSESSED`，不得声称通过。

脚本结果只能作为支持证据，不等同于最终判断。数据库失败、DOI 元数据缺失、风格风险信号、图像相似性或统计异常，都需要人工复核后才能下结论。

## 注意事项

这不是 AI detector，也不是学术不端判定工具。它是一个投稿前质量控制流程，用来在期刊投稿前发现高风险残留、伪造或不匹配参考文献、未被证据支撑的 claim、图像/源数据/统计自洽问题，以及格式和合规性问题。

这个 skill 会区分“已验证错误”和“需要人工确认的可疑项”。它不应静默改写科学结论，也不应把假设当成已验证结论。

任何 skill 或扫描器都不能保证发表数据绝对不存在错误。只有在解析覆盖完整、跨材料对账、反向质疑、修正后复扫和作者签字均完成后，才能表述为“在已评估范围内未发现尚未解决的问题”。

## 许可证

本仓库采用 [MIT License](LICENSE)。
