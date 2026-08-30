# Codex CLI 0.147.0 / GPT-5.6 Sol / high / ChatGPT Plus / Windows x64

这是 T-01 的一次 Windows、ChatGPT Plus、`as-used` harness 复测。三次运行均为独立空目录和 fresh session，按顺序执行，且只向模型发送一次精确的 `hi`。

## 场景

- Prompt：`hi-en-v1`，精确内容为两个 UTF-8 字节 `68 69`
- Agent：官方 OpenAI Codex CLI 0.147.0
- 模型：`gpt-5.6-sol`
- Reasoning effort：`high`
- 认证：ChatGPT 订阅登录
- 订阅：ChatGPT Plus
- 系统：Windows 11 10.0.26200，build 26200，x64
- 会话：每次均为 fresh session
- 工作区：每次均为独立空目录、非 Git 仓库
- 权限：`Workspace (Ask for approval)`
- Collaboration mode：`Default`
- Profile：`as-used`
- Plugins：11 个已安装并启用的插件，详见 [manifest.yaml](manifest.yaml)
- Skills：16 个实际观察到的注入 skills，详见 [manifest.yaml](manifest.yaml)
- MCP：`node_repl` 与 `openaiDeveloperDocs`
- Hooks：无显式 hooks；未观察到 hook 模型调用
- Quota：未预注册，不进入结果指标

## 三次结果

| Attempt | Input（含 cached） | Cached input | 非 cached input | Output | Context total | CLI total（不含 cached） | 回复延迟 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| R1 | 15,340 | 11,008 | 4,332 | 13 | 15,353 | 4,345 | 1,870 ms |
| R2 | 15,340 | 11,008 | 4,332 | 14 | 15,354 | 4,346 | 1,994 ms |
| R3 | 15,340 | 11,008 | 4,332 | 13 | 15,353 | 4,345 | 2,816 ms |

聚合值：

- Input（含 cached）中位数 15,340，范围 15,340–15,340
- Cached input 中位数 11,008，范围 11,008–11,008
- 非 cached input 中位数 4,332，范围 4,332–4,332
- Output 中位数 13，范围 13–14
- Context total 中位数 15,353，范围 15,353–15,354
- CLI total（不含 cached）中位数 4,345，范围 4,345–4,346
- 回复事件延迟中位数 1,994 ms，范围 1,870–2,816 ms
- reasoning output tokens、tool calls 和 approvals 三次均为 0

完整机器明细见 [RESULTS.csv](RESULTS.csv)。

## 如何解释

三次请求的可见输入都只有两个字节，但原生事件记录的 input context 每次均为 15,340 tokens，其中 11,008 tokens 标记为 cached input。三次的 input、cached input 和非 cached input 完全一致，只有短回复带来 1 token 的 output 差异。这表明在本次固定的 `as-used` 场景里，绝大部分输入上下文来自 Codex harness，而不是可见的 `hi`。

这里不把 CLI 显示的 total 解释为 ChatGPT Plus 订阅额度成本。Codex 的 cached input 是 input 的子集：

```text
non_cached_input_tokens
  = input_tokens_including_cached - cached_input_tokens

context_total_tokens
  = input_tokens_including_cached + output_tokens

cli_total_excluding_cached
  = non_cached_input_tokens + output_tokens
```

本场景也不能把 15,340 tokens 分摊到某个单独 plugin、skill、MCP 或系统提示；它测量的是登记的完整 harness 组合。

## 回复差异

- R1：`Hi! What can I help you with?`
- R2：`Hi! What would you like to work on?`
- R3：`Hi! What are we working on today?`

三次都没有工具调用、审批、网络 fallback 或错误。

## 证据

公开包包含：

- [预注册记录](evidence/preregistration.txt)
- [环境预检转录](evidence/preflight.txt)
- 一张已遮挡邮箱与 Session ID 的[场景状态图](evidence/environment.redacted.png)
- 三次完整回复截图：[R1](attempts/r1/response.png)、[R2](attempts/r2/response.png)、[R3](attempts/r3/response.png)
- 三次已裁掉 continuation/Session ID 行的 usage 截图：[R1](attempts/r1/usage.png)、[R2](attempts/r2/usage.png)、[R3](attempts/r3/usage.png)
- 三次精简事件记录：[R1](attempts/r1/events.sanitized.jsonl)、[R2](attempts/r2/events.sanitized.jsonl)、[R3](attempts/r3/events.sanitized.jsonl)
- 三次精确回复文本与逐次 `result.yaml`
- [私有原图哈希登记](evidence/private-evidence.md)和[像素处理审计](evidence/redaction-audit.txt)

含邮箱、Session ID 或 continuation 标识的原始截图只保存在 Git 仓库外。公开状态图只在两个登记矩形内改变像素；公开 usage 图是原图第一行的确定性像素裁剪；三张回复图与原图逐字节一致。

## 已知边界

- Quota 没有预注册，状态页中偶然出现的百分比不进入结果，也不归因于三次 `hi`。
- ChatGPT Plus 档位由公开状态图中的 `(Plus)` 核验；账号标识已遮挡。
- `as-used` harness 会随本地配置、插件版本和 Codex 运行时变化；结果只代表本清单与本时间窗口。
- Sites 插件处于启用状态，但实际注入上下文没有 `sites-building`、`sites-hosting`，活动 MCP 清单也没有 `sites-design-picker`，因此它们未登记为本场景的 active harness 成分。
