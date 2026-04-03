#!/usr/bin/env python3
"""Self-evolution logic for feed-agent."""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent))

from db import (
    get_active_keywords,
    get_candidate_keywords,
    get_sources,
    get_stats,
    get_keywords,
    add_keyword,
    promote_keyword,
    reject_keyword,
    log_evolution,
    init_db,
    Source,
)


def calculate_source_quality(project_root: Path, topic: str) -> List[Dict]:
    """Calculate quality metrics for all sources.

    Args:
        project_root: Project root directory
        topic: Current topic

    Returns:
        List of source quality metrics
    """
    import sqlite3

    db_path = (
        project_root / "data" / "feed_agent" / f"{topic.replace(' ', '_').lower()}.db"
    )
    if not db_path.exists():
        return []

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get quality metrics for each source
    cursor.execute(
        """
        SELECT 
            s.id,
            s.url,
            s.name,
            s.quality_score,
            s.relevance_avg,
            s.total_articles,
            s.promoted_articles,
            s.low_score_runs,
            s.status,
            COUNT(CASE WHEN a.relevance_score >= 7 THEN 1 END) as recent_promoted,
            COUNT(a.id) as recent_total,
            AVG(a.relevance_score) as recent_avg_score
        FROM sources s
        LEFT JOIN articles a ON s.id = a.source_id 
            AND a.fetched_at >= date('now', '-7 days')
        WHERE s.topic = ?
        GROUP BY s.id
        ORDER BY s.quality_score DESC
    """,
        (topic,),
    )

    rows = cursor.fetchall()
    conn.close()

    metrics = []
    for row in rows:
        avg_score = row["recent_avg_score"] or row["relevance_avg"] or 0.5

        metrics.append(
            {
                "id": row["id"],
                "url": row["url"],
                "name": row["name"],
                "quality_score": row["quality_score"],
                "relevance_avg": row["relevance_avg"],
                "total_articles": row["total_articles"],
                "promoted_articles": row["promoted_articles"],
                "recent_promoted": row["recent_promoted"] or 0,
                "recent_total": row["recent_total"] or 0,
                "recent_avg_score": avg_score,
                "low_score_runs": row["low_score_runs"],
                "status": row["status"],
            }
        )

    return metrics


def identify_prune_candidates(
    metrics: List[Dict], threshold: float = 0.3, min_runs: int = 3
) -> List[Dict]:
    """Identify sources that should be pruned.

    Args:
        metrics: Source quality metrics
        threshold: Minimum quality score threshold
        min_runs: Minimum consecutive low-score runs

    Returns:
        List of sources to prune
    """
    candidates = []

    for m in metrics:
        if m["status"] != "active":
            continue

        # Check if consistently low quality
        if m["quality_score"] < threshold and m["low_score_runs"] >= min_runs - 1:
            candidates.append(
                {
                    "url": m["url"],
                    "name": m["name"],
                    "quality_score": m["quality_score"],
                    "low_score_runs": m["low_score_runs"],
                    "reason": f"Quality score ({m['quality_score']:.2f}) below threshold ({threshold}) for {m['low_score_runs']} runs",
                }
            )

    return candidates


def identify_promote_candidates(
    metrics: List[Dict], threshold: float = 0.7
) -> List[Dict]:
    """Identify candidate sources ready for promotion.

    Args:
        metrics: Source quality metrics
        threshold: Minimum quality score threshold

    Returns:
        List of sources to promote
    """
    candidates = []

    for m in metrics:
        if m["status"] != "candidate":
            continue

        # Check if good quality
        if m["quality_score"] >= threshold:
            candidates.append(
                {
                    "url": m["url"],
                    "name": m["name"],
                    "quality_score": m["quality_score"],
                    "recent_avg_score": m["recent_avg_score"],
                    "reason": f"Quality score ({m['quality_score']:.2f}) exceeds threshold ({threshold})",
                }
            )

    return candidates


def extract_new_keywords(project_root: Path, topic: str, days: int = 7) -> List[str]:
    """Extract suggested keywords from recent high-scoring articles.

    Args:
        project_root: Project root directory
        topic: Current topic
        days: Number of days to look back

    Returns:
        List of suggested keywords
    """
    import sqlite3

    db_path = (
        project_root / "data" / "feed_agent" / f"{topic.replace(' ', '_').lower()}.db"
    )
    if not db_path.exists():
        return []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get core_points from high-scoring articles
    cursor.execute(
        """
        SELECT core_points
        FROM articles
        WHERE topic = ? AND relevance_score >= 7
        AND analyzed_at >= date('now', ? || ' days')
    """,
        (topic, f"-{days}"),
    )

    rows = cursor.fetchall()
    conn.close()

    # Extract keywords from core points
    current_keywords = set(get_keywords(project_root, topic))
    suggested = set()

    for row in rows:
        try:
            points = json.loads(row[0]) if row[0] else []
            for point in points:
                # Extract significant words (simple extraction)
                words = point.lower().split()
                for word in words:
                    if len(word) > 4 and word.isalpha():
                        if word not in current_keywords:
                            suggested.add(word)
        except Exception:
            pass

    return list(suggested)[:10]  # Limit to 10 suggestions


