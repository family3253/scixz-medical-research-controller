# Controller state machine

```text
RECEIVED
  ↓
INTERPRETED
  ↓
DRAFTED_BY_ZHONGSHU
  ↓
REVIEWED_BY_MENXIA ──封驳──> ROUTE_VETOED
  │                              ├──> NEEDS_CLARIFICATION
  │                              └──> ABORTED
  ↓
APPROVED_FOR_EXECUTION
  ├──授权不足──> AWAITING_USER_APPROVAL
  ↓
DISPATCHED_BY_SHANGSHU
  ↓
MINISTRIES_RUNNING
  ├──Skill 不可用──> DEGRADED_ROUTE
  ├──无进展──> STALLED
  ├──用户暂停──> PAUSED ──恢复──> MINISTRIES_RUNNING
  └──用户取消──> CANCELLED
  ↓
CRITIC_REVIEW
  ↓
CONSENSUS_COUNCIL
  ↓
VERIFICATION
  ├──失败──> REVISION_REQUIRED
  ├──无法恢复──> ROLLED_BACK
  └──通过──> PUBLISHED
```

## Invariants

- No domain Skill may run in `RECEIVED`, `INTERPRETED`, or `DRAFTED_BY_ZHONGSHU`.
- `NEEDS_CLARIFICATION` has no execution tickets.
- `AWAITING_USER_APPROVAL` has no external-side-effect or destructive ticket in `running` state.
- `APPROVED_FOR_EXECUTION` contains the approved Skill list, ministry ownership, dependencies, and acceptance criteria.
- `DEGRADED_ROUTE` names the unavailable Skill, approved fallback, and resulting confidence or output limitation.
- `PAUSED` preserves the previous active state and creates no new dispatches until resume.
- `CANCELLED` stops pending work, records the reason, and labels existing outputs partial or verified; it does not erase artifacts automatically.
- `STALLED` follows retry → escalation → snapshot rollback as defined in `observability_recovery.md`.
- `ROLLED_BACK` identifies the restored verified snapshot and any irreversible external effects that remain.
- `PUBLISHED` requires a verified run manifest and explicit unresolved-uncertainty list.
- A failed ministry ticket is not a successful result and cannot be silently omitted.
- Any scope expansion returns to 中书省 and 门下省 instead of being accepted by a worker.
- Non-semantic path existence and file-type preflight may run before approval; content analysis and domain conclusions may not.
- Each execution ticket has exactly one ledger entry keyed by ticket ID and input fingerprint, preventing accidental duplicate invocation.
