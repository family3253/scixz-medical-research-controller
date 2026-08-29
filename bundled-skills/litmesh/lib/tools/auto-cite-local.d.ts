/**
 * `auto_cite` without a key: the plugin itself finds a real paper for each
 * citation point using the free public search APIs (Semantic Scholar, PubMed
 * fallback, OpenAlex last resort), inserts numbered markers, and formats the
 * reference list (IEEE, APA, Vancouver, Nature, numbered) plus BibTeX.
 * Matching is local keyword overlap, not the paid service's model — good
 * matches, humbler ranking.
 * @module litmesh/tools/auto-cite-local
 */
import type { Paper } from '../paper.js';
import type { Runtime } from '../runtime.js';
/** Direct mode issues one platform search per citation point; bound the total. */
export declare const DIRECT_AUTOCITE_CAP = 30;
/** What one inserted marker replaced: a sentence end, or a `[CITE]` placeholder. */
interface CitePoint {
    /** Offset in the original text where the marker is inserted / the placeholder starts. */
    at: number;
    /** Length of the replaced placeholder (manual mode); 0 for insertion at a sentence end. */
    replaced: number;
    /** The sentence text driving the search (auto mode picks it; manual mode the containing sentence). */
    sentence: string;
}
/** Split text into sentences with their offsets, keeping the text verbatim. */
export declare function splitSentences(text: string): Array<{
    start: number;
    end: number;
    text: string;
}>;
/** Content words of a text: lowercase alphanumeric, no stopwords. */
export declare function tokenize(text: string): string[];
/** Salient query terms of one sentence: most frequent content words, longest first. */
export declare function sentenceKeywords(sentence: string, field?: string | undefined, max?: number): string;
/** How strongly a sentence and a paper belong together: 0 (none) to ~1+ (strong). */
export declare function matchScore(sentence: string, paper: Paper): number;
/** Pick the citation points for auto mode: the most content-dense sentences, spread over the text. */
export declare function pickAutoPoints(text: string, wanted: number): CitePoint[];
/** The `[CITE]` placeholders of manual mode become the points. */
export declare function pickManualPoints(text: string): CitePoint[];
export type CitationStyle = 'ieee' | 'apa' | 'vancouver' | 'nature' | 'numbered';
/**
 * Format one reference list entry in the requested style.
 * @param style - citation style; `numbered` and `ieee` share the bracket form.
 * @param paper - the matched paper.
 * @param number - the citation number.
 */
export declare function formatReference(style: CitationStyle, paper: Paper, number: number): string;
/** One `@article` entry for a paper. */
export declare function bibtexEntry(paper: Paper, number: number): string;
/** Arguments of the local pipeline, mirroring the tool schema's knobs. */
export interface LocalAutoCiteArgs {
    text: string;
    mode?: 'auto' | 'manual' | undefined;
    minCitations?: number | undefined;
    field?: string | undefined;
    yearPreference?: number | undefined;
    excludePreprints?: boolean | undefined;
    excludeConferences?: boolean | undefined;
    citationStyle?: CitationStyle | undefined;
    preferredVenues?: readonly string[] | undefined;
}
/** Result of the local pipeline, matching the `auto_cite` output schema. */
export interface LocalAutoCiteResult {
    annotatedText: string;
    references: Array<{
        number: number;
        formatted: string;
        title?: string;
        year?: number;
        doi?: string;
        url?: string;
        venue?: string;
        citedBy?: number;
        matchReason: string;
        relevanceScore?: number;
    }>;
    bibtex: string;
    stats: {
        citationCount: number;
        searchCount: number;
        processingTime: number;
    };
}
/**
 * Run the key-free auto-cite pipeline.
 * @param runtime - plugin runtime (search tools run in direct mode).
 * @param args - the validated tool arguments.
 * @param signal - cancellation.
 * @param agent - executing agent, threaded to the platform searches.
 * @returns the annotated text, the reference list, BibTeX, and stats.
 */
export declare function runLocalAutoCite(runtime: Runtime, args: LocalAutoCiteArgs, signal: AbortSignal | undefined, agent: object | undefined): Promise<LocalAutoCiteResult>;
export {};
