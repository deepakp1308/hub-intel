# HUB-INTEL v2.0

HubSpot Competitive Intelligence Agent producing weekly McKinsey-grade executive briefs for Mailchimp's R&A and Lead-to-Cash leadership.

## Output
- 2-page executive brief (Markdown + HTML + PDF)
- GitHub Pages deployment
- Slack DM with top 3 signals

## Architecture

```
IntelCollector → BriefSynthesizer → ReportRenderer → GitHubPublisher + SlackNotifier
     ↓                ↓                  ↓
  10 tracks      Claude API         HTML/PDF
  web research   McKinsey format    styled report
```

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Run with pre-written markdown
python -m hub_intel.agent --markdown reports/HUB-INTEL_2026-04-04.md --skip-publish --skip-notify

# Full automated run (requires ANTHROPIC_API_KEY)
export ANTHROPIC_API_KEY=sk-...
python -m hub_intel.agent --date "April 4, 2026" -v
```

## Configuration

| Env Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes (auto mode) | Claude API key for research + synthesis |
| `SLACK_BOT_TOKEN` | No | Slack bot token for DM notifications |
| `SLACK_USER_ID` | No | Slack user ID for DM target (default: W8FL6URHQ) |
| `GITHUB_PAGES_URL` | No | URL for report links |

## Testing

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## Weekly Schedule

GitHub Actions runs every Monday at midnight ET. Can also be triggered manually via `workflow_dispatch`.

## 10 Intelligence Tracks

1. Product & Platform Updates
2. AI & Breeze Intelligence
3. Reporting, Analytics & Attribution
4. Lead-to-Cash & CRM
5. Go-to-Market Messaging
6. SEO & Content Strategy
7. Digital Video & Social
8. Press, Partnerships & Org Signals
9. Pricing & Competitive Position
10. Voice of Market
