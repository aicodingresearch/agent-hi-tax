# T-50 中转站侧预注册

- Issue：[#96](https://github.com/aicodingresearch/agent-hi-tax/issues/96)
- 场景：同一 Codex CLI harness 下，先测 IKUN Family 网关，再测官方 API；两侧不交替。
- Agent：OpenAI Codex CLI 0.147.0
- OS：Windows 11 x64，build 26200，locale `zh-CN`，timezone `Asia/Shanghai`
- 模型标签：`gpt-5.6-sol`
- effort：`high`
- 输入：`prompt.txt`，严格为 UTF-8 `hi`，2 bytes，无换行
- 路由：third-party gateway，IKUN Family，公开域名 `api.ikungod.online`
- 工作区：独立空目录；R1/R2/R3 均为 fresh 会话
- 凭据：只在本机私有环境变量中提供；仓库不保存 key、token、cookie、Authorization header 或完整本机路径

本文件创建时尚未发送正式 `hi`。协议兼容性、实际 token usage、延迟、额度和模型观测值全部留到 preflight/attempt 证据中；无法公开验证的字段按仓库规定记录为 `not_exposed` 或 `not_provided`。

