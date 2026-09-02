# Antigravity CLI 1.1.23 / Gemini 3.7 Flash / high / Google AI Pro / Windows x64

这是 T-35“同一厂商、不同产品形态”的 CLI 侧数据包。正式采集按固定顺序与 Desktop 侧交替进行：CLI R1、Desktop R1、CLI R2、Desktop R2、CLI R3、Desktop R3。每次 CLI 运行都从独立空目录启动 fresh session，并且只发送一次精确的 `hi`。

## 场景

- Prompt：`hi-en-v1`，UTF-8 字节 `68 69`
- Agent：Google Antigravity CLI 1.1.23
- 模型与 effort：Gemini 3.7 Flash (High)
- 订阅：Google AI Pro
- 系统：Windows 11 10.0.26200，build 26200，x64
- 工作区：三个独立空目录，均非 Git 仓库
- Harness：`custom`；在产品默认配置上增加只读的本地 status-line 采集命令
- MCP / imported plugins / user hooks：无
- Built-in skills：5 个，详见 [manifest.yaml](manifest.yaml)

## 三次结果

| Attempt | `current_usage.input_tokens` | Status-line total input | Cache create | Cache read | Output | Context total | Gemini weekly remaining | Gemini 5h remaining | Latency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| R1 | 13,822 | 19,648 | 0 | 0 | 64 | 19,712 | 0.8799599 | 0.9259836 | not exposed |
| R2 | 13,818 | 19,648 | 0 | 0 | 166 | 19,814 | 0.8684655 | 0.857017 | not exposed |
| R3 | 13,820 | 19,648 | 0 | 0 | 172 | 19,820 | 0.8651249 | 0.8369735 | not exposed |

聚合值：

- `current_usage.input_tokens` 中位数 13,820，范围 13,818–13,822
- Status-line total input 中位数 19,648，三次完全一致
- Output 中位数 166，范围 64–172
- Context total 中位数 19,814，范围 19,712–19,820
- Cache creation/read 三次均为 0/0
- 交互式 status-line 未暴露响应延迟

完整逐次字段见 [RESULTS.csv](RESULTS.csv)。

## 原生字段语义

本包分别保留 Antigravity status-line JSON 的两个输入字段：

- `context_window.current_usage.input_tokens`：当前 usage 对象中的输入 token
- `context_window.total_input_tokens`：status line 暴露的累计输入 token

两者不是本仓库重新定义的同一字段。本场景的 `context_total_tokens` 定义为：

```text
context_total_tokens
  = context_window.total_input_tokens + context_window.total_output_tokens
```

这些数字描述固定 harness 下产品暴露的 token footprint，不等同于 API 价格或 Google AI Pro 订阅成本，也不能拆分归因到某个 built-in skill 或系统提示。

## T-35 对照边界

配对的 Desktop 2.11.0 场景保持同一账号、模型、effort、操作系统、prompt、空工作区和默认 review posture。Desktop 官方界面未提供可接受的逐会话 token 读数，因此本对照只能确认 CLI 侧的精确 token footprint；不会用本地 SQLite/Protobuf 逆向结果替代正式产品证据，也不会宣称精确的跨形态 token 差值。

账户额度在 CLI 与 Desktop 交替采集期间共享，而且五小时额度会受全局需求平滑影响，因此所有额度快照均标为 `contaminated`，不把相邻快照差值归因于单次 `hi`。

## 证据

公开包包含：

- 原预注册、自动升级后的 replacement preregistration
- [Status-line 测量说明](evidence/statusline-instrumentation.md)
- [私有原图与原始事件哈希登记](evidence/private-evidence.md)
- [公开文件脱敏审计](evidence/redaction-audit.txt)
- 三次白名单化的 pre-prompt / after-response status-line 快照
- 三次精确回复文本和逐次 `result.yaml`
- R3 的公开回复截图；R1/R2 回复图和三次 usage 图因含账号或路径而保留为私有证据

## 协议记录

原预注册写的是 CLI 1.1.22。第一次 launch-only preflight 在未发送 prompt 前发现产品已自动更新到 1.1.23；该启动没有进入正式 attempt。随后在 issue #42 留下 replacement preregistration 并冻结 1.1.23 场景，之后才进行三次正式采集。
