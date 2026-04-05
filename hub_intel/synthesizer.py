"""Synthesize collected intelligence into McKinsey-grade executive brief."""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from hub_intel.collector import Finding
from hub_intel.config import HubIntelConfig, CONTEXT_DIR, TEMPLATES_DIR

logger = logging.getLogger(__name__)

SYNTHESIS_SYSTEM_PROMPT = """\
You are HUB-INTEL, a competitive intelligence analyst producing CEO-ready briefs \
on HubSpot for Mailchimp's R&A and Lead-to-Cash leadership.

Output standard: McKinsey/BCG quality.
Writing rules:
1. Pyramid Principle: conclusion first, evidence second
2. No filler — every sentence earns its place
3. Quantify everything (numbers, percentages, dollar figures)
4. Competitive framing: every finding references Mailchimp L2C position
5. Strict 2-page ceiling — ruthlessly edit
6. Action verbs with deadlines in recommendations
7. Always validate the moat: does this week's news threaten ledger-anchored analytics?
"""


class BriefSynthesizer:
    """Synthesizes findings into the executive brief markdown."""

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
                raise RuntimeError("anthropic package required for synthesis")
        return self._client

    def synthesize(
        self,
        findings: Dict[str, List[Finding]],
        report_date: Optional[str] = None,
    ) -> str:
        """Generate the full McKinsey-format brief from findings."""
        if report_date is None:
            report_date = datetime.utcnow().strftime("%B %d, %Y")

        template = self._load_template()
        context = self._load_strategic_context()
        findings_text = self._format_findings(findings)

        prompt = (
            f"## Strategic Context\n{context}\n\n"
            f"## Collected Intelligence ({self._count_findings(findings)} findings)\n"
            f"{findings_text}\n\n"
            f"## Report Template\n{template}\n\n"
            f"## Instructions\n"
            f"Generate the HUB-INTEL executive brief for the week of {report_date}.\n"
            f"Use the template format exactly. Replace all placeholders with real findings.\n"
            f"Date all recommendations with specific deadlines (2 weeks out).\n"
            f"Ensure every section references our L2C competitive position.\n"
            f"The Competitive Moat Status section must explicitly confirm whether our "
            f"ledger-anchored analytics advantage still holds.\n"
            f"Output ONLY the markdown brief, nothing else."
        )

        try:
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=8192,
                system=SYNTHESIS_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except Exception as e:
            logger.error("Synthesis API call failed: %s", e)
            raise

    def synthesize_from_markdown(self, raw_markdown: str) -> str:
        """Pass through pre-written markdown (for manual/first report)."""
        return raw_markdown

    def _load_template(self) -> str:
        template_file = TEMPLATES_DIR / "brief_template.md"
        if template_file.exists():
            return template_file.read_text()
        return self._default_template()

    def _load_strategic_context(self) -> str:
        context_file = CONTEXT_DIR / "l2c_strategic.md"
        if context_file.exists():
            return context_file.read_text()
        return ""

    def _format_findings(self, findings: Dict[str, List[Finding]]) -> str:
        sections = []
        for track, items in findings.items():
            if not items:
                continue
            section = f"### {track.replace('_', ' ').title()}\n"
            for f in items:
                priority_emoji = {"red": "🔴", "yellow": "🟡", "green": "🟢"}.get(
                    f.priority, "⚪"
                )
                section += (
                    f"- {priority_emoji} **{f.title}**: {f.detail}"
                    f" [{', '.join(f.tags)}]\n"
                )
            sections.append(section)
        return "\n".join(sections)

    def _count_findings(self, findings: Dict[str, List[Finding]]) -> int:
        return sum(len(v) for v in findings.values())

    @staticmethod
    def _default_template() -> str:
        return """\
# HUB-INTEL | Week of [DATE]
**HubSpot Competitive Intelligence | Mailchimp R&A + L2C | Confidential**

---

## EXECUTIVE SNAPSHOT

| Signal | Insight | Mailchimp L2C Implication |
|--------|---------|--------------------------|
| 🔴 [signal] | [evidence] | [action] |
| 🟡 [signal] | [evidence] | [action] |
| 🟢 [signal] | [evidence] | [action] |

---

## I. PRODUCT & AI VELOCITY
[Tag: 🏢 CRM/L2C | 📊 R&A | 🤖 AI. End with **L2C implication:**]

## II. REPORTING & ANALYTICS POSITIONING
[Frame against L2C Analytics competitive matrix. End with **R&A implication:**]

## III. LEAD-TO-CASH & CRM CAPABILITIES
[Map to FY27 L2C roadmap. End with **L2C implication:**]

## IV. GO-TO-MARKET & DIGITAL PRESENCE
**Messaging:** [positioning]
**SEO/SEM:** [keywords, Academy]
**Video & Social:** [presence]
**Case Studies:** [verticals]

## V. MARKET SIGNALS
[press, partnerships, pricing, earnings]

## VI. VOICE OF MARKET

| Source | Positive | Negative | R&A/L2C-Specific |
|--------|----------|----------|--------------------|
| Reddit | | | |
| G2/Capterra | | | |

---

## COMPETITIVE MOAT STATUS
[Confirm structural advantages. Ledger-anchored moat status.]

## STRATEGIC IMPLICATIONS MATRIX

| Priority | HubSpot Move | Impact to Mailchimp R&A + L2C | Recommended Action | Owner |
|----------|-------------|-------------------------------|-------------------|-------|
| 🔴 | | | | |
| 🟡 | | | | |
| 🟢 | | | | |

---

*HUB-INTEL v2.0 | [DATE] | Sources: [count] | Next: [NEXT MONDAY]*
"""
