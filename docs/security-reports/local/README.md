# 本地扫描结果（2026-10-19，Asia/Shanghai）

- `sast-initial.xml`：首次实际扫描，4 项发现（3 项接口入口提示，1 项 CSRF 配置警告）。
- `sast-reviewed.xml`：应用具体审核例外后再次实际扫描，0 项未排除的安全发现，0 项分析错误。
- `sast-report.html`：从 reviewed XML 生成的可读报告，原始 XML 保留。
- 功能测试：7 项全部通过。审核说明见 ../../SECURITY_REVIEW.md。

这是本地运行证据。2026-10-19 升级 Tomcat 11.0.27 后，本地 SCA 复测通过（0 个有漏洞依赖，70 个唯一组件）；云端成功运行为 <https://github.com/Enahaha/infs-work1-secure-api/actions/runs/39237435374>。
