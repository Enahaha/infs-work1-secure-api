# Work 1：上传 GitHub 与运行 CI

## 配置已包含什么

`.github/workflows/ci.yml` 在 push、pull request 和手动运行时触发。两个任务各自运行：Tests and SAST，以及 Dependency vulnerability scan (SCA)。即使扫描失败也会尝试保留已有报告，不会忽略失败来制造绿色结果。

SAST 原始报告在 `target/spotbugsXml.xml`，可读报告在 `target/reports/sast-report.html`；SCA 报告在 `target/dependency-check-report.html` 和 `.json`。工作流将结果上传至 Artifacts，保留 30 天，应及时下载归档。

## 1. 创建空仓库

登录 GitHub，创建新仓库，例如 `infs-work1-secure-api`。作业要求公开仓库，选择 Public。不要勾选自动生成 README、.gitignore 或 License，因为本地已有项目。

## 2. NVD API Key 可选，可跳过申请

作业要求运行依赖漏洞检查并生成报告，没有要求申请 API Key。当前脚本 `scripts/run-sca.sh` 支持：

- 不提供 NVD_API_KEY 或值为空：匿名下载 NVD 数据，不因缺少 Key 提前失败。
- 提供非空 NVD_API_KEY：启用 Maven 的 nvd-key profile，从环境变量读取密钥。

无需为了开始扫描而申请 Key。匿名更新首次可能较慢，也可能受 NVD 限流影响；若实际更新失败，任务如实失败。不会关闭漏洞源或忽略错误来制造成功。

若已持有 Key，可以在 GitHub 仓库 Settings → Secrets and variables → Actions → New repository secret 添加 NVD_API_KEY。Fork PR 无法读取仓库 Secret，自动走匿名路径，不使用 pull_request_target 来取得密钥。

本地运行：`bash scripts/run-sca.sh`。真实 Key 不写进代码或命令参数。

## 3. 在 IDEA 上传

项目已初始化 Git 仓库，但还没有远程地址。可以在 IDEA 的 Git → GitHub → Share Project on GitHub 中创建并分享仓库（若使用这种方式，无需先在网页建同名仓库）；或连接前一步建好的空仓库后提交推送。

提交前查看文件列表：应包括 src、pom.xml、config、.github/workflows 和文档；不应包括 data、target、.idea 或 .env。报告截图中的本地实验密码/JWT 原图可本地留存，发布时使用经过遮挡的副本；不要把个人真实凭据放入仓库。

也可以在终端操作，先进入项目目录：

```bash
cd /Users/zhouzihao/INFS/work_1
git status
```

先检查要上传的图片及文件，再执行：

```bash
git add .
git commit -m "Implement secure notes API and security CI"
git branch -M main
```

然后从自己创建的仓库页面复制 HTTPS 地址，替换以下占位地址：

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

HTTPS 推送可使用 IDEA 的 GitHub 登录流程或 GitHub CLI 登录，GitHub 网页登录密码不能直接作为 Git 推送密码。若已有 origin，应先检查 git remote -v，避免重复添加。

## 4. 查看检查和报告

上传后打开 GitHub 仓库的 Actions → Work 1 - Tests and Security → 最新运行。

- Tests and SAST：确认测试数量、失败数，以及 FindSecBugs/SpotBugs 扫描结果。
- Dependency vulnerability scan (SCA)：等待漏洞库更新和扫描。
- 在该运行页面底部的 Artifacts 下载 tests-and-sast-reports 和 sca-reports。
- 解压 SAST 附件，打开 reports/sast-report.html（具体目录以附件内结构为准）。
- 解压 SCA 附件，用浏览器打开 dependency-check-report.html。

如果失败，打开红色步骤查看具体错误。下载/API 限流错误说明扫描未完成；漏洞发现说明需要分析依赖、升级或有依据地处理误报。不要把这两种失败当作扫描通过，也不要仅为通过而调高阈值或关闭检查。

## 5. 报告证据

保存：工作流总览截图、SAST 扫描结果截图、SCA 报告摘要截图，以及最后一次成功运行的页面链接。下载的附件建议保存在 docs/security-reports/ 下，以实际扫描时间区分。

只有实际完成全部任务、检查状态成功之后，才记录为最后一次成功流水线。当前配置文件本身不能当作扫描成功证明。

## 官方参考

- https://spotbugs.github.io/spotbugs-maven-plugin/usage.html
- https://dependency-check.github.io/DependencyCheck/dependency-check-maven/check-mojo.html
- https://github.com/actions/setup-java
- https://github.com/actions/upload-artifact

## 本地验证状态

2026-10-19：7 项功能测试通过；SAST 在应用逐项审核例外后通过，报告保存在 security-reports/local/。旧配置曾因缺少 NVD_API_KEY 而失败，不能视为依赖无漏洞。现已取消强制 Key 条件；新的匿名扫描结果应以实际运行记录为准。

本地扫描如需使用密钥，请通过本机环境变量 NVD_API_KEY 提供，不将真实值写进仓库。然后执行 `bash scripts/run-sca.sh`。

## 匿名更新兼容性修复

2026-10-19，运行 f46d745 时，13.0.0 即使未设置 Key 仍报 `Invalid API Key, length of 0`。官方 issue #8715 记录了该版本内部默认空 Key 的缺陷；仅取消外部必填检查不能解决。因此插件固定为 12.2.2（两个 profile 同步），并使用独立的 12.2.2 缓存目录。阈值仍为 CVSS >= 7，failOnError 仍启用，NVD 分析保留。

官方记录：https://github.com/dependency-check/DependencyCheck/issues/8715
