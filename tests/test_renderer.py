"""Tests for report renderer module."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from hub_intel.renderer import ReportRenderer


class TestReportRenderer:
    def test_to_html_basic(self, sample_markdown):
        renderer = ReportRenderer()
        html = renderer.to_html(sample_markdown)
        assert "<!DOCTYPE html>" in html
        assert "HUB-INTEL" in html
        assert "Confidential" in html

    def test_to_html_contains_styles(self, sample_markdown):
        renderer = ReportRenderer()
        html = renderer.to_html(sample_markdown)
        assert "Arial" in html
        assert "--black: #000000" in html
        assert "--dark-gray: #333333" in html

    def test_to_html_renders_tables(self, sample_markdown):
        renderer = ReportRenderer()
        html = renderer.to_html(sample_markdown)
        assert "<table" in html.lower() or "<th" in html.lower()

    def test_to_html_renders_headings(self, sample_markdown):
        renderer = ReportRenderer()
        html = renderer.to_html(sample_markdown)
        assert "EXECUTIVE SNAPSHOT" in html
        assert "PRODUCT" in html

    def test_basic_md_to_html_fallback(self):
        renderer = ReportRenderer()
        md = "# Title\n\nSome **bold** text.\n\n---\n\n| A | B |\n|---|---|\n| 1 | 2 |"
        html = renderer._basic_md_to_html(md)
        assert "<h1>Title</h1>" in html
        assert "<strong>bold</strong>" in html
        assert "<hr>" in html
        assert "<table>" in html

    def test_save_report(self, sample_markdown, tmp_path, monkeypatch):
        import hub_intel.renderer as renderer_mod
        monkeypatch.setattr(renderer_mod, "REPORTS_DIR", tmp_path / "reports")
        monkeypatch.setattr(renderer_mod, "DOCS_DIR", tmp_path / "docs")

        renderer = ReportRenderer()
        paths = renderer.save_report(sample_markdown, "2026-04-04")

        assert "markdown" in paths
        assert "html" in paths
        assert "github_pages" in paths
        assert paths["markdown"].exists()
        assert paths["html"].exists()
        assert paths["github_pages"].exists()

        # Verify markdown content
        md_content = paths["markdown"].read_text()
        assert "HUB-INTEL" in md_content

        # Verify HTML content
        html_content = paths["html"].read_text()
        assert "<!DOCTYPE html>" in html_content

    def test_to_pdf_without_weasyprint(self, sample_markdown, tmp_path):
        renderer = ReportRenderer()
        html = renderer.to_html(sample_markdown)
        result = renderer.to_pdf(html, tmp_path / "test.pdf")
        # May return None if weasyprint not installed — that's ok
        assert result is None or result.exists()
