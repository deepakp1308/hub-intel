"""Tests for main agent orchestrator."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from hub_intel.agent import HubIntelAgent, _date_slug
from hub_intel.config import HubIntelConfig


class TestDateSlug:
    def test_long_format(self):
        assert _date_slug("April 4, 2026") == "2026-04-04"

    def test_iso_format(self):
        assert _date_slug("2026-04-04") == "2026-04-04"

    def test_slash_format(self):
        assert _date_slug("04/04/2026") == "2026-04-04"

    def test_invalid_fallback(self):
        slug = _date_slug("not-a-date")
        # Should return today's date as fallback
        assert len(slug) == 10
        assert slug.count("-") == 2


class TestHubIntelAgent:
    def test_init(self, config):
        agent = HubIntelAgent(config)
        assert agent.config.anthropic_api_key == "test-key-000"
        assert agent.collector is not None
        assert agent.synthesizer is not None
        assert agent.renderer is not None

    def test_run_with_markdown_input(self, config, sample_markdown, tmp_path, monkeypatch):
        import hub_intel.renderer as renderer_mod
        monkeypatch.setattr(renderer_mod, "REPORTS_DIR", tmp_path / "reports")
        monkeypatch.setattr(renderer_mod, "DOCS_DIR", tmp_path / "docs")

        agent = HubIntelAgent(config)
        result = agent.run(
            report_date="April 4, 2026",
            markdown_input=sample_markdown,
            skip_publish=True,
            skip_notify=True,
        )

        assert result["date"] == "April 4, 2026"
        assert result["date_slug"] == "2026-04-04"
        assert "markdown" in result
        assert "paths" in result
        assert "markdown" in result["paths"]

    def test_run_skip_all(self, config, sample_markdown, tmp_path, monkeypatch):
        import hub_intel.renderer as renderer_mod
        monkeypatch.setattr(renderer_mod, "REPORTS_DIR", tmp_path / "reports")
        monkeypatch.setattr(renderer_mod, "DOCS_DIR", tmp_path / "docs")

        agent = HubIntelAgent(config)
        result = agent.run(
            report_date="April 4, 2026",
            markdown_input=sample_markdown,
            skip_collect=True,
            skip_publish=True,
            skip_notify=True,
        )
        assert result["published"] is False
        assert result["notified"] is False

    def test_run_renders_html(self, config, sample_markdown, tmp_path, monkeypatch):
        import hub_intel.renderer as renderer_mod
        monkeypatch.setattr(renderer_mod, "REPORTS_DIR", tmp_path / "reports")
        monkeypatch.setattr(renderer_mod, "DOCS_DIR", tmp_path / "docs")

        agent = HubIntelAgent(config)
        result = agent.run(
            report_date="April 4, 2026",
            markdown_input=sample_markdown,
            skip_publish=True,
            skip_notify=True,
        )
        html_path = result["paths"].get("html")
        assert html_path is not None
        from pathlib import Path
        assert Path(html_path).exists()
