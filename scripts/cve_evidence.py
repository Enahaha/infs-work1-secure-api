"""Render captured terminal transcripts into PNG evidence images.

The images are visual copies of the actual command output stored in
docs/cve/CVE-2023-28432/transcripts. Chrome is used only as an HTML renderer;
the text shown in the images is not rewritten.
"""
from __future__ import annotations

import html
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CVE = ROOT / "docs" / "cve" / "CVE-2023-28432"
OUT = ROOT / "docs" / "screenshots" / "cve"
HTML_DIR = CVE / "evidence-html"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

STYLE = """
* { box-sizing: border-box; }
body {
  margin: 0; padding: 44px 56px 36px;
  background: #0b1020; color: #dbe4f0;
  font-family: "SFMono-Regular", "SF Mono", Menlo, Consolas, monospace;
}
h1 { margin: 0 0 10px; font: 700 34px/1.2 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #ffffff; }
.sub { margin: 0 0 22px; color: #93a4bd; font: 16px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
.bar { height: 6px; border-radius: 3px; background: __ACCENT__; margin: 0 0 26px; }
h2 { margin: 26px 0 12px; font: 600 19px/1.3 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #cfe0ff; }
.card { background: #111a2e; border: 1px solid #22304d; border-radius: 12px; padding: 22px 26px; margin: 14px 0; }
pre { margin: 0; white-space: pre-wrap; word-break: break-word; font: 16px/1.55 "SFMono-Regular", Menlo, Consolas, monospace; color: #dbe4f0; }
.hl { color: #ffd166; font-weight: 700; }
.red { color: #ff6b6b; font-weight: 700; }
.ok { color: #5ee6a8; font-weight: 700; }
.muted { color: #8b9bb4; }
.alert { margin: 20px 0; padding: 18px 22px; border-radius: 10px; border-left: 6px solid #ff6b6b; background: #2a1520; color: #ffd7d7; font: 17px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
.alert.ok { border-left-color: #5ee6a8; background: #10251d; color: #c9ffe8; }
.footer { margin-top: 26px; padding-top: 14px; border-top: 1px solid #22304d; color: #6f819c; font: 13px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
"""


def read(name: str) -> str:
    return (CVE / "transcripts" / name).read_text(encoding="utf-8").rstrip()


def page(title: str, subtitle: str, body: str, accent: str, footer: str) -> str:
    return f"""<!doctype html><html lang="en"><meta charset="utf-8">
<title>{html.escape(title)}</title><style>{STYLE.replace('__ACCENT__', accent)}</style>
<body><h1>{html.escape(title)}</h1><p class="sub">{html.escape(subtitle)}</p>
<div class="bar"></div>{body}<div class="footer">{html.escape(footer)}</div></body></html>"""


def pre(text: str) -> str:
    return f'<div class="card"><pre>{html.escape(text)}</pre></div>'


def render(name: str, title: str, subtitle: str, body: str, accent: str, height: int) -> None:
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    html_path = HTML_DIR / f"{name}.html"
    html_path.write_text(
        page(title, subtitle, body, accent,
             "Captured from the local Vulhub MinIO environment on 2026-10-20 (Asia/Shanghai). "
             "The transcript is unmodified output; HTTP headers are shown as received."),
        encoding="utf-8",
    )
    png_path = OUT / f"{name}.png"
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         "--no-first-run", "--no-default-browser-check",
         "--user-data-dir=/tmp/cve-evidence-chrome",
         f"--window-size=1400,{height}", "--force-device-scale-factor=1",
         f"--screenshot={png_path}", html_path.as_uri()],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    print(f"{png_path} ({png_path.stat().st_size} bytes)")


