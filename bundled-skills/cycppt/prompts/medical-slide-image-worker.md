# Medical Slide Image Worker Prompt Template

```text
Generate one complete medical PPT slide image for the cycppt single-skill workflow.

Task dir: {{TASK_DIR}}
Slide id: {{SLIDE_ID}}
Slide number: {{SLIDE_NUMBER}}
Slide plan: {{SLIDE_PLAN_PATH}}
Prompt file: {{PROMPT_FILE}}
Output image: {{OUTPUT_IMAGE}}
Result JSON: {{RESULT_JSON}}
Reference images: {{REFERENCE_IMAGES}}
Figure inputs: {{FIGURE_INPUTS}}

You own only this slide image output and its result JSON. Do not write page-level manifest.json, page.pptx, preview.png, validation.json, editppt_run state, or final deck files.

Mandatory image backend:
- Use editppt image generate/edit/batch.
- Use editppt image edit when prompt execution requires source Figure inputs or style reference images.
- Do not call legacy yixue image generation scripts.
- Do not call non-`editppt image` generation tools.
- Do not locally compose the final slide with PIL, SVG, HTML screenshots, python-pptx, @oai/artifact-tool, direct native PPT generation, or any presentation authoring shortcut.

Prompt quality gate:
- Do not accept summary-style prompts.
- The prompt file must be a rich GPT Image 2 slide prompt with expanded style-key text, slide-specific plan, concrete layout geometry, evidence/asset binding instructions, negative constraints, and continuity rules.
- If the prompt has not passed `cycppt/scripts/validate-slide-prompt.py`, stop and return `status=failed` instead of generating from a weak prompt.
- If `editppt image` or its GPT Image 2 backend is unavailable, stop and report the blocker. Do not switch to artifact-tool, python-pptx, HTML/SVG screenshots, or native PPTX generation.

Page-template binding:
- Read `template_binding` from the slide plan when present.
- If `template_binding.reference_image` is set, include that exact image in the editppt image call and record it in `reference_images`.
- If `template_binding.external_page_id` is set, treat that page id as the exact subject-content layout choice; use `source_template` and `source_slide` to preserve its content-region structure, not merely its color palette.
- Different slides may intentionally bind different external page ids, but automatic bindings must share `deck.master_template_id` unless the user explicitly authorized cross-family selection.
- Preserve only the bound page's subject-content layout skeleton, whitespace, column structure, and evidence rhythm while replacing placeholder content with the slide plan's medical content.
- The deck-wide chrome is locked: header, footer, navigation presence and position, Logo area, title origin, page-number position, typography, brand colors, margins, and citation system must not drift between body slides.
- If `navigation_policy=none`, remove navigation bars or side navigation visible in a page reference. A reference image never overrides the deck-wide navigation policy.
- If `template_binding.campus_locked=true`, preserve the exact campus name and its matching campus photograph. Do not substitute another campus or a generic hospital image.
- If the binding is the 邵逸夫医院 common ending with `campus_specific=false`, preserve the provided THANK YOU / 谢谢！ layout and hospital/cooperation logos for any confirmed campus.

Evidence binding:
- Read `assets.required` and `FIGURE_INPUTS` before generation.
- Every item with `evidence_mode=original` must be included as an actual input image to `editppt image edit/batch` and recorded in `figure_inputs`; do not redraw or imitate it from text.
- Preserve original data-bearing pixels, labels, legends, groups, statistical marks, and aspect ratio. Only proportional scaling, blank-margin cropping, and non-obscuring external annotations are allowed.
- `derived` or `reconstructed` Figures/charts/medical visuals are allowed only for explanation, translation, or information restructuring and must visibly say “重构示意 / Derived from source” with the source citation.
- A Table may be reconstructed for readability or editability, but it must visibly say “表格重构 / Reconstructed from Table X”, preserve every value/denominator/unit/footnote, and retain the original citation.
- Do not redraw every source chart merely to match the deck style. Integrate original evidence with consistent frames, captions, spacing, and Chinese interpretation panels.
- Never let template placeholders leak into the output: remove “单位占位文字区域”, generic “LOGO”, institution/name/school/topic/date placeholders, and any sample metadata. If the real institution or Logo is not supplied, leave that area blank or use a neutral icon without text.

Visual quality-control loop:
- Inspect the actual generated image against the prompt, slide plan, Figure inputs, and reference images before accepting it.
- Review these checks explicitly: `text_readable`, `no_garbled_text`, `layout_complete`, `style_consistent`, `evidence_preserved`, `safe_margins`, and `no_visual_artifacts`. `style_consistent` includes chrome position/presence; `evidence_preserved` includes actual original-asset embedding and derived-label visibility.
- If any check fails, revise the generation instruction to address the concrete issue and regenerate. Use at most 3 total generation attempts.
- Do not return the last image merely because the retry budget is exhausted. If no attempt passes, return `status=failed`, preserve the issue list, and do not mark the slide ready.
- Record the accepted attempt number, all checks, issues, and a short review reason in `quality_review`.

Output must be a complete 16:9 PowerPoint page image: title, body text, evidence regions, citations/notes if requested, and visual design all inside the generated image. Preferred canvas is 2560x1440.

Before returning:
1. Verify {{OUTPUT_IMAGE}} exists.
2. Verify image dimensions and record them.
3. Write {{RESULT_JSON}} with slide_id, slide_number, prompt path, output path, reference image paths, figure input paths, backend command, size_px, attempt_count, quality_review, passed, warnings, and errors.

Required `quality_review` shape for a passed slide:

```json
{
  "passed": true,
  "attempt": 1,
  "checks": {
    "text_readable": true,
    "no_garbled_text": true,
    "layout_complete": true,
    "style_consistent": true,
    "evidence_preserved": true,
    "safe_margins": true,
    "no_visual_artifacts": true
  },
  "issues": [],
  "reason": "Accepted after visual comparison with the prompt, plan, evidence, and references."
}
```

Return only:
output_image=<absolute path>
result_json=<absolute path>
status=passed|failed
```
