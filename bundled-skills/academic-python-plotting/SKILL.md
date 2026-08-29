---
name: academic-python-plotting
description: Use when the user wants publication-ready quantitative figures in Python, especially with Matplotlib or Seaborn, for papers, theses, supplements, rebuttals, or journal submission. Make sure to use this whenever the request involves academic plotting, SCI/SSCI figure standards, Nature/Science-style charts, error bars, significance markers, vector export, journal-ready styling, or turning raw data/statistics into rigorous Python plotting code instead of generic business graphics. Prefer `academic-write-all-skill` as the first academic intake when the request is broad or mixed; use this skill as the dedicated downstream code-first Python plotting owner after AWAS has already fixed the plotting route.
---

# Academic Python Plotting

## Purpose

Turn quantitative data or statistical summaries into publication-ready Python plotting code that looks credible in an academic manuscript rather than a slide deck.

Default mindset:
- prefer clarity over decoration
- prefer 2D over 3D
- prefer vector-friendly output over screenshots
- prefer explicit statistical annotation over visual guesswork

## When to Use

Use this skill whenever the user:
- asks for Python figure code for a paper, thesis, preprint, supplement, or rebuttal
- mentions `matplotlib`, `seaborn`, `svg`, `pdf`, `dpi`, or journal formatting
- wants grouped bar charts, boxplots, violin plots, scatter/regression plots, heatmaps, forest plots, survival curves, coefficient plots, or multi-panel figures
- wants SEM / SD / CI error bars, p-value stars, brackets, sample size labels, or legend cleanup
- says their current AI-generated chart looks ugly, cheap, unprofessional, or not journal-ready

## Core Output Rule

Default to **directly runnable Python code** with short Chinese comments.

Unless the user explicitly asks otherwise, the output should include:
1. imports
2. data-loading or data-construction section
3. style configuration
4. plotting code
5. statistical annotation placeholders or implementation
6. export commands for SVG/PDF/PNG

## Visual Standard

Aim for top-journal-adjacent styling rather than flashy style.

### Typography
- Prefer `Times New Roman` for manuscript-facing figures unless the user names another required font.
- Use consistent font family across title, axis labels, ticks, and legend.
- Typical sizes:
  - axis labels: 10-12 pt
  - tick labels: 9-10 pt
  - legend: 9-10 pt
  - panel labels: 12-14 pt bold

### Color
- Use restrained, colorblind-friendly palettes.
- Prefer 2-6 clearly distinguishable colors.
- Avoid neon colors, rainbow defaults, strong gradients, glossy effects, and unnecessary transparency.
- If no palette is given, propose one concise palette and explain why it suits the figure.

### Geometry
- No 3D charts.
- No chartjunk.
- Keep spines, ticks, and gridlines intentional.
- Use line widths around 1.0-1.5 and marker sizes that survive print reduction.

## Statistical Discipline

If the chart represents inferential results, do not stop at basic drawing.

Where appropriate, include or reserve space for:
- SEM / SD / 95% CI error bars
- significance brackets and star labels
- exact p-values or placeholder comments for insertion
- sample size labels when scientifically relevant
- clear statement of what the error bars represent

If the statistical layer is missing from the user's input, say so briefly and provide the figure code in a way that makes those additions easy.

## Figure Selection Heuristics

Choose the figure type that best matches the data story.

- **group comparison with means** -> grouped bar chart only if distribution detail is not the main point
- **distribution comparison** -> boxplot or violin + jittered points
- **association between continuous variables** -> scatter + regression / smooth fit
- **matrix-like intensity patterns** -> heatmap with disciplined scale
- **effect sizes across models/groups** -> forest plot / coefficient plot
- **time course** -> line plot with confidence band
- **small multiple comparisons** -> faceted / multi-panel layout

If the user's requested chart is suboptimal, keep their intent but recommend a better academic alternative.

## Workflow

1. Read the data description carefully.
2. Identify variable roles: grouping, outcome, time, uncertainty, significance.
3. Choose the most defensible figure type.
4. Define a restrained academic style.
5. Write runnable Python code.
6. Add export lines for high-quality output.
7. Briefly note what the user may still need to fill in, such as exact p-values.

## Output Template

When producing code, prefer this structure:

```python
# 1) 导入库
# 2) 读取或构造数据
# 3) 统一设置期刊级绘图风格
# 4) 绘制主体图形
# 5) 添加误差线 / 显著性标记
# 6) 优化坐标轴、图例、留白
# 7) 导出 SVG/PDF/PNG
```

## Quality Checks

Before finishing, mentally check:
- Does the figure match the data structure?
- Is the palette print-safe and colorblind-friendlier than default?
- Are fonts and sizes consistent?
- Is there a path to SVG/PDF export?
- Are error bars / significance handled or explicitly noted?
- Would this look acceptable after being reduced into a two-column paper layout?

## What to Avoid

Avoid these unless the user explicitly insists:
- 3D bars, pies, donuts, gauges
- decorative gradients
- shadow/glow effects
- giant legends or oversized titles
- vague statements like “a beautiful chart” without code-level specifics

## Response Style

Be concrete. Give code, not just advice.
If the data are incomplete, make the assumptions explicit in one short note and still provide a strong plotting scaffold.
