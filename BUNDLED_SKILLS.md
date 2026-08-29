# Bundled companion Skills

This directory records the companion Skills copied into the public SciXZ release. They are kept in separate subdirectories so that users can install only the routes they need.

For the full list of Skills that users must download separately, see [`DOWNLOAD_GUIDE.md`](DOWNLOAD_GUIDE.md).

## Included local-only components

| Component | Role in SciXZ routes | Source / licensing note |
|---|---|---|
| `revise` | Point-by-point response and revision workflow | Local user-provided component; no standalone license file was present in the source snapshot. |
| `find-journal` | Journal-fit ranking and submission cascade | Local user-provided component; journal metrics and policies remain time-sensitive and require site verification. |
| `deterministic-local-file-reading` | Deterministic local-file intake and reader dispatch | Local user-provided component; machine-specific search paths were replaced with generic configured-directory wording. |
| `manage-refs` | Citation-key, CSL, cross-reference, and Zotero workflow | Retains the source `LICENSE.zotero-mcp` and `NOTICE.md` for the relevant component. |

## Public components referenced, not copied

These components have public GitHub sources and are intentionally referenced as dependencies rather than duplicated here: `nature-review-studio`, `academic-paper-reviewer`, `check-reporting`, `verify-refs`, and `sci-manuscript-preflight`. Use the public source or the version pinned by your local Skill catalog.

## Deliberately excluded

- `anthropics-docx`, `anthropics-pdf`, `anthropics-xlsx`, and `anthropics-pptx` because their source metadata explicitly marks them Proprietary.
- User-specific `memory/`, local audit logs, private journal profiles, machine binding registries, manuscript archives, datasets, credentials, tokens, and browser state.
- JANE and iPubMed implementations or credentials. They are external evidence adapters and must be configured at runtime.

## Installation guidance

Treat every subdirectory as an independent Skill package. Install the controller first, then add only the companion components required by the route. If a component has no standalone license declaration, keep it within the repository owner's authorized distribution boundary and do not repackage it as a general-purpose third-party library without confirming authorship and redistribution rights.
