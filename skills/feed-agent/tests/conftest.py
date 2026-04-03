"""Shared pytest fixtures for feed-agent tests."""

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def temp_project_root(tmp_path):
    """Create a temporary project root for feed-agent tests."""
    (tmp_path / "config").mkdir()
    (tmp_path / "data").mkdir()
    (tmp_path / "reports").mkdir()
    return tmp_path


@pytest.fixture
def temp_topic_db(temp_project_root):
    """Initialize an empty topic database for tests."""
    import db

    topic = "AI Agents"
    db.init_db(temp_project_root, topic)
    return temp_project_root, topic
