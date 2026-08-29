# Model Selection and Validation Rules

## Purpose

This reference defines how to interpret model families and validation layers in a paper-by-paper prediction-model workflow.

## Traditional vs Machine Learning

Treat these as **traditional**:
- logistic regression
- clinical score
- nomogram
- classical point-based rule

Treat these as **machine learning**:
- random forest
- gradient boosting / GBM
- XGBoost
- SVM
- neural networks
- similar ML classifiers

## Retention Logic

### Default rule
If the paper explicitly names a final / best / selected model, use that first.

### If the user wants comparison value
Retain:
- one traditional model
- one machine-learning model

unless the paper structure or the user explicitly justifies keeping more.

### If the source is a thesis
Do not treat every section as a prediction model.
Retain only the explicitly relevant prediction-model unit(s), plus any auxiliary evidence the user explicitly chooses to keep.

## Project Scope Rule: MDR-GNB and Subspecies

For the current project, the primary scope is:
- MDR-GNB
- accepted narrower sub-organism / resistance subsets confirmed by the user as belonging to the MDR-GNB family

Examples that may be retained when explicitly aligned to the project scope:
- CRE
- CPE
- CR-GNB
- ESBL-producing Enterobacterales / ESBL-EKP when the user has explicitly accepted them into scope

Examples that should not automatically enter the main pool:
- non-GNB targets such as VRE / MRSA
- broader endpoints that exceed the user’s chosen scope unless the user explicitly keeps them as subgroup or narrative evidence

When a paper contains both in-scope and out-of-scope units, retain only the in-scope units in the main collection workbook.

## Validation Interpretation

### Internal validation
- cross-validation
- bootstrap
- random split / holdout test in the same source population

### External validation subtypes
- temporal validation: same site, later period
- geographic validation: different sites or hospitals
- broader external validation: different institution / region / system

Always write the subtype explicitly.

## Performance Priority

When deciding how a retained unit will be used later, prioritize:

1. external validation / test performance
2. internal test performance
3. internal validation performance
4. training / apparent performance

Do not mix them casually.
