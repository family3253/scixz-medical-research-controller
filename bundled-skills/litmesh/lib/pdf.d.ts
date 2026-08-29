/**
 * PDF download, DOI resolution, and text extraction shared by every
 * `read_*` / `download_*` tool, plus the common full-text output shape.
 * @module litmesh/pdf
 */
import type { ContentBlock } from '@deepseek-ai/dsh-llm';
import type { InferValue, GenericCallView } from '@deepseek-ai/dsh-tools';
import type { Ai4ScholarClient, ApiErr } from './api-client.js';
import type { CreditsValue } from './paper.js';
/** A downloaded PDF. */
export interface PdfDownload {
    ok: true;
    data: Uint8Array;
    finalUrl: string;
}
/**
 * Download a PDF, rejecting bodies that are not PDFs (publisher landing pages).
 * @param client - the shared client (browser-like headers, timeout).
 * @param url - PDF URL.
 * @param options - cancellation and timeout.
 * @returns the bytes or a described failure.
 */
export declare function fetchPdf(client: Ai4ScholarClient, url: string, options: {
    signal?: AbortSignal | undefined;
    timeoutMs: number;
}): Promise<PdfDownload | ApiErr>;
/** Extracted text with the page count. */
export interface PdfText {
    text: string;
    pages: number;
}
/**
 * Extract text from PDF bytes.
 * @param data - PDF bytes.
 * @returns the concatenated page text and page count.
 */
export declare function extractPdfText(data: Uint8Array): Promise<PdfText>;
/** Candidate PDF URLs derived from a publisher landing page URL. */
export declare function pdfCandidatesFor(landingUrl: string): string[];
/** Outcome of resolving a DOI to PDF bytes. */
export type DoiResolution = (PdfDownload & {
    landingUrl: string;
}) | (ApiErr & {
    landingUrl?: string;
});
/**
 * Resolve a DOI through doi.org with PDF content negotiation, then try
 * publisher PDF URL patterns derived from the landing page. Publisher access
 * depends on the host network (institutional subscriptions).
 * @param client - the shared client.
 * @param doi - bare DOI.
 * @param options - cancellation and per-download timeout.
 * @returns the PDF with the URLs involved, or a described failure.
 */
export declare function resolveDoiToPdf(client: Ai4ScholarClient, doi: string, options: {
    signal?: AbortSignal | undefined;
    timeoutMs: number;
}): Promise<DoiResolution>;
/** Output schema of every full-text read tool. */
export declare const READ_OUTPUT_SCHEMA: {
    readonly type: "object";
    readonly additionalProperties: false;
    readonly properties: {
        readonly id: {
            readonly type: "string";
            readonly required: true;
            readonly description: "The identifier the call resolved.";
        };
        readonly title: {
            readonly type: "string";
        };
        readonly pdfUrl: {
            readonly type: "string";
            readonly required: true;
            readonly description: "URL the PDF was fetched from.";
        };
        readonly pages: {
            readonly type: "integer";
        };
        readonly totalChars: {
            readonly type: "integer";
            readonly required: true;
            readonly description: "Length of the whole extracted text.";
        };
        readonly offset: {
            readonly type: "integer";
            readonly required: true;
            readonly description: "Character offset this slice starts at.";
        };
        readonly text: {
            readonly type: "string";
            readonly required: true;
            readonly description: "The returned slice of extracted text.";
        };
        readonly truncated: {
            readonly type: "boolean";
            readonly required: true;
            readonly description: "True when text remains after this slice.";
        };
        readonly nextOffset: {
            readonly type: "integer";
            readonly description: "Offset to request the next slice.";
        };
        readonly credits: {
            readonly type: "object";
            readonly additionalProperties: false;
            readonly description: "AI4Scholar credit accounting for this call, when the API reported it.";
            readonly properties: {
                readonly charged: {
                    readonly type: "number";
                    readonly description: "Credits this call cost.";
                };
                readonly remaining: {
                    readonly type: "number";
                    readonly description: "Account balance after this call.";
                };
                readonly sessionTotal: {
                    readonly type: "number";
                    readonly description: "Credits charged by this plugin during the current session (process-local tally).";
                };
            };
        };
    };
};
/** The read tools' canonical value. */
export type ReadValue = InferValue<typeof READ_OUTPUT_SCHEMA>;
/**
 * Slice extracted text for one call.
 * @param full - the whole text.
 * @param offset - requested start (clamped).
 * @param maxChars - requested length (clamped to at least 1).
 * @returns the slice fields of {@link ReadValue}.
 */
export declare function sliceText(full: string, offset: number | undefined, maxChars: number): Pick<ReadValue, 'totalChars' | 'offset' | 'text' | 'truncated' | 'nextOffset'>;
/** Model-facing content for a read result: a header, the slice, and the continuation note. */
export declare function renderRead(value: ReadValue): ContentBlock[];
/** Pending-call card for a read tool. */
export declare function presentReadCall(label: string, id: string): GenericCallView;
/** Fold `credits` into a read value without leaving an undefined member. */
export declare function withCredits<T extends object>(value: T, credits: CreditsValue | undefined): T & {
    credits?: CreditsValue;
};
