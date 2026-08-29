/**
 * `auto_cite` without a key: the plugin itself finds a real paper for each
 * citation point using the free public search APIs (Semantic Scholar, PubMed
 * fallback, OpenAlex last resort), inserts numbered markers, and formats the
 * reference list (IEEE, APA, Vancouver, Nature, numbered) plus BibTeX.
 * Matching is local keyword overlap, not the paid service's model — good
 * matches, humbler ranking.
 * @module litmesh/tools/auto-cite-local
 */

import { compact } from '../paper.js'
import type { Paper } from '../paper.js'
import type { Runtime } from '../runtime.js'
import { runSemanticSearch } from './semantic-scholar.js'
import { runPubmedSearch } from './pubmed.js'
import { runOpenalexSearch } from './openalex.js'

/** Direct mode issues one platform search per citation point; bound the total. */
export const DIRECT_AUTOCITE_CAP = 30
/** Pause between platform searches, to stay friendly to the free rate limits. */
const SEARCH_PACE_MS = 400
const CANDIDATES_PER_POINT = 5

/** What one inserted marker replaced: a sentence end, or a `[CITE]` placeholder. */
interface CitePoint {
  /** Offset in the original text where the marker is inserted / the placeholder starts. */
  at: number
  /** Length of the replaced placeholder (manual mode); 0 for insertion at a sentence end. */
  replaced: number
  /** The sentence text driving the search (auto mode picks it; manual mode the containing sentence). */
  sentence: string
}

const STOPWORDS = new Set([
  'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'else', 'when', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'into', 'through', 'during', 'before', 'after', 'to', 'from', 'in', 'on', 'off', 'over', 'under', 'again', 'further', 'once', 'here', 'there', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just', 'should', 'now', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'would', 'could', 'might', 'must', 'shall', 'may', 'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their', 'we', 'our', 'you', 'your', 'he', 'she', 'his', 'her', 'they', 'which', 'who', 'whom', 'what', 'where', 'why', 'how', 'also', 'however', 'therefore', 'thus', 'hence', 'using', 'used', 'use', 'based', 'via', 'among', 'between', 'within', 'without', 'toward', 'towards', 'showed', 'shown', 'shows', 'show', 'study', 'studies', 'result', 'results', 'approach', 'method', 'methods', 'propose', 'proposed', 'paper', 'work', 'works', 'well', 'many', 'much', 'like', 'such',
])

