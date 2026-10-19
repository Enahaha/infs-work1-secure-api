"""Render the actual SpotBugs XML as an HTML report, without changing scan status."""
from pathlib import Path
from html import escape
import xml.etree.ElementTree as ET

source = Path("target/spotbugsXml.xml")
root = ET.parse(source).getroot()  # Missing/invalid XML must fail, never become a clean report.
if root.tag != "BugCollection":
    raise ValueError("Expected a SpotBugs BugCollection")
bugs = root.findall("BugInstance")
errors = root.find("Errors")
error_count = int(errors.get("errors", "0")) if errors is not None else 0
rows = []
for bug in bugs:
    location = bug.find("SourceLine")
    if location is None:
        location = bug.find(".//SourceLine")
    where = "" if location is None else location.get("sourcepath", "") + ":" + location.get("start", "")
    cells = [bug.get("type", ""), bug.get("priority", ""), where,
             bug.findtext("LongMessage") or bug.findtext("ShortMessage") or ""]
    rows.append("<tr>" + "".join("<td>" + escape(cell) + "</td>" for cell in cells) + "</tr>")
body = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Work 1 SAST report</title>
<style>body{font:16px system-ui;max-width:1100px;margin:48px auto;padding:0 24px;line-height:1.6}table{border-collapse:collapse;width:100%}td,th{border:1px solid #bbb;padding:12px;text-align:left}</style>
<h1>Work 1: SpotBugs + FindSecBugs</h1>
<p>Source: target/spotbugsXml.xml. SECURITY category, all confidence levels.</p>
<p>Reviewed exceptions: endpoint inventory in the two API controllers, and CSRF configuration for the stateless Bearer-only API. See docs/SECURITY_REVIEW.md and config/spotbugs-reviewed.xml.</p>
"""
body += f"<p><strong>Reported findings after documented exceptions: {len(bugs)}. Analysis errors: {error_count}.</strong></p>"
body += "<p>This is a rendering of the scan output; consult the CI job status for build success. It does not prove the absence of vulnerabilities.</p>"
body += "<table><tr><th>Rule</th><th>Priority</th><th>Location</th><th>Message</th></tr>"
body += "".join(rows) + "</table></html>"
output = Path("target/reports/sast-report.html")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(body, encoding="utf-8")
print(f"Rendered {len(bugs)} findings, {error_count} errors to {output}")
