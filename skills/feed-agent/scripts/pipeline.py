#!/usr/bin/env python3
"""Main pipeline orchestrator for feed-agent."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))

import yaml

from db import init_db, get_stats, get_sources, upsert_source, Source, add_keyword
from scout import run_scout, add_candidates_to_db
from fetcher import run_fetch, store_articles
from analyzer import run_analysis, store_analysis
from evolution import run_evolution, apply_evolution
from reporter import generate_report


def load_config(project_root: Path) -> Dict[str, Any]:
    """Load configuration from feed-agent.yaml.

    Args:
        project_root: Project root directory

    Returns:
        Configuration dict
    """
    config_path = project_root / "config" / "feed-agent.yaml"

    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)

    # Default configuration
    return {
        "topic": None,
        "version": "1.0",
        "providers": {
            "enabled": ["exa", "browser"],
            "exa": {"max_results": 10, "use_autosuggestions": True},
            "browser": {"headless": True, "timeout": 30},
        },
        "scoring": {
            "threshold": 7,
            "history_days": 30,
            "min_sources": 3,
        },
        "evolution": {
            "auto_add_threshold": 0.7,
            "prune_threshold": 0.3,
            "prune_consecutive": 3,
            "scout_interval_days": 7,
        },
        "reporting": {
            "output_dir": "reports/{topic}",
            "format": "markdown",
            "include_links": True,
            "max_articles": 20,
        },
        "keywords": {
            "auto_add": False,
            "auto_promote_min_confidence": 0.7,
            "auto_promote_min_occurrences": 2,
            "max_suggested": 10,
            "min_frequency": 3,
        },
    }


def save_config(project_root: Path, config: Dict[str, Any]) -> None:
    """Save configuration to feed-agent.yaml.

    Args:
        project_root: Project root directory
        config: Configuration dict
    """
    config_path = project_root / "config" / "feed-agent.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)


def init_topic(
    project_root: Path, topic: str, config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Initialize a new topic.

    Args:
        project_root: Project root directory
        topic: Topic to initialize
        config: Optional configuration

    Returns:
        Initialization result
    """
    # Initialize database
    db_path = init_db(project_root, topic)

    # Update config with topic
    if config:
        config["topic"] = topic
        save_config(project_root, config)
    else:
        config = load_config(project_root)
        config["topic"] = topic
        save_config(project_root, config)

    # Create directories
    sources_dir = project_root / "sources" / "feeds" / topic.replace(" ", "_").lower()
    sources_dir.mkdir(parents=True, exist_ok=True)

    reports_dir = project_root / "reports" / topic.replace(" ", "_").lower()
    reports_dir.mkdir(parents=True, exist_ok=True)

    return {
        "status": "initialized",
        "topic": topic,
        "db_path": str(db_path),
        "sources_dir": str(sources_dir),
        "reports_dir": str(reports_dir),
    }


def add_manual_source(
    project_root: Path, topic: str, url: str, name: str = None
) -> Dict[str, Any]:
    """Manually add a source.

    Args:
        project_root: Project root directory
        topic: Current topic
        url: Source URL
        name: Optional source name

    Returns:
        Result dict
    """
    source = Source(
        id=None,
        topic=topic,
        url=url,
        name=name or url,
        provider="manual",
        source_type="rss",
        status="active",
        quality_score=0.5,
    )

    source_id = upsert_source(project_root, source)

    return {
        "status": "added",
        "source_id": source_id,
        "url": url,
        "name": name or url,
    }


def run_pipeline(
    project_root: Path,
    topic: str = None,
    action: str = "full",
    as_of_date: str | None = None,
    window_days: int = 7,
) -> Dict[str, Any]:
    """Run the complete feed-agent pipeline.

    Note: This returns instructions for the agent to execute.
    The actual tool calls (exa, webfetch, LLM) must be made by the agent.

    Args:
        project_root: Project root directory
        topic: Topic to process
        action: Pipeline action (full, scout, fetch, analyze, report, evolve)

    Returns:
        Dict with instructions for each step
    """
    config = load_config(project_root)

    if not topic:
        topic = config.get("topic")
        if not topic:
            return {
                "error": "No topic configured. Run with --topic or use 'init' action."
            }

    steps = []

    if action in ["full", "scout"]:
        # Scout for new sources
        for provider in config.get("providers", {}).get("enabled", ["exa"]):
            steps.append(
                {
                    "step": "scout",
                    "provider": provider,
                    "instructions": run_scout(topic, project_root, provider),
                }
            )

    if action in ["full", "fetch", "report"]:
        # Fetch content from sources
        steps.append(
            {
                "step": "fetch",
                "instructions": run_fetch(topic, project_root),
            }
        )

    if action in ["full", "analyze", "report"]:
        # Analyze and score articles
        threshold = config.get("scoring", {}).get("threshold", 7)
        steps.append(
            {
                "step": "analyze",
                "instructions": run_analysis(topic, project_root, threshold),
            }
        )

    if action in ["full", "report"]:
        # Generate report
        target_date = as_of_date or datetime.now().strftime("%Y-%m-%d")
        report_path = (
            project_root
            / "reports"
            / topic.replace(" ", "_").lower()
            / f"{target_date}.md"
        )
        steps.append(
            {
                "step": "report",
                "report_path": str(report_path),
                "instructions": (
                    "Generate report using reporter.py "
                    f"--topic \"{topic}\" --output {report_path} "
                    f"--as-of-date {target_date} --window-days {window_days}"
                ),
            }
        )

    if action in ["full", "evolve"]:
        # Run self-evolution
        steps.append(
            {
                "step": "evolve",
                "instructions": run_evolution(topic, project_root),
            }
        )

    return {
        "topic": topic,
        "action": action,
        "steps": steps,
        "config": config,
    }


