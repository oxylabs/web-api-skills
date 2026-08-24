# Oxylabs Web API — Agent Skills

Skills that teach a coding agent to use the [Oxylabs Web API](https://github.com/oxylabs/gitbook-web-api)
for live web search and page reading.

| Skill | Use it for |
|---|---|
| `oxylabs-web-api` | Mechanics — the MCP tools, endpoint parameters, latency, errors, retries, and a CLI helper |
| `oxylabs-web-research` | The research method — search, pick sources, read, cite |
| `migrate-to-oxylabs` | Porting off Tavily, Exa, Firecrawl, Perplexity, Brave or Linkup |

## Install

```bash
git clone https://github.com/oxylabs/web-api-skills.git
cd web-api-skills
./install.sh              # ~/.claude/skills — available in every project
./install.sh --project    # ./.claude/skills — this repo only
export OXYLABS_WEB_API_KEY=your_api_key_here
```

The repo is also a Claude Code plugin — `.claude-plugin/marketplace.json` and
`plugin.json` at the root — so it can be added as a marketplace instead of copied by hand.

`.mcp.json` at the root wires up the [MCP server](https://github.com/oxylabs/web-api-mcp)
alongside the skills, so a project that adds this repo gets the tools and the method
together. It expects `oxylabs-web-api-mcp` on `PATH` (`uv tool install
git+https://github.com/oxylabs/web-api-mcp`). The key can come from the environment or from
a `.env` in the project — the server fills any unset `OXYLABS_*` variable from there, so
you do not have to put the key in the config file.

If you use the [MCP server](https://github.com/oxylabs/web-api-mcp), you may not need to
install anything: it bundles `oxylabs-web-api` and serves it over MCP as the
`oxylabs://skill/web-api` resource and the `web_research` prompt. Install the skills here
when you want them loaded without the server, or when you want `migrate-to-oxylabs`.

### Getting an API key

1. Log in to the [Oxylabs dashboard](https://dashboard.oxylabs.io).
2. Create a **Web API** instance — keys from other Oxylabs products don't work here.
3. Generate an API key on that instance.
4. `export OXYLABS_WEB_API_KEY=<key>`

Start a new session and run `/skills` to confirm both loaded. Re-run `install.sh` to upgrade.

### Manual install

Skills are plain directories. Copy them wherever your agent reads skills from:

```bash
cp -R skills/oxylabs-web-api ~/.claude/skills/
```

Claude Desktop, Cursor and other MCP/skill-aware clients follow the same pattern with
their own skills directory.

## Layout

```
.mcp.json                         # MCP server config, so skills and tools install together
.claude-plugin/
├── marketplace.json              # add this repo as a Claude Code marketplace
└── plugin.json
skills/
├── oxylabs-web-api/
│   ├── SKILL.md
│   └── scripts/web_api.py        # search / scrape / search-then-scrape, with retries
├── oxylabs-web-research/
│   └── SKILL.md
└── migrate-to-oxylabs/
    └── SKILL.md                  # parameter and response maps for six providers
```

## The helper script standalone

`web_api.py` has no dependencies beyond the Python standard library, so it is usable
outside an agent too:

```bash
export OXYLABS_WEB_API_KEY=your_api_key_here
python skills/oxylabs-web-api/scripts/web_api.py search "eu ai act deadlines" --max-results 5
python skills/oxylabs-web-api/scripts/web_api.py search "figma pricing" --scrape-top 2
python skills/oxylabs-web-api/scripts/web_api.py scrape "https://example.com/article"
```

## Prefer tools over a CLI?

The same two endpoints are available as MCP tools:
[web-api-mcp](https://github.com/oxylabs/web-api-mcp) — `search`, `scrape`, `extract`,
`check_scrape`, `read_scraped`, `list_scrapers` and `scrape_target`. Skills and MCP are
complementary: MCP gives the agent typed tools, skills give it the judgment for when and
how to use them. Both skills cover the tools as well as the HTTP endpoints, and tell the
agent to prefer the tools when the server is connected.

## License

MIT
