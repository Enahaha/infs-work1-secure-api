# 本地扫描结果（2026-10-19，Asia/Shanghai）

- `sast-initial.xml`：首次实际扫描，4 项发现（3 项接口入口提示，1 项 CSRF 配置警告）。
- `sast-reviewed.xml`：应用具体审核例外后再次实际扫描，0 项未排除的安全发现，0 项分析错误。
- `sast-report.html`：从 reviewed XML 生成的可读报告，原始 XML 保留。
- 功能测试：7 项全部通过。审核说明见 ../../SECURITY_REVIEW.md。

这是本地运行证据，不是 GitHub Actions 成功证明。依赖漏洞扫描尚未取得完成结果，不能宣称 SCA 通过。
