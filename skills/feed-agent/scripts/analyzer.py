#!/usr/bin/env python3
"""AI-based article analysis and scoring for feed-agent."""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))

from db import (
    add_keyword,
    get_articles,
    get_active_keywords,
    insert_article,
    update_source_quality,
    Article,
)


SCORING_PROMPT_TEMPLATE = """# Article Relevance Scoring

**Topic:** {topic}
**Tracked Keywords:** {keywords}
**Article Title:** {title}
**Article Content:** {content}

**Task:**
1. Score this article 0-10 for relevance to "{topic}"
2. Identify if this represents a NEW insight or repetition of known information
3. Extract 3-5 core points (key insights, findings, or developments)
4. Suggest any new keywords that should be tracked for this topic

**Response Format (JSON):**
{{
  "score": <integer 0-10>,
  "is_new_insight": <boolean>,
  "core_points": ["point 1", "point 2", "point 3"],
  "reasoning": "<brief explanation of the score>",
  "suggested_keywords": ["keyword1", "keyword2"]
}}

**Scoring Guide:**
- 9-10: Directly addresses {topic}, major new development or breakthrough
- 7-8: Highly relevant, contributes meaningful insight or useful information
- 5-6: Somewhat related, tangential relevance, context but not core
- 3-4: Peripheral connection, low signal-to-noise ratio
- 0-2: Not relevant to {topic}, should be filtered out
"""

HISTORICAL_COMPARISON_PROMPT = """# Historical Comparison

**Topic:** {topic}
**Current Article Core Points:**
{current_points}

**Recent Articles Core Points (last 7 days):**
{historical_points}

**Task:**
Compare the current article's core points against the historical record.
Determine if this is:
- "new": Novel information not covered before
- "continuation": Update or extension of previously reported story
- "duplicate": Same content from a different source (should be filtered)

**Response Format (JSON):**
{{
  "classification": "<new|continuation|duplicate>",
  "reasoning": "<brief explanation>",
  "related_article_ids": [<ids of related articles if continuation or duplicate>]
}}
"""


def get_scoring_prompt(
    topic: str, title: str, content: str, keywords: Optional[List[str]] = None
) -> str:
    """Generate the scoring prompt for an article.

    Args:
        topic: Current topic
        title: Article title
        content: Article content (truncated if needed)

    Returns:
        Formatted prompt string
    """
    # Truncate content if too long
    max_content = 3000
    if len(content) > max_content:
        content = content[:max_content] + "..."

    keyword_text = ", ".join(keywords or []) if keywords else "none"

    return SCORING_PROMPT_TEMPLATE.format(
        topic=topic,
        keywords=keyword_text,
        title=title,
        content=content,
    )


def get_historical_comparison_prompt(
    topic: str, current_points: List[str], historical_points: List[Dict]
) -> str:
    """Generate the historical comparison prompt.

    Args:
        topic: Current topic
        current_points: Core points of current article
        historical_points: List of historical article points

    Returns:
        Formatted prompt string
    """
    historical_text = ""
    for i, article in enumerate(historical_points[:10]):  # Limit to 10 recent articles
        historical_text += f"\n{i + 1}. {article.get('title', 'Unknown')}\n"
        points = article.get("core_points", [])
        for point in points[:3]:  # Limit to 3 points per article
            historical_text += f"   - {point}\n"

    return HISTORICAL_COMPARISON_PROMPT.format(
        topic=topic,
        current_points="\n".join([f"- {p}" for p in current_points]),
        historical_points=historical_text or "No historical data available",
    )


def parse_scoring_response(response: str) -> Dict[str, Any]:
    """Parse the LLM response for scoring.

    Args:
        response: Raw LLM response string

    Returns:
        Parsed dict with score, core_points, etc.
    """
    default = {
        "score": 5,
        "is_new_insight": True,
        "core_points": [],
        "reasoning": "Failed to parse response",
        "suggested_keywords": [],
    }

    try:
        # Try to extract JSON from response
        json_match = response
        if "```json" in response:
            json_match = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_match = response.split("```")[1].split("```")[0]

        data = json.loads(json_match.strip())

        result = default.copy()
        result["score"] = min(10, max(0, int(data.get("score", 5))))
        result["is_new_insight"] = data.get("is_new_insight", True)
        result["core_points"] = data.get("core_points", [])[:5]  # Max 5 points
        result["reasoning"] = data.get("reasoning", "")
        result["suggested_keywords"] = data.get("suggested_keywords", [])

        return result

    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"Warning: Could not parse scoring response: {e}", file=sys.stderr)
        return default


