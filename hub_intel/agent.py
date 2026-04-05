"""HUB-INTEL main orchestrator — ties collection, synthesis, rendering, delivery."""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from hub_intel.collector import IntelCollector
from hub_intel.config import HubIntelConfig, REPORTS_DIR
from hub_intel.notifier import SlackNotifier
from hub_intel.publisher import GitHubPublisher
from hub_intel.renderer import ReportRenderer
from hub_intel.synthesizer import BriefSynthesizer

logger = logging.getLogger("hub_intel")


class HubIntelAgent:
    """Main agent that orchestrates the full intelligence pipeline."""

    def __init__(self, config: Optional[HubIntelConfig] = None):
        self.config = config or HubIntelConfig.from_env()
        self.collector = IntelCollector(self.config)
        self.synthesizer = BriefSynthesizer(self.config)
        self.renderer = ReportRenderer()
        self.publisher = GitHubPublisher()
        self.notifier = SlackNotifier(self.config)

    def run(
        self,
        report_date: Optional[str] = None,
        skip_collect: bool = False,
        skip_publish: bool = False,
        skip_notify: bool = False,
        markdown_input: Optional[str] = None,
    ) -> dict:
        """Execute the full pipeline: collect → synthesize → render → publish → notify."""
        if report_date is None:
            report_date = datetime.utcnow().strftime("%B %d, %Y")

        date_slug = _date_slug(report_date)
        result = {"date": report_date, "date_slug": date_slug}

        logger.info("=== HUB-INTEL v2.0 | %s ===", report_date)

        # Phase 1: Collect
        if markdown_input:
            logger.info("Using provided markdown input")
            brief_md = markdown_input
            findings = {}
        elif skip_collect:
            logger.info("Skipping collection — using existing report")
            existing = REPORTS_DIR / f"HUB-INTEL_{date_slug}.md"
            if existing.exists():
                brief_md = existing.read_text()
            else:
                logger.error("No existing report found: %s", existing)
                return {"error": "No existing report"}
            findings = {}
        else:
            logger.info("Phase 1: Intelligence Collection")
            findings = self.collector.collect_all()
            total = sum(len(v) for v in findings.values())
            logger.info("Collected %d findings across %d tracks", total, len(findings))
            result["findings_count"] = total

            # Phase 2: Synthesis
            logger.info("Phase 2: Synthesis")
            brief_md = self.synthesizer.synthesize(findings, report_date)

        result["markdown"] = brief_md

        # Phase 3: Render
        logger.info("Phase 3: Rendering")
        paths = self.renderer.save_report(brief_md, date_slug)
        result["paths"] = {k: str(v) for k, v in paths.items()}
        logger.info("Saved: %s", list(paths.keys()))

        # Phase 4: Publish
        if not skip_publish and self.publisher.has_changes():
            logger.info("Phase 4: Publishing to GitHub")
            published = self.publisher.publish(date_slug)
            result["published"] = published
        else:
            logger.info("Phase 4: Skipped (no changes or --skip-publish)")
            result["published"] = False

        # Phase 5: Notify
        if not skip_notify and self.config.slack_bot_token:
            logger.info("Phase 5: Slack Notification")
            top_signals = SlackNotifier.extract_top_signals(findings)
            report_url = self.config.github_pages_url
            notified = self.notifier.notify(
                report_date, top_signals, report_url=report_url
            )
            result["notified"] = notified
        else:
            logger.info("Phase 5: Skipped (no Slack token or --skip-notify)")
            result["notified"] = False

        logger.info("=== HUB-INTEL complete ===")
        return result


def _date_slug(date_str: str) -> str:
    """Convert human date to YYYY-MM-DD slug."""
    for fmt in ("%B %d, %Y", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    # Fallback: use today
    return datetime.utcnow().strftime("%Y-%m-%d")


def main():
    parser = argparse.ArgumentParser(description="HUB-INTEL Competitive Intelligence Agent")
    parser.add_argument("--date", help="Report date (e.g., 'April 4, 2026')")
    parser.add_argument("--skip-collect", action="store_true", help="Skip intelligence collection")
    parser.add_argument("--skip-publish", action="store_true", help="Skip GitHub publish")
    parser.add_argument("--skip-notify", action="store_true", help="Skip Slack notification")
    parser.add_argument("--markdown", help="Path to pre-written markdown report")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    config = HubIntelConfig.from_env()

    markdown_input = None
    if args.markdown:
        markdown_input = Path(args.markdown).read_text()

    agent = HubIntelAgent(config)
    result = agent.run(
        report_date=args.date,
        skip_collect=args.skip_collect,
        skip_publish=args.skip_publish,
        skip_notify=args.skip_notify,
        markdown_input=markdown_input,
    )

    if "error" in result:
        logger.error("Agent failed: %s", result["error"])
        sys.exit(1)

    print(f"\nReport generated: {result.get('date')}")
    for fmt, path in result.get("paths", {}).items():
        print(f"  {fmt}: {path}")


if __name__ == "__main__":
    main()
