"""Tests for Slack notifier module."""
from __future__ import annotations

import pytest

from hub_intel.collector import Finding
from hub_intel.notifier import SlackNotifier
from hub_intel.config import HubIntelConfig


class TestSlackNotifier:
    def test_format_message(self, config):
        notifier = SlackNotifier(config)
        signals = [
            {"title": "Breeze AI", "detail": "NL reports", "priority": "red"},
            {"title": "Meetings", "detail": "AI lifecycle", "priority": "yellow"},
            {"title": "Pricing", "detail": "TCO play", "priority": "green"},
        ]
        msg = notifier._format_message("April 4, 2026", signals, "https://example.com")
        assert "HUB-INTEL" in msg
        assert "April 4, 2026" in msg
        assert ":red_circle:" in msg
        assert "Breeze AI" in msg
        assert "https://example.com" in msg

    def test_format_message_no_links(self, config):
        notifier = SlackNotifier(config)
        msg = notifier._format_message("April 4, 2026", [])
        assert "HUB-INTEL" in msg
        assert "View Full Report" not in msg

    def test_extract_top_signals(self, sample_findings):
        signals = SlackNotifier.extract_top_signals(sample_findings, limit=3)
        assert len(signals) == 3
        # Red should be first
        assert signals[0]["priority"] == "red"

    def test_extract_top_signals_limit(self, sample_findings):
        signals = SlackNotifier.extract_top_signals(sample_findings, limit=1)
        assert len(signals) == 1
        assert signals[0]["priority"] == "red"

    def test_extract_top_signals_empty(self):
        signals = SlackNotifier.extract_top_signals({})
        assert signals == []
