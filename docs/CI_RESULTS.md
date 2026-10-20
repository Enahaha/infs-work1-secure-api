# GitHub Actions successful run record

- Run: <https://github.com/Enahaha/infs-work1-secure-api/actions/runs/39237435374>
- Commit: `50b16bb38687f3953adea999539f4027f25c1d01`
- Status: **success**, both jobs passed.
- Time: 2026-10-19 18:26:10–18:28:00 (Asia/Shanghai).
- Tests and SAST: 38 s; 7 tests passed; SAST passed with the documented reviewed
  exceptions.
- SCA: 1 min 50 s; 70 unique components; the report lists no vulnerable
  dependencies and no analysis errors.
- NVD data: the Dependency-Check official mirror; the exact timestamp is in the
  JSON report `scanInfo`.

The GitHub artifacts, test results and logs were downloaded to
[`security-reports/github/39237435374/`](security-reports/github/39237435374/).

Remediation history: the anonymous NVD API update timed out; the official NVD
file mirror completed the download; the scan found vulnerabilities in Tomcat
11.0.24; `pom.xml` was upgraded to Tomcat 11.0.27; tests, SAST and SCA were
re-run successfully. See
[`DEPENDENCY_REMEDIATION.md`](DEPENDENCY_REMEDIATION.md).

Evidence screenshots: the Actions overview, the SAST report and the SCA report
summary are in [`screenshots/ci/`](screenshots/ci/). This record covers the
API/CI part. The Vulhub CVE reproduction, root cause, fix and regression tests
are documented in
[`cve/CVE-2023-28432/README.md`](cve/CVE-2023-28432/README.md).
