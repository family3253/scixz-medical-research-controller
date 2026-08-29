# Clinical AI and Machine Learning Ideas

Apply this module to regression or machine-learning prediction models, imaging AI, omics, EHR, multimodal models, digital biomarkers, and clinical decision support.

## Intended-Use First

Define before selecting an algorithm:

- target population and care setting;
- intended user and clinical decision;
- time zero and prediction horizon;
- predicted outcome and ascertainment method;
- predictor availability at the moment of intended use;
- comparator: current practice or a simple clinical model;
- action after a positive or high-risk result;
- acceptable harms from false positives, false negatives, delay, or inequity;
- study stage: development, internal evaluation, external evaluation, updating, impact, or implementation.

Reject “apply AI to dataset X” as an incomplete clinical question.

## Leakage and Validation Gate

- Split participants, sites, or time periods before learning preprocessing parameters, feature selection, imputation, normalization, resampling, or hyperparameters.
- Keep all records from one participant in the same partition.
- Apply SMOTE or other resampling only within training folds.
- Prevent predictors measured after outcome onset, diagnosis, treatment, or clinical suspicion from entering an earlier-risk model.
- Use nested resampling when tuning and performance estimation would otherwise share information.
- Reserve test or external-evaluation data until the model and threshold are locked.
- Prefer geographic, temporal, or independent-cohort evaluation when the intended use crosses sites or periods.
- Do not call a random holdout from the same source “external validation.”

## Sample and Outcome Gate

- Base sample-size planning on participants, events, candidate parameters, outcome prevalence/incidence, expected performance, and optimism; do not use a universal events-per-variable rule without justification.
- Define incident versus prevalent outcomes and competing events.
- Check label validity, adjudication, coding accuracy, missing outcome mechanisms, and class imbalance.
- For case-control sampling, do not report absolute risk or calibration without an appropriate correction and target-population data.
- Avoid selecting a high-dimensional model when event counts support only a simpler model.

## Performance and Clinical Value

Report more than AUROC:

- discrimination with uncertainty;
- calibration-in-the-large, calibration slope, and a calibration plot;
- clinically relevant sensitivity, specificity, predictive values, or time-to-event metrics;
- overall performance such as Brier score where appropriate;
- subgroup performance and fairness-relevant failure modes;
- decision-curve or other clinical-utility analysis when defensible;
- comparison with current practice and a simple baseline;
- uncertainty, optimism correction, and all prespecified analyses.

Do not infer clinical utility from discrimination alone. Do not infer biological causality from feature importance or SHAP values.

## Reproducibility and Reporting

- Use TRIPOD+AI for complete reporting of prediction-model studies using regression or machine learning.
- Use PROBAST+AI separately for quality, risk of bias, and applicability.
- For AI interventions or early clinical evaluation, add stage-appropriate guidance such as SPIRIT-AI, CONSORT-AI, or DECIDE-AI.
- Record data provenance, code and dependency versions, model specification, preprocessing, feature definitions, tuning space, seeds, thresholds, and evaluation protocol.
- Describe privacy, security, fairness, model updating, monitoring, and deployment drift where relevant.

Current primary sources:

- TRIPOD+AI, BMJ 2024: https://www.bmj.com/content/385/bmj-2023-078378
- PROBAST+AI, BMJ 2025: https://www.bmj.com/content/388/bmj-2024-082505

Verify whether later updates or specialty extensions exist before finalizing a protocol.
