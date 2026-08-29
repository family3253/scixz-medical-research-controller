# 外部 PPT 模板逐页库

该库用于把外部 PowerPoint 模板拆成“可逐页选择”的页面模板，而不是把整套 PPT 当成单一风格。

当前注册源目录：

`<PRIVATE_THESIS_WORKSPACE>\ppt模板`

当前索引结果：172 套源模板、5006 张页面。原始 PPT/PPTX 保留在 F 盘；页面预览和 manifest 缓存在：

`<USER_HOME>\.cache\yixueAIganhuo-PPT\external_ppt_page_library`

这是改名前已经生成的兼容缓存位置。技能入口、目录和新任务输出均使用 `cycppt`；保留该缓存命名是为了避免现有 5006 页预览索引中的绝对路径失效。重新完整导入模板库时可另行迁移缓存。

常用操作：

```powershell
# 重新扫描并渲染页面预览
python scripts/import-external-ppt-template-library.py `
  "<PRIVATE_THESIS_WORKSPACE>\ppt模板" `
  --render

# 搜索页面模板
python scripts/resolve-external-ppt-template.py `
  --query "方法 图表 浙大蓝" `
  --limit 20

# 将指定页面绑定到一个 slide
python scripts/resolve-external-ppt-template.py `
  --page-id ext-xxxxxxxxxxxx-s012 `
  --plan <ppt_plan.json> `
  --slide-id slide03 `
  --out-plan <updated_plan.json>

# 根据每页 role/layout 自动挑选不同页面模板
python scripts/resolve-external-ppt-template.py `
  --auto-bind `
  --plan <ppt_plan.json> `
  --out-plan <updated_plan.json>
```

绑定记录会写入 `template_binding.external_page_id`、`source_template`、`source_slide` 和 `reference_image`。生成时必须替换模板中的姓名、学校、日期、课题、示例数据和徽标等占位信息。
