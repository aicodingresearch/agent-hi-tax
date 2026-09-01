# Codex CLI 0.151.0 / GPT-5.6 Sol / high / ChatGPT Plus / Windows x64

这是 T-01（锚点 1）的一次独立复测。三次运行均使用官方 OpenAI Codex CLI、ChatGPT Plus 订阅登录、独立空目录和 fresh session，并且只向模型发送一次精确的 `hi`。

## 场景

- Claim：[aicodingresearch/agent-hi-tax#30](https://github.com/aicodingresearch/agent-hi-tax/issues/30)
- Prompt：`hi-en-v1`，精确内容为两个 UTF-8 字节 `68 69`
- Agent：官方 OpenAI Codex CLI 0.151.0
- 模型：`gpt-5.6-sol`
- Reasoning effort：`high`
- 认证与订阅：ChatGPT 订阅登录 / ChatGPT Plus
- 系统：Windows 11 10.0.26200，build 26200，x64
- 会话：每次均为 fresh session
- 工作区：每次均为独立空目录、非 Git 仓库
- 权限：`Workspace (Ask for approval)`
- Collaboration mode：`Default`（记录于运行前的[环境预检转录](evidence/preflight.txt)；公开状态图中的该值已遮挡）
- Profile：`as-used`
- 全局规则：`<CODEX_HOME>/AGENTS.md`，806 bytes，SHA-256 `a071ae5c25478e84abf40c0b9454d937b3c10786e38890b887445d3426ae4afb`
- Plugins：没有已安装插件
- Skills：6 个实际观察到的注入 skills，详见 [manifest.yaml](manifest.yaml)
- MCP：`codegraph` 已启用，但三次均未调用
- Hooks：无显式 hooks；未观察到 hook 模型调用
- Quota：预注册为不测量，不进入结果指标

## 三次结果

| Attempt | Input（含 cached） | Cached input | 非 cached input | Output | Context total | CLI total（不含 cached） | 回复延迟 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| R1 | 16,055 | 11,008 | 5,047 | 13 | 16,068 | 5,060 | 9,333 ms |
| R2 | 16,055 | 11,008 | 5,047 | 14 | 16,069 | 5,061 | 10,310 ms |
| R3 | 16,055 | 11,008 | 5,047 | 13 | 16,068 | 5,060 | 8,872 ms |

聚合值：

- Input（含 cached）中位数 16,055，范围 16,055–16,055
- Cached input 中位数 11,008，范围 11,008–11,008
- 非 cached input 中位数 5,047，范围 5,047–5,047
- Output 中位数 13，范围 13–14
- Context total 中位数 16,068，范围 16,068–16,069
- CLI total（不含 cached）中位数 5,060，范围 5,060–5,061
- 回复事件延迟中位数 9,333 ms，范围 8,872–10,310 ms
- reasoning output tokens、tool calls 和 approvals 三次均为 0

完整机器明细见 [RESULTS.csv](RESULTS.csv)。

## 如何解释

三次请求的可见人工输入都只有两个字节，但原生事件记录的 input context 每次均为 16,055 tokens，其中 11,008 tokens 标记为 cached input。三次的 input、cached input 和非 cached input 完全一致，只有短回复带来 1 token 的 output 差异。

rollout 还记录了一条由 harness 注入的全局 `AGENTS.md` 与环境上下文消息。它使用 `user` role 承载，但不是贡献者发送的额外聊天消息；逐次提取时将它与唯一人工 prompt `hi` 分开。该注入内容、skills、MCP 和其余系统定义共同属于本场景测量的 `as-used` harness。

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
- R2：`Hi! What would you like to work on?`
- R3：`Hi! What are we working on today?`

三次都没有工具调用或人工批准。

## 传输回退

三次请求都显示相同的运行时警告：WebSocket stream 因本机代理 URL scheme 不受支持而断开，CLI 随后回退到 HTTPS，并正常得到完整回复与一组原生 usage。预检中的 WebSocket reachability 检查已经报告同一警告。

本包将其登记为一致的 transport fallback，而不是模型或路由 fallback。公开证据只能证明 CLI 暴露了一个完成的回复和一个 token-count 事件，不能据此断言服务端内部是否发生过不可见重试。

## 证据

公开包包含：

- [预注册记录](evidence/preregistration.txt)
- [环境预检转录](evidence/preflight.txt)
- 一张已遮挡 Agents.md、账号邮箱、Collaboration mode 与 Session 值，同时保留 Account 行 `(Plus)` 标签的[场景状态图](evidence/environment.redacted.png)
- 一张只保留当前 Plus 套餐卡片的[订阅证据裁图](evidence/plan.png)
- 三次包含精确输入、传输回退警告和完整回复的截图
- 三次仅保留完整 Token usage 行的截图
- 三次从私有 rollout 提取的最小事件记录
- 三次精确回复文本与逐次 `result.yaml`
- [私有原图与 rollout 哈希登记](evidence/private-evidence.md)和[像素处理审计](evidence/redaction-audit.txt)

## 已知边界

- Quota 预注册为 `not_measured`；截图中偶然出现的百分比不进入结果，也不归因于三次 `hi`。
- ChatGPT Plus 由公开运行时 `/status` 图中 Account 行保留的 `(Plus)` 标签与公开套餐页面裁图交叉支持；邮箱和其他账号标识均已遮挡。
- `as-used` harness 包含全局 `AGENTS.md`、6 个 skills 和 `codegraph` MCP；结果不能分摊到其中某一个组件。
- 三次 input token 完全一致，且提取到的注入消息除等长工作区后缀外一致；没有在运行前取得完整配置文件的哈希，因此不以配置哈希单独证明场景恒定。
- 延迟只作本场景描述性元数据，不用于跨产品比较。
