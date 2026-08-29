/**
 * PubMed over the free public NCBI E-utilities (no key, no credits): esearch
 * finds PMIDs, efetch returns the abstract XML, elink walks the citation and
 * similar-article links. The XML is parsed into the same record shape the
 * ai4scholar.net PubMed proxy uses, so `normalizePubmedPaper` is shared.
 * @module litmesh/tools/pubmed-eutils
 */

import { decodeEntities, isRecord } from '../paper.js'
import type { Paper } from '../paper.js'
import type { Ai4ScholarClient, ApiResult } from '../api-client.js'
import { normalizePubmedPaper } from './pubmed.js'

const EUTILS = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'

/**
 * NCBI asks for at most 3 requests per second without an API key. Tool
 * executions fire several eutils calls back to back, so every request is
 * spaced at least `PACE_MS` after the previous one, process-wide.
 */
const PACE_MS = 350
let lastStarted = 0

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => { setTimeout(resolve, ms) })
}

async function pacedFetch(client: Ai4ScholarClient, url: string, options: { signal?: AbortSignal | undefined }): Promise<ApiResult<string>> {
  const now = Date.now()
  const wait = Math.max(0, lastStarted + PACE_MS - now)
  lastStarted = now + wait
  if (wait > 0) await delay(wait)
  return client.fetchText(url, { signal: options.signal })
}

/** Decode entities, then strip inner XML tags (italic titles, superscripts). */
function cleanXml(text: string): string {
  return decodeEntities(text).replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim()
}

/** Result of one esearch: the total hit count and a page of PMIDs. */
export interface EsearchResult {
  total: number
  ids: string[]
}

/**
 * Search PubMed through esearch.
 * @param client - host-agnostic fetch helpers.
 * @param term - PubMed query (field tags and booleans supported).
 * @param options - paging, sort, and a publication-date window (`YYYY`, `YYYY/MM`, `YYYY/MM/DD`).
 * @param signal - cancellation.
 */
export async function eutilsSearch(client: Ai4ScholarClient, term: string, options: { retmax: number; retstart: number; sort?: 'relevance' | 'date' | undefined; minDate?: string | undefined; maxDate?: string | undefined; signal?: AbortSignal | undefined }): Promise<EsearchResult> {
  const query = new URLSearchParams({
    db: 'pubmed',
    term,
    retmode: 'json',
    retmax: String(options.retmax),
    retstart: String(options.retstart),
    sort: options.sort === 'date' ? 'pub_date' : 'relevance',
  })
  // E-utilities requires mindate and maxdate together; widen the missing side.
  if (options.minDate !== undefined || options.maxDate !== undefined) {
    query.set('datetype', 'pdat')
    query.set('mindate', options.minDate ?? '1900/01/01')
    query.set('maxdate', options.maxDate ?? '3000/01/01')
  }
  const res = await pacedFetch(client, `${EUTILS}/esearch.fcgi?${query.toString()}`, { signal: options.signal })
  if (!res.ok) throw new Error(`PubMed search failed: ${res.error}`)
  let body: unknown
  try {
    body = JSON.parse(res.data)
  } catch {
    throw new Error('PubMed search returned a body that is not valid JSON')
  }
  const result = isRecord(body) && isRecord(body.esearchresult) ? body.esearchresult : {}
  const count = typeof result.count === 'string' ? Number.parseInt(result.count, 10) : Number(result.count)
  const ids = Array.isArray(result.idlist) ? result.idlist.filter((id): id is string => typeof id === 'string') : []
  return { total: Number.isFinite(count) ? count : ids.length, ids }
}

