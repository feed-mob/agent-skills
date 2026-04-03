#!/usr/bin/env python3
"""Feed Agent - Autonomous RSS/content aggregator with self-evolution capabilities."""

__version__ = "1.0.0"

from .search_provider import SearchProvider, SearchResult, FeedCandidate, SourceType
from .exa_adapter import ExaAdapter
from .browser_adapter import BrowserAdapter
from .db import Source, Article, init_db, get_sources, get_articles
from .scout import run_scout, discover_feeds_exa, discover_feeds_browser
from .fetcher import run_fetch, store_articles
from .analyzer import run_analysis, store_analysis
from .evolution import run_evolution, apply_evolution
from .reporter import generate_report
from .pipeline import run_pipeline, init_topic, load_config

__all__ = [
    "SearchProvider",
    "SearchResult",
    "FeedCandidate",
    "SourceType",
    "ExaAdapter",
    "BrowserAdapter",
    "Source",
    "Article",
    "init_db",
    "get_sources",
    "get_articles",
    "run_scout",
    "discover_feeds_exa",
    "discover_feeds_browser",
    "run_fetch",
    "store_articles",
    "run_analysis",
    "store_analysis",
    "run_evolution",
    "apply_evolution",
    "generate_report",
    "run_pipeline",
    "init_topic",
    "load_config",
]
