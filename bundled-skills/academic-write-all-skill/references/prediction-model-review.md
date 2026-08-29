# Prediction-Model Review

## Purpose
This file supports review-grade writing and appraisal when the target literature is about clinical prediction tools rather than general disease description.

Use it when the corpus contains scores, nomograms, risk scores, machine-learning models, or clinical prediction tools.

## 1. When To Route Here

Use this workflow when the user asks for any of the following:
- prediction model review
- nomogram review
- risk-score review
- model appraisal
- transportability / external validation discussion
- comparison of prediction tools for a disease, resistance phenotype, or clinical syndrome

## 2. First Question: Is This Really a Prediction Model Corpus?

Before writing, separate these categories:
- true prediction model studies
- risk-factor association studies
- descriptive epidemiology papers
- treatment/outcome prediction models unrelated to the infection-acquisition question
- pathogen-specific mortality models vs infection-acquisition models

Do not mix these casually.

## 2A. PDF Reading Bias for Prediction-Model Review

Prediction-model papers often hide crucial extraction targets outside the main narrative text.

Before concluding a field is “not reported,” check whether it appears in:
- supplementary PDF files
- appendix tables
- calibration or decision-curve figure panels
- online supplements or extended methods sections
- model formula / coefficient tables separate from the main results section

For this reason, prediction-model review should use a PDF-reading strategy that is table-aware, supplement-aware, and page-aware rather than relying on naive full-text extraction alone.

## 3. Minimum Extraction Dimensions

For each included study, try to extract:
- citation / identifier
- target population
- clinical setting
- organism or resistance phenotype target
- predicted outcome
- model type (`score`, `nomogram`, `ML`, `other`)
- candidate predictors
- final predictors retained
- derivation / internal validation / external validation
- discrimination metric(s) if reported
- calibration information if reported
- decision utility / threshold analysis if reported
- key limitations or transportability risks

For prediction-model meta work, this minimum set is usually not enough. Prefer a **study-by-study structured extraction register** that separates model development from model evaluation and preserves metric context.

### 3A. Prediction-Model Meta Extraction Priority

If the review may progress to quantitative or semi-quantitative synthesis, prioritize extraction quality in this order:

1. study identity and cohort definition
2. outcome definition and prediction horizon
3. model stage and exact data split (`training set`, `internal validation set`, `internal test set`, `temporal validation`, `geographic validation`, `external validation set`, `external test set`, `update / extension`)
4. exact performance metrics with their uncertainty context
5. calibration details
6. clinical utility / threshold details
7. transportability and implementation constraints

If these are unstable, incomplete, or inconsistent across studies, downgrade the output before pretending a tight meta-synthesis is ready.

### 3A2. Recommended Extraction Fields for Prediction-Model Meta

In addition to the minimum dimensions, try to extract the following whenever visible:

- derivation sample size and event count
- training-set sample size and event count when separately reported
- internal-validation-set sample size and event count when separately reported
- internal-test-set sample size and event count when separately reported
- validation sample size and event count
- external-validation-set sample size and event count when separately reported
- external-test-set sample size and event count when separately reported
- outcome prevalence / event fraction
- prediction horizon or time window
- candidate predictor count
- final predictor count
- missing-data handling method
- feature engineering / resampling / class-imbalance handling if relevant
- algorithm family and any ensemble structure
- threshold or operating point if reported
- discrimination metric name (`AUC`, `c-statistic`, `AUPRC`, etc.) and value
- uncertainty for discrimination metric (`95% CI`, `SE`, or enough information to reconstruct if visible)
- calibration metric type and value (`calibration slope`, `intercept`, `O:E`, calibration plot only, etc.)
- decision-curve / net-benefit reporting and threshold range
- whether the reported metric is from training, internal validation, internal test, cross-validation, bootstrap optimism correction, temporal validation, geographic validation, external validation, or external test
- whether the study compares multiple models and which one is deemed primary
- whether the model is intended for bedside use, surveillance, stewardship, or research-only contexts

If a paper uses vague language such as “validation cohort” or “test cohort,” do not assume it is external. Extract the exact wording first, then classify cautiously.

If the wording is only recoverable from a table, supplement, or figure caption, preserve that exact source location in the extraction register.

Do not collapse these into a single prose note if the later synthesis may depend on them.

