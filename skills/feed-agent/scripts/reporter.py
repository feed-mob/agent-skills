#!/usr/bin/env python3
"""Markdown report generation for feed-agent."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent))

from db import (
    build_story_key,
    create_report_run,
    get_active_keywords,
    get_articles,
    get_candidate_keywords,
    get_date_window,
    get_reported_story_keys,
    get_sources,
    get_stats,
    record_report_items,
    Article,
)


REPORT_TEMPLATE = """# {topic} Intelligence Report

**Date:** {date}  
**As Of:** {as_of_date} | **Coverage Window:** {window_start} to {window_end}  
**Freshness Basis:** published date (fallback: fetch date)  
**Sources Scanned:** {sources_count} | **Articles Found:** {articles_count} | **Promoted (>={threshold}):** {promoted_count}

---

## Core Insights

> Top insights from all promoted articles

{insights_table}

---

## Detailed Analysis

{detailed_analysis}

---

## Self-Evolution

### Source Quality Update

{source_quality_table}

### Keyword Adjustments

{keyword_adjustments}

---

## Pending Actions

{pending_actions}
"""


def format_insights_table(articles: List[Article]) -> str:
    """Format the core insights as a table.

    Args:
        articles: List of promoted articles

    Returns:
        Markdown table string
    """
    if not articles:
        return "*No articles met the promotion threshold*"

    rows = ["| # | Insight | Source | New? |", "|---|---------|--------|------|"]

    for i, article in enumerate(articles[:10], 1):
        new_marker = "Yes" if article.is_new_insight else "No"
        insight = article.core_points[0] if article.core_points else article.title
        if len(insight) > 100:
            insight = insight[:97] + "..."
        source = article.title[:50] if len(article.title) > 50 else article.title
        rows.append(f"| {i} | {insight} | {source} | {new_marker} |")

    return "\n".join(rows)


def format_detailed_analysis(articles: List[Article], threshold: int) -> str:
    """Format detailed analysis for each promoted article.

    Args:
        articles: List of promoted articles
        threshold: Minimum score threshold

    Returns:
        Markdown string
    """
    if not articles:
        return "*No articles met the promotion threshold*"

    sections = []

    for article in articles:
        new_badge = "**[NEW]**" if article.is_new_insight else ""

        section = f"""### {article.title}
**Score:** {article.relevance_score}/{threshold + 3} | **Source:** {article.title[:50]} | **New Insight:** {"Yes" if article.is_new_insight else "No"} {new_badge}

