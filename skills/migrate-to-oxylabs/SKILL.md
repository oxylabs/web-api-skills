---
name: migrate-to-oxylabs
description: Move a codebase from another web search or scraping API — Tavily, Exa, Firecrawl, Perplexity Search, Brave Search, Linkup — to the Oxylabs Web API. Use when asked to migrate, switch, replace, swap out, rip out or evaluate against one of those providers, when a repo already calls one of their endpoints and someone wants Oxylabs instead, or when someone asks what the equivalent parameter or response field is. Do NOT use it for the first integration of a greenfield project — that is `oxylabs-web-api`.
user-invocable: true
argument-hint: <provider to migrate from>
metadata:
  author: oxylabs
---

# Migrating to the Oxylabs Web API

Two endpoints replace whatever is there: `POST /v1/search` finds URLs, `POST /v1/scrape`
reads them. Base URL `https://webapi.oxylabs.io`, auth `Authorization: Bearer $OXYLABS_WEB_API_KEY`.

Read [`oxylabs-web-api`](../oxylabs-web-api/SKILL.md) for the endpoints themselves. This
file is only about getting off the old one.

## Do this first

```bash
# Which provider is actually in use, and where
grep -rniE "tavily|exa\.ai|firecrawl|perplexity\.ai|api\.search\.brave|linkup\.so" \
  --include='*.py' --include='*.ts' --include='*.js' --include='*.go' --include='*.rb' . \
  | grep -v node_modules
# And the keys they read
grep -rnoE "(TAVILY|EXA|FIRECRAWL|PERPLEXITY|BRAVE|LINKUP)_API_KEY" . | grep -v node_modules
```

Migrate the **call sites**, not the SDK. Most of these providers ship a client library whose
surface is wider than the code actually uses; porting the library is work nobody asked for.
Find the two or three functions that wrap search and fetch, change those, leave the rest.

## Parameter mapping

Every provider below has a `query`/`q` that maps to `query`, and a result-count knob that
maps to `max_results` (1–20, default 10). The rest:

### Tavily → `/v1/search`

| Tavily | Oxylabs | Note |
|---|---|---|
| `max_results` | `max_results` | Tavily allows more than 20; cap it |
| `country` | `location` | Tavily takes a country name, Oxylabs a two-letter code — `"germany"` becomes `"DE"` |
| `search_depth` | — | No depth ladder. One search |
| `include_answer` | — | **No synthesised answer.** Read the sources and write the answer yourself, with citations |
| `include_raw_content` | `POST /v1/scrape` | A separate call per URL, which is also what makes it cheap when you don't need it |
| `include_domains` / `exclude_domains` | — | Not supported. Filter `results[].url` client-side |
| `time_range`, `start_date`, `end_date` | — | Not supported |
| `topic: "news"` | — | Not supported, and news is not in the response |

### Exa → `/v1/search`

| Exa | Oxylabs | Note |
|---|---|---|
| `numResults` | `max_results` | |
| `userLocation` (2-letter) | `location` (2-letter) | Same code |
| `type` (`neural`/`fast`/`auto`/`deep`) | — | No modes. Exa's `instant` is the closest to what you get |
| `contents.highlights` | — | Scrape the page and read it, or `extract` the fields you want |
| `includeDomains` / `excludeDomains` | — | Client-side |
| `startPublishedDate` / `endPublishedDate` | — | Not supported |
| `category` | — | Not supported |
| Semantic/neural matching | — | **This is the real difference.** Oxylabs matches the query as written rather than reranking on meaning. Keyword-shaped queries win; sentence-shaped ones do not |

### Firecrawl → `/v1/search` + `/v1/scrape`

The closest fit in the list — Firecrawl also splits search from scrape.

| Firecrawl | Oxylabs | Note |
|---|---|---|
| `/v2/search` `limit` | `/v1/search` `max_results` | |
| `/v2/search` `location`, `country` | `location` | One field, a two-letter country code. Keep `country`; a city or region in `location` has no equivalent |
| `/v2/search` `scrapeOptions` | a separate `/v1/scrape` per URL | No hydration-in-search |
| `/v2/scrape` `formats: ["markdown"]` | `output: ["markdown"]` | Same idea, same default advice |
| `/v2/scrape` `formats: ["html"]` | `output: ["html"]` | |
| `/v2/scrape` `onlyMainContent` | — | Markdown is already the readable rendering |
| `/v2/scrape` `waitFor`, `actions` | `run_js: true` | No scripted actions. If you need clicks, this is not a drop-in |
| `/v2/scrape` JSON extraction | `output: ["json"]` + `json.prompt` | Prompt-described, no schema to maintain |
| `/v2/crawl`, `/v2/map` | — | **No crawl and no sitemap.** If the code crawls a whole domain, Oxylabs does not replace that half; keep it or rethink the design |
| `tbs` | — | Not supported |