def get_next_steps_after_scout(
    project_root: Path, topic: str, candidates: list
) -> Dict[str, Any]:
    """Get instructions for processing scout results.

    Args:
        project_root: Project root directory
        topic: Current topic
        candidates: List of discovered candidates

    Returns:
        Next step instructions
    """
    return {
        "action": "store_candidates",
        "instructions": f"""
            Save the discovered candidates to the database:
            
            python3 scripts/scout.py --project-root {project_root} --topic "{topic}" --action store
            
            Then decide which candidates to validate:
            - If confidence > 0.7: Promote to active immediately
            - If confidence 0.5-0.7: Add as candidate for validation
            - If confidence < 0.5: Skip
            
            After validation, run fetch to get content.
        """,
        "candidates": candidates,
    }


def get_next_steps_after_fetch(
    project_root: Path, topic: str, articles: list
) -> Dict[str, Any]:
    """Get instructions for processing fetch results.

    Args:
        project_root: Project root directory
        topic: Current topic
        articles: List of fetched articles

    Returns:
        Next step instructions
    """
    return {
        "action": "analyze_articles",
        "instructions": f"""
            For each article fetched:
            
            1. Use the LLM with the scoring prompt to evaluate relevance
            2. Parse the JSON response
            3. Store results using analyzer.py --action store
            
            Articles with score >= 7 will be included in the report.
        """,
        "article_count": len(articles),
    }


def get_next_steps_after_analysis(
    project_root: Path, topic: str, results: list
) -> Dict[str, Any]:
    """Get instructions for processing analysis results.

    Args:
        project_root: Project root directory
        topic: Current topic
        results: List of analysis results

    Returns:
        Next step instructions
    """
    promoted = [r for r in results if r.get("relevance_score", 0) >= 7]
    filtered = [r for r in results if r.get("relevance_score", 0) < 7]

    return {
        "action": "generate_report",
        "instructions": f"""
            Analysis complete:
            - Promoted: {len(promoted)} articles (score >= 7)
            - Filtered: {len(filtered)} articles (score < 7)
            
            Next step: Generate the markdown report
            
            python3 scripts/reporter.py --project-root {project_root} --topic "{topic}"
        """,
        "promoted_count": len(promoted),
        "filtered_count": len(filtered),
    }


def main():
    parser = argparse.ArgumentParser(description="Feed-agent pipeline orchestrator")
    parser.add_argument(
        "--project-root", type=Path, required=True, help="Project root directory"
    )
    parser.add_argument("--topic", help="Topic to process")
    parser.add_argument(
        "--action",
        choices=[
            "init",
            "config",
            "full",
            "scout",
            "fetch",
            "analyze",
            "report",
            "evolve",
            "add-source",
        ],
        default="full",
        help="Pipeline action",
    )
    parser.add_argument("--url", help="URL for add-source action")
    parser.add_argument("--name", help="Name for add-source action")
    parser.add_argument(
        "--as-of-date", help="Target date for date-anchored reporting (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--window-days",
        type=int,
        default=7,
        help="Inclusive day window ending on --as-of-date",
    )

    args = parser.parse_args()

    if args.action == "init":
        if not args.topic:
            print(
                json.dumps({"error": "Topic required for init action"}), file=sys.stderr
            )
            sys.exit(1)
        result = init_topic(args.project_root, args.topic)
        print(json.dumps(result, indent=2))

    elif args.action == "config":
        config = load_config(args.project_root)
        print(json.dumps(config, indent=2))

    elif args.action == "add-source":
        if not args.topic or not args.url:
            print(
                json.dumps({"error": "Topic and URL required for add-source action"}),
                file=sys.stderr,
            )
            sys.exit(1)
        result = add_manual_source(args.project_root, args.topic, args.url, args.name)
        print(json.dumps(result, indent=2))

    elif args.action == "stats":
        if not args.topic:
            print(
                json.dumps({"error": "Topic required for stats action"}),
                file=sys.stderr,
            )
            sys.exit(1)
        stats = get_stats(args.project_root, args.topic)
        print(json.dumps(stats, indent=2))

    else:
        result = run_pipeline(
            args.project_root,
            args.topic,
            args.action,
            args.as_of_date,
            args.window_days,
        )
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
