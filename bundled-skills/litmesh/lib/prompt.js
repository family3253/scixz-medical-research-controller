/**
 * The system-prompt guidance registered beside the tools. Kept short: it names
 * the tool families, when to reach for each, and how to cite.
 * @module litmesh/prompt
 */
/**
 * Build the guidance text for the enabled families.
 * @param enabled - the families whose tools were registered.
 * @returns the section text, or `undefined` when nothing is enabled.
 */
export function buildGuidance(enabled) {
    const direct = enabled.direct === true;
    const lines = [];
    const anySearch = enabled.semanticScholar || enabled.pubmed || enabled.googleScholar || enabled.arxiv;
    if (enabled.unified && anySearch) {
        lines.push('- search_papers: one call queries several platforms (default Semantic Scholar + PubMed; add arxiv / google-scholar via sources) and merges duplicates, ranking papers found on more than one platform first — a good first call for a new topic. Use the platform tools below for filters, sorting, and paging.');
    }
    // Full-text tools exist only under a family that ships PDFs.
    const fullText = enabled.fullText && (enabled.semanticScholar || enabled.arxiv || enabled.biorxiv || enabled.doi);
    if (enabled.semanticScholar) {
        lines.push('- Semantic Scholar (all fields' + (direct ? '; free via the public Graph API' : '; costs credits') + '): search_semantic is the default paper search; search_semantic_bulk for large sets; search_semantic_paper_match resolves a known title; search_semantic_snippets finds passages inside full texts; get_semantic_paper_detail / get_semantic_paper_batch fetch metadata and abstracts; get_semantic_citations / get_semantic_references walk the citation graph; search_semantic_authors / get_semantic_author_detail / get_semantic_author_papers / get_semantic_paper_authors / get_semantic_author_batch cover authors; get_semantic_recommendations(_for_paper) suggest similar papers.' + (fullText ? ' download_semantic / read_semantic_paper fetch open-access PDFs.' : '') + (direct ? ' The public pool is rate-limited (429s retry automatically); set SEMANTIC_SCHOLAR_API_KEY for higher limits.' : ''));
    }
    if (enabled.pubmed) {
        lines.push('- PubMed (biomedical, clinical' + (direct ? '; free via NCBI E-utilities' : '; costs credits') + '): search_pubmed, get_pubmed_paper_detail, get_pubmed_paper_batch, get_pubmed_citations, get_pubmed_related. Prefer it for medicine, biology, and health questions.');
    }
    if (enabled.googleScholar) {
        lines.push(direct
            ? '- search_google_scholar (broad coverage, cited-by counts; free): key-free mode answers from OpenAlex, since Google Scholar has no public API. Use it when other tools miss or cited-by counts are wanted.'
            : '- search_google_scholar (broadest coverage, cited-by counts; costs credits, slower): use when other tools miss or Google Scholar counts are wanted.');
    }
    if (enabled.arxiv) {
        lines.push('- arXiv (free): search_arxiv for preprints in physics, math, CS, stats, q-bio; download_arxiv gives the PDF link' + (fullText ? '; read_arxiv_paper returns the full text.' : '.'));
    }
    if (enabled.biorxiv) {
        lines.push('- bioRxiv / medRxiv (free): search_biorxiv / search_medrxiv list recent preprints by category and date window (not free-text search)' + (fullText ? '; read_biorxiv_paper / read_medrxiv_paper return full text.' : '.'));
    }
    if (enabled.doi) {
        lines.push('- download_by_doi' + (fullText ? ' / read_by_doi' : '') + ' (free) resolve any DOI to a PDF; paywalled publishers only work on a network with institutional access.');
    }
    if (fullText) {
        lines.push('- Full-text tools return the text in slices (offset/max_chars); read further slices only when the question needs them.');
    }
    if (enabled.autoCite) {
        lines.push(direct
            ? '- auto_cite (free, 20–90 s): when the user pastes academic text and asks for citations/references, call it directly — the plugin searches the public APIs per sentence and returns the annotated text plus a formatted reference list and BibTeX.'
            : '- auto_cite (costs credits, 20–90 s): when the user pastes academic text and asks for citations/references, call it directly and return the annotated text plus reference list.');
    }
    if (enabled.sciDraw) {
        lines.push('- sci_draw (costs credits, 30–90 s): scientific figures — generate, edit, style, compose, critique, SVG, vectorize. Tell the user it takes about a minute before calling; then show the returned image URL as a Markdown image.');
    }
    if (enabled.credits) {
        lines.push('- get_litmesh_credits (free) reports the credit balance and what this session has spent; results of billed tools already show credits charged/remaining.');
    }
    const anyBilled = !direct && (enabled.semanticScholar || enabled.pubmed || enabled.googleScholar || enabled.autoCite || enabled.sciDraw);
    if (anyBilled) {
        lines.push('- After a turn in which billed AI4Scholar tools ran, end your reply with one short line stating the credits those calls cost and the remaining balance (both appear at the end of each billed tool result), in the user\'s language.');
    }
    if (lines.length === 0)
        return undefined;
    return [
        `AI4Scholar literature tools are available${direct ? ' (key-free: every tool runs on free public APIs)' : ''}:`,
        ...lines,
        'For literature questions, call the tools instead of guessing; combine platforms when coverage matters. Present findings in Markdown and cite each paper by title with its DOI or link. Never fabricate papers, authors, identifiers, or figures that a tool did not return.',
    ].join('\n');
}
