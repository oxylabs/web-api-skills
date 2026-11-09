# Oxylabs Web API — Claude Code Plugin and Agent Skills

Welcome to the official repository overview for Oxylabs' Web API Skills. This guide is a developer-focused, technical reference covering what Web API Skills do. Skills that teach a coding agent to use the Oxylabs Web API for live web search and web fetch.

This repo works two ways: as a **Claude Code plugin** (the skills plus the Oxylabs-hosted MCP server, set up in one install) or as plain **agent skills** for Claude Code, Cursor, Codex and other skills-aware agents. See [Install](#install).


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

Claude Code can instead take the repo as a plugin — the skills plus the Oxylabs-hosted
MCP server, with nothing else to install:

```
/plugin marketplace add oxylabs/web-api-skills
/plugin install oxylabs-web-api@oxylabs-web-api
```

Claude Code asks for your Web API key when the plugin is enabled and keeps it in the
system keychain. To change it later, run `/plugin configure oxylabs-web-api@oxylabs-web-api`.

Skills are plain directories, so `git clone` + `./install.sh` (or `--project` for a
repo-local install, or a bare `cp -R skills/* ~/.claude/skills/`) also works.

## API key

1. Log in to the [Oxylabs dashboard](https://dashboard.oxylabs.io).
2. Create a **Web API** instance — keys from other Oxylabs products don't work here.
3. Generate an API key on that instance.
4. For the Claude Code plugin, paste it when Claude Code asks. For skills installed any
   other way, `export OXYLABS_WEB_API_KEY=<key>`.

Start a new session and run `/skills` — all three skills should be listed.

## MCP server (optional, recommended)

The plugin's `.mcp.json` connects to the Oxylabs-hosted
[MCP server](https://github.com/oxylabs/web-api-mcp) at `https://mcp.oxylabs.io/web-api-mcp`,
sending the key from the plugin's settings as `Authorization: Bearer <key>`. Other agents
can connect to the same URL with that header — see the
[web-api-mcp README](https://github.com/oxylabs/web-api-mcp#connect-to-the-remote-mcp-server)
for Codex, Cursor and others, or to run the server yourself.

The server also bundles the `oxylabs-web-api` skill itself (as the
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
- **429 with `title: "QUOTA_EXCEEDED"`** — the plan's quota is spent; retrying won't help.
- **Plugin MCP tools missing** — the key isn't set. Run
  `/plugin configure oxylabs-web-api@oxylabs-web-api`, then restart Claude Code.
- **`Authentication failed (401)` from the plugin's tools** — same as above: wrong product's
  key, or a typo. Re-enter it with `/plugin configure`.

## Learn More

For detailed configuration, advanced usage, and code examples in multiple languages, check the official documentation:

- [Get started with Web API](https://oxylabs.io/products/web-api)
- [Web API documentation](https://developers.oxylabs.io/products/web-api)

## License

MIT

## Contact Us

If you have questions or need support, reach out to us at [support@oxylabs.io](mailto:support@oxylabs.io), or through live chat in the [Oxylabs Dashboard](https://dashboard.oxylabs.io/). For enterprise inquiries, contact your dedicated account manager.