def analyze_article(
    topic: str,
    article: Article,
    historical_articles: List[Article] = None,
    keywords: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Analyze an article for relevance scoring.

    Note: The actual LLM call should be made by the agent.
    This function returns the prompts to use and default values.

    Args:
        topic: Current topic
        article: Article to analyze
        historical_articles: Recent articles for comparison

    Returns:
        Dict with scoring prompt and comparison prompt
    """
    scoring_prompt = get_scoring_prompt(topic, article.title, article.content, keywords)

    comparison_prompt = None
    if historical_articles:
        historical_data = [
            {"id": a.id, "title": a.title, "core_points": a.core_points or []}
            for a in historical_articles[:10]
        ]
        comparison_prompt = get_historical_comparison_prompt(
            topic, article.core_points or [], historical_data
        )

    return {
        "article_id": article.id,
        "article_url": article.url,
        "scoring_prompt": scoring_prompt,
        "comparison_prompt": comparison_prompt,
        "default_score": {
            "score": 5,
            "is_new_insight": True,
            "core_points": [],
            "reasoning": "Pending LLM analysis",
        },
    }


def get_analysis_instructions(
    topic: str, project_root: Path, min_score: int = 7
) -> Dict[str, Any]:
    """Get instructions for analyzing articles.

    Returns instructions for the agent to execute LLM-based analysis.

    Args:
        topic: Current topic
        project_root: Project root directory
        min_score: Minimum score for promotion

    Returns:
        Dict with instructions
    """
    # Get recent unanalyzed articles
    articles = get_articles(project_root, topic, min_score=0, days=1, limit=50)
    unanalyzed = [a for a in articles if not a.analyzed_at]

    if not unanalyzed:
        return {"status": "no_articles", "message": "No unanalyzed articles found"}

    # Get historical articles for comparison
    historical = get_articles(project_root, topic, min_score=7, days=7, limit=20)
    active_keywords = get_active_keywords(project_root, topic, limit=10)

    analysis_tasks = []
    for article in unanalyzed:
        task = analyze_article(topic, article, historical, active_keywords)
        analysis_tasks.append(task)

    return {
        "tool": "LLM",
        "active_keywords": active_keywords,
        "articles_to_analyze": len(analysis_tasks),
        "tasks": analysis_tasks,
        "instructions": f"""
            For each article in tasks:
            
            1. Use the LLM with the 'scoring_prompt' to evaluate relevance
               - Treat tracked keywords as strong relevance hints, not strict requirements
            2. Parse the JSON response to extract:
               - score (0-10)
               - is_new_insight (boolean)
               - core_points (array of strings)
               - reasoning (string)
               - suggested_keywords (array)
            
            3. If score >= {min_score}, compare against historical data using 'comparison_prompt'
            
            4. Store results using analyzer.py --action store
            
            Output format for each analyzed article:
            {{
                "article_id": <id>,
                "relevance_score": <0-10>,
                "is_new_insight": <boolean>,
                "core_points": ["point1", "point2", ...],
                "reasoning": "<brief explanation>",
                "suggested_keywords": ["keyword1", ...]
            }}
        """,
        "min_score": min_score,
        "output_path": str(
            project_root
            / "data"
            / "feed_agent"
            / f"{topic.replace(' ', '_').lower()}"
            / "analysis_results.json"
        ),
    }


def store_analysis(
    project_root: Path, topic: str, results: List[Dict]
) -> Dict[str, Any]:
    """Store analysis results in database.

    Args:
        project_root: Project root directory
        topic: Current topic
        results: List of analysis result dicts

    Returns:
        Stats dict
    """
    stats = {
        "analyzed": 0,
        "promoted": 0,
        "filtered": 0,
        "keywords_suggested": [],
    }

    for result in results:
        article_id = result.get("article_id")
        score = result.get("relevance_score", 0)

        # Update article in database
        try:
            db_path = (
                project_root
                / "data"
                / "feed_agent"
                / f"{topic.replace(' ', '_').lower()}.db"
            )
            import sqlite3

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE articles SET
                    relevance_score = ?,
                    is_new_insight = ?,
                    core_points = ?,
                    reasoning = ?,
                    analyzed_at = ?
                WHERE id = ?
                """,
                (
                    score,
                    1 if result.get("is_new_insight", True) else 0,
                    json.dumps(result.get("core_points", [])),
                    result.get("reasoning", ""),
                    datetime.now().isoformat(),
                    article_id,
                ),
            )

            conn.commit()
            conn.close()

            stats["analyzed"] += 1
            if score >= 7:
                stats["promoted"] += 1
            else:
                stats["filtered"] += 1

            # Collect suggested keywords
            for kw in result.get("suggested_keywords", [])[:3]:
                if kw not in stats["keywords_suggested"]:
                    stats["keywords_suggested"].append(kw)
                add_keyword(
                    project_root,
                    topic,
                    kw,
                    source="analysis",
                    status="candidate",
                    confidence=max(score / 10, 0.5),
                )

        except Exception as e:
            print(
                f"Error storing analysis for article {article_id}: {e}", file=sys.stderr
            )

    return stats


def run_analysis(topic: str, project_root: Path, min_score: int = 7) -> Dict[str, Any]:
    """Run the analysis process.

    Note: Returns instructions for agent to execute.

    Args:
        topic: Current topic
        project_root: Project root directory
        min_score: Minimum score to promote article

    Returns:
        Dict with instructions
    """
    return get_analysis_instructions(topic, project_root, min_score)


def main():
    parser = argparse.ArgumentParser(description="Article analysis for feed-agent")
    parser.add_argument(
        "--project-root", type=Path, required=True, help="Project root directory"
    )
    parser.add_argument("--topic", required=True, help="Topic to analyze")
    parser.add_argument("--action", choices=["analyze", "store"], default="analyze")
    parser.add_argument(
        "--min-score", type=int, default=7, help="Minimum score to promote"
    )
    parser.add_argument("--results", help="JSON file with analysis results to store")

    args = parser.parse_args()

    if args.action == "analyze":
        result = run_analysis(args.topic, args.project_root, args.min_score)
        print(json.dumps(result, indent=2))

    elif args.action == "store":
        if args.results:
            with open(args.results) as f:
                results = json.load(f)
        else:
            results = json.load(sys.stdin)

        stats = store_analysis(args.project_root, args.topic, results)
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
