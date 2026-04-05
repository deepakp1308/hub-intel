"""Shared test fixtures for HUB-INTEL."""
from __future__ import annotations

import pytest

from hub_intel.collector import Finding
from hub_intel.config import HubIntelConfig


@pytest.fixture
def config():
    """Test config with dummy values."""
    return HubIntelConfig(
        anthropic_api_key="test-key-000",
        slack_bot_token="xoxb-test-000",
        slack_user_id="W8FL6URHQ",
        model="claude-sonnet-4-20250514",
    )


@pytest.fixture
def sample_findings():
    """Sample findings for testing synthesis and rendering."""
    return {
        "product_updates": [
            Finding(
                track="product_updates",
                title="Breeze AI multi-object reporting",
                detail="Breeze now generates cross-object reports from NL queries.",
                source="hubspot.com/new",
                priority="red",
                tags=["R&A", "AI"],
            ),
            Finding(
                track="product_updates",
                title="Smarter Sales Meetings",
                detail="AI pre-meeting insights, summaries, and follow-up actions.",
                source="hubspot.com/new",
                priority="yellow",
                tags=["CRM/L2C"],
            ),
        ],
        "ai_breeze": [
            Finding(
                track="ai_breeze",
                title="4 production Breeze Agents",
                detail="Prospecting, Content, Data, Closing agents now stable.",
                source="hubspot.com/products/ai",
                priority="yellow",
                tags=["AI"],
            ),
        ],
        "pricing": [
            Finding(
                track="pricing",
                title="Marketing Hub Pro at $890/mo",
                detail="Plus $3K mandatory onboarding. Total cost opaque for SMBs.",
                source="hubspot.com/pricing",
                priority="green",
                tags=["Pricing"],
            ),
        ],
    }


@pytest.fixture
def sample_markdown():
    """Sample brief markdown for rendering tests."""
    return """\
# HUB-INTEL | Week of April 4, 2026
**HubSpot Competitive Intelligence | Mailchimp R&A + L2C | Confidential**

---

## EXECUTIVE SNAPSHOT

| Signal | Insight | Mailchimp L2C Implication |
|--------|---------|--------------------------|
| 🔴 Breeze AI reporting | Cross-object NL reports | Accelerate conversational reporting |
| 🟡 Smarter Meetings | AI meeting lifecycle | Map to L2C roadmap |
| 🟢 Pricing complexity | $890/mo + fees | TCO transparency play |

---

## I. PRODUCT & AI VELOCITY

HubSpot shipped Breeze AI updates across all Hubs. 🤖

**L2C implication:** Monitor Breeze agent expansion closely.

## II. REPORTING & ANALYTICS POSITIONING

Attribution remains Enterprise-gated at $3,600+/yr.

**R&A implication:** Our all-tier attribution is a clear differentiator.

---

*HUB-INTEL v2.0 | April 4, 2026 | Sources: 12 | Next: April 11, 2026*
"""


@pytest.fixture
def raw_findings_text():
    """Raw text from a simulated API response with FINDING blocks."""
    return """\
Here are the findings:

FINDING:
Title: Breeze Studio custom agents
Detail: Teams can now build custom AI agents without code via Breeze Studio marketplace.
Priority: yellow
Tags: AI, CRM/L2C
Source: hubspot.com/new

FINDING:
Title: Commerce Hub subscription billing
Detail: New subscription management with automated recurring invoicing and payment collection.
Priority: red
Tags: CRM/L2C, Pricing
Source: hubspot.com/products/commerce
"""
