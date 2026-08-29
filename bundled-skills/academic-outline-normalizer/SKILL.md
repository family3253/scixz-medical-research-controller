---
name: academic-outline-normalizer
description: Use when the user wants messy headings, broken section hierarchy, or a disorganized long academic draft turned into a clean multi-level outline. Make sure to use this whenever the request involves heading normalization, thesis structure cleanup, numbering like 1 / 1.1 / 1.1.1, TOC repair, section hierarchy diagnosis, or rebuilding a paper or dissertation outline without changing the core argument.
---

# Academic Outline Normalizer

## Purpose

Recover a clean, defensible heading hierarchy from a messy academic draft.

## When to Use

Use this skill whenever the user:
- has a long draft with broken or inconsistent heading levels
- wants headings renumbered into academic outline form such as `1 / 1.1 / 1.1.1`
- needs help rebuilding a thesis, dissertation, or paper structure
- says their table of contents is broken or Word heading logic has become chaotic
- wants scattered sections or mini-headings reorganized into a clean outline

## Core Rule

Preserve the core argument while repairing the structure.

Do not silently change the user’s main claims just to make the outline prettier.

## Normalization Rules

- Prefer no more than four heading levels unless the user explicitly requires more.
- Keep sibling sections parallel in granularity.
- Merge or relabel headings that are structurally redundant.
- Flag headings that are actually paragraph topics rather than real sections.

## Default Deliverable

Unless the user asks otherwise, provide:
1. a cleaned hierarchical outline
2. a short diagnosis of the main structure problems
3. optional suggestions for merging or renaming sections

## Workflow

1. Read the long text or heading list.
2. Identify current headings and implied hierarchy.
3. Detect inconsistencies, skips, and over-fragmentation.
4. Rebuild the outline using a clear numbering system.
5. Return the normalized outline and the key fixes.

## Response Style

Be architectural and concise. The output should feel like a clean structure map, not a rewritten manuscript.
