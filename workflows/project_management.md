# Project and reproducibility workflow

## Entry and scope

Use for research project initialization, status, memory, reproducibility, release, and submission-package synchronization. It does not update project memory or delete artifacts without approval.

## Inputs

Require project path or identifier, canonical manuscript/data locations, current phase, owners, deadlines, and desired status/checklist output.

## Route

Controller → 中书省 defines project objective and boundaries → 户部 checks paths/provenance → 尚书省 ticket. Primary: `manage-project`. Supporting: `version-dataset`, `sync-submission`, `verification`, and `task-status`.

## Outputs

Project manifest, phase status, risks/blockers, timeline/checklist, dataset/version fingerprints, and submission drift report when requested.

## Verification

Check that paths exist, memory facts are user-approved, versions are reproducible, and status claims are supported by files or logs.

## Failure/fallback

If a project is not initialized, create a plan or manifest without pretending analysis occurred. If a path is ambiguous, ask one focused clarification.
