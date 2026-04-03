#!/usr/bin/env python3
"""Database operations for feed-agent skill."""

import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


def get_db_path(project_root: Path, topic: str = None) -> Path:
    """Get the database path."""
    if topic:
        return (
            project_root
            / "data"
            / "feed_agent"
            / f"{topic.replace(' ', '_').lower()}.db"
        )
    return project_root / "data" / "feed_agent" / "feed_agent.db"


def get_connection(db_path: Path) -> sqlite3.Connection:
    """Get database connection with row factory."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(project_root: Path, topic: str = None) -> Path:
    """Create tables if they don't exist."""
    db_path = get_db_path(project_root, topic)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            url TEXT NOT NULL,
            name TEXT,
            provider TEXT DEFAULT 'manual',
            source_type TEXT DEFAULT 'rss',
            quality_score REAL DEFAULT 0.5,
            relevance_avg REAL DEFAULT 0.0,
            total_articles INTEGER DEFAULT 0,
            promoted_articles INTEGER DEFAULT 0,
            low_score_runs INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            discovered_from TEXT,
            last_fetched_at TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(topic, url)
        );

        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER,
            topic TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            title TEXT,
            content TEXT,
            summary TEXT,
            relevance_score INTEGER,
            is_new_insight INTEGER DEFAULT 1,
            core_points TEXT,
            reasoning TEXT,
            fetched_at TEXT DEFAULT (datetime('now')),
            analyzed_at TEXT,
            FOREIGN KEY (source_id) REFERENCES sources(id)
        );

        CREATE TABLE IF NOT EXISTS evolution_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            keyword TEXT NOT NULL,
            source TEXT DEFAULT 'user',
            score REAL DEFAULT 0.5,
            status TEXT DEFAULT 'candidate',
            confidence REAL DEFAULT 0.5,
            occurrence_count INTEGER DEFAULT 1,
            promotion_count INTEGER DEFAULT 0,
            rejection_count INTEGER DEFAULT 0,
            last_seen_at TEXT,
            last_promoted_at TEXT,
            updated_at TEXT DEFAULT (datetime('now')),
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(topic, keyword)
        );

        CREATE INDEX IF NOT EXISTS idx_sources_topic ON sources(topic);
        CREATE INDEX IF NOT EXISTS idx_sources_status ON sources(status);
        CREATE INDEX IF NOT EXISTS idx_articles_topic ON articles(topic);
        CREATE INDEX IF NOT EXISTS idx_articles_score ON articles(relevance_score);
        CREATE INDEX IF NOT EXISTS idx_articles_fetched ON articles(fetched_at DESC);
    """)

    _ensure_keyword_columns(cursor)

    conn.commit()
    conn.close()

    return db_path


def _ensure_keyword_columns(cursor: sqlite3.Cursor) -> None:
    """Backfill new keyword lifecycle columns for existing databases."""
    cursor.execute("PRAGMA table_info(keywords)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    required_columns = {
        "status": "TEXT DEFAULT 'candidate'",
        "confidence": "REAL DEFAULT 0.5",
        "occurrence_count": "INTEGER DEFAULT 1",
        "promotion_count": "INTEGER DEFAULT 0",
        "rejection_count": "INTEGER DEFAULT 0",
        "last_seen_at": "TEXT",
        "last_promoted_at": "TEXT",
        "updated_at": "TEXT DEFAULT (datetime('now'))",
    }

    for column, definition in required_columns.items():
        if column not in existing_columns:
            cursor.execute(f"ALTER TABLE keywords ADD COLUMN {column} {definition}")


@dataclass
class Source:
    id: Optional[int]
    topic: str
    url: str
    name: str = ""
    provider: str = "manual"
    source_type: str = "rss"
    quality_score: float = 0.5
    relevance_avg: float = 0.0
    total_articles: int = 0
    promoted_articles: int = 0
    low_score_runs: int = 0
    status: str = "active"
    discovered_from: str = ""
    last_fetched_at: Optional[str] = None


@dataclass
class Article:
    id: Optional[int]
    topic: str
    url: str
    source_id: Optional[int] = None
    title: str = ""
    content: str = ""
    summary: str = ""
    relevance_score: int = 0
    is_new_insight: bool = True
    core_points: List[str] = None
    reasoning: str = ""
    analyzed_at: Optional[str] = None

    def __post_init__(self):
        if self.core_points is None:
            self.core_points = []


def upsert_source(project_root: Path, source: Source) -> int:
    """Insert or update a source."""
    db_path = get_db_path(project_root, source.topic)
    init_db(project_root, source.topic)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO sources (topic, url, name, provider, source_type, quality_score, 
                            relevance_avg, total_articles, promoted_articles, 
                            low_score_runs, status, discovered_from)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(topic, url) DO UPDATE SET
            name = excluded.name,
            provider = excluded.provider,
            source_type = excluded.source_type,
            quality_score = excluded.quality_score,
            status = excluded.status
        """,
        (
            source.topic,
            source.url,
            source.name,
            source.provider,
            source.source_type,
            source.quality_score,
            source.relevance_avg,
            source.total_articles,
            source.promoted_articles,
            source.low_score_runs,
            source.status,
            source.discovered_from,
        ),
    )

    source_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return source_id


