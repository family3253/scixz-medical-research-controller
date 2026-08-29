# Permission matrix

SciXZ uses explicit call permissions so an Agent cannot bypass review, create a private execution chain, or trigger a message loop.

| Sender | May request | May not request |
|---|---|---|
| `总控中枢` | 中书省 intake; user clarification; final publication | domain execution without an approved route |
| `中书省` | 门下省 review; read-only feasibility consultation from 尚书省 | 六部 execution or final publication |
| `门下省` | return to 中书省; approve to 尚书省; request evidence clarification | execute a domain Skill |
| `尚书省` | issue tickets to 六部; request status; assemble completion barrier | rewrite the approved mandate |
| `六部` | report to 尚书省; request a controller-approved transfer | call another ministry or add a Skill directly |
| `Critic` | challenge worker reports through the collaboration barrier | execute new work or alter evidence |
| `Consensus/政事堂` | decision record to Verifier | reopen scope, dispatch Skills, or publish |
| `Verifier` | verification result to Finalizer or revision request to 尚书省 | silently fix scientific content |
| `Finalizer` | verified artifact to 总控中枢 | publish unverified or unauthorized content |

## Enforcement fields

Every envelope carries:

```yaml
sender_role: 兵部
recipient_role: 尚书省
ticket_id: T-001
mandate_id: scixz-...
hop_count: 2
max_hops: 8
dedupe_key: sha256(mandate_id + ticket_id + message_type + payload_fingerprint)
```

- Reject a sender/recipient pair absent from the matrix.
- Reject a message whose ticket does not authorize its purpose.
- Reject a duplicate `dedupe_key` unless it is an explicit retry record.
- Stop routing when `hop_count >= max_hops`; escalate to 尚书省 or the user instead of allowing a loop.
- A ministry-to-ministry collaboration request returns to 尚书省 for transfer. Workers never form an ungoverned side channel.

## Isolation

Each worker receives a scoped role context, immutable evidence references, an authorized Skill allowlist, and a per-run scratch namespace. Do not share raw credentials, unrelated conversation history, mutable project memory, or another worker's private scratch state. Shared outputs move through explicit artifacts and envelopes.
