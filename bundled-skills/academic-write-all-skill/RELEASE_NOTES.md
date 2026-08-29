# academic-write-all-skill Release Notes

## Release Title

`academic-write-all-skill` - unified academic writing, review, prediction-model appraisal, and research-lifecycle skill

## Summary

This release completes the transition from the earlier `cycwrite` identity into `academic-write-all-skill` and turns the repository into a more complete academic workflow package.

It now combines:
- paper-production routing
- review-project gating
- revision-coach behavior
- research-lifecycle routing from idea discovery to paper planning
- guarded self-update and capability-gap handling
- prediction-model review and appraisal support
- reusable live-routing and adversarial eval prompts
- repository-level smoke testing
- bilingual repository documentation
- one-command install guidance for OpenCode and OpenClaw
- reproducible release packaging

## Highlights

### New public identity
- renamed the published skill to `academic-write-all-skill`
- published at: `https://github.com/family3253/academic-write-all-skill`
- added migration notice in the old `cycwrite-skill` repo

### Expanded academic workflow coverage
- added research-lifecycle mode for:
  - idea discovery
  - novelty-check framing
  - literature-to-gap narrowing
  - experiment/result packaging
  - paper-plan handoff
- preserved paper-production and review-project routing from earlier absorbed skills
- added guarded self-update behavior:
  - bundled references first
  - stronger local skills second
  - external/GitHub learning third
  - explicit borrowed-logic labeling always

### Stronger prediction-model review support
- added a dedicated `Prediction-Model Review Mode`
- added `references/prediction-model-review.md`
- added a native working appraisal frame with:
  - TRIPOD-like reporting checks
  - PROBAST-like bias/applicability warning scan
  - CHARMS-like extraction discipline
- synced authoritative external standards guidance for:
  - `TRIPOD`
  - `TRIPOD+AI`
  - `PROBAST`
  - `PROBAST+AI`
- kept `CHARMS-style` wording conservative because no confirmed official `CHARMS+AI` variant was found
- added templates:
  - `assets/templates/prediction_model_evidence_matrix.csv`
  - `assets/templates/prediction_model_appraisal_checklist.md`

### Better installability
- OpenCode one-command install:
  - `npx skills add family3253/academic-write-all-skill -a opencode`
- OpenClaw one-command install:
  - `npx skills add family3253/academic-write-all-skill -a openclaw`
- renamed Windows runtime launchers to:
  - `bootstrap_academic_write_all_skill_runtime.bat`
  - `academic-write-all-skill.bat`

### Documentation and release polish
- rewrote `README.md` into Chinese/English bilingual format
- added packaging instructions to the README
- added `scripts/package_release.py` for reproducible release builds
- generated release artifacts under `dist/`

### Testing improvements
- expanded `evals/evals.json` beyond basic routing into:
  - guarded self-update tests
  - prediction-model review tests
  - adversarial external-fallback tests
- added `scripts/smoke_test.py` for repeatable repository smoke tests
- verified live harness routing for:
  - outline-only behavior
  - revision-coach behavior
  - review-output downgrade behavior
  - guarded self-update behavior
  - prediction-model review mode
  - adversarial TRIPOD/PROBAST/CHARMS external fallback behavior

## Verification Performed

### Harness-level behavior checks
Confirmed correct routing or controlled downgrade on these prompt families:
- outline-only prompt
- revision-coach prompt
- weak-corpus review downgrade prompt
- guarded self-update prompt
- adult MDR-GNB clinical prediction model review prompt
- adversarial external fallback prompt using TRIPOD / PROBAST / CHARMS-style methodology

### Repository/runtime checks
Confirmed passing:
- `python -m compileall scripts`
- `python scripts/awas_cli.py --help`
- `python scripts/smoke_test.py`
- project scaffold initialization
- project status inspection
- gate report generation
- release package generation via `python scripts/package_release.py --version 20260318`

### Packaged artifacts
Generated successfully:
- `dist/academic-write-all-skill-20260318.zip`
- `dist/academic-write-all-skill-20260318.zip.sha256`

## Migration Notes

If you previously used the old `cycwrite` repository or OpenCode install directory:
- switch to `academic-write-all-skill`
- reinstall using the new repo name
- use the new runtime launcher names in local Windows workflows
- treat the old `cycwrite-skill` repo as a redirect, not the primary update target

## Suggested GitHub Release Body

`academic-write-all-skill` is the new published home for the former `cycwrite` workflow skill.

This release upgrades the project from a writing router into a broader academic workflow router that can handle:
- idea and novelty stages
- literature and review-project stages
- paper drafting and revision stages
- evidence-sensitive downgrade behavior when source support is weak
- prediction-model appraisal using native working structure plus explicit external standards when needed

It also adds bilingual documentation, reusable eval prompts, a smoke-test script, OpenCode/OpenClaw install guidance, renamed Windows launchers, and a reproducible packaging flow.
