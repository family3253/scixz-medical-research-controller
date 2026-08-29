# Scoring Protocol v5.5

## Framework selection

Use the current official frameworks for every included report:

- TRIPOD+AI 2024 for reporting completeness of prediction-model development/evaluation using
  regression or machine learning. It supersedes TRIPOD 2015.
- PROBAST+AI 2025 for model development quality, performance-evaluation risk of bias, and
  applicability, regardless of regression or machine learning.

Primary sources:

- https://doi.org/10.1136/bmj-2023-078378
- https://doi.org/10.1136/bmj-2024-082505

The active item dictionary must be versioned. Do not use the sibling `check-reporting` skill's
legacy instruction that reserves TRIPOD+AI for ML only; the official 2024 statement covers both
regression and machine-learning methods and says the 2015 checklist should no longer be used.

## TRIPOD+AI assessment

Grain: `tripod_component_id × item_code`, where the component is a report-level eligible
development, evaluation, update, or inseparable combined component. Share genuinely report-level
items across models only through explicit references; do not duplicate evidence as if independently
reported.

Allowed item states:

- `PRESENT`
- `PARTIAL`
- `MISSING`
- `NOT_APPLICABLE` with justification
- `UNCLEAR`

Record item/subitem code, applicable study component (development/evaluation/update), status,
location, evidence, reviewer, and adjudication. The item-level long table is authoritative; any
wide matrix or adherence percentage is derived.

TRIPOD+AI is not a quality or risk-of-bias score. If a descriptive adherence rate is reported,
use fully present applicable items as numerator, report PARTIAL separately, and never rank or
weight studies by the rate.

## PROBAST+AI assessment

PROBAST+AI has two distinct parts:

1. Development: assess methodological quality and applicability once for each developed or updated
   model using the applicable development signalling questions.
2. Evaluation: assess risk of bias and applicability for each
   `model × outcome × dataset × analysis population/performance context` scope. Multiple metrics
   from the same scope share one evaluation assessment; materially different populations or contexts
   receive separate scopes. Distinguish apparent, tuning, internal-validation, and external-validation
   performance.

Use the official response scale in the active item dictionary (for example yes/probably yes/
probably no/no/no information/not applicable), then derive domain and overall judgments exactly
as specified by the tool. Do not convert signalling questions into an unvalidated numeric total.

Applicability by report type:

| Report component | Development part | Evaluation part |
|---|---:|---:|
| New model, no performance estimate | Yes | No for the absent evaluation |
| New model with apparent/internal/external performance | Yes | Yes for each distinct evaluation unit |
| Model update/recalibration | Yes | Yes when updated-model performance is evaluated |
| External evaluation only | No | Yes |
| Training dataset row without performance | Covered by development assessment | No independent evaluation row |

Keep three outputs separate:

- development quality;
- evaluation risk of bias;
- applicability concern.

Also keep author-reported limitations, review-identified methodological limitations, and TRIPOD+AI
reporting gaps as three separate evidence types. Only an explicit author statement with a source
locator may populate an author-reported limitation. Liu 2024 may be cited as prior-review context
but none of its PROBAST proportions or study-level judgments may be imported.

Each Development and Evaluation scope must carry `eligibility_scope_id` and the canonical
`model_id`; Evaluation must also carry outcome, dataset, analysis-population, and performance
context foreign keys. Do not merge a known-organism-input, future-event, organism-restricted, or
unresolved provisional branch with an eligible diagnostic model merely because both occur in one
report. Retain ineligible/pending branch inventory and eligibility evidence, but do not create an
active review-synthesis appraisal scope for it. Use an explicit non-applicability reason when a
report component is retained only for audit provenance.

## Independent double scoring

TRIPOD A/B and PROBAST A/B work independently from the full report and supplements. Each scored
item must have a locator and evidence. The third adjudicator replays the source for any item or
domain disagreement and records both original calls, final call, rationale, and source anchor.

Store reviewer A, reviewer B, and final evidence IDs separately. Use one official dictionary record
per row with a generic response field; its allowed values come from that dictionary row. Record
development quality concern, evaluation risk of bias, and applicability concern as distinct record
types. Do not place `LOW` in an ambiguously named `domain_quality` field or calculate a numeric
PROBAST total.

Validate `framework + assessment_type + item_code` against the active official dictionary. Copy the
dictionary-defined record type and validate every response against that row's response options. A
domain or overall `LOW/HIGH/UNCLEAR` judgment must never be written into a signalling-question row.

Do not infer “reported” from absence of criticism. Do not infer high risk solely from poor reporting;
when methods are unreported use the framework's unclear/no-information route unless the tool directs
otherwise.
