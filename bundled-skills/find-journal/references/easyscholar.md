# EasyScholar optional journal-rank adapter

EasyScholar can be used as an optional third-party API source for a known-journal lookup. It complements `sci-select`; it is not itself a Skill and it does not replace Clarivate, CAS, the journal publisher, or LetPub.

## Fields it can supply

The API's documented `officialRank.all` keys include:

- `sciif`: SCI Impact Factor/JCR IF label
- `sci`: SCI/JCR quartile label
- `ssci`: SSCI/JCR quartile label
- `jci`: JCI label
- `sciBase`: CAS basic-version partition
- `sciUp`: CAS upgraded-version major category
- `sciUpSmall`: CAS upgraded-version minor category
- `sciUpTop`: CAS upgraded-version Top flag
- `xr`: 2026 XinRui partition
- `xrSmall`: 2026 XinRui minor category
- `xrTop`: 2026 XinRui Top flag
- `sciwarn` / `xrWarn`: warning indicators when present

`customRank.rankInfo` and `customRank.rank` are preserved and decoded into dataset/rank records. The provider's `officialRank` means EasyScholar's maintained dataset; it should be labelled as a third-party aggregation and independently checked when the value is used for graduation, promotion, or formal submission documentation.

## Secure local configuration

Set the key in the local environment only:

```powershell
$env:EASY_SCHOLAR_SECRET_KEY = "<your-secret-key>"
python bundled-skills/find-journal/scripts/easyscholar_lookup.py "Journal of Global Antimicrobial Resistance" --pretty
```

Never put the key in `SKILL.md`, README files, JSON registries, run manifests, shell history, screenshots, issue reports, or Git commits. The adapter accepts the key only through `EASY_SCHOLAR_SECRET_KEY`, never as a command-line argument, and never prints the request URL.

## API limits and provenance

- Endpoint: `https://www.easyscholar.cc/open/getPublicationRank`
- Method: `GET`
- Parameters: `secretKey` and URL-encoded `publicationName`
- Rate limit: at most two requests per second; the adapter enforces a 0.5-second delay between multiple journals.
- Every result carries `provider`, `source_type`, `retrieved_at`, `api_code`, `api_message`, and field-level raw/normalized data.
- A failed request is `attempted`; a successful response without a requested field remains partial/missing. Do not convert missing data into a guessed value.

## What EasyScholar does not provide

The API does not provide LetPub's review-speed text. Keep a separate LetPub browser record with the page URL and retrieval date. Do not treat EasyScholar, LetPub, ShowJCR, JANE, or iPubMed as a substitute for authoritative Clarivate JCR/Master Journal List or the applicable CAS release.