/** Split text into sentences with their offsets, keeping the text verbatim. */
export function splitSentences(text: string): Array<{ start: number; end: number; text: string }> {
  const out: Array<{ start: number; end: number; text: string }> = []
  const re = /[^.!?\n]+[.!?]+["')\]]*\s*/g
  let m: RegExpExecArray | null
  while ((m = re.exec(text)) !== null) {
    const body = m[0]!
    const trimmedLength = body.trimEnd().length
    if (trimmedLength === 0) continue
    out.push({ start: m.index, end: m.index + trimmedLength, text: body.slice(0, trimmedLength) })
  }
  // A trailing fragment without terminal punctuation is still a sentence.
  const consumed = out.length > 0 ? out[out.length - 1]!.end : 0
  const tail = text.slice(consumed).trim()
  if (tail.length > 0) out.push({ start: text.indexOf(tail, consumed), end: text.indexOf(tail, consumed) + tail.length, text: tail })
  return out
}

/** Content words of a text: lowercase alphanumeric, no stopwords. */
export function tokenize(text: string): string[] {
  return text.toLowerCase().replace(/[^a-z0-9一-鿿]+/g, ' ').split(' ').filter((w) => w.length >= 3 && !STOPWORDS.has(w))
}

/** Salient query terms of one sentence: most frequent content words, longest first. */
export function sentenceKeywords(sentence: string, field?: string | undefined, max = 6): string {
  const counts = new Map<string, number>()
  for (const word of tokenize(sentence)) counts.set(word, (counts.get(word) ?? 0) + 1)
  const ranked = [...counts.entries()].sort((a, b) => b[1] - a[1] || b[0].length - a[0].length).map(([w]) => w)
  const picked = ranked.slice(0, max)
  const fieldTerms = field !== undefined ? tokenize(field).slice(0, 2).filter((t) => !picked.includes(t)) : []
  return [...picked, ...fieldTerms].join(' ')
}

/** How strongly a sentence and a paper belong together: 0 (none) to ~1+ (strong). */
export function matchScore(sentence: string, paper: Paper): number {
  const sentenceTokens = new Set(tokenize(sentence))
  if (sentenceTokens.size === 0) return 0
  const titleTokens = tokenize(paper.title)
  const abstractTokens = paper.abstract !== undefined ? tokenize(paper.abstract) : []
  const titleHits = titleTokens.filter((t) => sentenceTokens.has(t)).length
  const abstractHits = abstractTokens.filter((t) => sentenceTokens.has(t)).length
  const titleDenominator = Math.max(titleTokens.length, 1)
  const titleScore = (titleHits / titleDenominator) * 0.7 + (titleHits >= 2 ? 0.2 : 0)
  const abstractScore = Math.min(abstractHits / 12, 0.4)
  return titleScore + abstractScore
}

/** Pick the citation points for auto mode: the most content-dense sentences, spread over the text. */
export function pickAutoPoints(text: string, wanted: number): CitePoint[] {
  const sentences = splitSentences(text)
  const scored = sentences
    .map((s, i) => {
      const tokens = tokenize(s.text)
      const properNouns = (s.text.match(/\b[A-Z][a-z]{2,}/g) ?? []).filter((w) => !STOPWORDS.has(w.toLowerCase())).length
      const lengthFit = s.text.length >= 40 && s.text.length <= 500 ? 1 : 0
      return { i, score: tokens.length + properNouns * 2 + lengthFit * 3 }
    })
    .sort((a, b) => b.score - a.score)
    .slice(0, wanted)
    .map((s) => s.i)
    .sort((a, b) => a - b)
  return scored.map((i) => ({ at: sentences[i]!.end, replaced: 0, sentence: sentences[i]!.text }))
}

/** The `[CITE]` placeholders of manual mode become the points. */
export function pickManualPoints(text: string): CitePoint[] {
  const points: CitePoint[] = []
  const sentences = splitSentences(text)
  const re = /\[CITE\]/g
  let m: RegExpExecArray | null
  while ((m = re.exec(text)) !== null) {
    const at = m.index
    const containing = sentences.find((s) => at >= s.start && at <= s.end) ?? sentences.find((s) => s.start > at)
    points.push({ at, replaced: m[0]!.length, sentence: containing?.text.replace(/\[CITE\]/g, '').trim() ?? text.slice(Math.max(0, at - 200), at).trim() })
  }
  return points
}

/** Split a display name into initials and surname, Western order assumed. */
function nameParts(display: string): { initials: string; surname: string } {
  const parts = display.replace(/\s+/g, ' ').trim().split(' ')
  const surname = parts.length > 1 ? parts[parts.length - 1]! : display
  const initials = parts.slice(0, -1).map((p) => `${p[0]!.toUpperCase()}.`).join(' ')
  return { initials, surname }
}

function isPreprint(paper: Paper): boolean {
  return paper.source === 'arxiv' || paper.source === 'biorxiv' || paper.source === 'medrxiv' || /arxiv|biorxiv|medrxiv|preprint/i.test(paper.venue ?? '')
}

function isConference(paper: Paper): boolean {
  return /conference|proceedings|symposium|workshop|neurips|icml|iclr|cvpr|siggraph|kdd|www '?\d|acl|emnlp/i.test(paper.venue ?? '')
}

/** Format one author as `F. M. Surname` (IEEE / Nature style). */
function authorIEEE(display: string): string {
  const { initials, surname } = nameParts(display)
  return initials.length > 0 ? `${initials} ${surname}` : surname
}

/** Format one author as `Surname, F. M.` (APA style). */
function authorAPA(display: string): string {
  const { initials, surname } = nameParts(display)
  return initials.length > 0 ? `${surname}, ${initials}` : surname
}

/** Format one author as `Surname FM` (Vancouver style). */
function authorVancouver(display: string): string {
  const { initials, surname } = nameParts(display)
  return initials.length > 0 ? `${surname} ${initials.replace(/[. ]/g, '')}` : surname
}

function listIEEE(authors: readonly string[]): string {
  if (authors.length === 0) return 'Unknown authors'
  if (authors.length === 1) return authorIEEE(authors[0]!)
  if (authors.length === 2) return `${authorIEEE(authors[0]!)} and ${authorIEEE(authors[1]!)}`
  if (authors.length <= 6) return `${authors.slice(0, -1).map(authorIEEE).join(', ')}, and ${authorIEEE(authors[authors.length - 1]!)}`
  return `${authorIEEE(authors[0]!)} et al.`
}

function listAPA(authors: readonly string[]): string {
  if (authors.length === 0) return 'Unknown authors'
  const formatted = authors.slice(0, 10).map(authorAPA)
  if (authors.length === 1) return formatted[0]!
  if (authors.length > 10) return `${formatted.join(', ')} et al.`
  return `${formatted.slice(0, -1).join(', ')}, & ${formatted[formatted.length - 1]!}`
}

function listVancouver(authors: readonly string[]): string {
  if (authors.length === 0) return 'Unknown authors'
  if (authors.length <= 6) return authors.map(authorVancouver).join(', ')
  return `${authors.slice(0, 3).map(authorVancouver).join(', ')} et al.`
}

export type CitationStyle = 'ieee' | 'apa' | 'vancouver' | 'nature' | 'numbered'

/**
 * Format one reference list entry in the requested style.
 * @param style - citation style; `numbered` and `ieee` share the bracket form.
 * @param paper - the matched paper.
 * @param number - the citation number.
 */
export function formatReference(style: CitationStyle, paper: Paper, number: number): string {
  const year = paper.year !== undefined ? String(paper.year) : 'n.d.'
  const venue = paper.venue ?? ''
  const doiUrl = paper.doi !== undefined ? `https://doi.org/${paper.doi}` : paper.url
  switch (style) {
    case 'apa':
      return `${listAPA(paper.authors)} (${year}). ${paper.title}.${venue.length > 0 ? ` ${venue}.` : ''}${doiUrl !== undefined ? ` ${doiUrl}` : ''}`
    case 'vancouver':
      return `${listVancouver(paper.authors)} ${paper.title}.${venue.length > 0 ? ` ${venue}.` : ''} ${year}.${paper.doi !== undefined ? ` doi: ${paper.doi}.` : ''}`
    case 'nature': {
      const authors = paper.authors.length > 1
        ? `${paper.authors.slice(0, -1).map(authorIEEE).join(', ')} & ${authorIEEE(paper.authors[paper.authors.length - 1]!)}`
        : listIEEE(paper.authors)
      return `${authors} ${paper.title} ${venue} ${year}${paper.doi !== undefined ? `; doi:${paper.doi}` : ''}.`
    }
    case 'ieee':
    case 'numbered':
    default:
      return `[${number}] ${listIEEE(paper.authors)}, "${paper.title},"${venue.length > 0 ? ` ${venue},` : ''} ${year}.${paper.doi !== undefined ? ` doi: ${paper.doi}.` : ''}`
  }
}

/** Escape BibTeX brace content minimally. */
function bibtexEscape(text: string): string {
  return text.replace(/[{}]/g, (c) => `\\${c}`).replace(/\s+/g, ' ').trim()
}

/** One `@article` entry for a paper. */
export function bibtexEntry(paper: Paper, number: number): string {
  const author = paper.authors.map((a) => { const { initials, surname } = nameParts(a); return initials.length > 0 ? `${surname}, ${initials}` : surname }).join(' and ')
  const lines: string[] = [`@article{ref${number},`]
  lines.push(`  title = {${bibtexEscape(paper.title)}}`)
  if (author.length > 0) lines.push(`  author = {${bibtexEscape(author)}}`)
  if (paper.venue !== undefined) lines.push(`  journal = {${bibtexEscape(paper.venue)}}`)
  if (paper.year !== undefined) lines.push(`  year = {${paper.year}}`)
  if (paper.doi !== undefined) lines.push(`  doi = {${paper.doi}}`)
  lines.push(`  url = {${paper.url}}`)
  lines.push('}')
  return lines.join('\n')
}

/** Arguments of the local pipeline, mirroring the tool schema's knobs. */
export interface LocalAutoCiteArgs {
  text: string
  mode?: 'auto' | 'manual' | undefined
  minCitations?: number | undefined
  field?: string | undefined
  yearPreference?: number | undefined
  excludePreprints?: boolean | undefined
  excludeConferences?: boolean | undefined
  citationStyle?: CitationStyle | undefined
  preferredVenues?: readonly string[] | undefined
}

/** Result of the local pipeline, matching the `auto_cite` output schema. */
export interface LocalAutoCiteResult {
  annotatedText: string
  references: Array<{ number: number; formatted: string; title?: string; year?: number; doi?: string; url?: string; venue?: string; citedBy?: number; matchReason: string; relevanceScore?: number }>
  bibtex: string
  stats: { citationCount: number; searchCount: number; processingTime: number }
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => { setTimeout(resolve, ms) })
}

