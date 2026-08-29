/**
 * The system-prompt guidance registered beside the tools. Kept short: it names
 * the tool families, when to reach for each, and how to cite.
 * @module litmesh/prompt
 */
/** Which tool families the composition enabled. */
export interface EnabledFamilies {
    /** Key-free mode wording: free public APIs, no credits, no key instructions. */
    direct?: boolean;
    semanticScholar: boolean;
    pubmed: boolean;
    googleScholar: boolean;
    arxiv: boolean;
    biorxiv: boolean;
    doi: boolean;
    fullText: boolean;
    autoCite: boolean;
    sciDraw: boolean;
    credits: boolean;
    unified: boolean;
}
/**
 * Build the guidance text for the enabled families.
 * @param enabled - the families whose tools were registered.
 * @returns the section text, or `undefined` when nothing is enabled.
 */
export declare function buildGuidance(enabled: EnabledFamilies): string | undefined;
