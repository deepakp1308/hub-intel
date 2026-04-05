"""Tests for brief synthesizer module."""
from __future__ import annotations

import pytest

from hub_intel.synthesizer import BriefSynthesizer, SYNTHESIS_SYSTEM_PROMPT
from hub_intel.config import HubIntelConfig


class TestBriefSynthesizer:
    def test_init(self, config):
        synth = BriefSynthesizer(config)
        assert synth.config.anthropic_api_key == "test-key-000"

    def test_system_prompt_quality(self):
        assert "McKinsey" in SYNTHESIS_SYSTEM_PROMPT
        assert "Pyramid Principle" in SYNTHESIS_SYSTEM_PROMPT
        assert "moat" in SYNTHESIS_SYSTEM_PROMPT

    def test_format_findings(self, config, sample_findings):
        synth = BriefSynthesizer(config)
        text = synth._format_findings(sample_findings)
        assert "Product Updates" in text
        assert "Breeze AI multi-object reporting" in text
        assert "🔴" in text
        assert "🟡" in text
        assert "🟢" in text

    def test_format_findings_empty(self, config):
        synth = BriefSynthesizer(config)
        text = synth._format_findings({})
        assert text == ""

    def test_count_findings(self, config, sample_findings):
        synth = BriefSynthesizer(config)
        count = synth._count_findings(sample_findings)
        assert count == 4  # 2 + 1 + 1

    def test_default_template(self):
        template = BriefSynthesizer._default_template()
        assert "EXECUTIVE SNAPSHOT" in template
        assert "STRATEGIC IMPLICATIONS MATRIX" in template
        assert "COMPETITIVE MOAT STATUS" in template

    def test_synthesize_from_markdown(self, config, sample_markdown):
        synth = BriefSynthesizer(config)
        result = synth.synthesize_from_markdown(sample_markdown)
        assert result == sample_markdown

    def test_load_template(self, config):
        synth = BriefSynthesizer(config)
        template = synth._load_template()
        assert "EXECUTIVE SNAPSHOT" in template