/**
 * Run the key-free auto-cite pipeline.
 * @param runtime - plugin runtime (search tools run in direct mode).
 * @param args - the validated tool arguments.
 * @param signal - cancellation.
 * @param agent - executing agent, threaded to the platform searches.
 * @returns the annotated text, the reference list, BibTeX, and stats.
 */
export async function runLocalAutoCite(runtime: Runtime, args: LocalAutoCiteArgs, signal: AbortSignal | undefined, agent: object | undefined): Promise<LocalAutoCiteResult> {
  const started = Date.now()
  const style: CitationStyle = args.citationStyle ?? 'ieee'
  const wanted = Math.min(Math.max(1, args.minCitations ?? 10), DIRECT_AUTOCITE_CAP)
  const all = args.mode === 'manual' ? pickManualPoints(args.text) : pickAutoPoints(args.text, wanted)
  const points = all.slice(0, DIRECT_AUTOCITE_CAP)
  const clamped = all.length > DIRECT_AUTOCITE_CAP

  // Process points from the end so earlier offsets stay valid while inserting.
  const chosen: Array<{ point: CitePoint; paper: Paper; score: number } | undefined> = new Array(points.length).fill(undefined)
  const seen = new Map<string, Paper>() // identity -> paper, for reuse across points
  let searches = 0

  const searchOnce = async (query: string): Promise<Paper[]> => {
    // Semantic Scholar first (richest metadata); PubMed next for biomedical
    // wording; OpenAlex as the last resort, because the unauthenticated S2
    // pool is shared and can sit at 429 for minutes.
    searches += 1
    const s2 = await runSemanticSearch(runtime, { query, limit: CANDIDATES_PER_POINT }, signal, agent).catch(() => undefined)
    if (s2 !== undefined && s2.papers.length > 0) return s2.papers
    searches += 1
    const pubmed = await runPubmedSearch(runtime, { query, limit: CANDIDATES_PER_POINT }, signal, agent).catch(() => undefined)
    if (pubmed !== undefined && pubmed.papers.length > 0) return pubmed.papers
    searches += 1
    const openalex = await runOpenalexSearch(runtime, { query, wanted: CANDIDATES_PER_POINT }, signal).catch(() => undefined)
    return openalex?.papers ?? []
  }

  for (let i = 0; i < points.length; i++) {
    signal?.throwIfAborted()
    const point = points[i]!
    const query = sentenceKeywords(point.sentence, args.field)
    if (query.trim().length === 0) continue
    if (i > 0) await delay(SEARCH_PACE_MS)
    const candidates = await searchOnce(query)
    let best: { paper: Paper; score: number } | undefined
    for (const paper of candidates) {
      if (args.excludePreprints === true && isPreprint(paper)) continue
      if (args.excludeConferences === true && isConference(paper)) continue
      let score = matchScore(point.sentence, paper)
      if (args.yearPreference !== undefined && paper.year !== undefined) score -= Math.min(Math.abs(paper.year - args.yearPreference) * 0.02, 0.2)
      if (args.preferredVenues !== undefined) {
        const venue = paper.venue?.toLowerCase() ?? ''
        if (args.preferredVenues.some((v) => venue.includes(v.toLowerCase()))) score += 0.25
      }
      if (score >= 0.3 && (best === undefined || score > best.score)) best = { paper, score }
    }
    if (best !== undefined) {
      chosen[i] = { point, paper: best.paper, score: best.score }
      const key = best.paper.doi ?? best.paper.title.toLowerCase()
      seen.set(key, best.paper)
    } else {
      // Reuse an earlier match when the same wording returns nothing new.
      const reused = [...seen.values()].find((paper) => matchScore(point.sentence, paper) >= 0.3)
      if (reused !== undefined) chosen[i] = { point, paper: reused, score: matchScore(point.sentence, reused) }
    }
  }

  // Number the unique papers in first-appearance order.
  const numbers = new Map<Paper, number>()
  const ordered: Paper[] = []
  for (const hit of chosen) {
    if (hit === undefined) continue
    if (!numbers.has(hit.paper)) {
      numbers.set(hit.paper, ordered.length + 1)
      ordered.push(hit.paper)
    }
  }

  let annotated = args.text
  for (let i = points.length - 1; i >= 0; i--) {
    const hit = chosen[i]
    if (hit === undefined) continue
    const marker = `[${numbers.get(hit.paper)}]`
    const at = hit.point.at
    annotated = hit.point.replaced > 0
      ? annotated.slice(0, at) + marker + annotated.slice(at + hit.point.replaced)
      : annotated.slice(0, at) + ' ' + marker + annotated.slice(at)
  }

  const references = ordered.map((paper, i) => compact({
    number: i + 1,
    formatted: formatReference(style, paper, i + 1),
    title: paper.title,
    year: paper.year,
    doi: paper.doi,
    url: paper.url,
    venue: paper.venue,
    citedBy: paper.citationCount,
    matchReason: 'key-free local matching: query from the sentence, best Semantic Scholar / PubMed / OpenAlex hit by title and abstract keyword overlap',
    relevanceScore: Math.round(Math.max(...chosen.filter((c) => c !== undefined && c.paper === paper).map((c) => c!.score), 0) * 100) / 100,
  }))

  const citations = ordered.length
  const warning = citations === 0
    ? undefined
    : clamped || citations < Math.min(wanted, points.length)
      ? `key-free mode: matched ${citations} of ${points.length} citation point(s)${clamped ? ` (capped at ${DIRECT_AUTOCITE_CAP} points)` : ''}; local keyword matching is humbler than the paid Auto-Cite service`
      : undefined
  if (warning !== undefined && references.length > 0) {
    // Fold the note into the first reference's matchReason so the schema stays closed.
    references[0] = { ...references[0]!, matchReason: `${references[0]!.matchReason}. ${warning}` }
  }

  return {
    annotatedText: annotated,
    references,
    bibtex: ordered.map((paper, i) => bibtexEntry(paper, i + 1)).join('\n\n'),
    stats: { citationCount: citations, searchCount: searches, processingTime: (Date.now() - started) / 1000 },
  }
}
