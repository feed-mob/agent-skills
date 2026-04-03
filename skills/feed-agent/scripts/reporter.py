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
    get_active_keywords,
    get_articles,
    get_candidate_keywords,
    get_sources,
    get_stats,
    Article,
)


REPORT_TEMPLATE = """# {topic} Intelligence Report

**Date:** {date}  
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


def generate_report(
    topic: str, project_root: Path, threshold: int = 7, output_path: Path = None
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

    articles = get_articles(project_root, topic, min_score=threshold, days=1, limit=50)
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
        sources_count=stats.get("active_sources", 0),
        articles_count=stats.get("total_articles", 0),
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

    args = parser.parse_args()

    if not args.output:
        args.output = (
            args.project_root
            / "reports"
            / args.topic.replace(" ", "_").lower()
            / f"{datetime.now().strftime('%Y-%m-%d')}.md"
        )

    report = generate_report(args.topic, args.project_root, args.threshold, args.output)

    result = {
        "report_path": str(args.output),
        "generated_at": datetime.now().isoformat(),
        "article_count": len(
            get_articles(args.project_root, args.topic, min_score=args.threshold)
        ),
    }

    print(json.dumps(result, indent=2))
    print("\n---\n")
    print(report)


if __name__ == "__main__":
    main()
