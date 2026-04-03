#!/usr/bin/env python3
"""Exa search provider implementation."""

import json
import sys
from typing import List, Optional
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from search_provider import (
    SearchProvider,
    SearchResult,
    FeedCandidate,
    SourceType,
    SearchProviderError,
)


class ExaAdapter(SearchProvider):
    """Search provider using Exa (exa_web_search_exa tool).

    This adapter uses the Exa search API which provides high-quality,
    AI-optimized search results.
    """

    @property
    def name(self) -> str:
        return "exa"

    def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search using Exa web search.

        Note: This method returns placeholder results. The actual search
        must be performed by the agent using the exa_web_search_exa tool,
        and results passed to this adapter for processing.

        Args:
            query: Search query string
            max_results: Maximum number of results

        Returns:
            List of SearchResult objects (processed from tool output)
        """
        return []

    def search_with_results(self, tool_output: dict, topic: str) -> List[SearchResult]:
        """Process Exa tool output into SearchResult objects.

        Args:
            tool_output: Raw output from exa_web_search_exa tool
            topic: Topic for relevance filtering

        Returns:
            List of SearchResult objects
        """
        results = []

        if isinstance(tool_output, str):
            try:
                tool_output = json.loads(tool_output)
            except json.JSONDecodeError:
                return results

        for item in tool_output.get("results", []):
            url = item.get("url", "")
            title = item.get("title", "")
            snippet = item.get("content", "") or item.get("snippet", "")

            source_type = self._detect_source_type(url, snippet)

            results.append(
                SearchResult(
                    url=url,
                    title=title,
                    snippet=snippet,
                    source_type=source_type,
                    relevance_hint=None,
                )
            )

        return results

    def discover_feeds(self, topic: str, max_results: int = 5) -> List[FeedCandidate]:
        """Discover RSS feeds using topic-based queries.

        Note: This method returns placeholder queries. The actual discovery
        must be performed by the agent using search queries.

        Args:
            topic: Topic to discover feeds for
            max_results: Maximum number of feeds to discover

        Returns:
            List of suggested search queries
        """
        return []

    def get_discovery_queries(self, topic: str) -> List[str]:
        """Get search queries for feed discovery.

        Args:
            topic: Topic to discover feeds for

        Returns:
            List of search queries to try
        """
        queries = [
            f"{topic} RSS feed",
            f"{topic} news feed",
            f"{topic} blog RSS",
            f"best {topic} RSS feeds",
            f"{topic} newsletter RSS",
        ]
        return queries

    def _detect_source_type(self, url: str, content: str) -> SourceType:
        """Detect the type of source from URL and content.

        Args:
            url: Source URL
            content: Content snippet

        Returns:
            Detected SourceType
        """
        url_lower = url.lower()
        content_lower = content.lower() if content else ""

        if any(
            x in url_lower for x in ["/feed", "/rss", "/atom", "feed.xml", "rss.xml"]
        ):
            return SourceType.RSS

        if any(x in content_lower for x in ["<rss", "<atom", "application/rss"]):
            return SourceType.RSS

        blog_indicators = ["blog", "article", "post", "author"]
        if any(x in url_lower for x in blog_indicators):
            return SourceType.BLOG

        news_indicators = ["news", "breaking", "latest", "headline"]
        if any(x in url_lower for x in news_indicators) or any(
            x in content_lower for x in news_indicators
        ):
            return SourceType.NEWS

        return SourceType.UNKNOWN

    def process_feed_candidate(
        self, url: str, title: str, topic: str, discovered_from: str
    ) -> FeedCandidate:
        """Create a FeedCandidate from discovered URL.

        Args:
            url: Feed URL
            title: Feed title
            topic: Topic being searched
            discovered_from: How this feed was discovered

        Returns:
            FeedCandidate object
        """
        source_type = self._detect_source_type(url, "")

        return FeedCandidate(
            url=url,
            name=title or url,
            source_type=source_type,
            discovered_from=discovered_from,
            confidence=0.5,
        )


def main():
    """CLI interface for testing."""
    import argparse

    parser = argparse.ArgumentParser(description="Exa search provider")
    parser.add_argument("--topic", required=True, help="Topic to discover feeds for")
    parser.add_argument("--action", choices=["queries", "test"], default="queries")

    args = parser.parse_args()

    adapter = ExaAdapter()

    if args.action == "queries":
        queries = adapter.get_discovery_queries(args.topic)
        print(json.dumps({"queries": queries}, indent=2))


if __name__ == "__main__":
    main()
