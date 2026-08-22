---
name: oxylabs-web-research
description: Answer a question from live web sources with citations, using the Oxylabs Web API to search and then read the pages. Use for research tasks, competitive checks, fact-finding, price or spec lookups, "what's the current state of X", or any question where being out of date would make the answer wrong.
---

# Web research with the Oxylabs Web API

A loop for turning a question into a cited answer. Assumes the `oxylabs-web-api` skill for
endpoint mechanics — this skill is about the method.

## The loop

1. **Split the question.** Break it into the specific facts you need. "Is X cheaper than Y"
   is two lookups, not one.
2. **Search narrowly.** One query per fact, `max_results` 5–10. Query text should read like
   something a person would type, not a sentence.
3. **Pick sources, don't take the top hit.** Prefer primary sources — the vendor's own
   pricing page over a listicle, the filing over the news write-up, the docs over the blog.
   Position 1 is frequently SEO, not truth.
4. **Scrape 1–3 of them.** Read the actual page. Snippets truncate exactly where the
   qualifier lives.
5. **Extract with the URL attached.** Every fact carries the URL it came from as you collect
   it, not reconstructed afterwards.
6. **Check for conflict.** Two sources disagreeing is a finding, not noise. Report both and
   say which is more authoritative and why.
7. **Answer, then cite.** Conclusion first, sources under it.

## When to stop

Stop when the next scrape would not change the answer. Three good sources beats ten
skimmed ones. If two independent primary sources agree, that fact is done.

## Report shape

```markdown
**Answer:** <the direct answer, one or two sentences>

- <claim> — [source](https://url)
- <claim> — [source](https://url)

**Uncertain:** <anything you could not confirm, and what you tried>
```

## Rules that keep research honest

- **Never fill a gap from memory.** If the web didn't confirm it, it goes under
  *Uncertain* — silently substituting recollection for a source is the failure mode
  that makes research worthless.
- **Date everything time-sensitive.** Prices, headcounts, version numbers and rankings
  need "as of <date>" because they were true when the page was written, not necessarily now.
- **Report dead ends.** "Three sources didn't state the pricing" is a real result and
  saves the next person the same searches.
- **Don't launder a single source into three.** Three articles citing the same press
  release is one source.

## Geo-sensitive questions

Pricing, availability and rankings change by country. When the question is geographic,
pass `location` and say which locale the answer reflects — an unqualified "it costs $9"
is wrong somewhere.
