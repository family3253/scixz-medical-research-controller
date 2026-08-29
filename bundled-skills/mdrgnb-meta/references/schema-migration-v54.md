# v5.3 to v5.4 schema migration

This file preserves the historical v5.4 super-header rules. For active migration and repair,
`schema-recovery-v57.md` is authoritative: a super-header is archival provenance, not a canonical
fact model, and schema-created blanks must not be converted to source-level `NR`.

Frozen v5.3 branches are immutable. Migrate into a new directory and retain every source column.
The v5.4 table header is the ordered union of all legacy columns plus v5.4 fields; no input column
may be deleted or renamed in place.

## Eligibility super-header

Preserve all Pilot/Batch02 23 columns and Batch03 28 columns. Add:

`eligibility_scope_id, cohort_id, model_branch_id, parent_model_id, branch_label_raw,
model_specification_status, t0_code, current_organism_input_at_t0_01,
current_organism_input_level_code, organism_restriction_level_code,
organism_restriction_basis_code, prior_colonization_or_infection_history_only_01,
diagnostic_prognostic_code, branch_eligibility_status, eligibility_reason_code,
inventory_status, source_evidence_id, protocol_version, protocol_hash, branch_status,
migration_source_schema, migration_status`.

Keep aliases such as `assessment_id/evidence_id` during migration. New canonical fields may point
to the legacy value, but the source column remains unchanged. Use `UNCLEAR` when source replay is
needed; do not fabricate known-organism track, fixed-model status, or eligibility.

## Unit-inventory super-header

Preserve the union of Pilot/Batch02 32 columns and Batch03 23 columns, including both
`unit_id/inventory_id`, `cohort_id/physical_cohort_id`, `performance_ids/performance_id`,
`unit_status/inventory_status`, `source_anchor/source_evidence_id`, and all clinical/synthesis
buckets. Add `eligibility_scope_id, migration_source_schema, migration_status`.

Populate safe aliases without deleting the original:

- `unit_id <-> inventory_id` when one side is blank;
- `cohort_id <-> physical_cohort_id` when one side is blank;
- `performance_id -> performance_ids` for a single ID; never collapse a genuine list;
- `source_evidence_id -> source_anchor` only as an alias, not as proof that locator and evidence ID
  are semantically identical.

## Gate

After migration, every batch must have byte-identical ordered headers for each table type. Run
`qa_full40_coverage_v1.py`. Header equality, row preservation, unique identities, explicit
missingness, and cumulative report coverage are blocking. Migration success does not by itself
adjudicate ambiguous values or make a unit synthesis eligible.

The v4.5 index contains two raw `source_record_id=NR_ORIGINAL_ID` rows for STU-039/STU-040.
Preserve the raw value, add a unique `canonical_source_record_id` derived deterministically from
the stable report ID/DOI, and record the derivation. `--compat-v45-placeholders` may warn rather
than fail during read-only forward testing; a released v5.4 identity table must not retain duplicate
active canonical source-record IDs.

## SEMKEY crosswalk migration

Use `migrate_semkey_crosswalk_v54.py` only when a legacy crosswalk has no repeated A/B/third
source entity. It adds explicit v5.4 relation groups and then runs strict SEMKEY validation.
If any source entity is reused, automatic migration must stop with
`REQUIRES_FACTUAL_CROSSWALK_REPAIR`: the reuse may be a legitimate coarse-to-fine split or an
incorrect first-row placeholder. Repair requires source-adjudicated entity mapping and the
relation-group/cardinality evidence contract in `semantic-key-v1.md`; compatibility mode must not
downgrade this blocker.
