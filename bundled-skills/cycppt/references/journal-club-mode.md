# Journal-club Mode

Use this reference only when `authoring_mode=JOURNAL_CLUB`, including 文献汇报、论文解读、组会汇报, and journal club tasks centered on one or more research papers. Do not force this mode onto hospital work reports, guideline summaries, teaching decks, or direct visual conversion.

## Contents

- Required artifact order
- `paper_logic.json` contract
- Panel-level evidence ledger
- Slide-plan contract
- Page-count fit audit
- Validation gates

## Required artifact order

Create and validate artifacts in this order:

1. `source_inventory.json`
2. `paper_logic.json`
3. panel-level `figure_inventory.json`
4. `plans/ppt_plan.json`
5. `reports/deck_outline.md` and `reports/figure_ledger.csv`
6. slide prompts

Do not outline slides until the paper logic is explicit. Read the whole paper, Figure/Table captions, and the opening and closing paragraphs of each Results subsection; do not infer the story from the abstract alone.

## `paper_logic.json` contract

Require:

- `mode`: `journal_club`
- `bibliographic_identity`: title, journal, year, citation, and DOI or stable identifier
- `author_team`: first authors, corresponding authors, affiliations, collaboration structure, why the team matters, and source anchors
- `central_problem`
- `knowledge_gap`
- `hypothesis_or_claim`
- `system_and_data`
- `study_design`
- `evidence_chain`
- `final_conclusion`
- `scope_boundary`: what the study does not prove
- `content_fit_audit`: confirmed target count, evidence-based recommended range, status, and rationale

Each `evidence_chain` item must contain a unique `claim_id`, a claim, the experiment or analysis, one or more `evidence_refs`, an interpretation, and a caveat. `evidence_refs` must resolve to included evidence entries in `figure_inventory.json`.

Never invent author prestige, institutional reputation, contribution roles, or collaboration significance. Use the paper byline, affiliation block, contribution statement, acknowledgements, trial registration, and other source-visible evidence. Record `not_reported` when the paper does not report a field.

## Panel-level evidence ledger

Treat a Figure panel or Table as the default evidence unit. A combined crop is allowed only when the panels form one inseparable comparison.

For every candidate entry in `figure_inventory.json`, record:

- `asset_id`, `figure_id`, and optional `panel_id`
- `source_section`: `main_text`, `supplement`, `extended_data`, or `user_provided`
- source page/region, caption summary, supported claim, and visual type
- `include_decision`: `include`, `maybe`, or `exclude`
- decision reason and selection score components
- crop/output path, citation, evidence mode, and render policy

Score panel selection as:

```text
include_score = centrality_to_claim
              + closes_key_gap
              + method_explanatory_value
              + visual_readability
              - redundancy
              - excessive_detail
```

Prefer main-text evidence. Include supplemental or Extended Data evidence only when it closes a necessary evidence gap; record `exception_justification` and visibly label its source on the slide. Do not use journal logos, author portraits, stock images, web images, graphical abstracts, or generated substitutes as scientific evidence unless the user explicitly requests them. Generated decorative or explanatory visuals remain allowed but must not replace paper evidence.

Crop at 200–300 DPI and preserve axes, legends, scale bars, color bars, group labels, sample sizes, statistics, and panel labels. Prefer one evidence crop per result slide; use two or three only for a genuine comparison. Do not repeat a crop without a stated narrative reason.

Figures, charts, medical images, and source flow diagrams remain `original_preferred`. Tables may be `reconstruct_allowed` under the preservation and labeling rules in `SKILL.md`.

## Slide-plan contract

Use claim-driven titles. A Results title must state the finding; reject generic titles such as `研究结果`, `主要结果`, `Figure 2`, `Table 3`, `图2`, or `表3`.

Require every Results/evidence/mechanism slide to contain:

- `claim_id` mapped to `paper_logic.evidence_chain`
- at least one bound included evidence asset from that claim
- `interpretation.how_to_read`
- `interpretation.what_it_proves`
- `interpretation.caveat`
- speaker notes covering setup, axes/legend reading, interpretation, and caveat

Plan the narrative as: title, one-slide takeaway, author/team, broad problem, unresolved gap and guiding question, methods/design, claim-driven evidence sequence, integrated conclusion/model, strengths, limitations, scope boundary, and follow-up questions. Split a dense evidence chain instead of shrinking panels. Every added result slide must answer: “What claim does this make more believable?”

Store final critical appraisal under `ppt_plan.json` → `journal_club`:

- `strengths`
- `limitations`
- `scope_boundary`
- `follow_up_experiments`
- `discussion_questions`: 2–4 concrete group-meeting questions

The author/team slide must cite its source anchors. The plan must use every evidence entry marked `include`, or change unused entries to `maybe`/`exclude` with a reason.

## Page-count fit audit

Keep the user-confirmed slide count as the hard target. Do not override it with a default range. Before outlining, compare the confirmed count with the evidence chain and record `content_fit_audit.status` as `fit`, `underfilled`, `overfull`, or `user_override`. If the count would force unreadable panels or filler slides, report the mismatch and propose a revised concrete count; proceed with the confirmed count only when the user retains it.

## Validation gates

Run both commands before generating slide prompts:

```bash
python cycppt/scripts/validate-paper-logic.py \
  --paper-logic <task>/paper_logic.json \
  --figure-inventory <task>/figure_inventory.json

python cycppt/scripts/validate-journal-club-plan.py \
  --plan <task>/plans/ppt_plan.json \
  --paper-logic <task>/paper_logic.json \
  --figure-inventory <task>/figure_inventory.json
```

Stop before prompt generation when either validator fails.
