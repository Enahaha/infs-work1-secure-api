# Work 1 — Secure Notes API

Java 17 / Spring Boot 4.1.1 / Maven / Spring Security / Spring Data JPA / H2。

这是 Work 1 的 API 部分。GitHub CI 安全扫描已添加配置，仍需上传仓库并取得实际运行结果；真实 CVE 实验和最终报告尚未完成，不能将本文当作完整实验结果。

## 1. 启动

在 IntelliJ IDEA 中，将 Project SDK 和 Maven Runner JRE 都设为 JDK 17。
打开 `Work1Application.java`，在运行配置的 Environment variables 中设置：

```text
APP_DEMO_PASSWORD=Local-demo-2026!
```

这是本地实验密码示例，请勿使用个人账号的真实密码。首次运行会创建 alice、bob 两个实验用户，密码均取自该变量，数据库仅保存 BCrypt 哈希。生产系统应采用独立的账号开通流程。

也可以在终端运行：

```bash
cd /Users/zhouzihao/INFS/work_1
export JAVA_HOME="/Users/zhouzihao/Library/Java/JavaVirtualMachines/ms-17.0.15/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
export APP_DEMO_PASSWORD='Local-demo-2026!'
mvn spring-boot:run
```

服务监听 `http://127.0.0.1:8080`。没有首页，直接用 curl 或 Postman 测试接口。
IDEA 的 Working directory 应设置为项目目录；H2 文件保存在当前工作目录的 `data/` 下。
`data/` 已加入 Git 忽略规则。两个用户已存在后，重启时不必再提供初始化密码；更改环境变量不会重置现有密码。
JWT 使用每次启动随机生成的 RSA 密钥，因此重启后需要重新登录。此方案用于单实例本地教学，正式部署需安全持久化和管理密钥，并启用 HTTPS。

## 2. 按顺序测试接口

### 登录

```bash
curl -i -X POST http://127.0.0.1:8080/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"login":"alice","password":"Local-demo-2026!"}'
```

成功返回 200，以及 `token`、`tokenType`、`expiresIn`。令牌有效期为 1800 秒。
把返回的 token 复制到下面变量，不要包含外围双引号：

```bash
TOKEN='替换为登录返回的token'
```

### 创建笔记（自选接口）

```bash
curl -i -X POST http://127.0.0.1:8080/api/notes \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"content":"我的第一条安全笔记"}'
```

成功返回 201 和笔记记录。content 不得为空或仅包含空白，最长 2000 个字符。

### 查询自己的笔记

```bash
curl -i http://127.0.0.1:8080/api/data \
  -H "Authorization: Bearer $TOKEN"
```

成功返回 200 和 JSON 数组。只返回 JWT 对应用户的笔记。

### 验证未登录访问被拒绝

```bash
curl -i http://127.0.0.1:8080/api/data
```

应返回 401。错误密码、无效签名、过期令牌也会被拒绝。

## 3. 安全措施与实现位置

- **SQLi**：`UserAccountRepository`、`NoteRepository` 使用 Spring Data 的派生查询，框架绑定参数，不拼接 SQL。笔记内容即便含有 SQL 片段，也只作为数据保存。
- **XSS**：笔记以原文存储，通过 `NoteResponse.from` 在返回时进行 HTML 文本转义，避免反复转义。API 明确约定 content 是 HTML 转义后的文本，并以 JSON 返回。HTML 转义只对应 HTML 文本场景，不能当成 JavaScript、CSS 或 URL 等上下文的通用防护；客户端也不能先解码再作为不可信 HTML 插入。
- **密码**：BCrypt，cost=12。实验账号初始化密码要求 12–72 个可打印 ASCII 字符，以符合 BCrypt 的 72 字节上限。登录接口使用相同字符集约束。不存在的账号也执行一次哈希比对，错误账号与错误密码返回相同提示。
- **JWT**：RS256 签名，校验签名、有效期、issuer、audience 和用户标识。只接收 Authorization Bearer 令牌；不使用 Cookie 或服务端登录会话，因此关闭此 API 的 CSRF 防护。JWT 载荷不包含密码。
- **访问控制**：用户 ID 从通过验证的 JWT 获取，不接受客户端指定笔记所有者；查询也按用户 ID 过滤。
- **输入与错误**：Bean Validation 限制字段，非法 JSON 返回 400，不向响应暴露异常栈。不开放 H2 控制台。服务只绑定本机地址。

本教学版本未实现登录限速、刷新令牌、用户注销/禁用和持久化签名密钥，不应直接作为公网生产服务。

## 4. 读代码的顺序

1. `Work1Application`：程序入口。
2. `UserAccount` / `Note`：数据库中保存什么。
3. 两个 `Repository`：如何查询和保存。
4. `DemoDataInitializer`：首次运行如何创建实验用户。
5. `AuthController`：验证密码并签发 JWT。
6. `SecurityConfig`：进入接口之前如何校验 JWT。
7. `NoteController`：如何根据身份查询、创建笔记并安全输出。
8. `ApiExceptionHandler`：如何返回参数和登录错误。

## 5. 自动验证

```bash
mvn test
```

集成测试使用内存 H2，不修改本地文件数据库。覆盖真实登录和令牌签发、密码哈希、错误凭据、SQL 注入式用户名、未登录访问、过期/篡改/错误 issuer 和 audience 的令牌、笔记创建读取、用户数据隔离、HTML 转义、参数校验和非法 JSON。

## 6. Work 1 后续待完成

- 已配置 GitHub Actions；需上传 GitHub，在 push / pull request 时实际运行并保存测试、SAST 和 SCA 报告。
- 上传公开仓库并记录最后一次成功流水线链接。
- 选择 Vulhub CVE，在本地环境完成复现、根因分析、修复和回归测试。
- 保存真实命令、响应和截图，按手册要求制作 README 和报告，补充封面信息。

框架参考：[Spring Security JWT 官方文档](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html)。

## 7. GitHub Actions 与安全扫描

详细操作见 [CI 操作指南](docs/CI_GUIDE.md)。工作流位于 `.github/workflows/ci.yml`，仓库根目录必须是当前 work_1 目录（不能把它嵌套上传到另一个仓库的子目录后直接使用本工作流）。

| 检查 | 工具 | 失败条件 |
|---|---|---|
| 功能测试 | JUnit + Spring Boot / MockMvc | 测试失败或运行错误 |
| SAST | SpotBugs 4.10.5.0 + FindSecBugs 1.14.0 | SECURITY 类别的任意置信级别未排除发现项，或扫描运行错误 |
| SCA | OWASP Dependency-Check 13.0.0 | CVSS 大于等于 7 的发现项，或扫描运行错误 |

本地命令（使用 JDK 17）：

```bash
mvn -B -ntp test
mvn -B -ntp -Psast -DskipTests compile spotbugs:check
bash scripts/run-sca.sh
```

SCA 包括测试依赖。NVD 漏洞源启用；OSS Index 分析器因未配置独立账号而关闭。NVD API Key 是可选项，不是作业要求：未配置或为空时匿名下载 NVD 数据；非空时由脚本启用 nvd-key 配置，通过环境变量读取，不将密钥写入命令行。匿名首次更新可能较慢或受限流影响；数据更新或分析失败仍会使任务失败，不能当作扫描通过。

SAST 配置只聚焦 SECURITY 类别，具体审核例外及理由见 [审核记录](docs/SECURITY_REVIEW.md)，不等于完整的代码质量审计。扫描通过也不能证明不存在漏洞。GitHub 上的检查状态及附件应以实际运行结果为准。
