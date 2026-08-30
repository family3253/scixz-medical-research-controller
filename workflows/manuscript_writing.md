# Manuscript-writing workflow

## Entry and scope

Use for outlining, drafting, revising, translating, formatting, or compiling a research manuscript. It does not invent data, results, citations, or unsupported novelty. When the task involves substantive正文 writing, read `references/manuscript_section_depth.md` before drafting; generic fluency polishing alone is not sufficient.

## Inputs

Require study question, evidence/results, target article type, language, journal/template if known, and existing draft or outline. For introduction/discussion strengthening, also require a source manifest or searchable reference set and a section-level claim/evidence map. Missing evidence for a claimed result is blocking for prose that states the result.

Treat target-journal examples as style evidence only. Record what may be learned from them (section order, information density, tense, caption shape, or rhetorical pattern); never reuse their wording, claims, citations, or data as manuscript evidence.

## Route

Controller → 中书省 fixes manuscript purpose, section jobs, and evidence boundary → 门下省 checks claim scope, argument depth, and citation allocation → 尚书省 tickets. Primary: `academic-paper` or `scientific-writing`. Supporting: `research-lit`/`deep-research` for evidence discovery, `bib-search-citation`/`manage-refs` for citation allocation, `verify-refs` for source verification, `academic-paper-reviewer` or `scientific-critical-thinking` for a depth critic, `check-reporting`, and figure/table Skills when required. Do not invoke all supporting Skills by default; select only the tickets needed by the supplied manuscript and section.

## Outputs

Outline or revised manuscript, section briefs, claim–evidence notes, terminology decisions, references used, citation allocation/overlap report for introduction and discussion, unresolved placeholders, and compilation/package status when requested.

## Verification

Check that every quantitative/novelty claim is supported, each paragraph performs its documented job, the introduction forms a problem-to-question chain, the discussion provides finding-to-meaning-to-boundary reasoning, methods match results, figures/tables and citations are consistent, introduction/discussion citation overlap is justified, terminology is stable, and the requested format compiles or renders.

Use a dependency-aware sequence rather than drafting all sections at once:

1. freeze study facts, Methods inputs, terminology, article type, and journal constraints;
2. inventory analyses, tables, figures, panels, denominators, units, tests, and uncertainty;
3. stabilize the outline and section briefs;
4. draft figure legends and Results from the verified evidence map;
5. draft Discussion from findings plus a separate verified comparison-evidence pack;
6. finalize Introduction evidence and problem-to-question logic;
7. derive title, abstract, conclusion, keywords, and highlights from the stable manuscript;
8. run cross-section claim, number, terminology, citation, and length/character-limit checks.

Translation, polishing, and shortening require a change ledger or equivalent check that numbers, negation, modality, causal strength, terminology, citation markers, and paragraph jobs did not drift. Optimizing for AI-detector evasion is not a valid scientific objective.

## Failure/fallback

If results or references are missing, preserve placeholders and list what the user must provide. If compilation fails, report the exact error and do not conceal it with a format change.

## Section-depth execution gate

Before accepting a substantive writing ticket, create a `section_brief` for each requested section. For the introduction and discussion, create a `citation_ledger` and a separate evidence pool where possible. The final handoff must list shared references and a reason for each reuse. A section fails verification when it is merely longer, repeats the introduction in the discussion, uses citation clusters without proposition-level support, or adds a mechanism/causal/novelty claim not anchored to evidence.
