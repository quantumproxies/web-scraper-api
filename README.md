# Web Scraper API

[![ci](https://github.com/quantumproxies/web-scraper-api/actions/workflows/ci.yml/badge.svg)](https://github.com/quantumproxies/web-scraper-api/actions/workflows/ci.yml) ![python](https://img.shields.io/badge/python-3.9%2B-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)

Three jobs every scraping project starts with, from Python or the command line: read one page as clean Markdown (or HTML or text), list every URL a site exposes without crawling it, and crawl a site into Markdown pages ready for an LLM or a RAG index. The code is free and open source (MIT). It runs on the QuanticData Data API, so there are no proxies to rotate and no headless browser to keep alive: sign in once and run a command.

```bash
pip install git+https://github.com/quantumproxies/web-scraper-api
web-scraper login
web-scraper scrape https://en.wikipedia.org/wiki/Web_scraping --content-mode article -o page.md
```

`login` opens the QuanticData sign-in page in your browser. New accounts get $2 of free usage every month, no card required: [create one](https://app.quanticdata.io/register?utm_source=github&utm_medium=readme&utm_campaign=web-scraper-api).

## What it scrapes

| Command | Input | Returns | Per run |
|---|---|---|---|
| `web-scraper scrape` | URL | Markdown content, title, status, canonical, language, size, 11 fields per row ([docs and price](https://quanticdata.io/web-scraping-api/?utm_source=github&utm_medium=readme&utm_campaign=web-scraper-api)) | one page per call |
| `web-scraper map` | site URL | URL list, site total, count per section, 1 fields per row ([docs and price](https://quanticdata.io/crawl-map/?utm_source=github&utm_medium=readme&utm_campaign=web-scraper-api)) | up to 5,000 URLs |
| `web-scraper crawl` | start URL | URL, status, title, depth, Markdown content, 5 fields per row ([docs and price](https://quanticdata.io/crawl-map/?utm_source=github&utm_medium=readme&utm_campaign=web-scraper-api)) | up to 500 pages |

## Sample output

A real row from `web-scraper scrape https://en.wikipedia.org/wiki/Web_scraping --content-format markdown --content-mode article --max-tokens 250` (2026-10-22):

```json
{
  "url": "https://en.wikipedia.org/wiki/Web_scraping",
  "finalUrl": "https://en.wikipedia.org/wiki/Web_scraping",
  "status": 200,
  "contentType": "text/html; charset=UTF-8",
  "format": "markdown",
  "title": "Web scraping - Wikipedia",
  "metadata": {
    "description": null,
    "language": "en",
    "canonical": "https://en.wikipedia.org/wiki/Web_scraping",
    "image": null
  },
  "content": "For broader coverage of this topic, see [Data scraping](https://en.wikipedia.org/wiki/Data_scraping \"Data scraping\").\n\n**Web scraping**, **web harvesting**, or **web data extraction** is [data scraping](https://en.wikipedia.org/wiki/Data_scraping \"Data scraping\") used for [extracting data](https://en.wikipedia.org/wiki/Data_extraction \"Data extraction\") from [websites](https://en.wikipedia.org/wiki/Website \"Website\").[\\[1\\]](#cite_note-1) Web scraping software may directly access the [World Wide Web](https://en.wikipedia.org/wiki/World_Wide_Web \"World Wide Web\") using the [Hypertext Transfer Protocol](https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol \"Hypertext Transfer Protocol\") or a web browser.\n\n_[Content truncated to ~250 tokens — 168 more lines on the page.]_\n",
  "bytes": 236477,
  "durationMs": 3259,
  "quality": {
    "chars": 45197,
    "tokens": 11300,
    "words": 4303,
    "headings": 6,
    "tables": 0,
    "truncated": true,
    "returnedTokens": 232,
    "verdict": "good"
  }
}
```

## Python

```python
from quanticdata_web_scraper_api import WebScraper

web = WebScraper()  # saved login, or QUANTICDATA_API_KEY

page = web.scrape("https://en.wikipedia.org/wiki/Web_scraping", content_mode="article")
print(page.meta["title"])
print(page.meta["content"][:500])

site = web.map("https://quanticdata.io", search="/collectors/", limit=500)
print(site.meta["total"], [u["url"] for u in site][:5])

docs = web.crawl("https://quanticdata.io/docs/", limit=20, depth=2)
for p in docs:
    print(p["depth"], p["url"], len(p.get("content") or ""))
```

Each call returns a `Run`: iterate it for the rows (plain dicts), take `len()`, or save it with `to_csv()`, `to_json()`, `to_jsonl()` or `to_dataframe()` (pandas). Errors are specific: `InsufficientCredit`, `RateLimited`, `InvalidInput`, `JobFailed`, `AuthError`.

## Examples

- **A site as Markdown files**: Map a site, keep the URLs under one path and save each page as a .md file: a clean corpus for an LLM or a RAG index. See [`examples/site_to_markdown.py`](examples/site_to_markdown.py).
- **Docs crawl to JSON Lines**: Crawl a documentation site and write one JSON object per page (url, title, Markdown) for embeddings. See [`examples/crawl_to_jsonl.py`](examples/crawl_to_jsonl.py).
- **Sitemap audit**: List every URL a site publishes with its section and get the page count per section, a quick SEO inventory. See [`examples/sitemap_audit.py`](examples/sitemap_audit.py).

## Command line

Results print as a table; `-o file.csv`, `-o file.json` or `-o file.jsonl` writes a file. List inputs take `a b c`, `a,b,c`, `@file.txt` (one per line) or `-` (stdin). With `-o results.json` you get the whole API response; the table, CSV and JSONL views hold its main list.

### `web-scraper scrape`

One web page as clean Markdown (or HTML or text), with its title, canonical URL, language and status. Navigation, footers and cookie banners are left out by default.

```
web-scraper scrape URL [options]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `URL` | string |  | The page to read, e.g. https://en.wikipedia.org/wiki/Web_scraping. |
| `--content-format` | markdown / html / text / raw | `markdown` | markdown (default), html or text. |
| `--content-mode` | smart / article / full | `smart` | smart (whole page minus navigation and footer, the default), article (main article only) or full (entire body). |
| `--render` | boolean | `False` | Run the page in a headless browser so its JavaScript executes; billed at the render rate. |
| `--country` | string |  |  |
| `--max-tokens` | integer |  | Cut the Markdown at about this many tokens, at a section boundary. |
| `--query` | string |  | Keep only the sections of the page relevant to this question. |
| `--include-links` | boolean | `False` | Also return every link on the page, de-duplicated. |
| `--frontmatter` | boolean |  | Start the Markdown with YAML front matter (title, url, description, date). |

### `web-scraper map`

Every URL a site exposes, read from robots.txt, its sitemaps and the homepage links, without crawling it: the list plus the site-wide total and a count per section.

```
web-scraper map URL [options]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `URL` | string |  | The site, e.g. https://quanticdata.io. |
| `--limit` | integer | `100` | How many URLs to return, up to 5,000 (default 100); total and summary always cover the whole site. |
| `--search` | string |  | Only URLs containing this text, e.g. /blog/. |
| `--include-subdomains` | boolean | `False` | Include URLs on subdomains of the site. |
| `--sitemap-only` | boolean | `False` | Use only robots.txt and the sitemaps, skip the homepage links. |

### `web-scraper crawl`

A breadth-first crawl from a start URL: every page reached is converted to Markdown, with its URL, status, title and link depth. The CLI waits for the crawl to finish.

```
web-scraper crawl URL [options]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `URL` | string |  | Where the crawl starts, e.g. https://quanticdata.io/docs/. |
| `--limit` | integer | `50` | Maximum pages to crawl, up to 500 (default 50). |
| `--depth` | integer | `3` | How many links deep to follow from the start page, up to 10 (default 3). |
| `--content-mode` | smart / article / full | `smart` | smart (default), article or full, as for scrape. |
| `--include` | string[] |  | Only crawl URLs matching these patterns, e.g. /docs/*. |
| `--exclude` | string[] |  | Skip URLs matching these patterns. |
| `--country` | string |  |  |

## Output fields

<details><summary><code>web-scraper scrape</code>: 11 fields</summary>

| Field | Type | Description |
|---|---|---|
| `url` | string | Requested URL. |
| `finalUrl` | string | URL after redirects. |
| `status` | integer | HTTP status of the page. |
| `contentType` | string | Content type of the page. |
| `format` | string | Format of content. |
| `title` | string | Page title. |
| `metadata` | object | Description, language, canonical URL, image. |
| `content` | string | The page as Markdown, HTML or text. |
| `bytes` | integer | Size of the page as downloaded. |
| `durationMs` | integer | Time the call took, in milliseconds. |
| `quality` | object | Size of the extracted text (chars, tokens, words, headings, tables) and whether it was cut. |

</details>

<details><summary><code>web-scraper map</code>: 1 fields</summary>

| Field | Type | Description |
|---|---|---|
| `url` | string | A URL of the site. |

</details>

<details><summary><code>web-scraper crawl</code>: 5 fields</summary>

| Field | Type | Description |
|---|---|---|
| `url` | string | Page URL. |
| `status` | integer | HTTP status. |
| `title` | string | Page title. |
| `depth` | integer | Links from the start page (0 = the start page). |
| `content` | string or null | The page as Markdown. |

</details>

## Sign-in and API keys

- `web-scraper login` signs you in with OAuth 2.1 and PKCE in the browser. The token is stored in `~/.config/quanticdata/credentials.json` (readable only by you) and refreshed automatically. One login serves every QuanticData tool on the machine.
- No browser on the machine (SSH, Docker, Colab): run `web-scraper login --no-browser`, open the link anywhere, then paste back the address the browser ends on.
- Scripts and CI: set `QUANTICDATA_API_KEY` to a key from the dashboard, or store one with `web-scraper login --api-key`.
- `web-scraper logout` revokes the token. The connection is listed under API keys in the dashboard as "API · QuanticData CLI"; deleting that key disconnects every machine that uses it.

## Pricing

The code is free and MIT-licensed. Calls are billed to your QuanticData account at the prices on the Web Scraping API and Crawl & Map pages linked above; $2 of usage is free every month and failed calls are never billed. Plans with higher limits: [pricing](https://quanticdata.io/pricing/?utm_source=github&utm_medium=readme&utm_campaign=web-scraper-api).

## Other ways to call it

The same data over plain HTTP:

```bash
curl -X POST https://api.quanticdata.io/v1/scrape \
  -H "Authorization: Bearer $QUANTICDATA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://en.wikipedia.org/wiki/Web_scraping", "format": "markdown", "contentMode": "article", "max_tokens": 250}'
```

- [API reference](https://quanticdata.io/docs/?utm_source=github&utm_medium=readme&utm_campaign=web-scraper-api) with Python, Node, PHP and curl examples.
- [MCP server](https://quanticdata.io/mcp-server/?utm_source=github&utm_medium=readme&utm_campaign=web-scraper-api) to give Claude, Cursor or any MCP client the same tools.
- [n8n node](https://github.com/quantumproxies/n8n-nodes-quanticdata) for no-code workflows.

## FAQ

**Is this web scraper free?**

The code is free and MIT-licensed. Calls run on your QuanticData account: $2 of usage is free every month with no card, then you pay per call at the prices on the Web Scraping API and Crawl & Map pages. Failed calls are never billed.

**Does it handle JavaScript-heavy pages?**

Yes: add --render to run the page in a headless browser before it is converted. Plain pages are read without one, which is faster and cheaper.

**Is the output ready for an LLM?**

The Markdown keeps headings, lists, tables and absolute links and drops navigation, footers and cookie banners. --max-tokens cuts a long page at a section boundary and --query keeps only the relevant sections.

**How many URLs or pages per call?**

map returns up to 5,000 URLs per call and always reports the site-wide total; crawl reads up to 500 pages, up to 10 links deep.

**Can I save a page straight to a file?**

web-scraper scrape URL -o page.md writes the Markdown itself; -o page.json keeps the whole response with title, metadata and status.

**Which pages can I scrape?**

Public pages you are allowed to access. You are responsible for respecting each site's terms.

## Related scrapers

- [Google SERP API](https://github.com/quantumproxies/google-serp-api): Google SERP API for Python and the command line.
- [Google Maps Scraper](https://github.com/quantumproxies/google-maps-scraper): Google Maps scraper for Python and the command line.

## License

MIT. Built and maintained by [QuanticData](https://quanticdata.io/?utm_source=github&utm_medium=readme&utm_campaign=web-scraper-api).
