# Observability and recovery

The controller must make long or multi-agent work inspectable and recoverable without exposing hidden reasoning.

## Logs

Maintain three append-only views:

```yaml
flow_log:
  - at: timestamp
    from: 中书省
    to: 门下省
    event: submitted_for_review
    ticket_id: null
    summary: "Route R-001 submitted"

progress_log:
  - at: timestamp
    role: statistics
    ticket_id: T-004
    status: running
    summary: "Checking Cox assumptions and missingness"
    cost_or_budget_used: null

error_log:
  - at: timestamp
    ticket_id: T-004
    category: timeout
    message: "Worker exceeded the bounded wait"
    recovery: retrying
```

Record decisions, statuses, artifacts, and evidence references—not hidden chain-of-thought or raw credentials.

## User intervention

The run supports:

- `pause` — preserve current state and stop new dispatches;
- `resume` — restore the previous active state and recheck authority/dependencies;
- `cancel` — stop remaining tickets and mark outputs partial; destructive cleanup requires its own authority;
- `advance` — allowed only when gate invariants and dependencies already pass;
- `status` — return a concise view of active department, tickets, blockers, and verified outputs.

## Stall recovery

Use condition-based progress, not arbitrary optimism:

1. A ticket with no progress becomes `stalled` after the configured threshold.
2. Retry once using the same ticket and a new ledger retry record.
3. If still stalled, escalate to 门下省 for review of the plan or to 尚书省 for reassignment, depending on the failing stage.
4. If recovery fails, roll back to the last verified controller snapshot and mark the route `DEGRADED_ROUTE` or `BLOCKED`.
5. Never roll back external side effects as if they were local files; report irreversible state explicitly.

## Snapshot

Create a controller snapshot at `APPROVED_FOR_EXECUTION`, after each completed parallel wave, and before publication. A snapshot stores state, approved route, tickets, ledger, evidence versions, and verified outputs. It does not copy secrets or confidential raw inputs unnecessarily.
