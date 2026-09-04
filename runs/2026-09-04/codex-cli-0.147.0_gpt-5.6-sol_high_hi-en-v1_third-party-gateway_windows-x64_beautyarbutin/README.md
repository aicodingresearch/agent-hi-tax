# T-50：Codex CLI × gpt-5.6-sol × high × IKUN Family

这是 T-50 的中转站侧预注册包，使用 Codex CLI 0.147.0，在 Windows 11 x64 上通过 IKUN Family 网关请求 `gpt-5.6-sol`，effort 固定为 `high`。

- 任务：T-50
- Issue：[aicodingresearch/agent-hi-tax#96](https://github.com/aicodingresearch/agent-hi-tax/issues/96)
- 路由：`third-party-gateway`（IKUN Family，`api.ikungod.online`）
- 标准输入：`hi-en-v1`，文件内容严格为两个 UTF-8 字节 `hi`
- 计划运行：R1、R2、R3，均为独立 fresh 会话，先完成本中转站侧，再建立官方 API 侧；两侧不交替

当前正式 R1-R3 尚未开始，valid_repetitions 仍为 0。此前误在 preflight 目录发送过一次 hi，该 probe 已标为 invalid，仅作诊断证据，不计入聚合结果。网关兼容协议、正式运行 token usage 和额度字段须在 R1-R3 证据中如实记录；API key 只在本机私有环境变量中提供，绝不进入仓库。
