---
name: oxylabs-web-api
description: Search the live web and read any web page through the Oxylabs Web API. Use when a task needs current information, a source you cannot recall, or the contents of a specific URL — including JavaScript-heavy, paywalled-by-bot-check, or geo-restricted pages that a plain fetch cannot retrieve.
---

# Oxylabs Web API

Two endpoints. `search` finds URLs, `scrape` reads them. Base URL `https://webapi.oxylabs.io`.

## Setup check

The key lives in `OXYLABS_API_KEY`. If it is unset, stop and ask the user for it rather
than guessing — every call will 401 without it.

```bash
[ -n "$OXYLABS_API_KEY" ] && echo "key present" || echo "ask the user for OXYLABS_API_KEY"
```

## Search

```bash
curl -sS https://webapi.oxylabs.io/v1/search \
  -H "Authorization: Bearer $OXYLABS_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"query": "eu ai act compliance deadlines", "max_results": 5}'
```

| Field | Type | Notes |
|---|---|---|
| `query` | string, **required** | Non-empty. Write it like a search query, not a sentence. |
| `max_results` | integer, 1–20 | Default 10. |
| `location` | string | Geo context, e.g. `"Germany"`, `"New York,New York,United States"`. |

Returns `results[]` with `title`, `shortDescription`, `url`, `metadata.position`, plus
`related_searches[]` and `related_questions[]`.

**Descriptions are search snippets, not page content.** Never answer a factual question
from `shortDescription` alone — it is truncated and often stale. Scrape the source.

## Scrape

```bash
curl -sS https://webapi.oxylabs.io/v1/scrape \
  -H "Authorization: Bearer $OXYLABS_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://en.wikipedia.org/wiki/Artificial_intelligence"}'
```

`url` (string, required) must be an absolute `http(s)` URL. Scrape is heavier than
search — expect seconds, not milliseconds, and don't fire dozens in parallel.

## Helper script

`scripts/web_api.py` wraps both endpoints with retries on 429/5xx and prints JSON:

```bash
python scripts/web_api.py search "who acquired figma" --max-results 5
python scripts/web_api.py scrape "https://example.com/article"
python scripts/web_api.py search "best rain jacket 2026" --max-results 3 --scrape-top 2
```

`--scrape-top N` runs the search-then-read loop in one command, which is the pattern you
want most of the time.

## Errors

| Status | Meaning | What to do |
|---|---|---|
| 400 | Validation failed | Read `extra[].key` and `extra[].message`; fix that field. Do not retry unchanged. |
| 401 | Bad or missing key | Stop and tell the user. Retrying will not help. |
| 429 | Rate limited | Back off exponentially, reduce concurrency. |
| 5xx | Upstream trouble | Retry up to 3 times with backoff, then report. |

A 400 is a bug in your request. Fix the field the response names instead of retrying.

## Working rules

1. **Search to find, scrape to read.** One search, then scrape only the 1–3 URLs that
   actually look like they answer the question.
2. **Cite the URL** you scraped for every claim that came from the web.
3. **Don't scrape what you already have.** Re-reading the same URL twice in one task is
   wasted quota.
4. **Say when a page failed.** If a scrape errors, report which URL failed rather than
   quietly substituting your own recollection.
