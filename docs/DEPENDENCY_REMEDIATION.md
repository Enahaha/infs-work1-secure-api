# Dependency-Check scan and dependency remediation

Local measurement on 2026-10-19 with Dependency-Check 12.2.2, full scan including
test dependencies. The data came from the official mirror; the report records the
NVD data last-modified time as `2026-10-18T14:16:57Z`.

## Download issue

The page-by-page anonymous API update in GitHub run `39225032691` reached the
60-minute limit and was cancelled, so no complete scan report was produced.
After switching to the official Dependency-Check mirror, the first full local
download, import and analysis took about 50 seconds and generated HTML/JSON
reports. This is one measured run; the same speed is not guaranteed in every
environment.

## Actual finding and handling

Spring Boot 4.1.1 resolved Tomcat 11.0.24 by default. The report listed 11
vulnerability findings for `tomcat-embed-core`, 9 of them with a score >= 7,
which failed the build. This is a dependency-version finding; it does not mean
the vulnerabilities were actually exploited in this application. The concrete
impact depends on configuration, and individual data sources or vendors may
describe the affected scope or severity differently.

`pom.xml` now sets `tomcat.version=11.0.27`, upgrading `embed-core`, `embed-el`
and `embed-websocket` together. The risk threshold and error checks were kept;
no new CVE suppressions were added.

This is a Java application. Native DLLs inside dependency packages are not .NET
assemblies, so the inapplicable Assembly Analyzer was disabled to avoid requiring
the .NET SDK; Java JAR and NVD vulnerability analysis remain enabled. OSS Index
remains disabled because there are no separate credentials.

## Post-fix verification

- 7 integration tests passed.
- SAST passed with the existing reviewed exceptions; no new exceptions were
  added.
- The local SCA scan passed; the report lists no vulnerability findings and took
  about 5 seconds with the vulnerability-database cache.
- Before/after HTML/JSON reports and logs are saved in
  `security-reports/local/sca-before-tomcat-upgrade/` and
  `security-reports/local/sca-after-tomcat-upgrade/`.
- The GitHub Actions status should be taken from the latest actual run; a local
  success is not a substitute for cloud pipeline evidence.

## Official references

- Mirror and update limitations:
  <https://dependency-check.github.io/DependencyCheck/data/mirrornvd.html>
- Tomcat security page: <https://tomcat.apache.org/security-11.html>
- Tomcat 11.0.27 changelog:
  <https://tomcat.apache.org/tomcat-11.0-doc/changelog.html>

The dependency upgrade and these reports do not replace the Vulhub CVE
reproduction, root-cause analysis and fix experiment required by the second part
of the assignment.