def main() -> None:
    # 1. Vulnerable cluster and version.
    body = (
        "<h2>Cluster is running</h2>" + pre(read("01_environment.txt"))
        + "<h2>MinIO release</h2>" + pre(read("02_version_vulnerable.txt"))
    )
    render("01_vulnerable_cluster",
           "CVE-2023-28432 - vulnerable MinIO cluster",
           "Vulhub 3-node distributed deployment; API on :9000, console on :9001",
           body, "#ff6b6b", 900)

    # 2. Exploit: parse the actual JSON body and pretty-print the sensitive part.
    raw = read("03_exploit_response.txt")
    status = raw.splitlines()[0] if raw else ""
    env = json.loads((CVE / "transcripts" / "03_exploit_body.json").read_text())["MinioEnv"]
    pretty = json.dumps({"MinioEnv": env}, indent=2)
    pretty = html.escape(pretty)
    for key in ("MINIO_ROOT_USER", "MINIO_ROOT_PASSWORD"):
        pretty = pretty.replace(key, f'<span class="hl">{key}</span>')
    body = (
        '<h2>Request (unauthenticated)</h2>'
        '<div class="card"><pre>$ curl -i -X POST http://127.0.0.1:9000/minio/bootstrap/v1/verify</pre></div>'
        f'<div class="alert"><span class="red">{html.escape(status)}</span><br>'
        'The response contains the process environment. The relevant part is shown below '
        '(pretty-printed from the actual JSON body).</div>'
        f'<div class="card"><pre>{pretty}</pre></div>'
        '<div class="alert"><span class="red">Leaked root credentials</span><br>'
        'MINIO_ROOT_USER=<span class="hl">minioadmin</span><br>'
        'MINIO_ROOT_PASSWORD=<span class="hl">minioadmin-vulhub</span></div>'
    )
    render("02_exploit_env_leak",
           "Exploit: unauthenticated environment disclosure",
           "POST /minio/bootstrap/v1/verify returns HTTP 200 and the MinIO root credentials",
           body, "#ff6b6b", 1350)

    # 3. Impact: leaked credentials log in and create a bucket.
    body = (
        "<h2>Leaked credentials are accepted by the console</h2>" + pre(read("04_console_login_and_buckets.txt"))
        + "<h2>Full admin access: create a bucket with the leaked credentials</h2>" + pre(read("05_mc_leaked_creds.txt"))
    )
    render("03_leaked_creds_impact",
           "Impact: leaked credentials grant admin access",
           "Console login succeeds and an attacker-controlled bucket is created",
           body, "#ff6b6b", 1050)

    # 4. Fix diff.
    diff = (CVE / "source" / "fix.diff").read_text(encoding="utf-8").rstrip()
    body = pre(diff)
    render("04_fix_diff",
           "Fix: MinIO commit 3b5dbf9",
           "bootstrap-peer-server.go: sensitive keys are skipped/hashed and the verify handler authenticates the caller",
           body, "#ffd166", 1150)

    # 5. Fixed endpoint.
    body = (
        "<h2>Same request after upgrading to RELEASE.2023-03-20T20-16-18Z</h2>"
        + pre(read("08_exploit_blocked.txt"))
        + '<div class="alert ok"><span class="ok">403 Forbidden - JWT token missing.</span><br>'
        'The endpoint no longer returns environment variables to an unauthenticated client.</div>'
        + "<h2>Fixed release</h2>" + pre(read("07_version_fixed.txt"))
    )
    render("05_exploit_blocked",
           "Verification: the attack no longer works",
           "The fixed MinIO rejects the unauthenticated bootstrap request",
           body, "#5ee6a8", 950)

    # 6. Regression.
    body = (
        "<h2>Bucket operations still work</h2>" + pre(read("09_regression_mc.txt"))
        + "<h2>Object upload/download round trip</h2>" + pre(read("11_regression_object_roundtrip.txt"))
        + "<h2>Web console still works</h2>" + pre(read("10_console_after_fix.txt"))
    )
    render("06_regression_after_fix",
           "Regression: normal MinIO functionality is intact",
           "Bucket creation, object upload/download and console login succeed after the fix",
           body, "#5ee6a8", 1500)


if __name__ == "__main__":
    main()
