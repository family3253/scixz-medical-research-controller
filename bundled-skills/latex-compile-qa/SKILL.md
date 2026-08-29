---
name: "latex-compile-qa"
description: "Compiles LaTeX documents and troubleshoots build errors. Invoke when the user asks to compile LaTeX or fix LaTeX build failures."
---

# LaTeX Compile QA

Use this skill to compile LaTeX projects and diagnose common build failures.

## Workflow

- Identify the main .tex entry file
- Run an appropriate compile chain (latexmk or pdflatex/biber/bibtex)
- Inspect logs for errors and propose fixes

## Commands (Windows)

- latexmk -pdf <main>.tex
- pdflatex <main>.tex
- bibtex <main>
- biber <main>
- pdflatex <main>.tex (repeat as needed)

## Common Fixes

- Missing packages: install via TeX distribution or adjust \usepackage
- Undefined citations: run bibtex/biber and recompile
- Missing figures: verify file paths and extensions
