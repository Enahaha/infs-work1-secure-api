# SAST 发现项审核记录

首次本地扫描报告保留在 security-reports/local/sast-initial.xml。工具为 SpotBugs 4.10.5.0 + FindSecBugs 1.14.0，SECURITY 类别、Low 阈值（包含所有置信级别）。发现 4 项，逐项审核如下。

| 规则 | 数量 | 审核结论 |
|---|---|---|
| SPRING_ENDPOINT | 3 | 提示发现了 Spring 接口入口，用于人工审计，不是具体漏洞结论。已审查登录与笔记接口：仅登录开放，其余接口校验 JWT，查询按用户过滤，使用参数绑定和 HTML 文本输出转义。仅对这两个已审核控制器排除此信息项。 |
| SPRING_CSRF_PROTECTION_DISABLED | 1 | 对普通使用 Cookie 登录的网站是有效警告。本 API 只接收显式 Authorization Bearer 令牌，不启用 Cookie 认证、HTTP Basic 或表单登录，并设置 STATELESS。因此传统跨站请求无法通过浏览器自动附带身份凭证取得认证。仅对 SecurityConfig 中对应配置位置记录例外。 |

这些是基于当前设计的审核例外，不是修改代码后消除了 4 个漏洞，也不代表整个程序绝对安全。具体例外在 config/spotbugs-reviewed.xml 中；其他安全规则保留，阈值仍为 Low。如果以后引入 Cookie、Session、HTTP Basic 或表单登录，必须重新评估 CSRF 配置并删除或更新例外。

回归测试 cookiesAndHttpBasicDoNotAuthenticateRequests 验证：Cookie 中的有效 JWT 不会认证请求；Basic 凭据不会认证请求；显式 Bearer 才能访问，且不设置会话 Cookie。跨站策略和 XSS 风险仍需按各自场景处理。

参考：https://docs.spring.io/spring-security/reference/servlet/exploits/csrf.html
