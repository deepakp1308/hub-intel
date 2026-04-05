"""Render markdown reports to HTML and PDF."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from hub_intel.config import DOCS_DIR, REPORTS_DIR, TEMPLATES_DIR

logger = logging.getLogger(__name__)

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {{
    --navy: #162251;
    --page-bg: #f0f4f8;
    --primary-text: #1a1f36;
    --secondary-text: #6b7c93;
    --accent-blue: #0070d2;
    --ai-teal: #00b9a9;
    --chart-navy: #1e3a6e;
    --green: #1aab68;
    --red: #d13438;
    --card-border: #e8edf5;
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
    font-family: 'Inter', -apple-system, 'Helvetica Neue', Arial, sans-serif;
    background: var(--page-bg);
    color: var(--primary-text);
    line-height: 1.6;
    padding: 0;
}}

.report-container {{
    max-width: 900px;
    margin: 0 auto;
    padding: 40px;
}}

.report-header {{
    background: var(--navy);
    color: white;
    padding: 32px 40px;
    border-radius: 12px 12px 0 0;
    margin-bottom: 0;
}}

.report-header h1 {{
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 4px;
    letter-spacing: -0.5px;
}}

.report-header .subtitle {{
    font-size: 13px;
    opacity: 0.8;
}}

.report-body {{
    background: white;
    padding: 40px;
    border-radius: 0 0 12px 12px;
    border: 1px solid var(--card-border);
    box-shadow: 0 2px 8px rgba(26,40,96,0.06);
}}

h1 {{ font-size: 24px; font-weight: 700; margin: 0 0 16px 0; color: var(--primary-text); }}
h2 {{ font-size: 18px; font-weight: 600; margin: 32px 0 12px 0; color: var(--navy); border-bottom: 2px solid var(--card-border); padding-bottom: 8px; }}
h3 {{ font-size: 15px; font-weight: 600; margin: 20px 0 8px 0; color: var(--primary-text); }}

p {{ margin: 0 0 12px 0; font-size: 14px; color: var(--primary-text); }}

strong {{ font-weight: 600; }}

table {{
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 13px;
}}

th {{
    background: var(--navy);
    color: white;
    padding: 10px 12px;
    text-align: left;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

td {{
    padding: 10px 12px;
    border-bottom: 1px solid var(--card-border);
    vertical-align: top;
}}

tr:nth-child(even) td {{
    background: #f8fafd;
}}

hr {{
    border: none;
    border-top: 1px solid var(--card-border);
    margin: 24px 0;
}}

em {{ color: var(--secondary-text); font-size: 12px; }}

.priority-red {{ color: var(--red); font-weight: 600; }}
.priority-yellow {{ color: #d4a017; font-weight: 600; }}
.priority-green {{ color: var(--green); font-weight: 600; }}

@media print {{
    body {{ background: white; }}
    .report-container {{ padding: 0; max-width: 100%; }}
    .report-header {{ border-radius: 0; }}
    .report-body {{ border: none; box-shadow: none; border-radius: 0; }}
}}

@page {{
    size: letter;
    margin: 0.75in;
}}
</style>
</head>
<body>
<div class="report-container">
    <div class="report-header">
        <h1>{title}</h1>
        <div class="subtitle">{subtitle}</div>
    </div>
    <div class="report-body">
        {content}
    </div>
</div>
</body>
</html>
"""


