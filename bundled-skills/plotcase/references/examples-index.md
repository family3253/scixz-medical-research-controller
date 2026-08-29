# PlotCase Example Index

This skill can search a curated local index of PlotCase bundled examples before launching the GUI.

## Recommended query styles

- By chart type: 热图 / 火山图 / 森林图 / 小提琴图 / 网络图 / 游泳图
- By data scenario: 临床 / 组学 / 生存分析 / 差异分析 / 蛋白互作
- By output need: 适合论文 / 带显著性标记 / 进阶 / 多因素

## Search behavior

The search script matches against title, keywords, tags, and summary.
It returns the best local matches with the bundled example path so the user can open the corresponding example data in PlotCase.

The search command supports two output modes:

- `Text` for direct human reading
- `Json` for structured downstream processing and better encoding safety

## Index maintenance

The curated file `assets/examples/examples.json` can be regenerated from the local PlotCase install tree.

Use:

`scripts/generate_examples_index.ps1`

This scans the local `resources/app.asar.unpacked/content` directory, extracts category, example title, and a representative file from each example's `data` directory, then rewrites the JSON index.

## Suggested workflow

1. Search local PlotCase examples first.
2. Review the returned example titles and paths.
3. Launch PlotCase if the user wants to explore or recreate the example interactively.
