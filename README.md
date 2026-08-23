# Oxylabs Web API — Agent Skills

Skills that teach a coding agent to use the [Oxylabs Web API](https://github.com/oxylabs/gitbook-web-api)
for live web search and page reading.

| Skill | Use it for |
|---|---|
| `oxylabs-web-api` | Endpoint mechanics — parameters, errors, retries, and a CLI helper |
| `oxylabs-web-research` | The research method — search, pick sources, read, cite |

## Install

```bash
git clone https://github.com/oxylabs/web-api-skills.git
cd web-api-skills
./install.sh              # ~/.claude/skills — available in every project
./install.sh --project    # ./.claude/skills — this repo only
export OXYLABS_API_KEY=your_api_key_here
```

### Getting an API key

1. Log in to the [Oxylabs dashboard](https://dashboard.oxylabs.io).
2. Create a **Web API** instance — keys from other Oxylabs products don't work here.
3. Generate an API key on that instance.
4. `export OXYLABS_API_KEY=<key>`

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
skills/
├── oxylabs-web-api/
│   ├── SKILL.md
│   └── scripts/web_api.py        # search / scrape / search-then-scrape, with retries
└── oxylabs-web-research/
    └── SKILL.md
```

## The helper script standalone

`web_api.py` has no dependencies beyond the Python standard library, so it is usable
outside an agent too:

```bash
export OXYLABS_API_KEY=your_api_key_here
python skills/oxylabs-web-api/scripts/web_api.py search "eu ai act deadlines" --max-results 5
python skills/oxylabs-web-api/scripts/web_api.py search "figma pricing" --scrape-top 2
python skills/oxylabs-web-api/scripts/web_api.py scrape "https://example.com/article"
```

## Prefer tools over a CLI?

The same two endpoints are available as MCP tools:
[web-api-mcp](https://github.com/oxylabs/web-api-mcp). Skills and MCP are
complementary — MCP gives the agent typed tools, skills give it the judgment for when and
how to use them.

## License

MIT