def get_sources(project_root: Path, topic: str, status: str = None) -> List[Source]:
    """Get sources for a topic."""
    db_path = get_db_path(project_root, topic)
    if not db_path.exists():
        return []

    conn = get_connection(db_path)
    cursor = conn.cursor()

    if status:
        cursor.execute(
            "SELECT * FROM sources WHERE topic = ? AND status = ?", (topic, status)
        )
    else:
        cursor.execute("SELECT * FROM sources WHERE topic = ?", (topic,))

    rows = cursor.fetchall()
    conn.close()

    return [
        Source(
            id=row["id"],
            topic=row["topic"],
            url=row["url"],
            name=row["name"],
            provider=row["provider"],
            source_type=row["source_type"],
            quality_score=row["quality_score"],
            relevance_avg=row["relevance_avg"],
            total_articles=row["total_articles"],
            promoted_articles=row["promoted_articles"],
            low_score_runs=row["low_score_runs"],
            status=row["status"],
            discovered_from=row["discovered_from"],
            last_fetched_at=row["last_fetched_at"],
        )
        for row in rows
    ]


def update_source_fetched(project_root: Path, topic: str, source_id: int) -> None:
    """Update last_fetched_at for a source."""
    db_path = get_db_path(project_root, topic)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE sources SET last_fetched_at = ? WHERE id = ?",
        (datetime.now().isoformat(), source_id),
    )

    conn.commit()
    conn.close()


def update_source_quality(
    project_root: Path, topic: str, source_id: int, score: float, is_promoted: bool
) -> None:
    """Update source quality metrics."""
    db_path = get_db_path(project_root, topic)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE sources SET
            total_articles = total_articles + 1,
            promoted_articles = promoted_articles + ?,
            relevance_avg = (relevance_avg * total_articles + ?) / (total_articles + 1),
            quality_score = CAST(promoted_articles AS REAL) / (total_articles + 1)
        WHERE id = ?
        """,
        (1 if is_promoted else 0, score, source_id),
    )

    conn.commit()
    conn.close()


def insert_article(project_root: Path, article: Article) -> int:
    """Insert an article."""
    db_path = get_db_path(project_root, article.topic)
    init_db(project_root, article.topic)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO articles (source_id, topic, url, title, content, summary, 
                                  relevance_score, is_new_insight, core_points, reasoning)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                article.source_id,
                article.topic,
                article.url,
                article.title,
                article.content,
                article.summary,
                article.relevance_score,
                1 if article.is_new_insight else 0,
                json.dumps(article.core_points),
                article.reasoning,
            ),
        )
        article_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return article_id
    except sqlite3.IntegrityError:
        conn.close()
        return -1


def get_articles(
    project_root: Path, topic: str, min_score: int = 7, days: int = 1, limit: int = 50
) -> List[Article]:
    """Get articles for a topic with minimum score."""
    db_path = get_db_path(project_root, topic)
    if not db_path.exists():
        return []

    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM articles 
        WHERE topic = ? AND relevance_score >= ?
        AND date(fetched_at) >= date('now', ? || ' days')
        ORDER BY fetched_at DESC
        LIMIT ?
        """,
        (topic, min_score, f"-{days}", limit),
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        Article(
            id=row["id"],
            topic=row["topic"],
            url=row["url"],
            source_id=row["source_id"],
            title=row["title"],
            content=row["content"],
            summary=row["summary"],
            relevance_score=row["relevance_score"],
            is_new_insight=bool(row["is_new_insight"]),
            core_points=json.loads(row["core_points"]) if row["core_points"] else [],
            reasoning=row["reasoning"],
            analyzed_at=row["analyzed_at"],
        )
        for row in rows
    ]


