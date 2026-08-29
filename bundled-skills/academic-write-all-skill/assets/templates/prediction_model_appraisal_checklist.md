# Prediction Model Appraisal Checklist

Use this checklist when reviewing scores, nomograms, risk scores, or machine-learning prediction models.

## A. Native Working Appraisal

### Reporting completeness
- [ ] Population and setting are clearly defined
- [ ] Predicted outcome is explicitly defined
- [ ] Predictors are listed clearly
- [ ] Model type is identified (`score`, `nomogram`, `ML`, `other`)
- [ ] Validation type is stated
- [ ] At least one performance metric is reported

### Bias / applicability warning scan
- [ ] Single-center or narrow cohort risk noted
- [ ] Predictor definitions are clear enough for reuse
- [ ] Outcome definition matches the claimed clinical use
- [ ] External validation status is clear
- [ ] Calibration is reported or explicitly absent
- [ ] Transportability concerns are noted

### Extraction discipline
- [ ] Risk-factor studies separated from true prediction models
- [ ] Disease-topic review kept separate from model-appraisal review
- [ ] Evidence matrix fields are complete enough for synthesis

## B. External Standards (Borrow Explicitly When Needed)

### TRIPOD / TRIPOD+AI
Use when you need stronger reporting-completeness checks.

- [ ] Model development/reporting details are complete enough for reader understanding
- [ ] Predictor and outcome handling are explained
- [ ] Validation and model presentation are adequately reported
- [ ] Use `TRIPOD+AI` rather than `TRIPOD` when AI/ML methods materially shape the model

### PROBAST / PROBAST+AI
Use when you need stronger bias and applicability assessment.

- [ ] Participants/data source domain reviewed
- [ ] Predictors domain reviewed
- [ ] Outcome domain reviewed
- [ ] Analysis domain reviewed
- [ ] Use `PROBAST+AI` rather than `PROBAST` when AI/ML methods materially affect the assessment

### CHARMS-style extraction
Use when the review needs a more formal extraction scaffold.

- [ ] Study design captured
- [ ] Setting captured
- [ ] Population captured
- [ ] Outcome captured
- [ ] Predictors captured
- [ ] Model development/validation captured
- [ ] Performance and key limitations captured

## C. Provenance Labeling

When external standards are used, state it explicitly:
- [ ] borrowed external standard named clearly
- [ ] borrowed logic is not presented as native capability
- [ ] integrity gates remain active
