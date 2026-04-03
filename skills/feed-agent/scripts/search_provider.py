#!/usr/bin/env python3
"""Abstract base class for search providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class SourceType(Enum):
    RSS = "rss"
    BLOG = "blog"
    NEWS = "news"
    UNKNOWN = "unknown"


@dataclass
class SearchResult:
    url: str
    title: str
    snippet: str
    source_type: SourceType
    relevance_hint: Optional[float] = None


@dataclass
class FeedCandidate:
    url: str
    name: str
    source_type: SourceType
    discovered_from: str
    confidence: float = 0.5


class SearchProvider(ABC):
    """Base class for search providers.

    Implementations should provide search and feed discovery capabilities.
    Each provider has a unique identifier and configuration options.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier (e.g., 'exa', 'browser')."""
        pass

    @abstractmethod
    def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search for content related to query.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of SearchResult objects
        """
        pass

    @abstractmethod
    def discover_feeds(self, topic: str, max_results: int = 5) -> List[FeedCandidate]:
        """Discover RSS/feed URLs for a topic.

        Args:
            topic: Topic to discover feeds for
            max_results: Maximum number of feeds to discover

        Returns:
            List of FeedCandidate objects
        """
        pass

    def validate_feed_url(self, url: str) -> bool:
        """Check if a URL returns valid RSS/Atom content.

        Args:
            url: URL to validate

        Returns:
            True if URL appears to be a valid feed
        """
        import urllib.request
        import urllib.error

        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0 (compatible; FeedAgent/1.0)"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                content_type = response.headers.get("Content-Type", "")
                content = response.read(1000).decode("utf-8", errors="ignore")

                rss_indicators = [
                    "<rss",
                    "<feed",
                    "<atom",
                    "xmlns:atom",
                    "application/rss",
                    "application/atom",
                ]
                return any(
                    indicator in content_type.lower() or indicator in content.lower()
                    for indicator in rss_indicators
                )
        except Exception:
            return False

    def extract_feed_links(self, html_content: str, base_url: str) -> List[str]:
        """Extract RSS/Atom feed links from HTML content.

        Args:
            html_content: HTML to parse
            base_url: Base URL for resolving relative links

        Returns:
            List of feed URLs found
        """
        import re
        from urllib.parse import urljoin

        feeds = []

        link_patterns = [
            r'<link[^>]+type=["\']application/(rss|atom)\+xml["\'][^>]+href=["\']([^"\']+)["\']',
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]+type=["\']application/(rss|atom)\+xml["\']',
            r'<a[^>]+href=["\']([^"\']+(?:rss|feed|atom)[^"\']*)["\']',
        ]

        for pattern in link_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                url = match[-1] if isinstance(match, tuple) else match
                full_url = urljoin(base_url, url)
                if full_url not in feeds:
                    feeds.append(full_url)

        return feeds


class SearchProviderError(Exception):
    """Base exception for search provider errors."""

    pass


class SearchProviderTimeout(SearchProviderError):
    """Search operation timed out."""

    pass


class SearchProviderRateLimit(SearchProviderError):
    """Rate limit exceeded."""

    pass
