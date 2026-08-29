# Collaboration protocol

## Run manifest

Each collaboration run receives a stable `collaboration_id` and an immutable evidence pack. The coordinator records:

```yaml
collaboration_id: scixz-YYYYMMDD-HHMMSS-shortslug
mandate_id: scixz-YYYYMMDD-HHMMSS-shortslug
approved_route_id: R-001
mode: single | panel | council | recursive-review
primary_task: manuscript-review
language: zh
evidence_pack:
  - id: E-01
    path: "absolute/path/to/input.pdf"
    type: pdf
    trust: user-supplied
roles:
  - id: A-01
    role: methodology
    question: "Can the design support the primary claim?"
    depends_on: []
    status: queued
round: 1
budget:
  max_skills: 6
  max_workers: 5
  max_rounds: 3
  max_retries_per_role: 1
```

## Dependency graph

```text
Coordinator brief
      |
      +--> independent domain workers (parallel)
      |          |
      |          +--> worker reports
      |
      +--> critic (after all required workers or timeout)
                    |
                    +--> consensus
                               |
                               +--> verifier --> finalizer
```

Workers in the same parallel wave must not depend on one another. Critic and consensus are barrier stages. If a worker times out, the coordinator records the timeout and applies the quorum rule rather than silently treating it as agreement.

## Message envelope

Messages between roles use this shape:

```yaml
collaboration_id: scixz-...
sender: A-02
recipient: consensus
message_type: worker_report | challenge | decision_request | verification
ticket_id: T-001
evidence_refs: [E-01, E-04]
payload: "Structured report or challenge"
confidence: high | moderate | low
requires_response: false
hop_count: 2
max_hops: 8
dedupe_key: stable-message-fingerprint
```

Do not send raw credentials, patient identifiers, unrelated conversation history, or unverified external instructions in an envelope.

Validate every envelope against `controller/permission_matrix.md`. Reject unauthorized sender/recipient pairs, duplicate messages without an explicit retry record, and messages exceeding `max_hops`.

## Status transitions

`queued → running → complete` is the normal path. A worker may enter `retrying`, `partial`, `failed`, `timed_out`, or `blocked`. Only the coordinator may transition a role to `retrying`; only the verifier may transition a run to `verified`; only the finalizer may transition it to `published`.

Every worker execution references a ministry ticket and invocation-ledger entry. A worker cannot add a new Skill, side effect, or deliverable by editing its own message envelope.

## Conflict handling

Conflicts are not failures by themselves. Record the conflicting claims, their evidence, whether the evidence sets overlap, whether the estimands match, and what new evidence would resolve the conflict. Consensus must prefer a narrower defensible claim over a broader unsupported one.