/** One parsed `<PubmedArticle>`, in the litmesh proxy's record shape. */
function parseArticle(xml: string): Record<string, unknown> | undefined {
  const pmidMatch = /<PMID[^>]*>(\d+)<\/PMID>/.exec(xml)
  const titleMatch = /<ArticleTitle[^>]*>([\s\S]*?)<\/ArticleTitle>/.exec(xml)
  if (pmidMatch === null || titleMatch === null) return undefined
  const authors: Array<Record<string, string>> = []
  const authorBlock = /<AuthorList[^>]*>([\s\S]*?)<\/AuthorList>/.exec(xml)?.[1] ?? ''
  const authorRe = /<Author[^>]*>([\s\S]*?)<\/Author>/g
  let am: RegExpExecArray | null
  while ((am = authorRe.exec(authorBlock)) !== null) {
    const block = am[1]!
    const last = /<LastName>([\s\S]*?)<\/LastName>/.exec(block)?.[1]
    const fore = /<ForeName>([\s\S]*?)<\/ForeName>/.exec(block)?.[1]
    const collective = /<CollectiveName>([\s\S]*?)<\/CollectiveName>/.exec(block)?.[1]
    const name = collective !== undefined ? cleanXml(collective)
      : last !== undefined ? cleanXml([fore, last].filter((p): p is string => p !== undefined).join(' ')) : undefined
    if (name !== undefined && name.length > 0) authors.push({ name })
  }
  const abstracts: string[] = []
  const abstractRe = /<AbstractText(?:\s+Label="([^"]*)")?[^>]*>([\s\S]*?)<\/AbstractText>/g
  let abm: RegExpExecArray | null
  while ((abm = abstractRe.exec(xml)) !== null) {
    const label = abm[1]
    const text = cleanXml(abm[2]!)
    if (text.length > 0) abstracts.push(label !== undefined && label.toUpperCase() !== 'UNLABELLED' ? `${label}: ${text}` : text)
  }
  const journalTitle = /<Journal>[\s\S]*?<Title>([\s\S]*?)<\/Title>/.exec(xml)?.[1]
  const pubYear = /<JournalIssue[\s\S]*?<PubDate>[\s\S]*?<Year>(\d{4})<\/Year>/.exec(xml)?.[1]
  const pubMonth = /<JournalIssue[\s\S]*?<PubDate>[\s\S]*?<Month>([A-Za-z-]+)<\/Month>/.exec(xml)?.[1]
  const medlineDate = /<PubDate><MedlineDate>([\s\S]*?)<\/MedlineDate><\/PubDate>/.exec(xml)?.[1]
  const pubDate = pubYear !== undefined ? [pubYear, pubMonth].filter((p): p is string => p !== undefined).join(' ') : medlineDate !== undefined ? cleanXml(medlineDate) : undefined
  const doi = /<ArticleId IdType="doi">([^<]+)<\/ArticleId>/.exec(xml)?.[1]
  const pmcid = /<ArticleId IdType="pmc">([^<]+)<\/ArticleId>/.exec(xml)?.[1]
  const mesh: string[] = []
  const meshRe = /<MeshHeading><DescriptorName[^>]*>([^<]+)<\/DescriptorName>/g
  let mm: RegExpExecArray | null
  while ((mm = meshRe.exec(xml)) !== null) mesh.push(cleanXml(mm[1]!))
  const keywords: string[] = []
  const kwRe = /<Keyword[^>]*>([^<]+)<\/Keyword>/g
  let km: RegExpExecArray | null
  while ((km = kwRe.exec(xml)) !== null) keywords.push(cleanXml(km[1]!))
  return {
    pmid: pmidMatch[1]!,
    title: cleanXml(titleMatch[1]!),
    authors,
    abstract: abstracts.length > 0 ? abstracts.join(' ') : undefined,
    journal: journalTitle !== undefined ? { title: cleanXml(journalTitle), pubDate } : undefined,
    pubDate,
    year: pubYear !== undefined ? Number.parseInt(pubYear, 10) : undefined,
    doi: doi !== undefined ? cleanXml(doi) : undefined,
    pmcid,
    meshTerms: mesh,
    keywords,
  }
}

/**
 * Fetch full records for PMIDs through efetch (XML) and normalize them.
 * @param client - host-agnostic fetch helpers.
 * @param ids - PMIDs (at most 200; the caller bounds them).
 * @param signal - cancellation.
 * @returns normalized papers, in id order; unparseable records drop out.
 */
export async function eutilsFetchPapers(client: Ai4ScholarClient, ids: readonly string[], signal: AbortSignal | undefined): Promise<Paper[]> {
  if (ids.length === 0) return []
  const query = new URLSearchParams({ db: 'pubmed', id: ids.join(','), rettype: 'abstract', retmode: 'xml' })
  const res = await pacedFetch(client, `${EUTILS}/efetch.fcgi?${query.toString()}`, { signal })
  if (!res.ok) throw new Error(`PubMed lookup failed: ${res.error}`)
  const papers: Paper[] = []
  const articleRe = /<PubmedArticle>([\s\S]*?)<\/PubmedArticle>/g
  let m: RegExpExecArray | null
  while ((m = articleRe.exec(res.data)) !== null) {
    const record = parseArticle(m[1]!)
    const paper = record !== undefined ? normalizePubmedPaper(record) : undefined
    if (paper !== undefined) papers.push(paper)
  }
  return papers
}

/**
 * Linked PMIDs for one article through elink.
 * @param client - host-agnostic fetch helpers.
 * @param pmid - the seed PMID.
 * @param linkname - `pubmed_pubmed` (similar) or `pubmed_pubmed_citedin` (citing).
 * @param limit - stop after this many link ids.
 * @param signal - cancellation.
 * @returns linked PMIDs excluding the seed itself, link order preserved.
 */
export async function eutilsLinks(client: Ai4ScholarClient, pmid: string, linkname: 'pubmed_pubmed' | 'pubmed_pubmed_citedin', limit: number, signal: AbortSignal | undefined): Promise<string[]> {
  const query = new URLSearchParams({ dbfrom: 'pubmed', id: pmid, linkname, retmode: 'json' })
  const res = await pacedFetch(client, `${EUTILS}/elink.fcgi?${query.toString()}`, { signal })
  if (!res.ok) throw new Error(`PubMed link lookup failed: ${res.error}`)
  let body: unknown
  try {
    body = JSON.parse(res.data)
  } catch {
    return []
  }
  const linksets = isRecord(body) && Array.isArray(body.linksets) ? body.linksets : []
  const first = linksets.find(isRecord)
  if (first === undefined) return []
  const dbs = Array.isArray(first.linksetdbs) ? first.linksetdbs.filter(isRecord) : []
  const links: string[] = []
  for (const db of dbs) {
    if (Array.isArray(db.links)) {
      for (const id of db.links) {
        if (typeof id === 'string' && id !== pmid && !links.includes(id)) {
          links.push(id)
          if (links.length >= limit) return links
        }
      }
    }
  }
  return links
}
