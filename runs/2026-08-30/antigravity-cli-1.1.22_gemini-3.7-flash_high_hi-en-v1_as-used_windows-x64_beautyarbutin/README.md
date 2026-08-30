# Antigravity CLI 1.1.22 / Gemini 3.7 Flash / high / Google AI Pro / Windows x64

这是 T-24 的一次 Google Antigravity CLI 交互式 TUI 实测。三次运行均从独立空目录启动 fresh session，固定使用默认选中的 `Gemini 3.7 Flash (High)`，每次只向模型发送一次精确的 `hi`。

## 场景

- Prompt：`hi-en-v1`，精确内容为 UTF-8 字节 `68 69`
- Agent：Google Antigravity CLI 1.1.22
- 模型：Gemini 3.7 Flash
- Effort：`high`
- 订阅：Google AI Pro
- 系统：Windows 11 10.0.26200，build 26200，x64
- 会话：每次均为 fresh session
- 工作区：每次均为独立空目录、非 Git 仓库
- Harness：`as-used`，另启用只读的本地 status-line 测量命令
- MCP：无
- Imported plugins：无
- Built-in skills：5 个，详见 [manifest.yaml](manifest.yaml)

## 三次结果

| Attempt | `current_usage.input_tokens` | Status-line total input | Cache create | Cache read | Output | Context total | Gemini weekly remaining | Gemini 5h remaining | Latency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| R1 | 13,763 | 19,570 | 0 | 0 | 68 | 19,638 | 0.95753986 | 0.998442 | not exposed |
| R2 | 13,764 | 19,570 | 0 | 0 | 139 | 19,709 | 0.9574535 | 0.9979236 | not exposed |
| R3 | 13,757 | 19,570 | 0 | 0 | 41 | 19,611 | 0.9573672 | 0.9974061 | not exposed |

聚合值：

- `current_usage.input_tokens` 中位数 13,763，范围 13,757–13,764
- Status-line total input 中位数 19,570，三次完全一致
- Output 中位数 68，范围 41–139
- Context total 中位数 19,638，范围 19,611–19,709
- Cache creation/read 三次均为 0/0
- 产品未在交互式 status-line 中暴露响应延迟

完整逐次字段见 [RESULTS.csv](RESULTS.csv)。

## 原生字段语义

本包原样保留 Antigravity status-line JSON 的两种输入字段：

- `context_window.current_usage.input_tokens`：当前 usage 对象中的输入 token
- `context_window.total_input_tokens`：status line 暴露的累计输入 token

两者不是本仓库替厂商重新定义的同一字段，也不强行套用 Codex 的“cached 是 input 子集”或 Anthropic 的“cache bucket 相加”口径。跨产品索引使用本场景明确声明的 `total_input_tokens`，而当前 usage 输入仍逐次保留。

本场景的 `context_total_tokens` 定义为：

```text
context_total_tokens
  = context_window.total_input_tokens + context_window.total_output_tokens
```

这些数字描述本次固定 harness 下产品暴露的 token footprint，不等于 API 价格或 Google AI Pro 订阅成本，也不能拆分归因到某一个 built-in skill 或系统提示。

## 额度说明

Status-line JSON 与 `/usage` 页面均记录了账号级 Gemini weekly 和 five-hour remaining。它们在三次顺序快照中下降，但属于共享账号额度，并且界面明确说明 five-hour meter 会平滑全局需求。因此本包保留原生小数和截图，同时将 `quota.attribution` 标记为 `contaminated`；不把相邻快照差值宣称为单次 `hi` 的确定成本。

## 回复差异

- R1：`Hello! How can I help you today?`
- R2：`Hello! How can I help you with your project today?`
- R3：`Hello! How can I help you today?`

## 证据

公开包包含：

- 两轮预注册与 preflight 修正记录
- [共享启动环境图](evidence/environment.png)
- [Status-line 测量说明](evidence/statusline-instrumentation.md)
- [私有原图哈希登记](evidence/private-evidence.md)与[像素脱敏审计](evidence/redaction-audit.txt)
- 三次完整输入/回复截图：[R1](attempts/r1/response.png)、[R2](attempts/r2/response.png)、[R3](attempts/r3/response.png)
- 三次脱敏后的原生 `/usage` 视觉证据；R1 由 [顶部](attempts/r1/usage-header.png) 与 [主体](attempts/r1/usage.png) 两张组成
- 三次白名单化的 pre-prompt / after-response status-line 机器快照：R1 [before](attempts/r1/pre-prompt.sanitized.jsonl) / [after](attempts/r1/events.sanitized.jsonl)、R2 [before](attempts/r2/pre-prompt.sanitized.jsonl) / [after](attempts/r2/events.sanitized.jsonl)、R3 [before](attempts/r3/pre-prompt.sanitized.jsonl) / [after](attempts/r3/events.sanitized.jsonl)
- 三次精确回复文本与逐次 `result.yaml`

## 已知边界与协议记录

- 原始 status-line JSON 含邮箱、路径和会话标识，只保存在 Git 仓库外；公开的 before/after 事件只保留白名单安全字段。每个 before 事件均为发送 `hi` 前、token 仍为 0 且产品/计划/额度元数据已完整出现的第一条快照。
- 产品在退出后删除临时 transcript 路径，本包不使用截图文件时间冒充提供者事件时间，因此 timing 为 `not_exposed`。
- 在任何正式 `hi` 之前，第一次 status-line preflight 因 Windows `-File` 引号解析失败；修正、重新冻结并提交 replacement preregistration 后才开始三次正式运行。
- 更早的一次 quota-only TUI attempt 与关闭的 headless Draft PR 均保留为审计记录，但不计入本包三次有效运行。