### Perplexity Search → `/v1/search`

| Perplexity | Oxylabs | Note |
|---|---|---|
| `max_results` | `max_results` | |
| `country` (ISO alpha-2) | `location` (ISO alpha-2) | Same code |
| `search_context_size`, `max_tokens`, `max_tokens_per_page` | — | Scrape only what you decide to read; that is the budget control |
| `search_domain_filter` | — | Client-side |
| `search_recency_filter`, `*_date_filter` | — | Not supported |
| Chat completions with citations | — | **Oxylabs returns sources, not prose.** The synthesis is your agent's job |

### Brave Search → `/v1/search`

| Brave | Oxylabs | Note |
|---|---|---|
| `q` | `query` | |
| `count` (max 20) | `max_results` (max 20) | Same ceiling |
| `offset` | — | No pagination. Ask a narrower question |
| `country`, `search_lang`, `ui_lang` | `location` | `country` carries over as the same two-letter code; no language knobs |
| `freshness` | — | Not supported |
| `extra_snippets` | scrape the URL | |
| `/res/v1/llm-context` | `output: ["markdown"]` on the pages you pick | Their token-budgeted context has no direct equivalent; picking fewer pages is the substitute |

### Linkup → `/v1/search`

| Linkup | Oxylabs | Note |
|---|---|---|
| `q` | `query` | |
| `maxResults` | `max_results` | |
| `depth` (`fast`/`standard`/`deep`) | — | No ladder |
| `outputType: "sourcedAnswer"` | — | Sources only; write the answer yourself |
| `structuredOutputSchema` | `/v1/scrape` `output: ["json"]` + `json.prompt` | Per page, described in words rather than a schema |
| `includeDomains` / `excludeDomains`, `fromDate` / `toDate` | — | Client-side or unsupported |

## Response mapping

Every provider returns a list of results with a title, a snippet and a URL. The renames:

| Concept | Tavily | Exa | Firecrawl | Perplexity | Brave | Oxylabs |
|---|---|---|---|---|---|---|
| Envelope | `results` | `results` | `data.web` | `results` | `web.results` | `results` |
| Title | `title` | `title` | `title` | `title` | `title` | `title` |
| Snippet | `content` | `text`/`highlights` | `description` | `snippet` | `description` | `short_description` |
| URL | `url` | `url` | `url` | `url` | `url` | `url` |
| Rank | implicit | implicit | implicit | implicit | implicit | `metadata.position` |

`short_description` catches people out — it is the field most often missed in a port, and the
symptom is empty snippets rather than an error.

Oxylabs also returns `related_searches[]` (`query`) and `related_questions[]`
(`question`, plus nullable `title` and `snippet`), and a `metadata.request_id` worth
logging: it is what support traces a call by.

Two traps when you port the request and error handling: `query` is capped at 2048
characters, and `location` must be an ISO 3166-1 alpha-2 code — providers with no cap, or
code that passed a place name, will now get a `400`. And when every search engine fails,
the call is a `500` with `state: "faulted"`, not a `2xx` with an empty list; it is not
charged, so one retry is free.

## What does not port

Say these out loud before the migration starts, because finding them halfway through is
worse:

1. **No synthesised answer.** Tavily's `include_answer`, Perplexity's completions and
   Linkup's `sourcedAnswer` have no equivalent. The agent reads the sources and writes the
   answer. For an agent this is usually an improvement — the citations are real — but it is
   a code change, not a config change.
2. **No crawl, no sitemap.** Firecrawl `/crawl` and `/map` have no counterpart.
3. **No date, domain or freshness filters** on search. Filter client-side on `url`, and
   check dates on the page after scraping.
4. **No semantic search.** Rewrite sentence-shaped queries as keyword-shaped ones — this is
   the single biggest quality difference in a naive port, and it usually looks like "Oxylabs
   returns worse results" until the queries are fixed.
5. **News is absent** from the response.

## What you gain, and how to prove it

Worth writing into the migration PR rather than asserting:

- **Results ranked for the country you asked for**, not a semantic match on your phrasing
  someone else rebuilt. Verify with the same query at two `location` values.
- **Pages a plain client cannot fetch.** JS-heavy, bot-protected, geo-gated. Verify against a
  URL the old provider returned empty.
- **Markdown rendered server-side**, so no HTML-to-Markdown dependency and no tokens spent on
  markup. Verify by deleting that dependency.
- **Measured p50 1.3s / p95 2.7s** on search (2 589 live queries, concurrency 5).

## Migration order

1. Wrap the old provider behind one function if it isn't already.
2. Add an Oxylabs implementation of that function, behind an env flag.
3. Run both over a fixed query set and diff — result overlap, snippet quality, latency.
4. Fix the queries before judging the results (see point 4 above).
5. Flip the flag, keep the old path for one release, then delete it and its key.