def run_evolution(
    topic: str, project_root: Path, force: bool = False
) -> Dict[str, Any]:
    """Run the evolution process.

    Args:
        topic: Current topic
        project_root: Project root directory
        force: Force evolution even if recently run

    Returns:
        Evolution report
    """
    init_db(project_root, topic)

    # Calculate source quality
    metrics = calculate_source_quality(project_root, topic)

    # Identify prune candidates
    prune_candidates = identify_prune_candidates(metrics)

    # Identify promote candidates
    promote_candidates = identify_promote_candidates(metrics)

    # Extract suggested keywords and candidate keyword state
    suggested_keywords = extract_new_keywords(project_root, topic)
    promoted_keywords = promote_candidate_keywords(project_root, topic)

    # Log evolution
    report = {
        "topic": topic,
        "timestamp": datetime.now().isoformat(),
        "sources_analyzed": len(metrics),
        "prune_candidates": prune_candidates,
        "promote_candidates": promote_candidates,
        "active_keywords": get_active_keywords(project_root, topic, limit=10),
        "candidate_keywords": get_candidate_keywords(project_root, topic, limit=10),
        "suggested_keywords": suggested_keywords,
        "promoted_keywords": promoted_keywords,
        "stats": get_stats(project_root, topic),
    }

    if prune_candidates or promote_candidates or suggested_keywords:
        log_evolution(project_root, topic, "evolution_run", report)

    return report


def promote_candidate_keywords(
    project_root: Path,
    topic: str,
    min_occurrences: int = 2,
    min_confidence: float = 0.7,
) -> List[str]:
    """Promote strong candidate keywords to active status."""
    import sqlite3

    db_path = (
        project_root / "data" / "feed_agent" / f"{topic.replace(' ', '_').lower()}.db"
    )
    if not db_path.exists():
        return []

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT keyword
        FROM keywords
        WHERE topic = ?
          AND status = 'candidate'
          AND occurrence_count >= ?
          AND confidence >= ?
        ORDER BY confidence DESC, occurrence_count DESC
        """,
        (topic, min_occurrences, min_confidence),
    )
    rows = cursor.fetchall()
    conn.close()

    promoted = []
    for row in rows:
        keyword = row["keyword"]
        if promote_keyword(project_root, topic, keyword):
            promoted.append(keyword)

    return promoted


def apply_evolution(
    project_root: Path, topic: str, actions: Dict[str, Any]
) -> Dict[str, Any]:
    """Apply evolution actions (prune/promote sources, add keywords).

    Args:
        project_root: Project root directory
        topic: Current topic
        actions: Dict with prune_urls, promote_urls, add_keywords

    Returns:
        Applied actions report
    """
    import sqlite3

    db_path = (
        project_root / "data" / "feed_agent" / f"{topic.replace(' ', '_').lower()}.db"
    )
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    results = {
        "pruned": [],
        "promoted": [],
        "keywords_added": [],
    }

    # Prune sources
    for url in actions.get("prune_urls", []):
        cursor.execute(
            "UPDATE sources SET status = 'pruned' WHERE url = ? AND topic = ?",
            (url, topic),
        )
        if cursor.rowcount > 0:
            results["pruned"].append(url)

    # Promote sources
    for url in actions.get("promote_urls", []):
        cursor.execute(
            "UPDATE sources SET status = 'active' WHERE url = ? AND topic = ?",
            (url, topic),
        )
        if cursor.rowcount > 0:
            results["promoted"].append(url)

    # Add keywords
    for kw in actions.get("add_keywords", []):
        add_keyword(
            project_root, topic, kw, source="evolution", status="active", confidence=0.8
        )
        results["keywords_added"].append(kw)

    for kw in actions.get("promote_keywords", []):
        if promote_keyword(project_root, topic, kw):
            results.setdefault("keywords_promoted", []).append(kw)

    for kw in actions.get("reject_keywords", []):
        if reject_keyword(project_root, topic, kw):
            results.setdefault("keywords_rejected", []).append(kw)

    conn.commit()
    conn.close()

    # Log actions
    log_evolution(project_root, topic, "evolution_applied", results)

    return results


def main():
    parser = argparse.ArgumentParser(description="Self-evolution for feed-agent")
    parser.add_argument(
        "--project-root", type=Path, required=True, help="Project root directory"
    )
    parser.add_argument("--topic", required=True, help="Topic")
    parser.add_argument("--action", choices=["run", "apply"], default="run")
    parser.add_argument("--force", action="store_true", help="Force evolution")
    parser.add_argument("--actions", help="JSON file with actions to apply")

    args = parser.parse_args()

    if args.action == "run":
        report = run_evolution(args.topic, args.project_root, args.force)
        print(json.dumps(report, indent=2))

    elif args.action == "apply":
        if args.actions:
            with open(args.actions) as f:
                actions = json.load(f)
        else:
            actions = json.load(sys.stdin)

        results = apply_evolution(args.project_root, args.topic, actions)
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