def log_evolution(
    project_root: Path, topic: str, action: str, details: Dict[str, Any]
) -> None:
    """Log an evolution action."""
    db_path = get_db_path(project_root, topic)
    init_db(project_root, topic)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO evolution_log (topic, action, details) VALUES (?, ?, ?)",
        (topic, action, json.dumps(details)),
    )

    conn.commit()
    conn.close()


def add_keyword(
    project_root: Path,
    topic: str,
    keyword: str,
    source: str = "auto",
    status: str = "candidate",
    confidence: float = 0.5,
) -> None:
    """Add or update a keyword for a topic."""
    db_path = get_db_path(project_root, topic)
    init_db(project_root, topic)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()

    cursor.execute(
        """
        INSERT INTO keywords (
            topic, keyword, source, status, confidence, occurrence_count, last_seen_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, 1, ?, ?)
        ON CONFLICT(topic, keyword) DO UPDATE SET
            source = excluded.source,
            status = CASE
                WHEN keywords.status = 'rejected' AND excluded.status != 'active' THEN keywords.status
                ELSE excluded.status
            END,
            confidence = MAX(keywords.confidence, excluded.confidence),
            occurrence_count = keywords.occurrence_count + 1,
            last_seen_at = excluded.last_seen_at,
            updated_at = excluded.updated_at
        """,
        (topic, keyword, source, status, confidence, timestamp, timestamp),
    )

    conn.commit()
    conn.close()


def get_keywords(project_root: Path, topic: str) -> List[str]:
    """Get all non-rejected keywords for a topic."""
    db_path = get_db_path(project_root, topic)
    if not db_path.exists():
        return []

    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT keyword FROM keywords WHERE topic = ? AND status != 'rejected' ORDER BY confidence DESC, keyword ASC",
        (topic,),
    )

    rows = cursor.fetchall()
    conn.close()

    return [row["keyword"] for row in rows]


def _get_keywords_by_status(
    project_root: Path, topic: str, status: str, limit: int | None = None
) -> List[str]:
    """Get keywords for a topic filtered by status."""
    db_path = get_db_path(project_root, topic)
    if not db_path.exists():
        return []

    conn = get_connection(db_path)
    cursor = conn.cursor()

    query = (
        "SELECT keyword FROM keywords WHERE topic = ? AND status = ? "
        "ORDER BY confidence DESC, occurrence_count DESC, keyword ASC"
    )
    params: list[Any] = [topic, status]
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [row["keyword"] for row in rows]


def get_active_keywords(
    project_root: Path, topic: str, limit: int | None = None
) -> List[str]:
    """Get active keywords for a topic."""
    return _get_keywords_by_status(project_root, topic, "active", limit)


def get_candidate_keywords(
    project_root: Path, topic: str, limit: int | None = None
) -> List[str]:
    """Get candidate keywords for a topic."""
    return _get_keywords_by_status(project_root, topic, "candidate", limit)


def reject_keyword(project_root: Path, topic: str, keyword: str) -> bool:
    """Mark a keyword as rejected."""
    return _update_keyword_status(project_root, topic, keyword, "rejected")


