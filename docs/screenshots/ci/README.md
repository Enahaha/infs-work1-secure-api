# Work 1 — CI security screenshots

## Figure 1: GitHub Actions — all checks passed

File: `01_github_actions_all_checks_passed_39237435374.png`

Run: <https://github.com/Enahaha/infs-work1-secure-api/actions/runs/39237435374>

Commit: `50b16bb`. The screenshot shows the overall status **Success**, total
duration 1m 54s and 2 report artifacts. **Tests and SAST** passed in 38s;
**Dependency vulnerability scan (SCA)** passed in 1m 50s. The jobs run in
parallel, so the durations are not added together.

Caption: GitHub Actions automatically runs the functional tests, the static
application security scan and the dependency vulnerability check; both jobs
complete successfully and upload the reports.

The two yellow warnings in the screenshot are GitHub Actions tooling
deprecation notices for actions that target Node.js 20 (`upload-artifact@v4`,
`cache@v4`). GitHub is forcing those actions to run on Node.js 24. All steps
still passed. These notices are not vulnerability findings in the Java
dependencies.

There is also a notice about the `ubuntu-latest` runner migrating to Ubuntu 26;
this is a runner-environment notice, not a security warning.

![GitHub Actions — all checks passed](01_github_actions_all_checks_passed_39237435374.png)

## Figure 2: SAST report — 0 findings, 0 analysis errors

File: `02_sast_report.png`

Source: the `tests-and-sast-reports` artifact from run `39237435374`, file
`reports/sast-report.html`. The report is a rendering of the actual
`spotbugsXml.xml`: SpotBugs 4.10.5.0 with FindSecBugs 1.14.0, `SECURITY`
category at all confidence levels. After the reviewed exceptions documented in
[`SECURITY_REVIEW.md`](../../SECURITY_REVIEW.md), the report shows
**0 reported findings and 0 analysis errors**.

Caption: the SAST job completed with no unexcluded security-category findings.

![SAST report — 0 findings](02_sast_report.png)

## Figure 3: SCA report — 0 vulnerable dependencies

File: `03_sca_report_summary.png`

Source: the `sca-reports` artifact from run `39237435374`, file
`dependency-check-report.html`. OWASP Dependency-Check 12.2.2 scanned 134
dependencies (70 unique). The summary shows **0 vulnerable dependencies,
0 vulnerabilities found and 0 suppressed vulnerabilities**. The NVD data
timestamp in the JSON report is `2026-10-18T14:16:57Z`.

Caption: the SCA job completed and the report contains no known vulnerable
dependency findings.

![SCA report — 0 vulnerabilities](03_sca_report_summary.png)

The screenshots preserve the displayed report content; no values were edited.
The raw reports and logs are in
[`docs/security-reports/github/39237435374/`](../../security-reports/github/39237435374/).
