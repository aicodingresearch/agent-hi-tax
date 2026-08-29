# Codex CLI 0.147.0 / GPT-5.6 Sol / high / ChatGPT Plus（Windows x64）

这是贡献者 [@beautyarbutin](https://github.com/beautyarbutin) 对 T-01 的一次独立三重复复测。

## 场景

- Prompt：`hi-en-v1`，精确内容为两个 UTF-8 字节 `68 69`
- Agent：官方 OpenAI Codex CLI 0.147.0
- 模型：`gpt-5.6-sol`
- Reasoning effort：`high`
- 认证与订阅：ChatGPT 订阅登录；ChatGPT Plus（贡献者自报）
- 系统：Windows 11 x64，build 26200，`zh-CN`，`Asia/Shanghai`
- 会话：三次均为 fresh session，未 resume
- 工作区：三次均为独立空目录、非 Git 仓库
- 权限：`Workspace (Ask for approval)`；collaboration mode 为 `Default`
- Harness profile：`as-used`；启用项详见 [manifest.yaml](manifest.yaml) 与 [preflight.txt](evidence/preflight.txt)

## 三次结果

| Attempt | 全部输入 | Cached input | 非缓存输入 | 输出 | Context total | CLI total | 回复事件延迟 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| R1 | 15,489 | 11,008 | 4,481 | 13 | 15,502 | 4,494 | 99,626 ms |
| R2 | 15,489 | 11,008 | 4,481 | 13 | 15,502 | 4,494 | 99,781 ms |
| R3 | 15,489 | 11,008 | 4,481 | 14 | 15,503 | 4,495 | 100,179 ms |

聚合值：

- `context_total_tokens`：中位数 15,502，范围 15,502–15,503
- `cli_total_excluding_cached`：中位数 4,494，范围 4,494–4,495
- 回复事件延迟：中位数 99,781 ms，范围 99,626–100,179 ms
- tool calls、approvals 和 reasoning output tokens：三次均为 0

机器可读明细见 [RESULTS.csv](RESULTS.csv)。

## 如何解释

三次 `input_tokens_including_cached` 都是 15,489，而可见输入只有两个字节，说明本场景的主要输入来自实际使用的 Codex harness。`cached_input_tokens` 是 input 的子集；CLI 显示的 total 是非缓存输入加输出，不能解释为 ChatGPT Plus 的订阅成本。

三次请求都先发生 WebSocket timeout，再由 Codex CLI 回退到 HTTPS 并成功完成。因此约 100 秒的延迟包含 transport timeout，只描述本次真实观测，不能当作正常服务延迟。额度 UI 没有预注册，所有额度读数均排除在结果之外。

## 证据

- 场景级[脱敏预检转录](evidence/preflight.txt)
- 私有原件哈希与公开处理方式：[private-evidence.md](evidence/private-evidence.md)
- 回复截图：[R1](attempts/r1/response.png)、[R2](attempts/r2/response.png)、[R3](attempts/r3/response.png)
- R3 独立的 [Token usage 截图](attempts/r3/usage.png)
- 最小事件日志：[R1](attempts/r1/events.sanitized.jsonl)、[R2](attempts/r2/events.sanitized.jsonl)、[R3](attempts/r3/events.sanitized.jsonl)

原始状态、回复和退出截图保存在 Git 仓库外。公开图片只做固定坐标像素裁剪，不缩放、不模糊、不生成式重绘；保留区域已逐像素核验。账号标识、Session ID、resume 命令和本机绝对路径均未进入公开包。

## 已知偏差

- 三次请求均触发 WebSocket timeout 后的 HTTPS transport fallback；延迟指标受此事件影响。
- R2 提供的 `response.raw.png` 与 `status.raw.png` 完全相同；R2 公开回复图从包含完整输入、回复和 Token usage 的退出截图裁取。
- 配置根存在 `AGENTS.md`，但每次预提示 `/status` 均显示 `Agents.md: <none>`；场景记录为没有生效的 instruction file。
- 订阅档位为贡献者自报；原始状态截图显示 Plus，但因同时包含账号和 Session ID，只在本机留存，尚未标记为维护者核验的 `private_evidence`。
- 本场景为 Windows x64、ChatGPT Plus 和贡献者 `as-used` harness，与 macOS arm64、Pro 20x 参考样板存在多个混杂变量，不把差值归因于单一因素。
