# Work 1：API 功能与访问控制截图

> **English summary.** These screenshots were captured from actual `curl`
> requests against the local API. The main English README links the images
> directly; the detailed Chinese captions below are retained as a reference.
>
> | File | Request | Observed result |
> |---|---|---|
> | `01_login_success_200.png` | `POST /auth/login` with valid credentials | 200 + JWT |
> | `02_create_note_authenticated_201.png` | `POST /api/notes` with Bearer JWT | 201 + created note |
> | `03_get_notes_authenticated_200.png` | `GET /api/data` with Bearer JWT | 200 + own notes |
> | `04_get_notes_without_token_401.png` | `GET /api/data` without a token | 401 |
> | `05_login_wrong_password_401.png` | `POST /auth/login` with a wrong password | 401 |
> | `06_login_sqli_attempt_401.png` | `POST /auth/login` with an SQLi-style username | 401 |
> | `07_create_note_xss_escaped_201.png` | `POST /api/notes` with `<script>alert(1)</script>` | 201, response contains `&lt;script&gt;` |
> | `08_get_notes_bob_empty_200.png` | `GET /api/data` with Bob's token | 200 + `[]` |
> | `09_tampered_jwt_signature_rejected_401.png` | `GET /api/data` with a modified JWT signature | 401 `Invalid signature` |

以下截图由学生实际执行请求后提供，按登录、创建、查询、拒绝未认证访问的顺序归档。图片保持原样，仅复制和重命名，未裁剪或修改执行结果。

| 文件名 | 请求接口 | HTTP 状态码 | 说明 |
|---|---|---|---|
| 01_login_success_200.png | POST /auth/login | 200 | 登录成功并签发 JWT |
| 02_create_note_authenticated_201.png | POST /api/notes | 201 | 携带 JWT 创建笔记成功 |
| 03_get_notes_authenticated_200.png | GET /api/data | 200 | 携带 JWT 查询笔记成功 |
| 04_get_notes_without_token_401.png | GET /api/data | 401 | 未携带 JWT 访问被拒绝 |

## 报告图注

### 图 1：登录成功并签发 JWT

用户 alice 使用正确账号密码登录，服务器返回 JWT，令牌类型为 Bearer，有效期为 1800 秒。

截图响应头时间换算为北京时间：2026-10-19 11:52:56（UTC+8）。

![图 1：登录成功并签发 JWT](01_login_success_200.png)

### 图 2：携带 JWT 创建笔记成功

客户端携带 JWT 创建笔记，服务器返回新建笔记的 ID、内容和创建时间。

截图响应头时间换算为北京时间：2026-10-19 12:00:09（UTC+8）。

![图 2：携带 JWT 创建笔记成功](02_create_note_authenticated_201.png)

### 图 3：携带 JWT 查询笔记成功

客户端携带 JWT 访问数据接口，成功获取此前创建的笔记。

截图响应头时间换算为北京时间：2026-10-19 12:01:12（UTC+8）。

![图 3：携带 JWT 查询笔记成功](03_get_notes_authenticated_200.png)

### 图 4：未携带 JWT 访问被拒绝

客户端未提供 Authorization 令牌时，服务器返回 401，拒绝访问受保护的数据接口。

截图响应头时间换算为北京时间：2026-10-19 12:01:52（UTC+8）。

![图 4：未携带 JWT 访问被拒绝](04_get_notes_without_token_401.png)

## 证据范围

这组截图证明本次测试中登录、已认证创建和查询、未认证访问拒绝、错误密码拒绝和一次 SQL 注入式输入未绕过登录的实际结果。其中图 7 展示创建笔记响应中的 HTML 文本转义。图 3 与图 8 可结合测试步骤展示用户数据隔离，图 9 展示篡改 JWT 签名被拒绝。整组截图仍不能单独证明全面的 SQL 注入防护、所有输出上下文的 XSS 防护或过期令牌的拒绝效果；还需结合代码分析及对应测试。

第一张原图包含本地实验账号密码和当次 JWT，按用户要求保留原图。制作公开报告时可另做遮挡副本，保留本目录原始证据。

### 图 5：错误密码登录被拒绝

alice 使用错误密码登录，服务器返回 HTTP 401 和统一错误提示 Invalid username or password，未签发 JWT。

截图响应头时间换算为北京时间：2026-10-19 12:07:55（UTC+8）。

![错误密码登录被拒绝](05_login_wrong_password_401.png)

### 图 6：SQL 注入式用户名未能绕过登录

使用包含 SQL 片段的用户名（' OR '1'='1' --）提交登录请求，服务器返回 HTTP 401，未签发 JWT。这证明本次输入未绕过登录；SQL 注入防护原理还需结合 Repository 参数绑定实现解释。

截图响应头时间换算为北京时间：2026-10-19 12:11:06（UTC+8）。

![SQL 注入式用户名未能绕过登录](06_login_sqli_attempt_401.png)

### 图 7：包含脚本标记的笔记在响应中被转义

提交内容 `<script>alert(1)</script>` 后，服务器返回 HTTP 201，响应中的 content 为 `&lt;script&gt;alert(1)&lt;/script&gt;`，说明本次创建笔记响应按 HTML 文本场景进行了输出转义。本图不涉及浏览器执行，不能据此单独断言所有前端上下文均不存在 XSS。

截图响应头时间换算为北京时间：2026-10-19 12:13:15（UTC+8）。

![图 7：包含脚本标记的笔记在响应中被转义](07_create_note_xss_escaped_201.png)

### 图 8：Bob 查询返回空数组

使用按前述步骤获取的 Bob 令牌（变量 BOB_TOKEN）访问 GET /api/data，服务器返回 HTTP 200 和空数组 []。结合图 3 中 Alice 查询得到其创建的笔记，可作为本次用户数据隔离测试的配对证据。本图自身仅显示变量名称，不展示令牌对应的用户身份；报告应同时说明 Bob 登录及变量赋值过程。

截图响应头时间换算为北京时间：2026-10-19 15:19:15（UTC+8）。

![图 8：Bob 查询返回空数组](08_get_notes_bob_empty_200.png)

### 图 9：篡改 JWT 签名后访问被拒绝

从 Bob 的 JWT 中取出签名，修改其第一个字符，保持头部和载荷不变，再使用 BAD_TOKEN 请求 GET /api/data。服务器返回 HTTP 401，WWW-Authenticate 响应头包含 invalid_token 和 Signed JWT rejected: Invalid signature，表明本次请求因 JWT 签名无效被拒绝。结合图 8 的原令牌访问成功结果，展示 JWT 签名校验的效果。

截图响应头时间换算为北京时间：2026-10-19 15:29:10（UTC+8）。

![图 9：篡改 JWT 签名后访问被拒绝](09_tampered_jwt_signature_rejected_401.png)
