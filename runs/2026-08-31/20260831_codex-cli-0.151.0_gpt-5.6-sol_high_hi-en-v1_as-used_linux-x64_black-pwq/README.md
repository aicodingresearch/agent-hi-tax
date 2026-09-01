# Codex CLI 0.151.0 / GPT-5.6 Sol / high / ChatGPT Plus / WSL2 x86_64

这是 T-01 的一次 WSL2、ChatGPT Plus、`as-used` harness 独立复测。三次运行均在独立空目录和 fresh session 中顺序执行，每次只向模型发送一次精确的 `hi`。

## 场景

- Prompt：`hi-en-v1`，精确内容为两个 UTF-8 字节 `68 69`
- Agent：官方 OpenAI Codex CLI 0.151.0
- 模型：`gpt-5.6-sol`
- Reasoning effort：`high`
- 认证与路由：ChatGPT Plus 官方订阅
- 系统：Linux 6.6.87.2-microsoft-standard-WSL2，x86_64
- 会话：三次均为 fresh session
- 工作区：三个独立空目录，均不是 Git 仓库
- 权限：`Workspace (Ask for approval)`；filesystem `workspace-write/restricted`；network `restricted`
- Collaboration mode：`Default`
- Profile：`as-used`
- Plugins：未安装或启用 plugin；模型上下文包含 50 项推荐目录，但它们不是已安装 plugin
- Skills：5 个实际注入的 skills，详见 [manifest.yaml](manifest.yaml)
- MCP：无已配置 server
- Hooks：无显式 hooks；未观察到 hook 模型调用
- Quota：未预注册，不进入结果指标

## 三次结果

| Attempt | Input（含 cached） | Cached input | 非 cached input | Output | Context total | CLI total（不含 cached） | 回复延迟 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| R1 | 17,902 | 11,008 | 6,894 | 13 | 17,915 | 6,907 | 4,082 ms |
| R2 | 17,902 | 11,008 | 6,894 | 13 | 17,915 | 6,907 | 2,629 ms |
| R3 | 17,902 | 11,008 | 6,894 | 14 | 17,916 | 6,908 | 2,798 ms |

聚合值：

- Input（含 cached）中位数 17,902，三次相同
- Cached input 中位数 11,008，三次相同
- 非 cached input 中位数 6,894，三次相同
- Output 中位数 13，范围 13–14
- Context total 中位数 17,915，范围 17,915–17,916
- CLI total（不含 cached）中位数 6,907，范围 6,907–6,908
- 回复事件延迟中位数 2,798 ms，范围 2,629–4,082 ms
- reasoning output tokens、tool calls 和 approvals 三次均为 0

完整机器明细见 [RESULTS.csv](RESULTS.csv)。

## 如何解释

三次请求的可见输入均只有两个字节，但原生事件记录的 input context 每次为 17,902 tokens，其中 11,008 tokens 标记为 cached input。三次 input、cached input 和非 cached input 完全一致，只有 R3 的短回复多 1 个 output token。结果描述的是本次登记的完整 `as-used` harness，不能把输入量单独归因于某个 skill、推荐 plugin 目录或系统提示。

这里不把 CLI 显示的 total 解释为 ChatGPT Plus 订阅额度成本。Codex 的 cached input 是 input 的子集：

```text
non_cached_input_tokens
  = input_tokens_including_cached - cached_input_tokens

context_total_tokens
  = input_tokens_including_cached + output_tokens

cli_total_excluding_cached
  = non_cached_input_tokens + output_tokens
```

## 回复差异

- R1：`Hi! What can I help you with?`
- R2：`Hi! What can I help you with?`
- R3：`Hi! What would you like to work on?`

三次均没有工具调用、审批、错误或额外模型聊天消息。

## 证据

公开包包含：

- [预注册记录](evidence/preregistration.txt)和[环境预检](evidence/preflight.txt)
- [模型可见 skills](evidence/skills-prompt-input.txt)与[harness 分类证据](evidence/harness-prompt-input.txt)
- 一张遮挡账户邮箱与 Session ID 的[场景状态图](evidence/environment.redacted.png)
- 三次完整回复截图：[R1](attempts/r1/response.png)、[R2](attempts/r2/response.png)、[R3](attempts/r3/response.png)
- 三次 usage 截图：[R1](attempts/r1/usage.png)、[R2](attempts/r2/usage.png)、[R3](attempts/r3/usage.png)
- 三次精简事件记录：[R1](attempts/r1/events.sanitized.jsonl)、[R2](attempts/r2/events.sanitized.jsonl)、[R3](attempts/r3/events.sanitized.jsonl)
- 三次精确回复文本和逐次 `result.yaml`
- [源截图哈希登记](evidence/private-evidence.md)与[确定性脱敏审计](evidence/redaction-audit.txt)

含账户邮箱、Session ID 或 continuation ID 的源截图一直保存在 Git 仓库外。公开图只在登记矩形内使用终端背景色进行不透明遮挡，没有模糊、马赛克、缩放或生成式编辑。

## 已知边界

- T-01 Claim Issue 在采集完成后补建；场景本身已在 R1 前通过 `evidence/preregistration.txt` 本地预注册。
- R1 前在空工作区运行过一次本地 `codex debug prompt-input` 诊断，用于记录模型可见的 skills 和 harness 分类；它没有创建工作区文件或发送模型请求。
- Quota 没有预注册；截图中偶然出现的百分比不进入结果，也不归因于三次 `hi`。
- ChatGPT Plus 档位由公开状态图中的 `(Plus)` 核验，账户标识已遮挡。
- `as-used` harness 会随 Codex 运行时和本地配置变化；结果只代表本次登记的版本和时间窗口。
- `recommended_plugins` 和通用 apps instructions 虽然进入模型可见上下文，但不表示相应 plugin 或 App 已安装、连接或启用。
