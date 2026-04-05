"""Configuration for HUB-INTEL agent."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


ROOT_DIR = Path(__file__).resolve().parent.parent
CONTEXT_DIR = ROOT_DIR / "context"
TEMPLATES_DIR = ROOT_DIR / "templates"
REPORTS_DIR = ROOT_DIR / "reports"
DOCS_DIR = ROOT_DIR / "docs"

TRACKS = [
    "product_updates",
    "ai_breeze",
    "analytics_reporting",
    "ltc_crm",
    "gtm_messaging",
    "seo_content",
    "social_video",
    "market_signals",
    "pricing",
    "voice_of_market",
]

CANONICAL_SOURCES = {
    "product_updates": [
        "https://www.hubspot.com/new",
        "https://community.hubspot.com/t5/Releases-and-Updates/ct-p/releases-updates",
        "https://developers.hubspot.com/changelog",
    ],
    "ai_breeze": [
        "https://www.hubspot.com/products/artificial-intelligence",
    ],
    "analytics_reporting": [
        "https://www.hubspot.com/products/marketing/analytics",
        "https://knowledge.hubspot.com/reports",
    ],
    "ltc_crm": [
        "https://www.hubspot.com/products/crm",
        "https://www.hubspot.com/products/sales",
        "https://www.hubspot.com/products/commerce",
    ],
    "gtm_messaging": [
        "https://www.hubspot.com",
    ],
    "seo_content": [
        "https://blog.hubspot.com",
    ],
    "social_video": [
        "https://www.youtube.com/@HubSpot",
        "https://www.linkedin.com/company/hubspot/",
    ],
    "market_signals": [
        "https://www.hubspot.com/company/news",
        "https://ir.hubspot.com/",
    ],
    "pricing": [
        "https://www.hubspot.com/pricing",
        "https://www.hubspot.com/pricing/marketing",
    ],
    "voice_of_market": [
        "https://www.reddit.com/r/hubspot/",
        "https://www.g2.com/products/hubspot-marketing-hub/reviews",
    ],
}

KEY_PERSONNEL = {
    "Yamini Rangan": "CEO",
    "Dharmesh Shah": "CTO & Co-founder",
    "Andy Pitre": "EVP Product",
    "Kipp Bodnar": "CMO",
    "Kate Bueker": "CFO",
}


@dataclass
class HubIntelConfig:
    """Agent configuration loaded from environment."""

    anthropic_api_key: str = ""
    slack_bot_token: str = ""
    slack_user_id: str = "W8FL6URHQ"
    github_repo: str = ""
    github_pages_url: str = ""
    model: str = "claude-sonnet-4-20250514"
    max_search_results: int = 10
    report_date: str = ""
    tracks: List[str] = field(default_factory=lambda: list(TRACKS))

    @classmethod
    def from_env(cls) -> HubIntelConfig:
        return cls(
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            slack_bot_token=os.getenv("SLACK_BOT_TOKEN", ""),
            slack_user_id=os.getenv("SLACK_USER_ID", "W8FL6URHQ"),
            github_repo=os.getenv("GITHUB_REPO", ""),
            github_pages_url=os.getenv("GITHUB_PAGES_URL", ""),
            model=os.getenv("HUB_INTEL_MODEL", "claude-sonnet-4-20250514"),
            max_search_results=int(os.getenv("MAX_SEARCH_RESULTS", "10")),
        )

    def validate(self) -> List[str]:
        errors = []
        if not self.anthropic_api_key:
            errors.append("ANTHROPIC_API_KEY is required")
        return errors
