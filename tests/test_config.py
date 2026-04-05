"""Tests for configuration module."""
from __future__ import annotations

import os

from hub_intel.config import HubIntelConfig, TRACKS, CANONICAL_SOURCES, ROOT_DIR


class TestHubIntelConfig:
    def test_default_config(self):
        cfg = HubIntelConfig()
        assert cfg.anthropic_api_key == ""
        assert cfg.slack_user_id == "W8FL6URHQ"
        assert cfg.model == "claude-sonnet-4-20250514"
        assert cfg.max_search_results == 10
        assert cfg.tracks == list(TRACKS)

    def test_from_env(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-123")
        monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
        monkeypatch.setenv("SLACK_USER_ID", "U999")
        cfg = HubIntelConfig.from_env()
        assert cfg.anthropic_api_key == "sk-test-123"
        assert cfg.slack_bot_token == "xoxb-test"
        assert cfg.slack_user_id == "U999"

    def test_validate_missing_key(self):
        cfg = HubIntelConfig()
        errors = cfg.validate()
        assert "ANTHROPIC_API_KEY is required" in errors

    def test_validate_with_key(self):
        cfg = HubIntelConfig(anthropic_api_key="sk-test")
        errors = cfg.validate()
        assert len(errors) == 0

    def test_tracks_complete(self):
        assert len(TRACKS) == 10
        assert "product_updates" in TRACKS
        assert "voice_of_market" in TRACKS

    def test_canonical_sources_coverage(self):
        for track in TRACKS:
            assert track in CANONICAL_SOURCES, f"Missing sources for {track}"
            assert len(CANONICAL_SOURCES[track]) > 0

    def test_root_dir_exists(self):
        assert ROOT_DIR.exists()