**Core Points:**
"""
        for point in (article.core_points or [])[:5]:
            section += f"- {point}\n"

        if article.reasoning:
            section += f"\n**Why Relevant:** {article.reasoning}\n"

        section += f"\n**Link:** [{article.url}]({article.url})\n"

        sections.append(section)

    return "\n---\n\n".join(sections)


def format_source_quality_table(sources: List, stats: Dict) -> str:
    """Format source quality as a table.

    Args:
        sources: List of source objects
        stats: Statistics dict

    Returns:
        Markdown table string
    """
    rows = [
        "| Source | Avg Score | Status | Action |",
        "|--------|-----------|--------|--------|",
    ]

    for source in sources[:10]:
        name = source.name[:30] if len(source.name) > 30 else source.name
        score = f"{source.quality_score:.2f}" if source.quality_score else "N/A"

        if source.status == "active":
            if source.quality_score and source.quality_score < 0.3:
                status = "Warning"
                action = "Monitor"
            else:
                status = "Active"
                action = "Maintained"
        elif source.status == "candidate":
            status = "Candidate"
            action = "Pending validation"
        else:
            status = "Pruned"
            action = "Removed"

        rows.append(f"| {name} | {score} | {status} | {action} |")

    return "\n".join(rows)


def format_keyword_adjustments(
    suggested_keywords: List[str],
    active_keywords: List[str],
    candidate_keywords: List[str],
    added: List[str] = None,
) -> str:
    """Format keyword adjustment section.

    Args:
        suggested_keywords: List of suggested keywords
        added: List of keywords that were added

    Returns:
        Markdown string
    """
    if (
        not suggested_keywords
        and not added
        and not active_keywords
        and not candidate_keywords
    ):
        return "*No keyword adjustments suggested*"

    lines = []

    if active_keywords:
        lines.append(f"- **Active Keywords:** {', '.join(active_keywords[:8])}")

    if candidate_keywords:
        lines.append(f"- **Candidate Keywords:** {', '.join(candidate_keywords[:8])}")

    if added:
        lines.append(f"- **Added:** {', '.join(added)}")

    if suggested_keywords:
        lines.append(f"- **Suggested:** {', '.join(suggested_keywords[:5])}")
        lines.append(f"- **Reasoning:** Frequently appearing in high-scoring articles")

    return "\n".join(lines)


def format_pending_actions(
    prune_candidates: List, promote_candidates: List, suggested_keywords: List
) -> str:
    """Format pending actions section.

    Args:
        prune_candidates: Sources to potentially prune
        promote_candidates: Sources to potentially promote
        suggested_keywords: Suggested new keywords

    Returns:
        Markdown string
    """
    actions = []

    if promote_candidates:
        actions.append(
            f"- [ ] **Sources to promote:** {len(promote_candidates)} candidate(s) awaiting approval"
        )
        for c in promote_candidates[:3]:
            actions.append(
                f"  - {c.get('name', c.get('url'))} (score: {c.get('quality_score', 'N/A')})"
            )

    if prune_candidates:
        actions.append(
            f"- [ ] **Sources to review:** {len(prune_candidates)} source(s) with low quality scores"
        )
        for c in prune_candidates[:3]:
            actions.append(
                f"  - {c.get('name', c.get('url'))} (score: {c.get('quality_score', 'N/A')})"
            )

    if suggested_keywords:
        actions.append(
            f"- [ ] **Keywords to add:** {len(suggested_keywords)} suggestion(s)"
        )
        actions.append(f"  - {', '.join(suggested_keywords[:5])}")

    if not actions:
        return "*No pending actions*"

    return "\n".join(actions)


def select_report_articles(
    articles: List[Article], reported_story_keys: set[str], include_repeats: bool = False
) -> List[Article]:
    """Choose the canonical article for each reportable story."""
    selected = []
    seen_story_keys = set()

    for article in articles:
        article.story_key = article.story_key or build_story_key(
            article.title, article.core_points
        )
        article.story_status = article.story_status or "new"

        if article.story_key in seen_story_keys:
            continue
        if (
            not include_repeats
            and article.story_key in reported_story_keys
            and article.story_status != "continuation"
        ):
            continue

        seen_story_keys.add(article.story_key)
        selected.append(article)

    return selected


def generate_report(
    topic: str,
    project_root: Path,
    threshold: int = 7,
    output_path: Path = None,
    as_of_date: str | None = None,
    window_days: int = 7,
    include_repeats: bool = False,
    persist: bool = True,
) -> str:
    """Generate the markdown intelligence report.

    Args:
        topic: Current topic
        project_root: Project root directory
        threshold: Minimum score threshold
        output_path: Optional path to save report

    Returns:
        Generated markdown report
    """
    from evolution import (
        calculate_source_quality,
        extract_new_keywords,
        identify_prune_candidates,
        identify_promote_candidates,
    )

    window_start, window_end = get_date_window(as_of_date, window_days)
    window_articles = get_articles(
        project_root,
        topic,
        min_score=threshold,
        days=window_days,
        limit=100,
        as_of_date=window_end,
    )
    reported_story_keys = get_reported_story_keys(project_root, topic, before_date=window_end)
    articles = select_report_articles(
        window_articles, reported_story_keys, include_repeats=include_repeats
    )
    sources = get_sources(project_root, topic)
    stats = get_stats(project_root, topic)

    metrics = calculate_source_quality(project_root, topic)
    prune_candidates = identify_prune_candidates(metrics)
    promote_candidates = identify_promote_candidates(metrics)
    suggested_keywords = extract_new_keywords(project_root, topic)
    active_keywords = get_active_keywords(project_root, topic, limit=10)
    candidate_keywords = get_candidate_keywords(project_root, topic, limit=10)

    insights_table = format_insights_table(articles)
    detailed_analysis = format_detailed_analysis(articles, threshold)
    source_quality_table = format_source_quality_table(sources, stats)
    keyword_adjustments = format_keyword_adjustments(
        suggested_keywords,
        active_keywords,
        candidate_keywords,
    )
    pending_actions = format_pending_actions(
        prune_candidates, promote_candidates, suggested_keywords
    )

    report = REPORT_TEMPLATE.format(
        topic=topic.title(),
        date=datetime.now().strftime("%Y-%m-%d"),
        as_of_date=window_end,
        window_start=window_start,
        window_end=window_end,
        sources_count=stats.get("active_sources", 0),
        articles_count=len(window_articles),
        promoted_count=len(articles),
        threshold=threshold,
        insights_table=insights_table,
        detailed_analysis=detailed_analysis,
        source_quality_table=source_quality_table,
        keyword_adjustments=keyword_adjustments,
        pending_actions=pending_actions,
    )

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)

    if persist:
        report_id = create_report_run(
            project_root, topic, window_end, window_start, window_end, threshold
        )
        record_report_items(project_root, topic, report_id, articles)

    return report


def main():
    parser = argparse.ArgumentParser(description="Report generation for feed-agent")
    parser.add_argument(
        "--project-root", type=Path, required=True, help="Project root directory"
    )
    parser.add_argument("--topic", required=True, help="Topic")
    parser.add_argument(
        "--threshold", type=int, default=7, help="Minimum score threshold"
    )
    parser.add_argument("--output", type=Path, help="Output path for report")
    parser.add_argument(
        "--as-of-date", help="Target date for the report window (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--window-days",
        type=int,
        default=7,
        help="Inclusive day window ending on --as-of-date",
    )
    parser.add_argument(
        "--include-repeats",
        action="store_true",
        help="Include stories that appeared in earlier reports",
    )

    args = parser.parse_args()

    target_date = args.as_of_date or datetime.now().strftime("%Y-%m-%d")

    if not args.output:
        args.output = (
            args.project_root
            / "reports"
            / args.topic.replace(" ", "_").lower()
            / f"{target_date}.md"
        )

    window_articles = get_articles(
        args.project_root,
        args.topic,
        min_score=args.threshold,
        days=args.window_days,
        limit=100,
        as_of_date=target_date,
    )
    prior_story_keys = get_reported_story_keys(
        args.project_root, args.topic, before_date=target_date
    )
    selected_articles = select_report_articles(
        window_articles,
        prior_story_keys,
        include_repeats=args.include_repeats,
    )
    report = generate_report(
        args.topic,
        args.project_root,
        args.threshold,
        args.output,
        as_of_date=target_date,
        window_days=args.window_days,
        include_repeats=args.include_repeats,
    )

    result = {
        "report_path": str(args.output),
        "generated_at": datetime.now().isoformat(),
        "as_of_date": target_date,
        "window_days": args.window_days,
        "article_count": len(selected_articles),
    }

    print(json.dumps(result, indent=2))
    print("\n---\n")
    print(report)


if __name__ == "__main__":
    main()
