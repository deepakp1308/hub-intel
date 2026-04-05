"""Slack notification for HUB-INTEL reports."""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

from hub_intel.collector import Finding
from hub_intel.config import HubIntelConfig

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Sends report notifications via Slack DM."""

    def __init__(self, config: HubIntelConfig):
        self.config = config
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                from slack_sdk import WebClient
                self._client = WebClient(token=self.config.slack_bot_token)
            except ImportError:
                raise RuntimeError("slack_sdk required for notifications")
        return self._client

    def notify(
        self,
        date_str: str,
        top_signals: List[Dict],
        report_url: Optional[str] = None,
        pdf_url: Optional[str] = None,
    ) -> bool:
        """Send DM with top signals and report links."""
        message = self._format_message(date_str, top_signals, report_url, pdf_url)
        try:
            response = self.client.chat_postMessage(
                channel=self.config.slack_user_id,
                text=message,
                mrkdwn=True,
            )
            logger.info("Slack DM sent: %s", response.get("ts", ""))
            return True
        except Exception as e:
            logger.error("Slack notification failed: %s", e)
            return False

    def _format_message(
        self,
        date_str: str,
        top_signals: List[Dict],
        report_url: Optional[str] = None,
        pdf_url: Optional[str] = None,
    ) -> str:
        priority_emoji = {"red": ":red_circle:", "yellow": ":large_yellow_circle:", "green": ":large_green_circle:"}

        lines = [
            f":star: *HUB-INTEL | Week of {date_str}*",
            "",
            "*Top Signals:*",
        ]

        for i, signal in enumerate(top_signals[:3], 1):
            emoji = priority_emoji.get(signal.get("priority", ""), ":white_circle:")
            lines.append(f"{i}. {emoji} *{signal.get('title', '')}* — {signal.get('detail', '')}")

        lines.append("")

        if report_url:
            lines.append(f":link: <{report_url}|View Full Report>")
        if pdf_url:
            lines.append(f":page_facing_up: <{pdf_url}|Download PDF>")

        lines.extend([
            "",
            "_HUB-INTEL v2.0 | Competitive Intelligence Agent_",
        ])

        return "\n".join(lines)

    @staticmethod
    def extract_top_signals(
        findings: Dict[str, List[Finding]], limit: int = 3
    ) -> List[Dict]:
        """Extract top N signals sorted by priority (red > yellow > green)."""
        priority_order = {"red": 0, "yellow": 1, "green": 2}
        all_findings = []
        for items in findings.values():
            all_findings.extend(items)

        all_findings.sort(key=lambda f: priority_order.get(f.priority, 3))

        return [
            {"title": f.title, "detail": f.detail, "priority": f.priority}
            for f in all_findings[:limit]
        ]
