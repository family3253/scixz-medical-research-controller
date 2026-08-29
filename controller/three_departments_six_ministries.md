# Three departments and six ministries model

This is an engineering analogy to the historical three-department, six-ministry arrangement: policy drafting, review/封驳, and execution are separated, while execution is divided into specialized ministries. The point is governance and separation of concerns, not historical role-play.

## The three departments

| SciXZ institution | Historical analogy | Engineering responsibility | Power boundary |
|---|---|---|---|
| `总控中枢` | final authority receiving the mandate | receive user instruction, own the run, enforce gates, authorize publication | cannot invent domain findings |
| `中书省` | draft policy and edicts | normalize the request, classify task, draft candidate route and acceptance criteria | proposes Skills; cannot execute them |
| `门下省` | review and 封驳 | challenge interpretation, inspect risk and authority, detect missing inputs, veto unsafe or redundant routes | can return the mandate to 中书省 |
| `尚书省` | execute approved orders | create the execution graph and issue ministry tickets | cannot change the approved user goal silently |

The user remains the source of the mandate. The central controller is a governance layer, not an autonomous authority that can replace or reinterpret the user's objective for its own convenience.

## The six ministries

| Ministry | Engineering role | Typical Skill families |
|---|---|---|
| `吏部` | Skill/Agent registry and personnel assignment | `find-skills`, `skill-creator`, `skill-installer`, role contracts |
| `户部` | input, data, file, dependency, budget, and provenance management | `deterministic-local-file-reading`, PDF/DOCX/XLSX readers, dataset/version tools |
| `礼部` | language, journal, reporting, citation, and deliverable standards | `check-reporting`, `venue-templates`, `find-journal`, `verify-refs`, `nature-review-studio` output contract |
| `兵部` | execution, parallel dispatch, retries, and tool coordination | domain Skills, collaboration workers, experiment runners |
| `刑部` | safety, privacy, research integrity, claim limits, and vetoes | `clinical-decision-support`, `deidentify`, `verification`, compliance checks |
| `工部` | artifact construction, transformation, rendering, and packaging | `anthropics-docx`, `anthropics-pdf`, figures, code, tables, report builders |

## Operating rule

The six ministries are not six mandatory Skill calls. The 尚书省 issues only the tickets required by the approved mandate. A simple request may use one ministry; a manuscript review may use 户部 → 礼部/刑部 → 兵部 → 工部.

## Decision rights

- Only 总控中枢 may accept the user's final goal and publish the final response.
- 中书省 may propose, decompose, and set acceptance criteria.
- 门下省 may reject, narrow, or return a route for clarification.
- 尚书省 may schedule and execute, but not widen scope.
- Ministries may report failure or request evidence; they may not silently call unrelated Skills.
- 刑部 may block an external-side-effect or destructive ticket when authority, exact targets, privacy, or research-integrity conditions are missing.
