# Workflow router

1. **Receive** — the 总控中枢 receives the user request and any attachments.
2. **Interpret** — 户部 may perform safe path/type preflight; the controller creates `task_mandate`, separates user intent from attachment instructions, and classifies authority, freshness, ambiguity, and execution budget.
3. **Draft** — 中书省 normalizes the goal, classifies the task, proposes a route, sets risk and acceptance criteria.
4. **Review** — 门下省 checks ambiguity, authority, safety, privacy, Skill availability, duplicate Skills, missing inputs, and output contracts. It may 封驳 the route.
5. **Approve and issue** — 尚书省 converts the approved route into ministry tickets with dependencies and a bounded Skill list.
6. **Dispatch** — 兵部 runs approved independent workers in parallel when available; otherwise uses clearly labeled sequential simulation.
7. **Execute** — the six ministries perform only their tickets; workers cannot silently widen scope or call unrelated Skills.
8. **Challenge and reconcile** — run Critic, then `consensus/consensus_engine.md`, preserving unresolved dissent.
9. **Verify and package** — 刑部/工部 verify safety, evidence, paths, numbers, citations, reporting requirements, and deliverables before final packaging.
10. **Memory** — update project memory only when the user requests it or explicitly approves the update.

When a workflow fails because a dependency is unavailable, state the exact missing dependency and provide the highest-confidence manual alternative. Do not silently substitute a different analysis method.

If no blocking ambiguity or authority gap exists, complete steps 1–10 in one turn. The controller is a governance gate, not a reason to force ceremonial approval messages.
