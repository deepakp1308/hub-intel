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
:root {{
    --black: #000000;
    --dark-gray: #333333;
    --mid-gray: #666666;
    --light-gray: #999999;
    --border-gray: #cccccc;
    --bg-gray: #f5f5f5;
    --row-alt: #fafafa;
    --header-bg: #222222;
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
    font-family: Arial, Helvetica, sans-serif;
    font-size: 10pt;
    background: #ffffff;
    color: var(--black);
    line-height: 1.55;
    padding: 0;
}}

.report-container {{
    max-width: 900px;
    margin: 0 auto;
    padding: 40px;
}}

.report-header {{
    background: var(--header-bg);
    color: #ffffff;
    padding: 28px 36px;
    border-radius: 4px 4px 0 0;
    margin-bottom: 0;
}}

.report-header h1 {{
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 4px;
    color: #ffffff !important;
}}

.report-header .subtitle {{
    font-size: 9pt;
    color: #cccccc;
}}

.report-body {{
    background: #ffffff;
    padding: 36px;
    border-radius: 0 0 4px 4px;
    border: 1px solid var(--border-gray);
}}

h1 {{ font-size: 18pt; font-weight: 700; margin: 0 0 14px 0; color: var(--black); }}
h2 {{ font-size: 13pt; font-weight: 700; margin: 28px 0 10px 0; color: var(--black); border-bottom: 2px solid var(--dark-gray); padding-bottom: 6px; }}
h3 {{ font-size: 11pt; font-weight: 700; margin: 18px 0 6px 0; color: var(--dark-gray); }}

p {{ margin: 0 0 10px 0; font-size: 10pt; color: var(--black); }}

strong {{ font-weight: 700; color: var(--black); }}

table {{
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 9pt;
}}

th {{
    background: var(--dark-gray);
    color: #ffffff;
    padding: 8px 10px;
    text-align: left;
    font-weight: 700;
    font-size: 8pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

td {{
    padding: 8px 10px;
    border-bottom: 1px solid var(--border-gray);
    vertical-align: top;
    color: var(--black);
}}

tr:nth-child(even) td {{
    background: var(--row-alt);
}}

hr {{
    border: none;
    border-top: 1px solid var(--border-gray);
    margin: 20px 0;
}}

em {{ color: var(--mid-gray); font-size: 9pt; }}

@media print {{
    body {{ background: white; }}
    .report-container {{ padding: 0; max-width: 100%; }}
    .report-header {{ border-radius: 0; }}
    .report-body {{ border: none; border-radius: 0; }}
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
        # Extract title and subtitle before stripping them from body
        subtitle = "HubSpot Competitive Intelligence | Mailchimp R&A + L2C | Confidential"
        for line in markdown_text.split("\n"):
            if line.startswith("**") and "Confidential" in line:
                subtitle = line.strip("*").strip()
                break

        for line in markdown_text.split("\n"):
            if line.startswith("# "):
                title = line.lstrip("# ").strip()
                break

        # Strip the H1 title and bold subtitle from body to avoid duplication
        body_lines = []
        skip_next_blank = False
        for line in markdown_text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("# ") and title in stripped:
                skip_next_blank = True
                continue
            if stripped.startswith("**") and "Confidential" in stripped:
                skip_next_blank = True
                continue
            if skip_next_blank and stripped == "":
                skip_next_blank = False
                continue
            skip_next_blank = False
            body_lines.append(line)
        body_md = "\n".join(body_lines)

        try:
            import markdown as md
            html_content = md.markdown(
                body_md,
                extensions=["tables", "fenced_code", "nl2br"],
            )
        except ImportError:
            html_content = self._basic_md_to_html(body_md)

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
