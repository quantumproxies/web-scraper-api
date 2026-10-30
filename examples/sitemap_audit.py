"""Inventory of a site's URLs, with a page count per section.

    python sitemap_audit.py https://quanticdata.io --limit 5000

Writes urls.csv (url, section) and prints the site-wide total and the count
per top-level section as the API reports it, so you can compare it with what
you expect to be indexed.
"""

import argparse
from urllib.parse import urlsplit

from quanticdata_web_scraper_api import WebScraper, write


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("site")
    parser.add_argument("--limit", type=int, default=5000, help="URLs to list, up to 5000")
    parser.add_argument("--out", default="urls.csv")
    args = parser.parse_args()

    site = WebScraper().map(args.site, limit=args.limit)
    rows = []
    for u in site:
        path = urlsplit(u["url"]).path.strip("/")
        rows.append({"url": u["url"], "section": "/" + path.split("/")[0] if path else "/"})
    write(rows, args.out)

    print(f"total URLs on the site: {site.meta.get('total')}, listed: {len(rows)} -> {args.out}")
    for section, count in sorted((site.meta.get("summary") or {}).items(), key=lambda kv: -kv[1]):
        print(f"  {section:30} {count}")


if __name__ == "__main__":
    main()
