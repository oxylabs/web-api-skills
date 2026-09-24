#!/usr/bin/env python3
"""Oxylabs Web API CLI: search, scrape, or search-then-scrape in one call.

Usage:
    python web_api.py search "query" [--max-results 10] [--location DE] [--scrape-top N]
    python web_api.py scrape "https://example.com" [--format markdown|html] [--location DE] [--run-js]

Scrapes request Markdown from the API by default — it renders server-side, so nothing is
converted here.

Reads OXYLABS_WEB_API_KEY from the environment. Prints JSON on stdout, diagnostics on stderr.
Exit codes: 0 ok, 1 request failed, 2 bad usage or missing key.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request

BASE_URL = os.environ.get("OXYLABS_BASE_URL", "https://webapi.oxylabs.io").rstrip("/")
TIMEOUT = float(os.environ.get("OXYLABS_TIMEOUT", "120"))
RETRY_STATUSES = {429, 500, 502, 503, 504}
MAX_ATTEMPTS = 3


def die(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def api_key() -> str:
    key = os.environ.get("OXYLABS_WEB_API_KEY", "").strip()
    if not key:
        die("OXYLABS_WEB_API_KEY is not set. Ask the user for a key; do not guess one.", 2)
    return key


def call(path: str, payload: dict, method: str = "POST", timeout: float = TIMEOUT) -> dict:
    """POST/GET with backoff on 429 and 5xx. 4xx other than 429 fails immediately."""
    body = json.dumps(payload).encode() if payload is not None else None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        req = urllib.request.Request(
            f"{BASE_URL}{path}",
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {api_key()}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = json.loads(resp.read())
            # A 2xx is not the whole story: "faulted" in the envelope means the work
            # failed upstream even though the status code says otherwise.
            if isinstance(body, dict) and body.get("status") == "faulted":
                die(f"{path} returned a 2xx with status=faulted: {str(body)[:600]}")
            return body
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:600]
            if exc.code == 429 and "QUOTA_EXCEEDED" in detail:
                die("429 QUOTA_EXCEEDED — the plan's quota is spent. Stop and tell the user.")
            if exc.code in RETRY_STATUSES and attempt < MAX_ATTEMPTS:
                # Full jitter, so concurrent callers do not all retry on the same second.
                wait = round(random.uniform(0, 2**attempt), 1)
                print(f"{path} -> {exc.code}, retrying in {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            if exc.code == 401:
                die("401 Unauthorized — the API key was rejected. Stop and tell the user.")
            die(f"{path} -> HTTP {exc.code}: {detail}")
        except urllib.error.URLError as exc:
            if attempt < MAX_ATTEMPTS:
                time.sleep(random.uniform(0, 2**attempt))
                continue
            die(f"Could not reach {BASE_URL}{path}: {exc.reason}")
    die(f"{path} failed after {MAX_ATTEMPTS} attempts")
    raise AssertionError("unreachable")


def do_search(args: argparse.Namespace) -> dict:
    if not 1 <= args.max_results <= 20:
        die("--max-results must be between 1 and 20", 2)
    if not 1 <= len(args.query) <= 2048:
        die("query must be between 1 and 2048 characters", 2)
    if args.location and not (len(args.location) == 2 and args.location.isalpha()):
        die('--location must be a two-letter country code, e.g. "DE"', 2)
    payload = {"query": args.query, "max_results": args.max_results}
    if args.location:
        payload["location"] = args.location
    out = call("/v1/search", payload)

    if args.scrape_top:
        urls = [r["url"] for r in out.get("results", [])[: args.scrape_top]]
        pages = []
        for url in urls:
            print(f"scraping {url}", file=sys.stderr)
            try:
                pages.append({"url": url, "page": call("/v1/scrape", scrape_body(url))})
            except SystemExit:
                # One dead URL should not lose the results we already have.
                pages.append({"url": url, "error": "scrape failed"})
        out["scraped"] = pages
    return out


def scrape_body(
    url: str, fmt: str = "markdown", location: str | None = None, run_js: bool = False
) -> dict:
    """Request body for /v1/scrape. `output` is a list; the API renders the format."""
    body: dict = {"url": url, "output": [fmt]}
    if location:
        body["location"] = location
    if run_js:
        body["run_js"] = True
    return body


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="search the live web")
    s.add_argument("query")
    s.add_argument("--max-results", type=int, default=10, help="1-20, default 10")
    s.add_argument("--location", help='two-letter country code, e.g. "DE"')
    s.add_argument(
        "--scrape-top",
        type=int,
        metavar="N",
        help="also scrape the top N result URLs and attach them under `scraped`",
    )

    p = sub.add_parser("scrape", help="read one URL")
    p.add_argument("url")
    p.add_argument(
        "--format",
        choices=["markdown", "html"],
        default="markdown",
        help="output format the API renders (default markdown)",
    )
    p.add_argument("--location", help='two-letter country code, e.g. "DE"')
    p.add_argument(
        "--run-js",
        action="store_true",
        help="execute page JavaScript — only after a plain scrape came back empty; much slower",
    )

    args = parser.parse_args()
    if args.cmd == "search":
        result = do_search(args)
    else:
        if not args.url.startswith(("http://", "https://")):
            die("url must be an absolute http(s) URL", 2)
        result = call(
            "/v1/scrape",
            scrape_body(args.url, args.format, args.location, args.run_js),
            # A run_js render can take the full 150s; don't let the default timeout cut it off.
            timeout=max(TIMEOUT, 180.0) if args.run_js else TIMEOUT,
        )

    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
