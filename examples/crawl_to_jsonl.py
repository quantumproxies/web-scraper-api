"""Crawl a documentation site into JSON Lines for embeddings.

    python crawl_to_jsonl.py https://quanticdata.io/docs/ --limit 100 --depth 3

Writes docs.jsonl, one object per page: url, title, depth and the Markdown
text. Feed it to your embedding pipeline or vector database loader.
"""

import argparse
import json

from quanticdata_web_scraper_api import WebScraper


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("start_url")
    parser.add_argument("--limit", type=int, default=100, help="pages at most (up to 500)")
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--include", nargs="*", help="only URLs matching these patterns, e.g. /docs/*")
    parser.add_argument("--out", default="docs.jsonl")
    args = parser.parse_args()

    crawl = WebScraper().crawl(args.start_url, limit=args.limit, depth=args.depth,
                               include=args.include, content_mode="article")
    with open(args.out, "w", encoding="utf-8") as fh:
        for page in crawl:
            if page.get("status") != 200 or not page.get("content"):
                continue
            record = {"url": page["url"], "title": page.get("title"), "depth": page.get("depth"),
                      "text": page["content"]}
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"{len(crawl)} pages crawled, written to {args.out}")


if __name__ == "__main__":
    main()
