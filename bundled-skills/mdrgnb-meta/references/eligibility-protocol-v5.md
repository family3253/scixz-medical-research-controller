# Eligibility Protocol v5.5

## Review question

In adults at a current clinical/sampling decision point, which patient- or episode-level
multivariable models classify an eligible MDR-GNB state that is already present but hidden, while
the current causative organism is unknown, and how well are those models validated and reported?

## Eligibility scope

Judge one row per:

`report_id × study_id × cohort_id × outcome_id × model_id/model_branch_id × t0_signature`.

A fixed deployable specification is a `model`. A named candidate/optimized branch whose final
specification is unresolved remains a provisional model inventory row with
`model_specification_status=FINAL_FEATURE_SET_UNREPORTED`; it cannot enter synthesis.

Required identity and status fields are defined in `extraction-and-units-v5.md`. Preserve separate
A/B/third/final decisions and evidence IDs.

## Current-state rule

Use `DIAGNOSTIC_CURRENT_STATE` when the infection, colonization/carriage, positive-specimen state,
or resistant etiology already exists at model application T0 and later microbiology reveals its
hidden label. Result availability after T0 is not prognosis.

Use `PROGNOSTIC_FUTURE_EVENT` when baseline is explicitly negative or the event/state first arises
after T0: future acquisition, incident infection, death, recurrence, deterioration, or similar.
An admission/short-window swab may identify admission prevalence when the source supports that
interpretation; record the exact collection window.

## Known-current-organism dual-track rule

Evaluate two independent exclusion tracks.

### Track A: model input at T0

Set `current_organism_input_at_t0_01=1` and exclude that branch when it requires a known current
GNB/Gram-negative signal, Enterobacterales/Enterobacteriaceae, genus, species, or current
resistance/ESBL/CRE phenotype result.

Reason: `EXCLUDE_KNOWN_CURRENT_ORGANISM_INPUT_AT_T0`.

### Track B: analytic cohort restriction

Set `organism_restricted_cohort_01=1` and exclude when design eligibility or post-hoc analytic
selection restricts the current episode to known GNB, Enterobacterales, genus, or species before
resistance classification, even if the model itself uses clinical predictors only.

Reason: `EXCLUDE_ORGANISM_RESTRICTED_COHORT`.

Do not mistake prior colonization/infection history, a post-T0 reference-standard result,
descriptive post-outcome organism distributions, or a broad syndrome's etiologic classes for
known-current-organism input or cohort restriction.

## Model evidence

Require a patient/episode-level multivariable equation, score, nomogram, rule, supervised
classifier, or external evaluation that outputs a probability/score/class and has at least one
usable performance result somewhere in the eligible branch. A development-training role without
performance is inventory-only when another eligible performance context exists.

Exclude association-only analysis, single-marker ROC, isolate/AST/omics/spectral/laboratory-only
classification, causal/treatment-effect models, and a report/model with no usable prediction
performance anywhere. Formula/code availability, leakage, weak validation, absent calibration,
poor performance, and “risk factors” wording do not determine eligibility.

## Mixed and two-stage reports

Create separate eligibility scopes for eligible current-state and future-event outcomes; a base
branch using current organism/phenotype inputs and a clinical-only optimized branch; fixed and
unresolved branches; or admission colonization and later hospital-acquired infection. Never share
one eligibility row, outcome ID, performance unit, or synthesis membership across such branches.

Derive report status only after branch adjudication:

- eligible branch(es) only: `INCLUDE_DIAGNOSTIC_MODEL`;
- eligible plus excluded/pending branch: `INCLUDE_DIAGNOSTIC_BRANCH_ONLY`;
- all branches finally excluded: report-level exclusion;
- only pending branches: `PENDING_PROTOCOL_ADJUDICATION`, never synthesis eligible.

## Population and phenotype

Include explicit adults, author-defined adults without contrary evidence, reports with no evidence
of pediatric enrollment, and the user-approved >=16 cohort (`ADULT_ACCEPTED_16PLUS`). Exclude
explicit inseparable pediatric enrollment from the adult primary review.

For the locked v5.5 set, include `STU-016` in the primary analysis because the report calls the
cohort adult and reports median age 54 years; mark its 12--76-year range and exclude it from the
strict-adult sensitivity set. Exclude `STU-005` because all participants were CRE-negative at
baseline and the target was future first detection/acquisition.

Eligible organism × phenotype families include MDR-GNB, CRE/CPE, CR-GNB, CRAB, CRPA, and eligible
ESBL-producing GNB/Enterobacterales targets. Exclude MRSA, VRE, fungi, intrinsic resistance, and
inseparable broad MDRO composites. Preserve source definitions and laboratory standard/year.

## Branch fields and controlled states

Required fields:

`eligibility_scope_id, report_id, study_id, cohort_id, outcome_id, model_id, model_branch_id,
parent_model_id, branch_label_raw, model_specification_status, model_application_t0_raw, t0_code,
target_state_onset_raw, target_present_at_t0_01, future_event_target_01,
reference_specimen_time_raw, reference_result_time_raw, organism_unknown_at_t0_01,
current_organism_input_at_t0_01, current_organism_input_level_code,
organism_restricted_cohort_01, organism_restriction_level_code,
organism_restriction_basis_code, prior_colonization_or_infection_history_only_01,
diagnostic_prognostic_code, branch_eligibility_status, eligibility_reason_code,
inventory_status, synthesis_eligible_01, source_evidence_id, reviewer_id, review_round,
protocol_version, protocol_hash, branch_status`.

Branch status values:

- `INCLUDE_DIAGNOSTIC_CURRENT_STATE`
- `EXCLUDE_PROGNOSTIC_FUTURE_EVENT`
- `EXCLUDE_KNOWN_CURRENT_ORGANISM_INPUT_AT_T0`
- `EXCLUDE_ORGANISM_RESTRICTED_COHORT`
- `EXCLUDE_NO_PREDICTION_MODEL`
- `EXCLUDE_PURE_LAB_CLASSIFIER`
- `EXCLUDE_INELIGIBLE_PHENOTYPE`
- `EXCLUDE_PEDIATRIC_ONLY_OR_INSEPARABLE`
- `EXCLUDE_NONHUMAN`
- `EXCLUDE_PUBLICATION_TYPE`
- `PENDING_FINAL_MODEL_SPECIFICATION`
- `PENDING_FULLTEXT_OR_SOURCE`
- `PENDING_PROTOCOL_ADJUDICATION`
- `INVENTORY_ONLY_NO_USABLE_PERFORMANCE`

Missing full text is not an exclusion reason. Every final exclusion requires a source-anchored
reason; title wording alone cannot establish no prediction model.
