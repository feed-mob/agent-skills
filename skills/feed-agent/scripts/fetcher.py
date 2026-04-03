#!/usr/bin/env python3
"""Content fetching for feed-agent."""

import argparse
import json
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from html import unescape
from urllib.error import URLError
from urllib.request import Request, urlopen

try:
    import feedparser
except ImportError:
    print(
        "Error: feedparser not installed. Run: pip install feedparser", file=sys.stderr
    )
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent))

from db import get_sources, insert_article, update_source_fetched, Article, Source


def strip_html(text: str) -> str:
    """Remove HTML tags and normalize text."""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", "", text)
    clean = unescape(clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def parse_date(entry: dict) -> Optional[str]:
    """Parse date from feed entry."""
    for field in ["published_parsed", "updated_parsed", "created_parsed"]:
        if hasattr(entry, field) and getattr(entry, field):
            try:
                from time import mktime

                dt = datetime.fromtimestamp(mktime(getattr(entry, field)))
                return dt.isoformat()
            except (TypeError, ValueError, OverflowError):
                pass

    for field in ["published", "updated", "created"]:
        if hasattr(entry, field) and getattr(entry, field):
            return getattr(entry, field)

    return None


def normalize_entry(entry: dict, source: Source) -> dict:
    """Normalize a feed entry to our format."""
    guid = entry.get("id") or entry.get("link") or entry.get("title", "")
    url = entry.get("link", "")
    title = strip_html(entry.get("title", "Untitled"))

    author = entry.get("author", "")
    if not author and "authors" in entry and entry["authors"]:
        author = entry["authors"][0].get("name", "")

    summary = ""
    if "summary" in entry:
        summary = strip_html(entry["summary"])
    elif "description" in entry:
        summary = strip_html(entry["description"])
    if len(summary) > 500:
        summary = summary[:497] + "..."

    published_at = parse_date(entry)

    return {
        "guid": guid,
        "url": url,
        "title": title,
        "author": author,
        "summary": summary,
        "published_at": published_at,
        "source_id": source.id,
        "source_name": source.name,
    }


def fetch_feed(url: str, timeout: int = 30) -> tuple[List[dict], Optional[str]]:
    """Fetch and parse an RSS/Atom feed.

    Args:
        url: Feed URL
        timeout: Request timeout in seconds

    Returns:
        Tuple of (items list, error message or None)
    """
    try:
        request = Request(
            url, headers={"User-Agent": "Mozilla/5.0 (compatible; FeedAgent/1.0)"}
        )
        with urlopen(request, timeout=timeout) as response:
            content = response.read()

        feed = feedparser.parse(content)

        if feed.bozo and not feed.entries:
            error_msg = (
                str(feed.bozo_exception)
                if hasattr(feed, "bozo_exception")
                else "Parse error"
            )
            return [], error_msg

        items = []
        for entry in feed.entries:
            items.append(dict(entry))

        return items, None

    except URLError as e:
        return [], f"URL error: {e.reason}"
    except TimeoutError:
        return [], "Timeout"
    except Exception as e:
        return [], str(e)


def fetch_full_content(url: str, timeout: int = 30) -> tuple[str, Optional[str]]:
    """Fetch full article content from URL.

    Note: For complex pages, the agent should use webfetch tool
    to extract the main content.

    Args:
        url: Article URL
        timeout: Request timeout

    Returns:
        Tuple of (content, error)
    """
    try:
        request = Request(
            url, headers={"User-Agent": "Mozilla/5.0 (compatible; FeedAgent/1.0)"}
        )
        with urlopen(request, timeout=timeout) as response:
            html = response.read().decode("utf-8", errors="ignore")

        # Basic text extraction - agent should use webfetch for better results
        # Remove scripts and styles
        html = re.sub(
            r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE
        )
        html = re.sub(
            r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE
        )

        # Try to find main content
        main_patterns = [
            r"<article[^>]*>(.*?)</article>",
            r"<main[^>]*>(.*?)</main>",
            r'<div[^>]*class=["\'][^"\']*content[^"\']*["\'][^>]*>(.*?)</div>',
            r'<div[^>]*id=["\'][^"\']*content[^"\']*["\'][^>]*>(.*?)</div>',
        ]

        for pattern in main_patterns:
            match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
            if match:
                content = strip_html(match.group(1))
                if len(content) > 500:
                    return content[:5000], None

        # Fallback: extract all text
        content = strip_html(html)
        return content[:5000], None

    except Exception as e:
        return "", str(e)


def get_fetch_instructions(topic: str, project_root: Path) -> Dict[str, Any]:
    """Get instructions for fetching content.

    Returns instructions for the agent to execute fetching.
    The agent should use webfetch tool for full content extraction.

    Args:
        topic: Current topic
        project_root: Project root directory

    Returns:
        Dict with instructions
    """
    sources = get_sources(project_root, topic, status="active")

    if not sources:
        return {"error": "No active sources found. Run scout first.", "sources": []}

    return {
        "tool": "webfetch",
        "sources": [
            {
                "id": s.id,
                "url": s.url,
                "name": s.name,
                "type": s.source_type,
            }
            for s in sources
        ],
        "instructions": f"""
            For each source:
            
            1. If source type is 'rss':
               - Fetch the RSS feed URL
               - Parse entries (title, link, summary, published)
               - For each entry, use webfetch to get full content from the link
               
            2. If source type is 'blog' or 'news':
               - Use webfetch to get the main page content
               - Extract article links
               - Use webfetch on each article link for full content
            
            3. Store results in database using fetcher.py --action store
            
            Output format for each article:
            {{
                "source_id": <id>,
                "url": "<article_url>",
                "title": "<title>",
                "content": "<full_content>",
                "summary": "<summary_from_rss>",
                "published_at": "<iso_date>"
            }}
        """,
        "output_path": str(
            project_root
            / "data"
            / "feed_agent"
            / f"{topic.replace(' ', '_').lower()}"
            / "raw_items.json"
        ),
    }


def store_articles(
    project_root: Path, topic: str, articles: List[Dict]
) -> Dict[str, Any]:
    """Store fetched articles in database.

    Args:
        project_root: Project root directory
        topic: Current topic
        articles: List of article dicts

    Returns:
        Stats dict
    """
    stats = {
        "total": len(articles),
        "stored": 0,
        "duplicates": 0,
        "errors": 0,
    }

    for article_data in articles:
        article = Article(
            id=None,
            topic=topic,
            url=article_data.get("url", ""),
            source_id=article_data.get("source_id"),
            title=article_data.get("title", ""),
            content=article_data.get("content", ""),
            summary=article_data.get("summary", ""),
        )

        try:
            article_id = insert_article(project_root, article)
            if article_id > 0:
                stats["stored"] += 1
            else:
                stats["duplicates"] += 1
        except Exception as e:
            stats["errors"] += 1
            print(f"Error storing article: {e}", file=sys.stderr)

    return stats


def run_fetch(topic: str, project_root: Path) -> Dict[str, Any]:
    """Run the fetching process.

    Note: Returns instructions for agent to execute.

    Args:
        topic: Current topic
        project_root: Project root directory

    Returns:
        Dict with instructions
    """
    return get_fetch_instructions(topic, project_root)


def main():
    parser = argparse.ArgumentParser(description="Content fetching for feed-agent")
    parser.add_argument(
        "--project-root", type=Path, required=True, help="Project root directory"
    )
    parser.add_argument("--topic", required=True, help="Topic to fetch")
    parser.add_argument("--action", choices=["fetch", "store"], default="fetch")
    parser.add_argument("--url", help="Single URL to fetch")
    parser.add_argument("--articles", help="JSON file with articles to store")

    args = parser.parse_args()

    if args.action == "fetch":
        result = run_fetch(args.topic, args.project_root)
        print(json.dumps(result, indent=2))

    elif args.action == "store":
        if args.articles:
            with open(args.articles) as f:
                articles = json.load(f)
        else:
            articles = json.load(sys.stdin)

        stats = store_articles(args.project_root, args.topic, articles)
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
