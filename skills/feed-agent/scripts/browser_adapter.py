#!/usr/bin/env python3
"""Browser-based search provider implementation."""

import json
import re
import sys
from typing import List, Optional
from pathlib import Path
from urllib.parse import urljoin, urlparse

sys.path.insert(0, str(Path(__file__).parent))

from search_provider import SearchProvider, SearchResult, FeedCandidate, SourceType


class BrowserAdapter(SearchProvider):
    """Search provider using agent-browser for web scraping.

    This adapter uses the agent-browser skill to navigate search engines
    and extract results. It can be used as a fallback when API-based
    providers are not available.
    """

    # Search engines to scrape
    SEARCH_ENGINES = {
        "google": {
            "url": "https://www.google.com/search?q={query}",
            "result_selector": "div.g a[href^='/url']",
            "title_selector": "h3",
        },
        "duckduckgo": {
            "url": "https://duckduckgo.com/?q={query}",
            "result_selector": "a.result__a",
            "title_selector": "a.result__a",
        },
    }

    @property
    def name(self) -> str:
        return "browser"

    def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search using browser automation.

        Note: This method returns empty. The actual search must be
        performed using the agent-browser skill, and results passed
        to process_results() for parsing.

        Args:
            query: Search query string
            max_results: Maximum number of results

        Returns:
            Empty list (use get_search_instructions() instead)
        """
        return []

    def get_search_instructions(self, query: str, engine: str = "google") -> dict:
        """Get instructions for agent-browser to perform search.

        Args:
            query: Search query string
            engine: Search engine to use ("google" or "duckduckgo")

        Returns:
            Dict with URL and selectors for browser automation
        """
        engine_config = self.SEARCH_ENGINES.get(engine, self.SEARCH_ENGINES["google"])

        return {
            "url": engine_config["url"].format(query=query.replace(" ", "+")),
            "result_selector": engine_config["result_selector"],
            "title_selector": engine_config["title_selector"],
            "instructions": f"""
                Navigate to: {engine_config["url"].format(query=query.replace(" ", "+"))}
                Wait for results to load
                Extract all result links using selector: {engine_config["result_selector"]}
                For each result, extract the title and URL
            """,
        }

    def process_results(self, raw_html: str, base_url: str) -> List[SearchResult]:
        """Process raw HTML from search results.

        Args:
            raw_html: HTML content from search results page
            base_url: Base URL for resolving relative links

        Returns:
            List of SearchResult objects
        """
        results = []

        # Extract links from HTML
        link_pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>'
        matches = re.findall(link_pattern, raw_html, re.IGNORECASE)

        seen_urls = set()
        for url, title in matches:
            # Skip navigation/irrelevant links
            if any(
                x in url.lower() for x in ["javascript:", "#", "mailto:", "/search?"]
            ):
                continue

            # Resolve relative URLs
            full_url = urljoin(base_url, url)

            # Skip duplicates
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            # Clean title
            clean_title = re.sub(r"\s+", " ", title).strip()

            source_type = self._detect_source_type(full_url, "")

            results.append(
                SearchResult(
                    url=full_url, title=clean_title, snippet="", source_type=source_type
                )
            )

        return results

    def discover_feeds(self, topic: str, max_results: int = 5) -> List[FeedCandidate]:
        """Get instructions for discovering feeds via browser.

        Note: Returns empty list. Use get_feed_discovery_instructions().
        """
        return []

    def get_feed_discovery_instructions(self, topic: str) -> dict:
        """Get instructions for discovering RSS feeds via browser.

        Args:
            topic: Topic to discover feeds for

        Returns:
            Dict with instructions for browser automation
        """
        search_queries = [
            f"{topic} RSS feed",
            f"{topic} news site",
        ]

        return {
            "queries": search_queries,
            "instructions": f"""
                For each query:
                1. Search on Google/DuckDuckGo
                2. Visit top 5 results
                3. Look for:
                   - <link rel="alternate" type="application/rss+xml"> tags
                   - Links containing /feed, /rss, /atom
                   - RSS icons in the page
                4. Extract feed URLs
            """,
            "feed_selectors": [
                'link[type="application/rss+xml"]',
                'link[type="application/atom+xml"]',
                'a[href*="/feed"]',
                'a[href*="/rss"]',
                'a[href*="feed.xml"]',
            ],
        }

    def extract_feeds_from_page(self, html: str, page_url: str) -> List[str]:
        """Extract feed URLs from a webpage.

        Args:
            html: HTML content of the page
            page_url: URL of the page (for resolving relative links)

        Returns:
            List of feed URLs found
        """
        feed_urls = []

        # Look for <link> tags for RSS/Atom
        link_patterns = [
            r'<link[^>]+type=["\']application/rss\+xml["\'][^>]+href=["\']([^"\']+)["\']',
            r'<link[^>]+type=["\']application/atom\+xml["\'][^>]+href=["\']([^"\']+)["\']',
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]+type=["\']application/rss\+xml["\']',
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]+type=["\']application/atom\+xml["\']',
        ]

        for pattern in link_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                full_url = urljoin(page_url, match)
                if full_url not in feed_urls:
                    feed_urls.append(full_url)

        # Look for common feed paths
        common_paths = ["/feed", "/rss", "/atom.xml", "/feed.xml", "/rss.xml"]
        parsed = urlparse(page_url)
        for path in common_paths:
            potential_feed = f"{parsed.scheme}://{parsed.netloc}{path}"
            if potential_feed not in feed_urls:
                feed_urls.append(potential_feed)

        return feed_urls

    def _detect_source_type(self, url: str, content: str) -> SourceType:
        """Detect the type of source from URL patterns."""
        url_lower = url.lower()

        if any(
            x in url_lower for x in ["/feed", "/rss", "/atom", "feed.xml", "rss.xml"]
        ):
            return SourceType.RSS

        if "blog" in url_lower:
            return SourceType.BLOG

        if any(x in url_lower for x in ["news", "breaking", "latest"]):
            return SourceType.NEWS

        return SourceType.UNKNOWN


def main():
    """CLI interface for testing."""
    import argparse

    parser = argparse.ArgumentParser(description="Browser search provider")
    parser.add_argument("--topic", required=True, help="Topic to discover feeds for")
    parser.add_argument(
        "--action", choices=["instructions", "test"], default="instructions"
    )

    args = parser.parse_args()

    adapter = BrowserAdapter()

    if args.action == "instructions":
        instructions = adapter.get_feed_discovery_instructions(args.topic)
        print(json.dumps(instructions, indent=2))


if __name__ == "__main__":
    main()
