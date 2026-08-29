<!-- 仓库公开开源时，删除本页及 README 中的链接行。 -->

# 私有试点须知

[English](internal-pilot.md) | **中文**

本页只适用于仓库仍为私有状态时的受邀贡献者。

## 接受邀请前

- 先在 GitHub 账号开启双因素认证（2FA）。组织强制要求 2FA，未开启的账号无法加入。
- 在 GitHub 邮箱设置中开启 **Keep my email addresses private**。commit 使用 GitHub noreply 地址，避免仓库未来公开后真实邮箱随 Git 历史泄露：

  ```sh
  git config user.email "<id>+<login>@users.noreply.github.com"
  ```

## 贡献路径

受邀者以 **Read** 权限协作：fork 仓库，clone 自己的私有 fork，创建分支，再提交 Pull Request。fork 会保持私有；如果你失去对上游私有仓库的访问权，GitHub 会自动删除该 fork。

首次贡献建议预留约 **1 小时**，足以完成一个场景。熟悉流程后，一次贡献通常约 **30 分钟**即可完成。

Windows 用户需在 Git Bash 或 WSL 等 POSIX 环境中运行校验脚本。环境预检请在 PowerShell 使用以下等价命令（将 `<agent>` 替换为实际命令）：

```powershell
Get-Command <agent> | Select-Object -ExpandProperty Source
<agent> --version
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber, OSArchitecture
(Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
```

## 私密联系

私有试点期间如有隐私问题或疑似泄露，请直接通过收到邀请的渠道联系维护者。GitHub 私密漏洞报告不适用于私有仓库；仓库公开后再启用。
