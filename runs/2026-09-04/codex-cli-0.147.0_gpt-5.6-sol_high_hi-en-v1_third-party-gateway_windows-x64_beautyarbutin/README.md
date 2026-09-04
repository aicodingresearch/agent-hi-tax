# T-50：Codex CLI × gpt-5.6-sol × high × IKUN Family

这是 T-50 的中转站侧预注册包，使用 Codex CLI 0.147.0，在 Windows 11 x64 上通过 IKUN Family 网关请求 `gpt-5.6-sol`，effort 固定为 `high`。

- 任务：T-50
- Issue：[aicodingresearch/agent-hi-tax#96](https://github.com/aicodingresearch/agent-hi-tax/issues/96)
- 路由：`third-party-gateway`（IKUN Family，`api.ikungod.online`）
- 标准输入：`hi-en-v1`，文件内容严格为两个 UTF-8 字节 `hi`
- 计划运行：R1、R2、R3，均为独立 fresh 会话，先完成本中转站侧，再建立官方 API 侧；两侧不交替

当前仅完成预注册，`valid_repetitions` 为 0，尚未发送正式 `hi`。网关兼容协议、实际观测模型、token usage 和额度字段须在 preflight/运行证据中如实记录；API key 只在本机私有环境变量中提供，绝不进入仓库。

