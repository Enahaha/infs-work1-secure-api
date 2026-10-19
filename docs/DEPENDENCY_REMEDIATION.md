# Dependency-Check 扫描与依赖修复

2026-10-19 本地实测，使用 Dependency-Check 12.2.2，完整扫描含测试依赖。数据来自官方镜像，报告标注 NVD 数据最后修改时间为 2026-10-18T14:16:57Z。

## 下载问题

逐页匿名 API 更新的 GitHub 运行 39225032691 达到 60 分钟上限被取消，未产生完整扫描报告。改用 Dependency-Check 官方镜像后，本地首次完整下载、导入和分析约 50 秒，生成了 HTML/JSON 报告。这是一次实测耗时，不保证所有环境都有相同速度。

## 实际发现和处理

Spring Boot 4.1.1 默认解析到 Tomcat 11.0.24。报告对 tomcat-embed-core 列出 11 个漏洞发现，其中 9 项评分 >= 7，触发构建失败。这是依赖版本发现，不等于已经在本应用中实际利用了这些漏洞；具体影响取决于配置，个别数据源与厂商对影响范围或严重性的描述也可能不同。

在 pom.xml 设置 tomcat.version=11.0.27，统一升级 embed-core、embed-el 和 embed-websocket。保留风险阈值和错误检查，没有新增 CVE 忽略项。

本项目为 Java 应用，依赖包中的 native DLL 不是 .NET 应用程序集，因此关闭不适用的 Assembly Analyzer，避免要求安装 .NET SDK；Java JAR 和 NVD 漏洞分析仍启用。OSS Index 仍因没有独立凭据而关闭。

## 修复后验证

- 7 项集成测试全部通过。
- SAST 在既有已审核例外下通过，无新增例外。
- 本地 SCA 扫描通过，报告没有列出漏洞发现，耗时约 5 秒（已有漏洞库缓存）。
- 修复前后 HTML/JSON 和日志保存在 security-reports/local/sca-before-tomcat-upgrade/ 与 sca-after-tomcat-upgrade/。
- GitHub Actions 的通过状态应以最新运行实际结果为准，本地成功不能替代云端流水线证据。

## 官方依据

- 镜像及更新局限：https://dependency-check.github.io/DependencyCheck/data/mirrornvd.html
- Tomcat 安全公告：https://tomcat.apache.org/security-11.html
- Tomcat 11.0.27 更新记录：https://tomcat.apache.org/tomcat-11.0-doc/changelog.html

上述依赖升级及报告不能替代作业后半部分的 Vulhub CVE 复现、根因分析和修复实验。
