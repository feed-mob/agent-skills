"""Tests for DB-backed keyword lifecycle and keyword-driven discovery."""

import db
import scout
import analyzer


class TestKeywordLifecycle:
    def test_add_keyword_defaults_to_candidate_status(self, temp_topic_db):
        project_root, topic = temp_topic_db

        db.add_keyword(project_root, topic, "tool use", source="analysis")

        keywords = db.get_keywords(project_root, topic)

        assert keywords == ["tool use"]
        assert db.get_active_keywords(project_root, topic) == []
        assert db.get_candidate_keywords(project_root, topic) == ["tool use"]

    def test_promote_keyword_moves_it_to_active(self, temp_topic_db):
        project_root, topic = temp_topic_db

        db.add_keyword(project_root, topic, "browser automation", source="analysis")

        db.promote_keyword(project_root, topic, "browser automation")

        assert db.get_active_keywords(project_root, topic) == ["browser automation"]
        assert db.get_candidate_keywords(project_root, topic) == []


class TestKeywordDrivenScout:
    def test_discovery_queries_include_active_keywords(self, temp_topic_db):
        project_root, topic = temp_topic_db
        db.add_keyword(project_root, topic, "tool use", source="analysis")
        db.add_keyword(project_root, topic, "planning", source="analysis")
        db.promote_keyword(project_root, topic, "tool use")
        db.promote_keyword(project_root, topic, "planning")

        queries = scout.get_exa_discovery_queries(
            topic, db.get_active_keywords(project_root, topic)
        )

        assert f"{topic} RSS feed" in queries
        assert f"{topic} tool use RSS feed" in queries
        assert f"{topic} planning RSS feed" in queries


class TestKeywordDrivenAnalyzer:
    def test_scoring_prompt_includes_tracked_keywords(self):
        prompt = analyzer.get_scoring_prompt(
            "AI Agents",
            "New agent framework",
            "This article covers planning and browser automation.",
            ["planning", "browser automation"],
        )

        assert "Tracked Keywords:" in prompt
        assert "planning" in prompt
        assert "browser automation" in prompt
