# Collaboration state schema

The state is a coordination artifact, not a scientific result. Keep it separate from worker reports and user-facing deliverables.

```yaml
run:
  collaboration_id: string
  mandate_id: string
  approved_route_id: string
  mode: single | panel | council | recursive-review
  status: intake | planning | running | stalled | paused | cancelled | challenging | consensus | verifying | verified | rolled_back | published | blocked
  primary_task: string
  language: zh | en | other
  user_goal: string
  evidence_pack: EvidenceItem[]
  roles: RoleState[]
  rounds: RoundState[]
  decision_log: Decision[]
  invocation_ledger: Invocation[]
  flow_log: FlowEvent[]
  progress_log: ProgressEvent[]
  last_verified_snapshot: string|null
  unresolved: string[]
  output_paths: string[]

EvidenceItem:
  id: string
  path_or_locator: string
  type: string
  provenance: user-supplied | verified-source | derived | assumption
  sensitivity: public | confidential | deidentified | restricted
  instruction_authority: none | reference-only | user-authorized
  checksum_or_version: string|null

RoleState:
  id: string
  role: string
  question: string
  depends_on: string[]
  status: queued | running | retrying | complete | partial | failed | timed_out | blocked
  authorized_ticket: string
  report_path: string|null
  retries: integer
  confidence: high | moderate | low | unknown

RoundState:
  number: integer
  purpose: independent | critic | consensus | revision | verification
  completed_roles: string[]
  critical_issues_open: integer

Decision:
  id: string
  statement: string
  supporting_evidence: string[]
  dissenting_roles: string[]
  confidence: high | moderate | low
  approved_by: string[]

Invocation:
  ticket_id: string
  skill_name: string
  skill_md: string
  input_fingerprint: string
  status: queued | running | complete | partial | failed | timed_out | blocked
  output_paths: string[]
  verification: pending | passed | failed

FlowEvent:
  at: string
  from_role: string
  to_role: string
  event: string
  ticket_id: string|null
  summary: string

ProgressEvent:
  at: string
  role: string
  ticket_id: string
  status: string
  summary: string
```

Minimum invariants:

1. Every final claim has an evidence reference or is labeled as an assumption.
2. Every completed role has a report or an explicit failure record.
3. A run cannot be `published` before `verifying` succeeds.
4. A consensus decision records dissenting roles, including an empty list.
5. Output paths are absolute and point to files created or verified in the current run.
6. Every worker report references an approved ministry ticket.
7. Every Skill invocation has exactly one ledger entry for its ticket and input fingerprint.
8. `published` is reachable only from `verified` and only by the finalizer.
9. Every envelope satisfies the permission matrix, dedupe, and hop-limit rules.
10. Paused or cancelled runs create no new worker dispatches.
