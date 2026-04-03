#!/usr/bin/env python3
"""Source discovery and validation for feed-agent."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))

from db import (
    upsert_source,
    get_sources,
    init_db,
    log_evolution,
    get_active_keywords,
    Source,
)
from search_provider import FeedCandidate, SourceType


def get_exa_discovery_queries(
    topic: str, keywords: Optional[List[str]] = None, max_keywords: int = 5
) -> List[str]:
    """Generate search queries for feed discovery.

    Args:
        topic: Topic to discover feeds for

    Returns:
        List of search queries
    """
    queries = [
        f"{topic} RSS feed",
        f"{topic} news feed subscribe",
        f"{topic} blog RSS",
        f"best {topic} blogs RSS",
        f"{topic} newsletter RSS",
        f"site:medium.com {topic}",
        f"site:substack.com {topic}",
    ]

    for keyword in (keywords or [])[:max_keywords]:
        queries.extend(
            [
                f"{topic} {keyword} RSS feed",
                f"{topic} {keyword} blog",
                f"{topic} {keyword} newsletter",
            ]
        )

    return list(dict.fromkeys(queries))


def process_exa_results(results: List[Dict], topic: str) -> List[FeedCandidate]:
    """Process results from Exa search into feed candidates.

    Args:
        results: Raw results from exa_web_search_exa
        topic: Current topic

    Returns:
        List of FeedCandidate objects
    """
    candidates = []

    for result in results:
        url = result.get("url", "")
        title = result.get("title", "")
        snippet = result.get("content", "") or result.get("snippet", "")

        # Detect if this is a feed URL
        is_feed = any(
            x in url.lower() for x in ["/feed", "/rss", "/atom", "feed.xml", "rss.xml"]
        )

        # Detect source type
        source_type = SourceType.RSS if is_feed else SourceType.UNKNOWN
        if "blog" in url.lower() or "blog" in title.lower():
            source_type = SourceType.BLOG
        elif "news" in url.lower() or "news" in title.lower():
            source_type = SourceType.NEWS

        candidates.append(
            FeedCandidate(
                url=url,
                name=title or url,
                source_type=source_type,
                discovered_from="exa",
                confidence=0.7 if is_feed else 0.5,
            )
        )

    return candidates


def validate_candidate(candidate: FeedCandidate) -> bool:
    """Validate if a candidate URL is a valid RSS/Atom feed.

    Args:
        candidate: Feed candidate to validate

    Returns:
        True if valid feed URL
    """
    import urllib.request
    import urllib.error

    url = candidate.url

    # Quick check for obvious feed URLs
    feed_indicators = ["/feed", "/rss", "/atom", "feed.xml", "rss.xml", "atom.xml"]
    if any(x in url.lower() for x in feed_indicators):
        return True

    # Try to fetch and validate
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (compatible; FeedAgent/1.0)"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            content_type = response.headers.get("Content-Type", "")
            content = response.read(2000).decode("utf-8", errors="ignore")

            # Check for feed indicators in content
            feed_indicators = [
                "<rss",
                "<feed",
                "<atom:",
                "application/rss",
                "application/atom",
            ]
            has_feed = any(
                x in content_type.lower() or x in content.lower()
                for x in feed_indicators
            )

            return has_feed
    except Exception:
        return False


def score_candidate_relevance(candidate: FeedCandidate, topic: str) -> float:
    """Score candidate relevance to topic using LLM.

    Note: The actual LLM call should be made by the agent.
    This function returns a default score based on URL/title analysis.

    Args:
        candidate: Feed candidate
        topic: Current topic

    Returns:
        Relevance score (0-1)
    """
    url_lower = candidate.url.lower()
    title_lower = candidate.name.lower()
    topic_lower = topic.lower()
    topic_words = set(topic_lower.split())

    score = 0.5

    # Check for topic match in URL
    if topic_lower in url_lower:
        score += 0.2

    # Check for topic words in title
    title_words = set(title_lower.split())
    overlap = len(topic_words & title_words)
    score += min(overlap * 0.1, 0.3)

    # Bonus for RSS-specific URLs
    if any(x in url_lower for x in ["/feed", "/rss", "feed.xml"]):
        score += 0.1

    return min(score, 1.0)


def discover_feeds_exa(
    topic: str, project_root: Path, max_candidates: int = 10
) -> Dict[str, Any]:
    """Instruction for discovering feeds using Exa.

    Returns instructions for the agent to execute using exa_web_search_exa tool.

    Args:
        topic: Topic to discover feeds for
        project_root: Project root directory
        max_candidates: Maximum candidates to return

    Returns:
        Dict with instructions and candidate storage path
    """
    active_keywords = get_active_keywords(project_root, topic, limit=5)
    queries = get_exa_discovery_queries(topic, active_keywords)

    db_path = init_db(project_root, topic)
    candidates_path = (
        project_root
        / "sources"
        / "feeds"
        / topic.replace(" ", "_").lower()
        / "candidates.json"
    )
    candidates_path.parent.mkdir(parents=True, exist_ok=True)

    return {
        "tool": "exa_web_search_exa",
        "queries": queries,
        "active_keywords": active_keywords,
        "max_candidates": max_candidates,
        "instructions": f"""
            For each query in the list, use exa_web_search_exa with:
            - query: The search query
            - numResults: 10
            - category: Use "auto" for general searches
            
            Collect all results and filter for:
            1. URLs that contain RSS/feed indicators
            2. URLs from content sites (blogs, news, publications)
            3. URLs relevant to: {topic}
            4. Prefer results matching tracked keywords: {", ".join(active_keywords) if active_keywords else "none"}
            
            Save candidates to: {candidates_path}
            
            Format:
            {{
                "topic": "{topic}",
                "discovered_at": "<timestamp>",
                "candidates": [
                    {{"url": "...", "name": "...", "source_type": "rss|blog|news", "confidence": 0.5-1.0}}
                ]
            }}
        """,
        "output_path": str(candidates_path),
    }


def discover_feeds_browser(topic: str, project_root: Path) -> Dict[str, Any]:
    """Instruction for discovering feeds using browser automation.

    Returns instructions for the agent to execute using agent-browser skill.

    Args:
        topic: Topic to discover feeds for
        project_root: Project root directory

    Returns:
        Dict with instructions
    """
    active_keywords = get_active_keywords(project_root, topic, limit=5)
    candidates_path = (
        project_root
        / "sources"
        / "feeds"
        / topic.replace(" ", "_").lower()
        / "candidates.json"
    )

    return {
        "tool": "agent-browser",
        "instructions": f"""
            Use the agent-browser skill to:
            
            1. Search for "{topic} RSS feed" on Google or DuckDuckGo
            2. Also search for keyword-driven variations when useful: {", ".join(active_keywords) if active_keywords else "none"}
            3. Visit the top 5 search results
            4. For each page, look for:
               - <link rel="alternate" type="application/rss+xml"> tags
               - Links containing /feed, /rss, /atom
               - RSS icons in the page header/footer
            5. Extract any feed URLs found
            6. Save candidates to: {candidates_path}
            
            Format:
            {{
                "topic": "{topic}",
                "discovered_at": "<timestamp>",
                "candidates": [
                    {{"url": "...", "name": "...", "source_type": "rss|blog|news"}}
                ]
            }}
        """,
        "output_path": str(candidates_path),
    }


def add_candidates_to_db(project_root: Path, topic: str, candidates: List[Dict]) -> int:
    """Add discovered candidates to database as 'candidate' status.

    Args:
        project_root: Project root directory
        topic: Current topic
        candidates: List of candidate dicts

    Returns:
        Number of candidates added
    """
    added = 0

    for c in candidates:
        source = Source(
            id=None,
            topic=topic,
            url=c["url"],
            name=c.get("name", c["url"]),
            provider=c.get("discovered_from", "manual"),
            source_type=c.get("source_type", "unknown"),
            quality_score=c.get("confidence", 0.5),
            status="candidate",
        )

        try:
            upsert_source(project_root, source)
            added += 1
        except Exception as e:
            print(f"Warning: Could not add candidate {c['url']}: {e}", file=sys.stderr)

    # Log evolution
    log_evolution(
        project_root,
        topic,
        "candidates_discovered",
        {"count": added, "sources": [c["url"] for c in candidates[:5]]},
    )

    return added


def promote_candidate(project_root: Path, topic: str, url: str) -> bool:
    """Promote a candidate source to active status.

    Args:
        project_root: Project root directory
        topic: Current topic
        url: Candidate URL to promote

    Returns:
        True if promoted successfully
    """
    sources = get_sources(project_root, topic, status="candidate")

    for source in sources:
        if source.url == url:
            source.status = "active"
            upsert_source(project_root, source)
            log_evolution(project_root, topic, "source_promoted", {"url": url})
            return True

    return False


def run_scout(topic: str, project_root: Path, provider: str = "exa") -> Dict[str, Any]:
    """Run the scouting process.

    Note: This returns instructions for the agent. The agent must execute
    the actual search using the appropriate tool.

    Args:
        topic: Topic to discover feeds for
        project_root: Project root directory
        provider: Search provider to use

    Returns:
        Dict with instructions
    """
    init_db(project_root, topic)

    if provider == "exa":
        return discover_feeds_exa(topic, project_root)
    elif provider == "browser":
        return discover_feeds_browser(topic, project_root)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def main():
    parser = argparse.ArgumentParser(description="Source discovery for feed-agent")
    parser.add_argument(
        "--project-root", type=Path, required=True, help="Project root directory"
    )
    parser.add_argument("--topic", required=True, help="Topic to discover feeds for")
    parser.add_argument(
        "--provider", default="exa", choices=["exa", "browser"], help="Search provider"
    )
    parser.add_argument("--action", choices=["discover", "promote"], default="discover")
    parser.add_argument("--url", help="URL to promote (for promote action)")

    args = parser.parse_args()

    if args.action == "discover":
        result = run_scout(args.topic, args.project_root, args.provider)
        print(json.dumps(result, indent=2))

    elif args.action == "promote":
        if not args.url:
            print(
                json.dumps({"error": "URL required for promote action"}),
                file=sys.stderr,
            )
            sys.exit(1)
        success = promote_candidate(args.project_root, args.topic, args.url)
        print(json.dumps({"promoted": success, "url": args.url}))


if __name__ == "__main__":
    main()
