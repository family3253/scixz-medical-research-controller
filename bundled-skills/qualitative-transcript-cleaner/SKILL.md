---
name: qualitative-transcript-cleaner
description: Use when the user wants raw interview transcripts, audio transcriptions, or qualitative conversation records cleaned into structured, analysis-ready text. Make sure to use this whenever the request involves qualitative interviews, verbatim transcripts, speaker labels, NVivo import preparation, timestamp cleanup, filler-word reduction, or preserving emotional pauses while standardizing transcript layout.
---

# Qualitative Transcript Cleaner

## Purpose

Convert messy interview transcripts into clean, structured, analysis-ready dialogue text for qualitative research workflows.

## When to Use

Use this skill whenever the user:
- has raw interview transcription text that needs cleanup
- wants `访谈者` / `受访者` style speaker-label normalization
- needs transcript cleanup before NVivo, MAXQDA, Atlas.ti, or manual coding
- wants timestamps, broken line wraps, or ASR noise removed
- wants filler words reduced without changing the substantive meaning
- needs hesitation or emotional pauses preserved in a readable way

## Core Rule

Remain faithful to the speaker’s meaning.

Do not rewrite substantive content, strengthen claims, or silently improve reasoning. The goal is transcript normalization, not stylistic ghostwriting.

## Cleaning Rules

- Remove obvious ASR noise, duplicate fragments, and accidental line breaks.
- Reduce meaningless filler such as `啊`, `嗯`, `那个` when they do not carry analytic value.
- Preserve pauses, hesitation, or emotional cues when they matter to interpretation.
- Keep speaker turns explicit and consistent.

## Formatting Rule

Prefer a clean dialogue layout such as:

`【访谈者：】`
`【受访者：】`

If the user has a different speaker naming convention, preserve it consistently.

## Workflow

1. Read the raw transcript.
2. Separate speaker turns.
3. Remove timestamps and mechanical noise if not needed.
4. Normalize speaker labels.
5. Lightly clean filler words while preserving meaning and emotion.
6. Output a clean import-ready transcript.

## Response Style

Be faithful, restrained, and structurally clear. The result should feel like a high-quality research transcript, not polished prose.
