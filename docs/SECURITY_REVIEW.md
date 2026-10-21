# SAST finding review

The first local scan report is kept at
[`security-reports/local/sast-initial.xml`](security-reports/local/sast-initial.xml).
The tool is SpotBugs 4.10.5.0 with FindSecBugs 1.14.0, `SECURITY` category,
Low threshold (all confidence levels). Four findings were reviewed:

| Rule | Count | Review conclusion |
|---|---|---|
| `SPRING_ENDPOINT` | 3 | Endpoint-inventory hint for manual audit, not a concrete vulnerability finding. The login and notes endpoints were reviewed: only login is public; the other endpoints validate JWT; queries are filtered by user; parameter binding and HTML text output escaping are used. The hint is excluded only for the two reviewed controllers. |
| `SPRING_CSRF_PROTECTION_DISABLED` | 1 | A valid warning for sites that use cookie-based login. This API accepts only an explicit `Authorization: Bearer` token; cookie authentication, HTTP Basic and form login are not enabled, and the API is STATELESS. Traditional cross-site requests cannot make the browser attach the credentials automatically. The exception is recorded only for the corresponding configuration location in `SecurityConfig`. |

These are reviewed exceptions based on the current design. They are not four
vulnerabilities removed by code changes, and they do not prove that the whole
program is absolutely secure. The exceptions are in
[`config/spotbugs-reviewed.xml`](../config/spotbugs-reviewed.xml); all other security
rules remain enabled at the Low threshold. If cookies, sessions, HTTP Basic or
form login are introduced later, the CSRF configuration must be re-evaluated and
the exception removed or updated.

The regression test `cookiesAndHttpBasicDoNotAuthenticateRequests` verifies that a
valid JWT in a cookie does not authenticate a request, Basic credentials do not
authenticate a request, and only an explicit Bearer token is accepted (with no
session cookie set). Cross-site policy and XSS risks still need to be handled in
their own contexts.

Reference: <https://docs.spring.io/spring-security/reference/servlet/exploits/csrf.html>
