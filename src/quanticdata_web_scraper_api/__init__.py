"""Web Scraper API: Web scraper API for Python and the command line: any page to clean Markdown, HTML or text, every URL of a site from its sitemaps, and full site crawls to Markdown for LLMs and RAG. Free and open source; sign in with your QuanticData account, no proxies or headless browser to run.

    from quanticdata_web_scraper_api import WebScraper

    scraper = WebScraper()   # saved login (`web-scraper login`) or QUANTICDATA_API_KEY
    run = scraper.scrape(...)   # one page as Markdown, HTML or text
    run = scraper.map(...)   # every URL of a site, from sitemaps and links
    run = scraper.crawl(...)   # crawl a site into Markdown pages
"""

from typing import Any, Dict, Optional, Sequence, Union

from ._qd.client import Client, Run
from ._qd.errors import (APIError, AuthError, InsufficientCredit, InvalidInput, JobFailed, JobTimeout,
                         QuanticDataError, RateLimited)
from ._qd.output import write

__version__ = "0.1.0"
__all__ = ["WebScraper", "Run", "write", "APIError", "AuthError", "InsufficientCredit", "InvalidInput",
           "JobFailed", "JobTimeout", "QuanticDataError", "RateLimited", "__version__"]


def _as_list(value: Any) -> Any:
    if value is None or isinstance(value, (list, tuple)):
        return list(value) if value is not None else None
    return [value]


class WebScraper:
    """Web Scraper API on the QuanticData Data API.

    Every method runs one collector and returns a :class:`Run`: iterate it for the
    rows (plain dicts, typed in ``types``), or save it with ``to_csv()``,
    ``to_json()``, ``to_jsonl()`` or ``to_dataframe()``.
    """

    def __init__(self, api_key: Optional[str] = None, *, timeout: float = 180.0) -> None:
        self.client = Client(api_key, user_agent="web-scraper/0.1.0 (+https://github.com/quantumproxies/web-scraper-api)", timeout=timeout)

    def scrape(
        self, url: str,
        *,
        content_format: Optional[str] = None,
        content_mode: Optional[str] = None,
        render: Optional[bool] = None,
        country: Optional[str] = None,
        max_tokens: Optional[int] = None,
        query: Optional[str] = None,
        include_links: Optional[bool] = None,
        frontmatter: Optional[bool] = None,
        timeout: float = 1800.0,
    ) -> Run:
        """One web page as clean Markdown (or HTML or text), with its title, canonical URL, language and status. Navigation, footers and cookie banners are left out by default.

        Args:
            url: The page to read, e.g. https://en.wikipedia.org/wiki/Web_scraping.
            content_format: markdown (default), html or text. One of: markdown, html, text, raw.
            content_mode: smart (whole page minus navigation and footer, the default), article (main article only) or full (entire body). One of: smart, article, full.
            render: Run the page in a headless browser so its JavaScript executes; billed at the render rate.
            country: country
            max_tokens: Cut the Markdown at about this many tokens, at a section boundary.
            query: Keep only the sections of the page relevant to this question.
            include_links: Also return every link on the page, de-duplicated.
            frontmatter: Start the Markdown with YAML front matter (title, url, description, date).
            timeout: seconds to wait before giving up.

        Returns a Run: ``meta`` is the whole response, ``rows`` its ``response`` list (see ``types.ScrapeRow``).
        """
        payload = {
            "url": url,
            "format": content_format,
            "contentMode": content_mode,
            "render": render,
            "country": country,
            "max_tokens": max_tokens,
            "query": query,
            "include_links": include_links,
            "frontmatter": frontmatter,
        }
        return self.client.layer("scrape", {**{}, **payload}, rows_key=None, row_field='value', timeout=timeout)

    def map(
        self, url: str,
        *,
        limit: Optional[int] = None,
        search: Optional[str] = None,
        include_subdomains: Optional[bool] = None,
        sitemap_only: Optional[bool] = None,
        timeout: float = 1800.0,
    ) -> Run:
        """Every URL a site exposes, read from robots.txt, its sitemaps and the homepage links, without crawling it: the list plus the site-wide total and a count per section.

        Args:
            url: The site, e.g. https://quanticdata.io.
            limit: How many URLs to return, up to 5,000 (default 100); total and summary always cover the whole site.
            search: Only URLs containing this text, e.g. /blog/.
            include_subdomains: Include URLs on subdomains of the site.
            sitemap_only: Use only robots.txt and the sitemaps, skip the homepage links.
            timeout: seconds to wait before giving up.

        Returns a Run: ``meta`` is the whole response, ``rows`` its ``links`` list (see ``types.MapRow``).
        """
        payload = {
            "url": url,
            "limit": limit,
            "search": search,
            "includeSubdomains": include_subdomains,
            "sitemapOnly": sitemap_only,
        }
        return self.client.layer("map", {**{}, **payload}, rows_key='links', row_field='url', timeout=timeout)

    def crawl(
        self, url: str,
        *,
        limit: Optional[int] = None,
        depth: Optional[int] = None,
        content_mode: Optional[str] = None,
        include: Optional[Union[str, Sequence[str]]] = None,
        exclude: Optional[Union[str, Sequence[str]]] = None,
        country: Optional[str] = None,
        timeout: float = 1800.0,
    ) -> Run:
        """A breadth-first crawl from a start URL: every page reached is converted to Markdown, with its URL, status, title and link depth. The CLI waits for the crawl to finish.

        Args:
            url: Where the crawl starts, e.g. https://quanticdata.io/docs/.
            limit: Maximum pages to crawl, up to 500 (default 50).
            depth: How many links deep to follow from the start page, up to 10 (default 3).
            content_mode: smart (default), article or full, as for scrape. One of: smart, article, full.
            include: Only crawl URLs matching these patterns, e.g. /docs/*.
            exclude: Skip URLs matching these patterns.
            country: country
            timeout: seconds to wait before giving up.

        Returns a Run: ``meta`` is the whole response, ``rows`` its ``pages`` list (see ``types.CrawlRow``).
        """
        payload = {
            "url": url,
            "limit": limit,
            "depth": depth,
            "contentMode": content_mode,
            "include": _as_list(include),
            "exclude": _as_list(exclude),
            "country": country,
        }
        return self.client.layer("crawl", {**{}, **payload}, rows_key='pages', row_field='value', timeout=timeout)
