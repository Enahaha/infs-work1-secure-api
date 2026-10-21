# Local scan results (2026-10-19, Asia/Shanghai)

- `sast-initial.xml`: first actual scan; 4 findings (3 endpoint-inventory hints,
  1 CSRF-configuration warning).
- `sast-reviewed.xml`: re-scan after the documented exceptions; 0 unexcluded
  security findings, 0 analysis errors.
- `sast-report.html`: readable report generated from the reviewed XML; the
  original XML is kept.
- Functional tests: 7/7 passed. Review notes: `../../SECURITY_REVIEW.md`.

This is local evidence. After upgrading Tomcat to 11.0.27 on 2026-10-19, the
local SCA re-test passed (0 vulnerable dependencies, 70 unique components); the
successful cloud run is
<https://github.com/Enahaha/infs-work1-secure-api/actions/runs/39237435374>.
