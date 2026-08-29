# Quality Checks

These checks apply only to the upstream medical planning worker.

## Source and Figure Inventory

- Source topic, disease area, method, cohort/model, intervention/exposure, endpoint, key result, and limitation are summarized.
- PDF Figure estimates are based on main Figure numbers, not subfigure letters.
- Raw extracted image candidates are separated from final usable evidence Figures.
- Discarded images have explicit reasons.
- Tables are not counted as Figures unless the parent explicitly requests table images.
- Final `figure_inventory.json` maps every usable evidence asset with `asset_id`, `source_pdf`, `source_page`, `source_region`, `kind`, `evidence_mode`, `output_path`, and `citation`.
- Original Figures/charts/medical-image crops use `evidence_mode=original`; Tables may use `original` or `reconstructed`; generated explanatory visuals use `derived` or `reconstructed`.
- Every asset records `render_policy`: `original_preferred` for Figures/charts/images, and `original_preferred` or `reconstruct_allowed` for Tables.
- An original asset exists at `output_path`, resolves to its source PDF/page/region, and is bound to the intended slide under `assets.required`.

## Plan Quality

- `ppt_plan.json` has exactly one entry per target slide.
- Slide ids and numbers are continuous.
- Every slide has role, title, core message, layout regions, references, and `speaker_notes_zh`.
- Evidence Figure bindings are medically meaningful and not decorative.
- Slide dependencies follow the style-continuity graph:
  - slide 1 has no style dependency
  - slide 2 depends on slide 1
  - slide 3+ depend on slide 1 and slide 2
- `generation_keys` are present or inferable.
- The deck uses one coherent master family plus explicit per-page `template_binding` records for subject-content layouts.
- External PowerPoint references are page-level assets: each selected page must record `external_page_id`, `external_template_id`, `source_template`, `source_slide`, and an existing `reference_image`. Automatic bindings must share `deck.master_template_id` unless cross-family selection was explicitly authorized.
- `deck.template_consistency_policy=single_template_family`, `deck.template_mode=per_page_within_master_family`, and `deck.deck_chrome_locked=true` are present by default.
- Default `deck.navigation_policy=none`; pages marked as 横排导航、竖排导航、导航栏、导航条, or equivalent navigation demos are not selected.
- Template priority is enforced: organization/campus lock > explicit user selection > existing planned binding > automatic selection for unbound pages. Automatic selection must never silently replace a non-empty binding.
- A page template binding records its `style_selector` and/or `reference_image`, plus a short reason; low-confidence automatic matches remain unbound instead of being guessed.
- Page-level templates change the subject-content layout only. Typography, palette, citations, header, footer, navigation, Logo area, title origin, page number, and medical evidence rules remain deck-consistent.

## Prompt Quality

- Prompt files exist for every slide.
- Prompt files include expanded style key text, not only key names.
- Prompt files include the slide plan and medical evidence constraints.
- Prompt files forbid fake authors, institutions, dates, citations, sample sizes, P values, and unsupported statistics.
- Prompts instruct evidence Figure preservation and aspect-ratio preservation when source Figures are bound.
- Prompts name each `evidence_mode=original` asset path and require it to be passed as a real image input, not redrawn from prose.
- Prompts require visible “重构示意 / Derived from source” labeling for reconstructed non-table evidence and “表格重构 / Reconstructed from Table X” labeling for reconstructed Tables.
- When a page has `template_binding.reference_image`, its prompt names the reference and explains which template geometry must be inherited.
- The prompt explicitly states that `template_binding` controls only the subject-content region and that deck chrome is locked.

## Generated Slide Quality

Every full-authoring slide result must contain a passed `quality_review` based on inspection of the actual generated image, not only the prompt or API response.

Required checks:

- `text_readable`: titles, labels, citations, and body text are legible at slide scale.
- `no_garbled_text`: no pseudo-text, duplicated characters, broken glyphs, or mixed-language corruption.
- `layout_complete`: all planned regions and required evidence are present; no truncated module or missing panel.
- `style_consistent`: the page follows the deck master and any bound content layout without a visual jump; header/footer/navigation presence and position, Logo area, title origin, page number, typography, and brand palette match the other body slides.
- `evidence_preserved`: original Figures, Tables, imaging, charts, and values are actually embedded, remain medically faithful, and keep their aspect ratio; derived/reconstructed assets are visibly labeled.
- `safe_margins`: no title, body text, reference, logo, or evidence object touches or crosses unsafe edges.
- `no_visual_artifacts`: no generation seams, masks, strange borders, watermarks, duplicate objects, or malformed anatomy.

If a check fails, regenerate with a correction targeted at the recorded issue. Use at most 3 total attempts. A failed final review must return a failed slide result instead of silently accepting the last image.

## 邵逸夫医院院区检查

When `deck.organization_template.template_id` is `srrsh-report-2024-v9`:

- `deck.campus` must be exactly one of 庆春院区、钱塘院区、阿拉尔院区、大运河院区、绍兴院区。
- The first slide must contain a `template_binding` with `campus_locked=true` and the same campus value.
- The first-slide reference image must resolve to that campus's mapped cover; never validate by title text alone.
- The last slide must bind `ending/thank_you.png` with `campus_specific=false`.
- Original template slides 6 and 7 are forbidden as cover or ending sources.

## Handoff Quality

- The worker returns only structured paths and status.
- The parent can dispatch slide image workers without reopening full PDF text.
- No downstream PPTX reconstruction artifacts are created by this skill.
