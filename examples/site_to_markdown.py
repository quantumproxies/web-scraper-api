"""Save every page under one path of a site as a Markdown file.

    python site_to_markdown.py https://quanticdata.io --path /docs/ --out corpus --limit 50

Lists the site's URLs with map (no crawl), keeps those containing --path,
then reads each one as Markdown with front matter and writes it to
corpus/<slug>.md. Re-running skips files that already exist.
"""

import argparse
import os
import re

from quanticdata_web_scraper_api import QuanticDataError, WebScraper


def slug(url: str) -> str:
    path = re.sub(r"^https?://[^/]+", "", url).strip("/") or "index"
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", path)[:120]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("site")
    parser.add_argument("--path", default="/", help="keep URLs containing this text")
    parser.add_argument("--out", default="corpus")
    parser.add_argument("--limit", type=int, default=50, help="pages to save at most")
    args = parser.parse_args()

    web = WebScraper()
    urls = [u["url"] for u in web.map(args.site, search=args.path, limit=args.limit)]
    os.makedirs(args.out, exist_ok=True)
    saved = 0
    for url in urls:
        target = os.path.join(args.out, slug(url) + ".md")
        if os.path.exists(target):
            continue
        try:
            page = web.scrape(url, frontmatter=True)
        except QuanticDataError as e:
            print(f"skip {url}: {e}")
            continue
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(page.meta.get("content") or "")
        saved += 1
    print(f"{saved} new pages in {args.out}/ ({len(urls)} URLs matched)")


if __name__ == "__main__":
    main()
