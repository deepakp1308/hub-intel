"""Tests for intelligence collector module."""
from __future__ import annotations

import pytest

from hub_intel.collector import Finding, IntelCollector, TRACK_PROMPTS
from hub_intel.config import HubIntelConfig, TRACKS


class TestFinding:
    def test_create_finding(self):
        f = Finding(
            track="product_updates",
            title="Test finding",
            detail="Some detail here",
            priority="red",
            tags=["AI"],
        )
        assert f.track == "product_updates"
        assert f.priority == "red"
        assert "AI" in f.tags

    def test_to_dict(self):
        f = Finding(track="ai_breeze", title="T", detail="D", priority="green")
        d = f.to_dict()
        assert d["track"] == "ai_breeze"
        assert d["title"] == "T"
        assert "date_collected" in d

    def test_default_values(self):
        f = Finding(track="t", title="T", detail="D")
        assert f.priority == "green"
        assert f.tags == []
        assert f.source == ""


class TestIntelCollector:
    def test_init(self, config):
        collector = IntelCollector(config)
        assert collector.config.anthropic_api_key == "test-key-000"

    def test_track_prompts_complete(self):
        for track in TRACKS:
            assert track in TRACK_PROMPTS, f"Missing prompt for {track}"
            assert len(TRACK_PROMPTS[track]) > 20

    def test_parse_findings(self, config, raw_findings_text):
        collector = IntelCollector(config)
        findings = collector._parse_findings("ai_breeze", raw_findings_text)
        assert len(findings) == 2
        assert findings[0].title == "Breeze Studio custom agents"
        assert findings[0].priority == "yellow"
        assert "AI" in findings[0].tags
        assert findings[1].title == "Commerce Hub subscription billing"
        assert findings[1].priority == "red"

    def test_parse_findings_empty(self, config):
        collector = IntelCollector(config)
        findings = collector._parse_findings("test", "No findings here.")
        assert len(findings) == 0

    def test_parse_findings_partial(self, config):
        text = "FINDING:\nTitle: Only title\n"
        collector = IntelCollector(config)
        findings = collector._parse_findings("test", text)
        # Missing detail should skip
        assert len(findings) == 0

    def test_collect_from_raw(self, config, raw_findings_text):
        collector = IntelCollector(config)
        findings = collector.collect_from_raw("test_track", raw_findings_text)
        assert len(findings) == 2
        assert all(f.track == "test_track" for f in findings)

    def test_collect_all_handles_errors(self, config, mocker):
        """Collect all tracks gracefully handles individual track failures."""
        collector = IntelCollector(config)
        mocker.patch.object(
            collector, "collect_track", side_effect=Exception("API error")
        )
        results = collector.collect_all()
        # Should return empty lists for all tracks, not raise
        assert len(results) == len(config.tracks)
        for track_results in results.values():
            assert track_results == []
