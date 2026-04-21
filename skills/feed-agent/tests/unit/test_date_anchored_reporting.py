"""Tests for date-anchored reporting and repeat suppression."""

from pathlib import Path

import db
import reporter


def add_source(project_root: Path, topic: str, url: str, name: str) -> int:
    """Create an active source for report tests."""
    return db.upsert_source(
        project_root,
        db.Source(
            id=None,
            topic=topic,
            url=url,
            name=name,
            provider="test",
            source_type="rss",
            status="active",
            quality_score=0.9,
        ),
    )


def add_article(
    project_root: Path,
    topic: str,
    source_id: int,
    url: str,
    title: str,
    published_at: str,
    core_point: str,
    story_key: str,
    story_status: str = "new",
) -> int:
    """Insert a promoted article into the test DB."""
    return db.insert_article(
        project_root,
        db.Article(
            id=None,
            topic=topic,
            source_id=source_id,
            url=url,
            title=title,
            content="full article content",
            summary="summary",
            relevance_score=8,
            is_new_insight=story_status != "duplicate",
            core_points=[core_point],
            reasoning="highly relevant",
            analyzed_at=f"{published_at}T12:00:00",
            published_at=f"{published_at}T09:00:00",
            story_key=story_key,
            story_status=story_status,
        ),
    )


class TestDateAnchoredReporting:
    def test_report_uses_target_date_window_based_on_published_at(self, temp_topic_db):
        project_root, topic = temp_topic_db
        source_id = add_source(project_root, topic, "https://example.com/feed", "Example")

        add_article(
            project_root,
            topic,
            source_id,
            "https://example.com/old-story",
            "Old story fetched recently",
            "2026-04-08",
            "Older than the requested 7-day window",
            "old-story",
        )
        add_article(
            project_root,
            topic,
            source_id,
            "https://example.com/new-story",
            "New story inside window",
            "2026-04-15",
            "Inside the requested 7-day window",
            "new-story",
        )

        report = reporter.generate_report(
            topic,
            project_root,
            threshold=7,
            as_of_date="2026-04-17",
            window_days=7,
        )

        assert "Coverage Window:** 2026-04-11 to 2026-04-17" in report
        assert "New story inside window" in report
        assert "Old story fetched recently" not in report

    def test_report_hides_previously_reported_story_across_adjacent_days(
        self, temp_topic_db
    ):
        project_root, topic = temp_topic_db
        source_a = add_source(project_root, topic, "https://example.com/feed-a", "Feed A")
        source_b = add_source(project_root, topic, "https://example.com/feed-b", "Feed B")

        add_article(
            project_root,
            topic,
            source_a,
            "https://example.com/story-day-one",
            "ChatGPT ads arrive",
            "2026-04-17",
            "OpenAI launched ads in ChatGPT for pilot advertisers",
            "chatgpt-ads-launch",
        )
        first_report = reporter.generate_report(
            topic,
            project_root,
            threshold=7,
            as_of_date="2026-04-17",
            window_days=7,
        )

        add_article(
            project_root,
            topic,
            source_b,
            "https://example.net/story-day-two",
            "Another outlet covers the same ChatGPT ad launch",
            "2026-04-18",
            "OpenAI launched ads in ChatGPT for pilot advertisers",
            "chatgpt-ads-launch",
        )
        second_report = reporter.generate_report(
            topic,
            project_root,
            threshold=7,
            as_of_date="2026-04-18",
            window_days=7,
        )

        assert "ChatGPT ads arrive" in first_report
        assert "Another outlet covers the same ChatGPT ad launch" not in second_report
        assert "No articles met the promotion threshold" in second_report

    def test_report_allows_meaningful_continuation_to_reappear(self, temp_topic_db):
        project_root, topic = temp_topic_db
        source_id = add_source(project_root, topic, "https://example.com/feed", "Example")

        add_article(
            project_root,
            topic,
            source_id,
            "https://example.com/story-initial",
            "Initial platform launch",
            "2026-04-17",
            "OpenAI launched ads in ChatGPT for pilot advertisers",
            "chatgpt-ads-launch",
        )
        reporter.generate_report(
            topic,
            project_root,
            threshold=7,
            as_of_date="2026-04-17",
            window_days=7,
        )

        add_article(
            project_root,
            topic,
            source_id,
            "https://example.com/story-update",
            "Self-serve tools expand the ad launch",
            "2026-04-18",
            "OpenAI expanded ChatGPT ads with self-serve tooling",
            "chatgpt-ads-launch",
            story_status="continuation",
        )

        report = reporter.generate_report(
            topic,
            project_root,
            threshold=7,
            as_of_date="2026-04-18",
            window_days=7,
        )

        assert "Self-serve tools expand the ad launch" in report
