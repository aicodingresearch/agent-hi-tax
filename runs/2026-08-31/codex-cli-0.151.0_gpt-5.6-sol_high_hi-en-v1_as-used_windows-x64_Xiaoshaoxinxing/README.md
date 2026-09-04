# OpenAI Codex CLI 0.151.0 / GPT-5.6 Sol / high / ChatGPT Plus / Windows x64

这是 T-01 的一次 Windows、ChatGPT Plus、`as-used` harness 复测。三次运行均为独立空目录和 fresh session，按顺序执行，且只向模型发送一次精确的 `hi`。

## 场景

- Prompt：`hi-en-v1`，精确内容为两个 UTF-8 字节 `68 69`
- Agent：官方 OpenAI Codex CLI 0.151.0
- 模型：`gpt-5.6-sol`
- Reasoning effort：`high`
- Service tier：`fast`（三次 footer 均一致；未在启动命令中显式固定）
- 认证：ChatGPT 订阅登录
- 订阅：ChatGPT Plus
- 系统：Windows 11 10.0.26200，build 26200，x64
- 会话：每次均为 fresh session
- 工作区：每次均为独立空目录、非 Git 仓库
- 权限：`Workspace (Ask for approval)`
- Collaboration mode：`Default`
- Profile：`as-used`
- Plugins：未暴露
- Skills：未暴露
- MCP：无启用 MCP；`codex mcp list` 中 `cua_repl` 为 disabled
- Hooks：无显式 hooks；未观察到 hook 模型调用
- Quota：未测量，不进入结果指标

## 三次结果

| Attempt | Input（含 cached） | Cached input | 非 cached input | Output | Context total | CLI total（不含 cached） | 回复延迟 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| R1 | 14,426 | not_exposed | not_exposed | 13 | 14,439 | not_exposed | not_measured |
| R2 | 14,426 | not_exposed | not_exposed | 13 | 14,439 | not_exposed | not_measured |
| R3 | 14,426 | not_exposed | not_exposed | 13 | 14,439 | not_exposed | not_measured |

聚合值：

- Input（含 cached）中位数 14,426，范围 14,426-14,426
- Output 中位数 13，范围 13-13
- Context total 中位数 14,439，范围 14,439-14,439
- Cached input、非 cached input、reasoning output tokens 和 CLI total（不含 cached）未由退出 UI 暴露
- 三次均未观察到工具调用、审批、网络 fallback 或错误

完整机器明细见 [RESULTS.csv](RESULTS.csv)。

## 如何解释

三次请求的可见输入都只有两个字节，但 Codex CLI 退出界面的原生 usage 每次均显示 14,426 input tokens 和 13 output tokens，总计 14,439 tokens。由于本次只取得 Level B 证据，cached input、非 cached input、reasoning output tokens 与 cache write input 未暴露，公开包不对这些字段做推断。

这里不把 CLI 显示的 total 解释为 ChatGPT Plus 订阅额度成本。本场景测量的是登记的完整 `as-used` harness 组合，不能把 14,426 input tokens 分摊到某个单独配置项或系统提示。

## 回复差异

- R1：`Hi! What can I help you with?`
- R2：`Hi! What can I help you with?`
- R3：`Hi! What can I help you with?`

三次回复文本一致。

## 证据

公开包包含：

- [环境预检转录](evidence/preflight.txt)
- 一张已遮挡账号、Session ID 与 quota 详情的[场景状态图](evidence/environment.redacted.png)
- 一张已裁剪账号与支付信息的[订阅档位图](evidence/subscription-plan.png)
- 三次完整回复截图：[R1](attempts/r1/response.png)、[R2](attempts/r2/response.png)、[R3](attempts/r3/response.png)
- 三次已遮挡账号、Session ID、quota 详情与 resume 命令的 usage 截图：[R1](attempts/r1/usage.png)、[R2](attempts/r2/usage.png)、[R3](attempts/r3/usage.png)
- 三次精简事件记录：[R1](attempts/r1/events.sanitized.jsonl)、[R2](attempts/r2/events.sanitized.jsonl)、[R3](attempts/r3/events.sanitized.jsonl)
- 三次精确回复文本与逐次 `result.yaml`
- [私有原图哈希登记](evidence/private-evidence.md)和[像素处理审计](evidence/redaction-audit.txt)

含账号标识、Session ID、continuation 标识、完整本地路径或 quota 详情的原始截图只保存在 Git 仓库外。公开图使用不透明矩形遮挡或裁剪，没有使用模糊或马赛克。

## 已知边界

- 本次 quota 没有测量，不能归因到三次 `hi`。
- 认领 Issue #88 于 2026-09-03 在测量完成后补提；场景 manifest 本身在三次运行前已经固定。
- ChatGPT Plus 档位由公开订阅截图核验；账号标识和支付信息已移除。
- `as-used` harness 会随本地配置、插件版本和 Codex 运行时变化；结果只代表本清单与本时间窗口。
- Fast service tier 是根据三次公开 footer 截图事后映射的，虽然三次保持一致，但没有在 `launch-command.txt` 中显式固定。
- cached input 和非 cached input 未暴露，因此本包只支持 input、output 和 context total 层面的结论。
