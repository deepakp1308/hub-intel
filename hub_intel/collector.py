"""Intelligence collection across 10 research tracks."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from hub_intel.config import CANONICAL_SOURCES, HubIntelConfig, CONTEXT_DIR

logger = logging.getLogger(__name__)


@dataclass
class Finding:
    """A single intelligence finding."""

    track: str
    title: str
    detail: str
    source: str = ""
    priority: str = "green"  # red, yellow, green
    tags: List[str] = field(default_factory=list)
    date_collected: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "track": self.track,
            "title": self.title,
            "detail": self.detail,
            "source": self.source,
            "priority": self.priority,
            "tags": self.tags,
            "date_collected": self.date_collected,
        }


TRACK_PROMPTS = {
    "product_updates": (
        "Search for HubSpot product updates, new features, and platform changes "
        "released in the past 7 days. Focus on all Hubs: Marketing, Sales, Service, "
        "Content, Data, Commerce. Include version numbers and release dates."
    ),
    "ai_breeze": (
        "Search for HubSpot Breeze AI updates: Breeze Agents (Prospecting, Content, "
        "Data, Closing), Breeze Assistant, Breeze Studio, Breeze Marketplace. "
        "Any new AI capabilities, model upgrades, or agent expansions."
    ),
    "analytics_reporting": (
        "Search for HubSpot reporting and analytics updates: Custom Report Builder, "
        "AI-generated reports, multi-object cross-entity reporting, attribution models, "
        "Data Studio, dashboards. Is attribution still Enterprise-gated?"
    ),
    "ltc_crm": (
        "Search for HubSpot CRM, Sales Hub, Commerce Hub, and Service Hub updates. "
        "Pipeline management, deal tracking, invoicing, payments, quotes, subscriptions. "
        "Any post-close analytics or proposal performance features?"
    ),
    "gtm_messaging": (
        "Search for HubSpot go-to-market messaging, positioning, competitive claims. "
        "How do they position against Mailchimp? What is their value proposition? "
        "Any new analyst recognition from G2, Forrester, or Gartner?"
    ),
    "seo_content": (
        "Search for HubSpot SEO strategy, content marketing, HubSpot Academy updates, "
        "new certifications, comparison pages. What keywords are they targeting?"
    ),
    "social_video": (
        "Search for HubSpot social media presence: YouTube, LinkedIn, TikTok. "
        "Executive thought leadership from Yamini Rangan, Dharmesh Shah, Andy Pitre, "
        "Kipp Bodnar. Recent video content themes."
    ),
    "market_signals": (
        "Search for HubSpot press releases, partnerships, M&A activity, earnings, "
        "revenue signals. Any C-suite changes or organizational restructuring?"
    ),
    "pricing": (
        "Search for HubSpot pricing changes across all Hubs. Current pricing tiers, "
        "seat-based model, contact pricing, mandatory onboarding fees, HubSpot Credits. "
        "Marketing Hub: Starter, Pro, Enterprise pricing."
    ),
    "voice_of_market": (
        "Search Reddit r/hubspot, G2, Capterra, Trustpilot for recent HubSpot reviews "
        "and sentiment. Focus on reporting feedback, CRM migration stories, "
        "HubSpot vs Mailchimp comparisons."
    ),
}


class IntelCollector:
    """Collects competitive intelligence from web sources."""

    def __init__(self, config: HubIntelConfig):
        self.config = config
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.config.anthropic_api_key)
            except ImportError:
                raise RuntimeError("anthropic package required for collection")
        return self._client

    def collect_all(self) -> Dict[str, List[Finding]]:
        """Run all 10 collection tracks."""
        results = {}
        for track in self.config.tracks:
            logger.info("Collecting track: %s", track)
            try:
                findings = self.collect_track(track)
                results[track] = findings
                logger.info("Track %s: %d findings", track, len(findings))
            except Exception as e:
                logger.error("Track %s failed: %s", track, e)
                results[track] = []
        return results

    def collect_track(self, track: str) -> List[Finding]:
        """Collect intelligence for a single track using Claude API."""
        prompt = TRACK_PROMPTS.get(track, "")
        if not prompt:
            logger.warning("No prompt for track: %s", track)
            return []

        sources = CANONICAL_SOURCES.get(track, [])
        source_list = "\n".join(f"- {s}" for s in sources)

        context = self._load_strategic_context()

        full_prompt = (
            f"You are a competitive intelligence analyst researching HubSpot.\n\n"
            f"## Strategic Context\n{context}\n\n"
            f"## Research Task\n{prompt}\n\n"
            f"## Canonical Sources\n{source_list}\n\n"
            f"Return your findings as a structured list. For each finding:\n"
            f"- Title: brief headline\n"
            f"- Detail: 2-3 sentences with specifics (numbers, dates, features)\n"
            f"- Priority: red (urgent threat), yellow (monitor), green (our advantage holds)\n"
            f"- Tags: CRM/L2C, R&A, AI, GTM, Pricing (pick relevant ones)\n"
            f"- Source: URL or source name\n\n"
            f"Format each finding as:\n"
            f"FINDING:\n"
            f"Title: ...\nDetail: ...\nPriority: ...\nTags: ...\nSource: ...\n"
        )

        try:
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=4096,
                messages=[{"role": "user", "content": full_prompt}],
            )
            text = response.content[0].text
            return self._parse_findings(track, text)
        except Exception as e:
            logger.error("API call failed for track %s: %s", track, e)
            return []

    def collect_from_raw(self, track: str, raw_text: str) -> List[Finding]:
        """Create findings from pre-collected raw text."""
        return self._parse_findings(track, raw_text)

    def _load_strategic_context(self) -> str:
        context_file = CONTEXT_DIR / "l2c_strategic.md"
        if context_file.exists():
            return context_file.read_text()[:3000]
        return ""

    def _parse_findings(self, track: str, text: str) -> List[Finding]:
        """Parse structured findings from response text."""
        findings = []
        blocks = text.split("FINDING:")

        for block in blocks[1:]:  # skip preamble
            lines = block.strip().split("\n")
            data = {}
            for line in lines:
                line = line.strip()
                if line.startswith("Title:"):
                    data["title"] = line[6:].strip()
                elif line.startswith("Detail:"):
                    data["detail"] = line[7:].strip()
                elif line.startswith("Priority:"):
                    data["priority"] = line[9:].strip().lower()
                elif line.startswith("Tags:"):
                    data["tags"] = [t.strip() for t in line[5:].split(",")]
                elif line.startswith("Source:"):
                    data["source"] = line[7:].strip()

            if data.get("title") and data.get("detail"):
                findings.append(Finding(
                    track=track,
                    title=data["title"],
                    detail=data.get("detail", ""),
                    source=data.get("source", ""),
                    priority=data.get("priority", "green"),
                    tags=data.get("tags", []),
                ))

        return findings
