/**
 * OpenAlex (api.openalex.org, free, no key) — the key-free stand-in for
 * Google Scholar: the broadest open scholarly index, with cited-by counts.
 * Google Scholar itself exposes no public API, so direct mode routes
 * `search_google_scholar` here and labels the results `openalex`.
 * @module litmesh/tools/openalex
 */
import { compact, int, isRecord, str } from '../paper.js';
const OPENALEX_API = 'https://api.openalex.org/works';
/** OpenAlex hard per-page ceiling. */
const OPENALEX_PAGE_CAP = 200;
const SOURCE = 'openalex';
/** Rebuild the abstract from OpenAlex's inverted index. */
function abstractFromInverted(value) {
    if (!isRecord(value))
        return undefined;
    const positions = [];
    for (const [word, slots] of Object.entries(value)) {
        if (Array.isArray(slots)) {
            for (const slot of slots) {
                if (typeof slot === 'number' && Number.isInteger(slot))
                    positions.push({ word, index: slot });
            }
        }
    }
    if (positions.length === 0)
        return undefined;
    return positions.sort((a, b) => a.index - b.index).map((p) => p.word).join(' ');
}
/**
 * Normalize one OpenAlex `results[]` record.
 * @param record - untyped work record.
 * @returns the normalized paper, or `undefined` for a record without a title.
 */
export function normalizeOpenalexWork(record) {
    if (!isRecord(record))
        return undefined;
    const title = str(record, 'display_name') ?? str(record, 'title');
    if (title === undefined)
        return undefined;
    const idUrl = str(record, 'id');
    const workId = idUrl !== undefined ? idUrl.replace(/^https?:\/\/openalex\.org\//, '') : undefined;
    const doiUrl = str(record, 'doi');
    const doi = doiUrl !== undefined ? doiUrl.replace(/^https?:\/\/doi\.org\//, '') : undefined;
    const authorships = Array.isArray(record.authorships) ? record.authorships.filter(isRecord) : [];
    const authors = authorships
        .flatMap((a) => (isRecord(a.author) ? [str(a.author, 'display_name')] : []))
        .filter((n) => n !== undefined);
    const location = isRecord(record.primary_location) ? record.primary_location : undefined;
    const source = location !== undefined && isRecord(location.source) ? location.source : undefined;
    const venue = source !== undefined ? str(source, 'display_name') : undefined;
    const oa = isRecord(record.open_access) ? record.open_access : {};
    const landing = location !== undefined ? str(location, 'landing_page_url') : undefined;
    const pdf = location !== undefined ? str(location, 'pdf_url') : undefined;
    const url = landing ?? idUrl ?? (doi !== undefined ? `https://doi.org/${doi}` : `https://openalex.org/${workId ?? ''}`);
    const ids = isRecord(record.ids) ? record.ids : {};
    return compact({
        source: SOURCE,
        id: workId ?? url,
        title,
        authors,
        year: int(record, 'publication_year'),
        date: str(record, 'publication_date'),
        venue,
        abstract: abstractFromInverted(record.abstract_inverted_index),
        citationCount: int(record, 'cited_by_count'),
        doi,
        url,
        pdfUrl: pdf ?? str(oa, 'oa_url'),
        externalIds: compact({ DOI: doi, OpenAlex: workId, PMID: str(ids, 'pmid')?.replace(/^https?:\/\/pubmed\.ncbi\.nlm\.nih\.gov\//, '') }),
        extra: compact({ workType: str(record, 'type'), isOa: typeof oa.is_oa === 'boolean' ? oa.is_oa : undefined }),
    });
}
/**
 * Run one OpenAlex search (the direct-mode backend of `search_google_scholar`).
 * @param runtime - plugin runtime (client only).
 * @param params - query, wanted count, and year range.
 * @param signal - cancellation.
 * @returns the normalized result set.
 */
export async function runOpenalexSearch(runtime, params, signal) {
    const wanted = Math.max(1, Math.min(params.wanted, OPENALEX_PAGE_CAP));
    const filters = [];
    if (params.yearFrom !== undefined)
        filters.push(`from_publication_date:${params.yearFrom}-01-01`);
    if (params.yearTo !== undefined)
        filters.push(`to_publication_date:${params.yearTo}-12-31`);
    const query = new URLSearchParams({
        search: params.query,
        'per-page': String(wanted),
        page: '1',
        select: 'id,doi,title,display_name,publication_year,publication_date,authorships,primary_location,cited_by_count,open_access,ids,type,abstract_inverted_index',
    });
    if (filters.length > 0)
        query.set('filter', filters.join(','));
    const res = await runtime.client.fetchJson(`${OPENALEX_API}?${query.toString()}`, { signal });
    if (!res.ok)
        throw new Error(`OpenAlex search failed: ${res.error}`);
    const papers = (res.data.results ?? []).map(normalizeOpenalexWork).filter((p) => p !== undefined);
    const reported = typeof res.data.meta?.count === 'number' ? Math.trunc(res.data.meta.count) : papers.length;
    return compact({
        source: SOURCE,
        query: params.query,
        total: reported,
        papers,
        truncated: reported > papers.length,
        warning: 'key-free mode: results come from OpenAlex (Google Scholar has no free public API).',
    });
}
