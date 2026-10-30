"""Row types of each command, for editors and type checkers (rows are plain dicts)."""

from typing import Any, Dict, List, Optional

try:  # Python 3.8+
    from typing import TypedDict
except ImportError:  # pragma: no cover
    from typing_extensions import TypedDict  # type: ignore


class ScrapeRow(TypedDict, total=False):
    """One row of `web-scraper scrape` (POST /v1/scrape)."""

    url: str
    """Requested URL."""
    finalUrl: str
    """URL after redirects."""
    status: int
    """HTTP status of the page."""
    contentType: str
    """Content type of the page."""
    format: str
    """Format of content."""
    title: str
    """Page title."""
    metadata: Dict[str, Any]
    """Description, language, canonical URL, image."""
    content: str
    """The page as Markdown, HTML or text."""
    bytes: int
    """Size of the page as downloaded."""
    durationMs: int
    """Time the call took, in milliseconds."""
    quality: Dict[str, Any]
    """Size of the extracted text (chars, tokens, words, headings, tables) and whether it was cut."""

class MapRow(TypedDict, total=False):
    """One row of `web-scraper map` (POST /v1/map)."""

    url: str
    """A URL of the site."""

class CrawlRow(TypedDict, total=False):
    """One row of `web-scraper crawl` (POST /v1/crawl)."""

    url: str
    """Page URL."""
    status: int
    """HTTP status."""
    title: str
    """Page title."""
    depth: int
    """Links from the start page (0 = the start page)."""
    content: Optional[str]
    """The page as Markdown."""