If any field is missing, mark it explicitly rather than filling it by guesswork.

## 3B. Native Working Appraisal Frame

Before invoking external standards, the skill should already be able to do a built-in working appraisal using these three buckets:

### Reporting completeness (TRIPOD-like native baseline)
- are population, setting, and outcome clearly defined?
- are predictors listed clearly enough to understand bedside availability?
- is the model form explained (`score`, `nomogram`, `ML`, other)?
- are validation and performance metrics reported?
- is there enough information for a reader to understand how the model would be used?
- is it clear which dataset or split each reported performance metric comes from?

### Bias / applicability warning scan (PROBAST-like native baseline)
- is the cohort narrow, single-center, or otherwise hard to generalize?
- are predictor or outcome definitions unclear?
- is there evidence of weak validation or only development-stage optimism?
- is calibration absent or underreported?
- does the target outcome actually match the clinical decision the paper claims to support?
- are reported performance metrics tied to the correct validation tier, or are development metrics being presented as if they were transportable performance?
- are internal test results being described as if they were true external validation?

### Structured extraction discipline (CHARMS-like native baseline)
- capture study, population, setting, outcome, predictors, model type, validation, and major limits
- keep risk-factor studies separate from finished prediction-model studies
- keep disease-topic synthesis separate from model-appraisal synthesis
- keep development-stage metrics separate from external-validation metrics
- keep training, internal validation, internal test, external validation, and external test results in distinct fields whenever the article allows it
- keep comparable performance metrics grouped by metric definition rather than by whichever number looks strongest

This native frame is intentionally lighter than the formal external checklists, but it gives the skill a stronger built-in floor before escalation.
## 4. Recommended Review Structure

### A. Why prediction is needed
Explain the clinical decision problem first.
Examples:
- empiric antibiotic selection
- early risk stratification
- identifying high-risk carriers or high-risk ICU admissions
- selecting patients for intensified surveillance

### B. Model landscape map
Group studies by:
- target setting (CAP, HAP/VAP, ICU, oncology, colonized patients, etc.)
- outcome type (MDR pathogen, carbapenem-requiring infection, CR-GNB carriage, bacteremia, specific pathogen infection)
- model form (simple score, nomogram, ML model)

### C. Methodological appraisal
Discuss:
- whether predictors are available at point of care
- whether the model was externally validated
- whether calibration was reported
- whether transportability is plausible across hospitals or countries
- whether the endpoint is clinically coherent

For prediction-model meta work, discuss not only whether a metric exists, but whether it is comparable across studies and attached to the correct validation stage.

If multiple tiers are reported, privilege external evaluation over internal evaluation for transportability claims, and do not let training-set or internal-only results dominate the narrative.

### D. Clinical usefulness
Discuss what the model can realistically support and what it cannot.
Do not assume a model is clinically useful just because the AUC looks respectable.

### E. Evidence gaps
Highlight:
- lack of external validation
- narrow single-center cohorts
- over-specialized populations
- mixed pathogen definitions
- mismatch between predicted outcome and bedside decision need
- inconsistent metric definitions or unpooled metric reporting
- calibration underreporting even when discrimination is prominently reported
- unclear distinction between internal and external evaluation datasets

## 5. Hard Rules

- do not treat a risk-factor paper as a finished prediction model paper
- do not assume a nomogram figure proves adequate model reporting
- do not compare models head-to-head unless outcomes and settings are genuinely comparable
- do not overstate clinical adoption readiness when external validation is weak or absent
- when appraisal requirements exceed native coverage, explicitly borrow stronger local-skill logic or external reporting/appraisal patterns and label the borrowing

## 6. Safe Appraisal Language

Preferred phrases:
- `the available models are highly setting-specific`
- `external validation appears limited`
- `reported discrimination is not enough to establish transportability`
- `the evidence base supports a review-grade synthesis, not a universal implementation recommendation`
- `the current literature is better viewed as a set of scenario-specific tools than a unified prediction framework`

## 7. Output-Level Guidance

Use the strongest honest level:
- `submission-grade review draft` only if coverage, appraisal, and model comparison are already mature
- `review-grade evidence synthesis` when there is enough to compare families of models but not enough for final claims
- `evidence map` when studies are too heterogeneous to synthesize tightly
- `framework memo` when the corpus is still incomplete