class ReportRenderer:
    """Converts markdown briefs to HTML and PDF."""

    def __init__(self):
        pass

    def to_html(self, markdown_text: str, title: str = "HUB-INTEL") -> str:
        """Convert markdown brief to styled HTML."""
        try:
            import markdown as md
            html_content = md.markdown(
                markdown_text,
                extensions=["tables", "fenced_code", "nl2br"],
            )
        except ImportError:
            html_content = self._basic_md_to_html(markdown_text)

        # Extract subtitle from first bold line
        subtitle = "HubSpot Competitive Intelligence | Mailchimp R&A + L2C | Confidential"
        for line in markdown_text.split("\n"):
            if line.startswith("**") and "Confidential" in line:
                subtitle = line.strip("*").strip()
                break

        # Extract title from first H1
        for line in markdown_text.split("\n"):
            if line.startswith("# "):
                title = line.lstrip("# ").strip()
                break

        return HTML_TEMPLATE.format(
            title=title,
            subtitle=subtitle,
            content=html_content,
        )

    def to_pdf(self, html: str, output_path: Path) -> Optional[Path]:
        """Convert HTML to PDF using weasyprint if available."""
        try:
            from weasyprint import HTML as WPHTML
            WPHTML(string=html).write_pdf(str(output_path))
            logger.info("PDF generated: %s", output_path)
            return output_path
        except ImportError:
            logger.warning("weasyprint not installed — PDF skipped")
            return None
        except Exception as e:
            logger.error("PDF generation failed: %s", e)
            return None

    def save_report(
        self,
        markdown_text: str,
        date_str: str,
    ) -> dict:
        """Save report in all formats. Returns paths."""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        DOCS_DIR.mkdir(parents=True, exist_ok=True)

        slug = f"HUB-INTEL_{date_str}"
        paths = {}

        # Markdown
        md_path = REPORTS_DIR / f"{slug}.md"
        md_path.write_text(markdown_text, encoding="utf-8")
        paths["markdown"] = md_path

        # HTML
        html = self.to_html(markdown_text)
        html_path = REPORTS_DIR / f"{slug}.html"
        html_path.write_text(html, encoding="utf-8")
        paths["html"] = html_path

        # GitHub Pages copy
        pages_path = DOCS_DIR / "index.html"
        pages_path.write_text(html, encoding="utf-8")
        paths["github_pages"] = pages_path

        # Archive copy for GitHub Pages
        archive_path = DOCS_DIR / f"{slug}.html"
        archive_path.write_text(html, encoding="utf-8")
        paths["archive"] = archive_path

        # PDF (optional)
        pdf_path = REPORTS_DIR / f"{slug}.pdf"
        result = self.to_pdf(html, pdf_path)
        if result:
            paths["pdf"] = pdf_path

        logger.info("Report saved: %s", {k: str(v) for k, v in paths.items()})
        return paths

    @staticmethod
    def _basic_md_to_html(text: str) -> str:
        """Minimal markdown-to-HTML fallback."""
        import re
        lines = text.split("\n")
        html_lines = []
        in_table = False

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("# "):
                html_lines.append(f"<h1>{stripped[2:]}</h1>")
            elif stripped.startswith("## "):
                html_lines.append(f"<h2>{stripped[3:]}</h2>")
            elif stripped.startswith("### "):
                html_lines.append(f"<h3>{stripped[4:]}</h3>")
            elif stripped.startswith("---"):
                html_lines.append("<hr>")
            elif stripped.startswith("|"):
                if not in_table:
                    html_lines.append("<table>")
                    in_table = True
                cells = [c.strip() for c in stripped.split("|")[1:-1]]
                if all(c.replace("-", "").replace(":", "") == "" for c in cells):
                    continue
                row = "".join(f"<td>{c}</td>" for c in cells)
                html_lines.append(f"<tr>{row}</tr>")
            else:
                if in_table:
                    html_lines.append("</table>")
                    in_table = False
                if stripped.startswith("**") and stripped.endswith("**"):
                    html_lines.append(f"<p><strong>{stripped[2:-2]}</strong></p>")
                elif stripped.startswith("*") and stripped.endswith("*"):
                    html_lines.append(f"<p><em>{stripped[1:-1]}</em></p>")
                elif stripped:
                    # Bold/italic inline
                    processed = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", stripped)
                    processed = re.sub(r"\*(.+?)\*", r"<em>\1</em>", processed)
                    html_lines.append(f"<p>{processed}</p>")

        if in_table:
            html_lines.append("</table>")

        return "\n".join(html_lines)
