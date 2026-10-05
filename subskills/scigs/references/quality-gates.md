# Quality Gates

`READY` requires all of these:

1. Every mandatory journal rule is supported by current official evidence.
2. The content digest is unchanged except for explicitly approved administrative/reference actions.
3. Citation-to-bibliography integrity passes, or a journal-approved exception is documented.
4. Blinding/privacy checks pass when applicable.
5. Figures, tables, and supplements are reconciled.
6. The final DOCX renders to PDF/page images and every page is visually inspected.
7. The package contains only required files and has a manifest.
8. `FORMAT_CHANGE_LOG.md` records sources, actions, checks, blockers, and manual steps.

Missing renderer, missing evidence, unresolved conflicts, identity findings, or unexpected scientific-text changes are `BLOCKED`, not “probably ready.”
