# Antigravity 2.0 Desktop 2.11.0 / Gemini 3.7 Flash / high / Google AI Pro / Windows x64

这是 T-35“同一厂商、不同产品形态”的 Desktop 侧数据包。正式采集按固定顺序与 CLI 侧交替进行：CLI R1、Desktop R1、CLI R2、Desktop R2、CLI R3、Desktop R3。每次 Desktop 运行都使用独立空项目和 fresh conversation，并且只发送一次精确的 `hi`。

## 场景

- Prompt：`hi-en-v1`，UTF-8 字节 `68 69`
- Agent：Google Antigravity 2.0 Desktop 2.11.0
- 模型与 effort：Gemini 3.7 Flash High
- Speed：`Fast`
- 订阅：Google AI Pro
- 系统：Windows 11 10.0.26200，build 26200，x64
- 工作区：三个独立空目录，均非 Git 仓库
- Security Preset：`Default`
- Artifact Review Policy：`Always Ask`
- MCP / imported plugins / user hooks：无
- Built-in skills：5 个，详见 [manifest.yaml](manifest.yaml)

## 三次结果

| Attempt | Response | Input tokens | Output tokens | Context total | Latency | Formal quota before/after |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | `Hello! How can I help you today? Let me know what you'd like to work on!` | not exposed | not exposed | not exposed | not exposed | not measured |
| R2 | `Hello! How can I help you today?` | not exposed | not exposed | not exposed | not exposed | not measured |
| R3 | `Hello! How can I help you with your project today?` | not exposed | not exposed | not exposed | not exposed | not measured |

完整逐次字段见 [RESULTS.csv](RESULTS.csv)。Desktop 官方界面只显示分钟级消息时间，不能由此推出响应延迟，因此 timing 仍为 `not_exposed`。

## 计量边界

Antigravity Desktop 2.11.0 的正式界面没有暴露本次 conversation 的精确 token 计数，也没有提供可接受的官方 conversation-ID 查询入口。本包不会将客户端本地 SQLite/Protobuf 字段的非官方解码结果作为正式数据，因为仓库规则禁止为取得数据而逆向客户端。

每次 start 图中的百分比是未显式刷新的 rounded quota preview，仅用于连接项目、模型和 effort；它们不构成正式的 `quota.before`。本次没有采集 Desktop 的正式 pre/post quota 快照，所以逐次 quota 写 `not_measured`。此外，额度池与交替运行的 CLI 侧共享，场景级归因仍为 `contaminated`。

详见 [measurement-boundary.md](evidence/measurement-boundary.md)。

## T-35 对照边界

配对的 CLI 1.1.23 场景保持同一账号、模型、effort、操作系统、prompt、空工作区和 request-review posture。CLI 侧通过官方 status-line 接口取得三次精确 token；Desktop 侧没有等价的正式接口。因此该 pair 可以比较客户端形态、公开证据能力和可观察回复，但不能宣称精确的跨形态 token 差值。

## 证据

本包为 Level B（公开视觉证据）：

- 三次 start 图连接独立项目、Gemini 3.7 Flash High、Fast 和未刷新的 quota preview
- 三次 response 图连接精确 `hi`、回复文本、分钟级界面时间和模型选择
- 六张图都经过逐张目视审计，原样复制，无裁剪、遮挡或生成式处理
- `response.txt` 与 `result.yaml` 保留三次精确回复和字段状态
- [preflight.txt](evidence/preflight.txt) 登记版本、配置、空工作区和私有 UI 证据哈希
- [private-evidence.md](evidence/private-evidence.md) 登记原图及配置证据哈希

## 协议记录

Desktop 预注册完成后，配对的 CLI 在首次 launch-only preflight 中自动从 1.1.22 更新到 1.1.23。该启动没有发送 prompt。Desktop 配置未变化，但在正式采集前补充了指向 CLI 1.1.23 的 replacement preregistration。正式三次 Desktop attempt 均在 replacement 之后完成。
