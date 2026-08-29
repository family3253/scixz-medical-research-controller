# Banana Slides Design Review and Local Adaptation

This note records the architectural ideas reviewed from `Anionex/banana-slides` and the independent adaptations made in `cycppt`.

## License Boundary

Banana Slides is distributed under AGPL-3.0. This project does not copy Banana Slides source files or transplant its application code. The local changes below are clean-room implementations of general workflow ideas, written for the existing yixue runtime and its non-commercial license.

## Adapted Ideas

### 1. Bounded visual quality-control loop

Generated slide images are inspected against the prompt, plan, evidence, and reference images. A slide may be retried for concrete defects, but the loop stops after three attempts and never silently accepts an unreviewed final image.

The structured review covers:

- readable text
- absence of garbled text
- complete planned layout
- deck and template consistency
- medical evidence preservation
- safe margins
- absence of visual artifacts

### 2. Per-page template binding

The deck keeps a default `deck.style_selector`. Individual slides may add `template_binding` with a page-specific style selector, reference image, descriptive constraints, confidence, and matching reason. Explicit command-line style selection remains the highest-priority override.

### 3. Safer resumable state

Run state, page jobs, and deck manifests use atomic same-directory temporary writes followed by `os.replace`. This reduces the chance of truncated JSON after interruption or process termination.

## Deliberately Not Imported

- the Banana Slides web frontend, database, API server, or desktop application
- provider-specific account and OAuth integrations
- its editable-image extraction implementation
- its AGPL-licensed source code

The local skill remains focused on medical source understanding, evidence-faithful slide generation, and deterministic editable PPTX reconstruction.
