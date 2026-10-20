"""Build the Work 1 report HTML and PDF from Markdown.

Requires the `markdown` Python package and Google Chrome. Chrome is used only
as the HTML-to-PDF renderer so that the PDF matches the HTML preview.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "docs" / "report"
MD = REPORT_DIR / "Work1-Report.md"
HTML = REPORT_DIR / "Work1-Report.html"
PDF = REPORT_DIR / "Work1-Report.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: A4; margin: 17mm 16mm 18mm 16mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  margin: 0; color: #17202a;
  font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  font-size: 10.2pt; line-height: 1.5;
}
a { color: #0b5cad; text-decoration: none; }
p { margin: 0 0 7pt; text-align: justify; }
h1, h2, h3, h4 { color: #102a43; page-break-after: avoid; }
h1 { font-size: 20pt; border-bottom: 2px solid #102a43; padding-bottom: 4pt; margin: 16pt 0 10pt; }
h2 { font-size: 15pt; margin: 18pt 0 8pt; border-bottom: 1px solid #bcccdc; padding-bottom: 3pt; }
h3 { font-size: 11.8pt; margin: 13pt 0 5pt; }
h4 { font-size: 10.6pt; margin: 10pt 0 4pt; }
ul, ol { margin: 4pt 0 8pt 16pt; padding: 0; }
li { margin: 2pt 0; }
table { border-collapse: collapse; width: 100%; margin: 7pt 0 10pt; font-size: 9pt; page-break-inside: avoid; }
th, td { border: 1px solid #aebdcc; padding: 4pt 6pt; vertical-align: top; text-align: left; }
th { background: #eaf1f8; color: #102a43; }
code { font-family: "SFMono-Regular", Menlo, Consolas, monospace; font-size: 8.8pt; background: #f2f4f7; padding: 1pt 2pt; border-radius: 2pt; }
pre { background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 4pt; padding: 7pt 9pt; margin: 6pt 0 9pt; page-break-inside: avoid; }
pre code { background: none; padding: 0; font-size: 8.1pt; line-height: 1.35; white-space: pre-wrap; word-break: break-word; }
img { display: block; max-width: 100%; max-height: 10.8cm; margin: 8pt auto 3pt; border: 1px solid #d0d7de; page-break-inside: avoid; }
p > img + em, p > img { page-break-inside: avoid; }
.page-break { page-break-before: always; }
.title-page { text-align: center; padding-top: 48mm; page-break-after: always; }
.title-page .course { font-size: 13pt; letter-spacing: 1.2pt; color: #486581; margin-bottom: 22mm; text-align: center; }
.title-page h1 { font-size: 27pt; border: none; margin: 0 0 7mm; padding: 0; page-break-after: avoid; }
.title-page h2 { font-size: 15.5pt; border: none; margin: 0 0 9mm; padding: 0; line-height: 1.35; page-break-after: avoid; }
.title-page .subtitle { font-size: 12pt; color: #334e68; margin-bottom: 16mm; text-align: center; }
.title-page .meta { width: 72%; margin: 0 auto 12mm; font-size: 10.5pt; border: none; }
.title-page .meta td { border: none; padding: 3pt 8pt; text-align: left; }
.title-page .meta td:first-child { color: #486581; width: 34%; text-align: right; }
.title-page .repo { font-size: 8.2pt; color: #52606d; line-height: 1.5; text-align: center; word-break: break-all; }
@media print { a { color: #102a43; } }
"""


def main() -> None:
    source = MD.read_text(encoding="utf-8")
    body = markdown.markdown(
        source,
        extensions=["tables", "fenced_code", "toc", "attr_list", "md_in_html", "sane_lists"],
    )
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Work 1 — Secure REST API and CVE-2023-28432</title>
<style>{CSS}</style></head>
<body>{body}</body></html>"""
    HTML.write_text(html, encoding="utf-8")

    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
         "--no-default-browser-check", "--no-pdf-header-footer",
         "--user-data-dir=/tmp/work1-report-chrome",
         "--virtual-time-budget=5000",
         f"--print-to-pdf={PDF}", HTML.as_uri()],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    print(f"HTML: {HTML} ({HTML.stat().st_size} bytes)")
    print(f"PDF:  {PDF} ({PDF.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
