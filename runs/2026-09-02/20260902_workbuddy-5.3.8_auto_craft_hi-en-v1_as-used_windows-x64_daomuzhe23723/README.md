# 首个 Windows 平台 WorkBuddy 5.3.8 / Auto / craft 实测包

这是 Agent Hi Tax 第一个在 Windows 平台（x64）上实测的 WorkBuddy 5.3.8 桌面 IDE 包，也是第一个完全由 Auto 路由到 deepseek-v4-flash 的 WorkBuddy 包。

## 场景

- Prompt：`hi-en-v1`，精确内容为两个 UTF-8 字节 `68 69`
- Agent：腾讯 WorkBuddy 5.3.8 桌面 IDE（Windows 11 10.0.26200，x64）
- 请求模型：`Auto`
- 实际模型：R1、R2、R3 均为 `deepseek-v4-flash`
- UI 场景：`日常办公`
- 原生数据库 mode：`craft`
- 权限：`fullAccess`，UI 显示“允许完全访问”
- 会话：每次均为独立目录、空白 fresh session
- 提交方式：在 WorkBuddy IDE 中人工选择目录、确认状态并手工提交 `hi`
- Profile：`as-used`
- 计量：WorkBuddy 原生 Token 与产品积分

## 三次结果

| Attempt | 实际模型 | Input（含缓存） | Cached input | 非缓存 input | Output | Thinking | Context total | 积分 | 事件耗时 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| R1 | DeepSeek-V4-Flash | 35,981 | 0 | 35,981 | 646 | 482 | 36,627 | 3.25 | 10.433 秒 |
| R2 | DeepSeek-V4-Flash | 35,981 | 896 | 35,085 | 404 | 263 | 36,385 | 3.11 | 7.777 秒 |
| R3 | DeepSeek-V4-Flash | 36,465 | 896 | 35,569 | 712 | 544 | 37,177 | 3.23 | 10.413 秒 |

WorkBuddy 的缓存与总量关系为：

```text
non_cached_input_tokens
  = input_tokens_including_cached - cached_input_tokens

context_total_tokens
  = input_tokens_including_cached + output_tokens
```

`reasoning_output_tokens` 是 `output_tokens` 的子集，不能再次相加。三次都只有一个原生 message API 调用，没有工具调用、Web 调用或人工批准。

聚合值：

- Input 中位数 35,981，范围 35,981–36,465；
- Cached input 中位数 896，范围 0–896；
- 非缓存 input 中位数 35,569，范围 35,085–35,981；
- Output 中位数 646，范围 404–712；
- Context total 中位数 36,627，范围 36,385–37,177；
- 事件耗时中位数 10.413 秒，范围 7.777–10.433 秒；
- 积分中位数 3.23，范围 3.11–3.25。

完整机器明细见 [RESULTS.csv](RESULTS.csv)，场景变量见 [manifest.yaml](manifest.yaml)。

## 与 mac 参考样板的差异

参考场景为 `20260815_workbuddy-5.3.13_auto_craft_hi-en-v1_as-used_mac-arm64`（macOS 5.3.13）。本包同时改变平台（Windows x64）和版本（5.3.8）两个变量，因此任何数值差异都不能归因于单一原因。同时这也是 T-16 所需要的首个 Windows WorkBuddy 数据点。

主要观察到的版本/平台差异：

1. **实际路由全部落在 deepseek-v4-flash**：参考样板的 R1/R2 路由到 `glm-5.2`，R3 才路由到 `deepseek-v4-flash`；而 5.3.8 Windows 三次均路由到 `deepseek-v4-flash`。
2. **SQLite 记账 key 不同**：5.3.8 的 `session_usage.credit_json` 使用 `conversationRequestId` 作为 key，而 5.3.13 参考样板的 watcher 按 `messageId` 去重。JSONL 中的 `providerData.conversationRequestId` 与之对应。
3. **切目录后 session 不软删除**：参考样板提到“5.3.13 在 GUI 切换目录后可能软删除上一条 session”；5.3.8 实测三条 session 的 `deleted_at` 均保持 `NULL`，事后仍可回查。
4. **输入上下文跨 attempt 漂移**：R3 的 prompt_tokens 比 R1/R2 多 484 tokens，归因于同账号记忆系统在三次 attempt 之间注入了更新的 profile/记忆内容。

## 空目录不等于空上下文

三次工作区在启动前都为空且不是 Git 仓库，但回复仍暴露了全局 Harness 上下文，且层次一次比一次深：

- R2 主动引用了工作区 basename `agent-hi-tax-lab`。
- R3 直接复述了用户长期记忆画像中的三条主线：简历 PDF 结构化解析 + OA 录入自动化、科大讯飞技能赛道参赛准备、基于哈佛 CBDB 的婚姻联盟网络与入仕预测建模。

这些都不来自可见的两个字符 `hi`。它们证明桌面 Agent 的首次请求会注入身份、记忆、工作区元数据等全局上下文；“空目录”只能排除项目文件，不能自动得到裸模型请求。

## 视觉回复差异

三次均为中文回复，均围绕“建立长期基本设置”展开，但长度和具体问法各不相同。三次都没有工具调用。

本项目只记录这种观察，不从三个样本推断稳定语言偏好、人格或模型指纹。

## 机器记录与积分交叉核验

每次完成后，本机只读 watcher 从 WorkBuddy fresh-session JSONL 提取全部带 `providerData.rawUsage` 的调用，按私有 `messageId` 去重，再用 SQLite `session_usage.credit_json` 逐 request 交叉核验。

三次均为：

- 1 个唯一 API call；
- JSONL `rawUsage.credit` 与 SQLite 积分完全匹配；
- 0 个工具调用；
- 0 个 Web 调用；
- session 状态为 completed。

watcher 在回复完成后读取本地记录并发送通知，不参与 WorkBuddy 推理，也没有额外模型调用。

## 证据

公开包包含：

- 场景级[环境与插件预检截图](evidence/environment.redacted.png)；
- 三次空白启动截图：[R1](attempts/r1/start.png)、[R2](attempts/r2/start.png)、[R3](attempts/r3/start.png)；
- 三次完整回复截图：[R1](attempts/r1/response.png)、[R2](attempts/r2/response.png)、[R3](attempts/r3/response.png)；
- 场景级[预检转录](evidence/preflight.txt)和 [Harness 状态](evidence/harness.txt)；
- 三份最小脱敏事件：[R1](attempts/r1/events.sanitized.jsonl)、[R2](attempts/r2/events.sanitized.jsonl)、[R3](attempts/r3/events.sanitized.jsonl)；
- 私有原图与公开副本的[哈希登记](evidence/private-evidence.md)和[遮挡审计](evidence/redaction-audit.txt)；
- 所有公开文件的 SHA-256。

私有原图不进入 Git。本包的公开截图中未出现用户名、主机名、home 路径、邮箱或 session UUID，因此所有公开图片均为原图的像素级精确副本；遮挡审计中声明的矩形数量为 0。

## 已知边界

- 未取得 WorkBuddy 订阅档位、倍率或账户总余额，因此只记录逐次原生积分。
- WorkBuddy 没有 CLI 状态流程；空目录由终端准备，Agent 状态和 prompt 由 GUI 手工操作。
- 5.3.8 在 GUI 切换目录后未软删除已完成 session，与 5.3.13 参考样板的观察相反。
- UI 的“日常办公”和数据库的 `craft` 同时保留，不假设二者是同一字段的翻译。
- Exact skills、MCP 和每次请求实际注入的 plugin/tool schema 未暴露。
- `Auto` 路由使本场景不是单一底层模型的受控比较。
