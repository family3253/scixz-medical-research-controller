# n8n to Skill mapping

## Node families

| n8n family | Skill interpretation | Conversion rule |
|---|---|---|
| manual/chat/webhook/schedule trigger | entry condition | keep trigger intent, not n8n runtime syntax |
| file/database reader | input adapter | require explicit paths, formats, and read-only behavior |
| split/loop/merge/code | deterministic core | convert to tested library/CLI code when reusable |
| LLM/agent node | reasoning adapter | replace model binding with a role, schema, and evidence boundary |
| HTTP/API node | external adapter | strip query secrets; document authority, privacy, retries, and provenance |
| execute-command node | high-risk runtime | never execute during conversion; reimplement only if necessary and tested |
| file export | output contract | validate schema, encoding, path, and record counts |
| email/push/browser/form node | external side effect | require explicit destination, payload preview, and current authorization |

## Canonicalization questions

Before creating a Skill, ask:

1. Does an installed Skill already produce the same artifact?
2. Is the workflow's value the capability, or only its provider-specific plumbing?
3. Can the deterministic core be tested without API credentials?
4. Are the prompts factual instructions or merely prose wrappers around a schema?
5. Does conversion preserve source-item-to-output traceability?

If an existing owner covers the output, add the useful validation/routing pattern there and record
the n8n workflow as an implementation reference. Avoid duplicate mega-Skills.