## 8. Suggested Evidence Matrix Columns

A good matrix usually includes:
- Study
- Population
- Setting
- Organism / resistance target
- Outcome
- Model type
- Predictors
- Validation type
- Discrimination
- Calibration
- Utility / DCA
- Main limitations
- Review note

For prediction-model meta extraction, a stronger matrix usually adds:
- Development N / events
- Training N / events
- Internal validation N / events
- Internal test N / events
- Validation N / events
- External validation N / events
- External test N / events
- Prediction horizon
- Validation tier
- Metric context
- Uncertainty available?
- Missing-data handling
- Resampling / imbalance handling
- Calibration metric detail
- Threshold / operating point
- Intended use context

## 9. Borrowed External Standards

If methodological appraisal becomes the bottleneck, it is acceptable to borrow external reporting or appraisal patterns, but only with explicit labeling.

Preferred external standards for this situation:
- `TRIPOD` for traditional regression / score / nomogram reporting completeness
- `TRIPOD+AI` when the prediction model uses AI / machine-learning methods or AI-specific workflow elements
- `PROBAST` for traditional bias / applicability appraisal
- `PROBAST+AI` when AI or machine-learning methodology materially changes the bias/applicability assessment
- `CHARMS`-style extraction logic when the review needs a structured data-extraction frame for prediction-model studies

When the task is specifically a prediction-model meta-analysis, the safest operational interpretation is:
- `TRIPOD` / `TRIPOD+AI` help decide what reporting details should have been extractable
- `PROBAST` / `PROBAST+AI` help decide whether extracted performance should be trusted and how transportable it may be
- `CHARMS`-style logic helps decide which study, predictor, outcome, validation, and metric fields must be preserved for later synthesis

Current conservative note:
- a formal, official `CHARMS+AI` equivalent is not treated as confirmed here, so the repository uses `CHARMS-style` language rather than claiming an authoritative AI extension by name

## 9A. Practical Infusion from PROBAST+AI and TRIPOD+AI

The following operational rules are strongly supported by the extracted guideline text and should shape prediction-model meta extraction and appraisal:

### From PROBAST+AI
- classify each study or model contribution as `development`, `evaluation`, or `combination` before appraisal
- assess model development and model evaluation separately rather than collapsing them into a single quality judgment
- for model evaluation, treat apparent performance, internal validation, and external validation as distinct analysis contexts
- in the analysis domain, examine whether performance measures such as calibration, discrimination, and net benefit were evaluated appropriately
- if data splitting created training and test datasets, look for explicit evidence that data leakage was avoided
- if resampling was used, check whether all model-development steps were replicated within the resampling process

### From TRIPOD+AI Supplement
- report data sources separately for development and evaluation datasets
- specify whether the study concerns development, validation/testing, or both
- if data were partitioned, describe how and why they were partitioned, including the role of training, hyperparameter tuning, and testing datasets
- describe the internal validation method explicitly, such as bootstrapping or cross-validation, and whether all model-building steps were replayed during internal evaluation
- report all model-performance measures and plots used, including discrimination, calibration, and clinical utility
- report performance estimates for all evaluations undertaken, including development data, evaluation data, and internal validation processes
- for external validation/testing, describe how predictions were calculated from the original model and how the evaluation data differed from the development data
- discuss external validation/testing results in relation to development-data performance and any other validation results

### Consequence for Prediction-Model Meta Extraction

For a review or meta-analysis, these guideline-backed rules mean:
- never create one pooled “validation” field when the paper actually reports multiple tiers
- extract development, internal validation, internal test, and external validation/testing results separately whenever recoverable
- if a paper reports only `validation` or `test` without clear qualification, preserve the exact wording and avoid upgrading it to external validation by assumption
- if a paper compares development and evaluation data, preserve those design differences because they affect transportability interpretation

Good phrasing:
- `For model-appraisal structure, I am borrowing a prediction-model review pattern from external reporting/appraisal standards such as TRIPOD/PROBAST.`
- `This appraisal scaffold is borrowed and should not be mistaken for native fully implemented runtime support.`
- `I am using a CHARMS-like extraction frame to organize study characteristics, but that external structure is being applied explicitly rather than presented as a native built-in methodology.`
