# SciXZ central controller

The central controller is the only first responder for an explicit `/scixz` request. It interprets the user's intent, creates a task mandate, sends it through the three-department gate, and only then authorizes Skill or Agent execution.

The controller does not replace domain expertise. It governs when domain expertise is allowed to run, what evidence it may see, what artifact it may write, and how its result is reviewed.

Read in this order:

1. `command_interpreter.md`
2. `three_departments_six_ministries.md`
3. `skill_decision_engine.md`
4. `permission_matrix.md`
5. `state_machine.md`
6. `observability_recovery.md`
