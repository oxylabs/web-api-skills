# Oxylabs Web API — Agent Skills

Skills that teach a coding agent to use the Oxylabs Web API for live web search and web fetch.

| Skill | Use it for |
|---|---|
| `oxylabs-web-api` | Mechanics — the MCP tools, endpoint parameters, latency, errors, retries, and a CLI helper |
| `oxylabs-web-research` | The research method — search, pick sources, read, cite |
| `migrate-to-oxylabs` | Porting off Tavily, Exa, Firecrawl, Perplexity, Brave or Linkup |

## Install

Works with any skills-aware agent (Claude Code, Cursor, Codex, …):

```bash
npx skills add oxylabs/web-api-skills
```

Claude Code can instead take the repo as a plugin — skills and the MCP server wired
together:

```
/plugin marketplace add oxylabs/web-api-skills
/plugin install oxylabs-web-api
```

Skills are plain directories, so `git clone` + `./install.sh` (or `--project` for a
repo-local install, or a bare `cp -R skills/* ~/.claude/skills/`) also works.

## API key

1. Log in to the [Oxylabs dashboard](https://dashboard.oxylabs.io).
2. Create a **Web API** instance — keys from other Oxylabs products don't work here.
3. Generate an API key on that instance.
4. `export OXYLABS_WEB_API_KEY=<key>`

Start a new session and run `/skills` — all three skills should be listed.

## MCP server (optional, recommended)

`.mcp.json` at the root wires up the [MCP server](https://github.com/oxylabs/web-api-mcp),
so a project that adds this repo gets typed tools alongside the skills. It expects the
binary on `PATH`:

```bash
uv tool install git+https://github.com/oxylabs/web-api-mcp
```

The key comes from the environment or a `.env` in the project — never from the config
file. The server also bundles the `oxylabs-web-api` skill itself (as the
`oxylabs://skill/web-api` resource), so with the server alone you get tools and method;
install this repo's skills when you also want `migrate-to-oxylabs`, or no server at all.

## The helper script standalone

`skills/oxylabs-web-api/scripts/web_api.py` is stdlib-only Python, usable outside an
agent too:

```bash
export OXYLABS_WEB_API_KEY=your_api_key_here
python skills/oxylabs-web-api/scripts/web_api.py search "eu ai act deadlines" --max-results 5
python skills/oxylabs-web-api/scripts/web_api.py search "figma pricing" --scrape-top 2
python skills/oxylabs-web-api/scripts/web_api.py scrape "https://example.com/article"
```

## Troubleshooting

- **401 with a valid-looking key** — it is almost always a key from a different Oxylabs
  product. Web API needs its own instance and key.
- **429 mentioning quota** — the plan's quota is spent; retrying won't help.
- **MCP server fails to connect (`Executable not found: oxylabs-web-api-mcp`)** — the
  binary isn't installed; run the `uv tool install` line above.

## License

MIT
