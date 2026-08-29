# Pool Governance Protocol v5.5

## Two pools

### AUDIT_POOL_40

This immutable report-level audit pool contains exactly 40 unique reports mapped from 41 source
records by the frozen `01_Source_Report_Index`. An excluded report remains in this pool. Under
v5.5, `STU-005` remains in the audit pool but is excluded from the review; the primary diagnostic
analysis set contains 39 reports and the strict-adult sensitivity set contains 38.

Required fields:

`audit_membership_id, source_record_ids, report_id, study_id, audit_set_40_01,
identity_source_workbook, identity_source_sheet, source_index_sha256, audit_status,
protocol_version, pool_version, decision_evidence_id, last_updated`.

### Diagnostic synthesis pool

This versioned long table contains eligible branch/performance memberships. Required fields:

`synthesis_membership_id, pool_version, parent_audit_membership_id, report_id, study_id,
eligibility_scope_id, outcome_id, model_id, dataset_id, analysis_population_id, performance_id,
synthesis_group_id, synthesis_eligible_01, exclusion_or_pending_code, primary_secondary_code,
selection_rank, selection_rationale, independent_cohort_id, dependent_effect_cluster_id,
adjudication_status, final_evidence_id, frozen_at`.

Only a finally adjudicated current-state diagnostic branch with a fixed model, usable compatible
performance, resolved identity/dependency, and `synthesis_eligible_01=1` may be a member. Pending,
future-event, known-current-organism-input, organism-restricted, no-model, and inventory-only units
are excluded but remain traceable in atomic/audit tables.

## Versioning and derivation

- Use immutable `pool_version`; never edit a frozen membership in place.
- Record parent version and dated additions/removals with evidence.
- Derive report-level status from branch memberships; never derive branch eligibility from a
  report-level status.
- `CANDIDATE_ACTIVE` is an audit/workflow state, not synthesis eligibility.
- Freeze analysis sets only after eligibility, SEMKEY, source identity, coverage, dependency, and
  numeric QA pass.
- One-effect-per-cohort primary selection must follow the synthesis hierarchy, not maximum AUC.

## Required QA

Verify exactly 40 unique audit reports, one study mapping per report unless explicitly modeled,
foreign-key agreement with the frozen source index, unique memberships, final evidence for every
active synthesis member, and zero pending/ineligible units in synthesis. Audit pool counts and
synthesis counts must never be asserted equal. Additionally verify 39 primary diagnostic reports,
38 strict-adult reports, `STU-005` excluded, and `STU-016` present only in the primary set.