def promote_keyword(project_root: Path, topic: str, keyword: str) -> bool:
    """Promote a keyword to active status."""
    db_path = get_db_path(project_root, topic)
    if not db_path.exists():
        return False

    conn = get_connection(db_path)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute(
        """
        UPDATE keywords
        SET status = 'active',
            promotion_count = promotion_count + 1,
            last_promoted_at = ?,
            updated_at = ?,
            confidence = MAX(confidence, 0.7)
        WHERE topic = ? AND keyword = ?
        """,
        (timestamp, timestamp, topic, keyword),
    )
    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return changed


def _update_keyword_status(
    project_root: Path, topic: str, keyword: str, status: str
) -> bool:
    """Update a keyword status."""
    db_path = get_db_path(project_root, topic)
    if not db_path.exists():
        return False

    conn = get_connection(db_path)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    if status == "rejected":
        cursor.execute(
            """
            UPDATE keywords
            SET status = 'rejected',
                rejection_count = rejection_count + 1,
                updated_at = ?
            WHERE topic = ? AND keyword = ?
            """,
            (timestamp, topic, keyword),
        )
    else:
        cursor.execute(
            "UPDATE keywords SET status = ?, updated_at = ? WHERE topic = ? AND keyword = ?",
            (status, timestamp, topic, keyword),
        )
    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return changed


def get_stats(project_root: Path, topic: str) -> Dict[str, Any]:
    """Get statistics for a topic."""
    db_path = get_db_path(project_root, topic)
    if not db_path.exists():
        return {"sources": 0, "articles": 0, "promoted": 0}

    conn = get_connection(db_path)
    cursor = conn.cursor()

    stats = {}

    cursor.execute(
        "SELECT COUNT(*) FROM sources WHERE topic = ? AND status = 'active'", (topic,)
    )
    stats["active_sources"] = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM sources WHERE topic = ? AND status = 'candidate'",
        (topic,),
    )
    stats["candidate_sources"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM articles WHERE topic = ?", (topic,))
    stats["total_articles"] = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM articles WHERE topic = ? AND relevance_score >= 7",
        (topic,),
    )
    stats["promoted_articles"] = cursor.fetchone()[0]

    cursor.execute(
        "SELECT AVG(quality_score) FROM sources WHERE topic = ? AND status = 'active'",
        (topic,),
    )
    result = cursor.fetchone()[0]
    stats["avg_quality"] = result if result else 0.0

    cursor.execute(
        "SELECT COUNT(*) FROM keywords WHERE topic = ? AND status = 'active'",
        (topic,),
    )
    stats["active_keywords"] = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM keywords WHERE topic = ? AND status = 'candidate'",
        (topic,),
    )
    stats["candidate_keywords"] = cursor.fetchone()[0]

    conn.close()

    return stats


def main():
    parser = argparse.ArgumentParser(description="Database operations for feed-agent")
    parser.add_argument(
        "--project-root", type=Path, required=True, help="Project root directory"
    )
    parser.add_argument("--topic", type=str, help="Topic to operate on")
    parser.add_argument(
        "command", choices=["init", "stats", "list-sources", "list-keywords"]
    )

    args = parser.parse_args()

    if args.command == "init":
        path = init_db(args.project_root, args.topic)
        print(json.dumps({"status": "initialized", "path": str(path)}))

    elif args.command == "stats":
        stats = get_stats(args.project_root, args.topic)
        print(json.dumps(stats, indent=2))

    elif args.command == "list-sources":
        sources = get_sources(args.project_root, args.topic)
        print(
            json.dumps(
                [
                    {
                        "name": s.name,
                        "url": s.url,
                        "status": s.status,
                        "quality": s.quality_score,
                        "provider": s.provider,
                    }
                    for s in sources
                ],
                indent=2,
            )
        )

    elif args.command == "list-keywords":
        keywords = get_keywords(args.project_root, args.topic)
        print(json.dumps({"keywords": keywords}, indent=2))


if __name__ == "__main__":
    main()
