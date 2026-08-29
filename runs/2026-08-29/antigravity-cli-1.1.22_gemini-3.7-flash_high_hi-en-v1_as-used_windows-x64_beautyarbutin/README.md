# Antigravity CLI 1.1.22 / Gemini 3.7 Flash / high / Google AI Pro

这是 T-23 的 Antigravity CLI 场景，使用官方 headless print 模式，对固定模型连续执行三次 fresh `hi`。

## 场景

- Prompt：`hi-en-v1`，精确内容为两个 UTF-8 字节 `68 69`
- Agent：Antigravity CLI 1.1.22
- 模型：`gemini-3.7-flash-high`，界面标签为 `Gemini 3.7 Flash (High)`
- Effort：`high`
- 账号档位：Google AI Pro
- 路由：Google 第一方订阅登录
- 系统：Windows 11 x64，build 26200
- Profile：`as-used`
- 工作区：每次均为独立空目录且不是 Git 仓库
- 会话：每次启动新的 `agy -p` 进程，不使用 continue、conversation 或 resume
- 提交方式：固定命令参数中的精确字符串 `hi`
- 原生计量：Antigravity CLI `--output-format json` 的 `usage` 和 `duration_seconds`

固定启动命令见 [`launch-command.txt`](launch-command.txt)。

## 三次结果

| Attempt | Input | Cache read | Output | Thinking | Native total | Native duration |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| R1 | 13,727 | 0 | 154 | 112 | 13,881 | 2.784 s |
| R2 | 13,723 | 0 | 29 | 20 | 13,752 | 2.110 s |
| R3 | 13,723 | 0 | 72 | 36 | 13,795 | 3.215 s |

聚合值：

- Input 中位数 13,723，范围 13,723–13,727；
- Output 中位数 72，范围 29–154；
- Thinking 中位数 36，范围 20–112；
- Native total 中位数 13,795，范围 13,752–13,881；
- Native duration 中位数 2.784 秒，范围 2.110–3.215 秒。

三次原生记录都满足：

```text
total_tokens = input_tokens + output_tokens
```

因此本场景中的 `thinking_tokens` 作为原生细分字段单独保留，但不再次加到 total；三次 `cache_read_tokens` 都是 0。完整机器明细见 [`RESULTS.csv`](RESULTS.csv)。

## 观察结论

可见输入只有两个字节，但三次原生 input 均约为 13.7K tokens。这个结果直接证明 Antigravity CLI 的首轮请求包含大量不可见上下文；它不能仅由可见的 `hi` 解释。由于产品没有逐项暴露系统提示、工具定义和 built-in skill 的实际注入 token，本样本不把 13.7K 进一步武断拆分到某个 harness 组件。

三次 input 只相差 4 tokens，而回复长度和 thinking 差异较大。这支持“固定 harness 上下文较稳定”的本机观察，但三个样本不足以推断所有账号、版本或模型的普遍分布。

## Harness

预检发现：

- 没有配置 MCP server、导入插件、自定义 agent、用户规则、用户 skill 或 hook；
- CLI 可发现 5 个 built-in、model-invocable skills；
- built-in tools 的完整定义和实际注入内容未暴露；
- effective permission 与 filesystem profile 未暴露；
- 三次固定相同版本、模型、effort、命令、网络设置和空目录条件。

详情见 [`evidence/preflight.txt`](evidence/preflight.txt) 和 [`evidence/harness.txt`](evidence/harness.txt)。

## 证据与隐私

公开包包含：

- [脱敏环境截图](evidence/environment.redacted.png)，保留版本、套餐、模型和 effort；
- [预注册记录](evidence/preregistration.txt)；
- 三次最小脱敏原生 JSON 记录：[R1](attempts/r1/events.sanitized.jsonl)、[R2](attempts/r2/events.sanitized.jsonl)、[R3](attempts/r3/events.sanitized.jsonl)；
- 三次精确回复文本及 SHA-256；
- [私有原件哈希登记](evidence/private-evidence.md)和[遮挡审计](evidence/redaction-audit.txt)。

原始 JSON 含 conversation identifier，含账号邮箱的原始截图也具有隐私性，因此它们从未进入 Git。公开 JSON 删除了 conversation identifier，公开截图用完全不透明的实色块遮挡邮箱。

本场景没有每次 response 的原生截图；prompt、reply 和 usage 由官方 print-mode JSON、固定 launch command 和精确回复文件连接。套餐与配置由公开脱敏环境截图连接。

## 已知边界

- 本场景测量的是官方 CLI 的 headless print surface，不等同于交互式 TUI；不能把差值直接归因于模型。
- `duration_seconds` 是 CLI 原生 JSON 字段，不是外部端到端秒表；进程启动和退出开销不在该数字中解释。
- `/usage` 只在正式运行前以零 turn、零 token 的本地命令观察一次；没有用滚动窗口百分比估算每次成本。
- Google AI Pro 订阅额度不能由这些 token 直接换算；quota attribution 因而是 `not_measured`。
- 原生 `input_tokens` 与 `cache_read_tokens` 的一般关系不从三个 cache-read 为 0 的样本外推。
