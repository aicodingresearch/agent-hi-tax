# T-50：Codex CLI × gpt-5.6-sol × high × ChatGPT Plus

这是 T-50 的官方订阅侧预注册包。网关侧 R1–R3 已先完成；本侧使用同一 Codex CLI、模型、effort、Windows 环境和 prompt，但切换到官方 ChatGPT Plus 路由，两个路由块不交替。

- 任务：T-50
- Issue：[aicodingresearch/agent-hi-tax#96](https://github.com/aicodingresearch/agent-hi-tax/issues/96)
- 路由：first-party-subscription（OpenAI / ChatGPT Plus）
- Agent：Codex CLI 0.147.0
- 模型：gpt-5.6-sol
- effort：high
- 标准输入：hi-en-v1，严格为两个 UTF-8 字节 hi
- 计划运行：R1、R2、R3，均为独立 fresh session 和空目录

正式运行尚未开始。preflight 只用于确认官方路由、版本、模型、effort、权限和 token 初始值；正式三次运行前不发送 hi。

