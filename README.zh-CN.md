# Agent Hi Tax

[English](README.md) | **中文**

> 一句 `hi` 的全链路成本观察。

有人发现，自己只是向 AI Agent 发了一句 `hi`，订阅额度却下降了 1% 甚至更多。

这可能来自模型推理，也可能来自 Agent 启动时加载的规则、工具、skills、MCP、工作区上下文、历史会话、缓存策略或计费取整。Agent Hi Tax 想做一件简单而有趣的事：把这些真实观察按照统一规则记录下来。

我们不急着判断哪一个 Agent “最好”，先认真回答一个更小的问题：

> 在一个明确、可复核的环境里，发出一句完全相同的输入，到底发生了什么，又消耗了什么？

[查看 Hi Tax Index：所有 Agent 场景的汇总对比](RESULTS.zh-CN.md) | [按最短路径参与贡献](CONTRIBUTING.zh-CN.md#外部贡献者最短路径)

## 这是什么

Agent Hi Tax 是一个由社区共同维护、以证据为基础的 AI Agent 消耗观察仓库。

任何 Agent 产品都在观察范围内：CLI、IDE、桌面端或网页端，官方或第三方，官方订阅或本地自部署都可以。已经采过样的产品只是起点，本项目没有一份固定的“可接受 Agent 清单”。

每次测试都会记录一套完整场景，包括：

- 使用了哪个 Agent 和哪一种载体；
- Agent 的精确版本；
- 使用了哪个模型；
- reasoning effort 或 thinking 档位；
- Plus、Pro、Max、Team、API 或其他计费方式；
- 官方订阅、官方 API、第三方中转或本地自部署路由；
- fresh、warm 或 resumed 会话；
- 工作区、规则文件、工具、插件、skills、MCP 和 hooks；
- 精确输入、可见回复和延迟；
- token、积分、额度百分比、请求数或其他原生消耗单位；
- 运行前后截图、机器日志和文件哈希。

一次运行可以简化为下面这条链路：

```text
精确输入
  → Agent 产品与 harness
  → 会话、规则、工具与工作区上下文
  → 模型、effort 与请求路由
  → 回复、token、积分、额度与延迟
  → 脱敏后的证据包
```

这里的 “Tax” 是一个带有玩笑意味的称呼，指极小输入经过完整 Agent 系统时产生的可观察开销，不代表法律或财务意义上的税费。

## 这不是什么

本项目不是：

- 模型智力或代码能力 benchmark；
- 模型 API 的通用价格表；
- 不同厂商之间的简单排行榜；
- 用订阅额度百分比反推精确 token 的工具；
- 对截图、日志或贡献者身份提供绝对真实性担保的系统。

一条结果描述的是当时那套完整执行栈，不能自动推广成“这个底层模型永远需要这么多 token”。

不同原生单位也不能强行混合。Token、订阅百分比、积分、请求次数和货币应分别展示，只有存在公开、精确的换算依据时才允许换算。

## 第一个标准样板

首个样板已经完成：官方 Codex CLI 0.147.0、`gpt-5.6-sol`、`high`、ChatGPT Pro 20x、macOS arm64、`as-used` harness，使用完全相同的 `hi` 连续进行了 3 次 fresh-session 测试。

![Codex CLI 首个 hi-en-v1 样板回复](runs/2026-08-14/codex-cli-0.147.0_gpt-5.6-sol_high_hi-en-v1_as-used_mac-arm64/attempts/r3/response.png)

| 指标 | R1 | R2 | R3 |
| --- | ---: | ---: | ---: |
| 输入（含 cached input） | 13,950 | 13,950 | 13,950 |
| Cached input | 5,888 | 0 | 9,984 |
| 输出 | 14 | 13 | 14 |
| 上下文总量 | 13,964 | 13,963 | 13,964 |
| CLI 显示口径的 total（非缓存 input + output） | 8,076¹ | 13,963 | 3,980 |

最有意思的发现不是某一个孤立数字，而是：同一 harness 的输入上下文稳定在约 13.95K tokens，但自动缓存会让 CLI 显示的 total 出现很大波动。这个 total 不能直接解释成订阅额度成本。

¹ R1 没有保存退出界面截图，该值由公开事件字段确定性推导；R2、R3 同时有事件记录与私有原始退出截图。

查看[完整样板、原始口径和公开证据](runs/2026-08-14/codex-cli-0.147.0_gpt-5.6-sol_high_hi-en-v1_as-used_mac-arm64/README.md)，以及[首轮实测带来的流程修订](docs/first-sample-lessons.zh-CN.md)。

## 第二个标准样板

第二个样板使用官方 Claude Code 2.1.220、`claude-fable-5`、`high`、Claude Max、macOS arm64 和保留真实用户配置的 `as-used` harness，同样顺序执行了 3 次 fresh-session `hi`。

| 指标 | R1 | R2 | R3 |
| --- | ---: | ---: | ---: |
| 原生普通 input | 2 | 2 | 2 |
| Cache creation input | 25,441 | 25,006 | 25,006 |
| Cache read input | 0 | 0 | 0 |
| 派生总输入 | 25,443 | 25,008 | 25,008 |
| 原生 output | 30 | 37 | 37 |
| 上下文总量 | 25,473 | 25,045 | 25,045 |
| UI 整秒耗时 | 5 秒 | 8 秒 | 6 秒 |

三次可见回复完全一致：`Hi! What can I help you with today?`。最醒目的“Hi Tax”是：两个可见字符对应的普通 input 只有 2 tokens，但首次请求同时创建了约 25K 的 1 小时 cache。

Claude 的三个 input 字段是相加关系，与首个 Codex 样板中 cached input 属于 input 子集的关系不同。项目因此升级了 attempt 模板和校验器，不再试图用一个厂商的 total 解释另一个厂商。

查看[完整 Claude Code 样板](runs/2026-08-15/claude-code-2.1.220_claude-fable-5_high_hi-en-v1_as-used_mac-arm64/README.md)，以及[第二轮流程修订](docs/second-sample-lessons.zh-CN.md)。

## 第三个标准样板与最新流程教训

第三个样板继续使用 Claude Code 2.1.220 和 `high` effort，但模型改为 `claude-opus-5`。三次派生总输入为 24,837、24,666、24,600 tokens，回复出现三个短文本变体。

这个样板最重要的贡献不是模型间差值，而是截图发现了一个混杂变量：Fable 样板 footer 为 `bypass permissions on`，Opus 样板为 `manual mode on`。因此两者 342 tokens 的总输入中位数差异被明确标成 `mode-confounded`，不能归因于模型。贡献流程据此增加了 permission/footer mode 的三次一致性检查，以及 manifest 的 comparison/confounder 字段。

查看[完整 Opus 样板和公开脱敏证据](runs/2026-08-15/claude-code-2.1.220_claude-opus-5_high_hi-en-v1_as-used_mac-arm64/README.md)。

## 第四个标准样板：WorkBuddy Auto 路由

第四个样板使用 WorkBuddy 5.3.13 桌面 IDE，固定选择 `Auto / 日常办公 / 允许完全访问`，在三个独立空目录和 fresh session 中人工提交 `hi`。

| 指标 | R1 | R2 | R3 |
| --- | ---: | ---: | ---: |
| 实际模型 | GLM-5.2 | GLM-5.2 | DeepSeek-V4-Flash |
| Input（含缓存） | 32,119 | 33,043 | 33,193 |
| Cached input | 9,920 | 9,920 | 8,960 |
| Output | 382 | 436 | 631 |
| Context total | 32,501 | 33,479 | 33,824 |
| WorkBuddy 积分 | 4.46 | 4.66 | 0.74 |
| 事件耗时 | 11.628 秒 | 8.470 秒 | 7.893 秒 |

它带来了两条新的方法教训：第一，固定选择 `Auto` 时，requested model 是场景变量，实际路由模型是逐次结果；第二，空目录并不等于空 Harness。R2 仍读到了全局 Git identity，R3 还把工作区 basename 当成了任务语义。公开证据已确定性脱敏。

查看[完整 WorkBuddy 样板、积分交叉核验和公开视觉证据](runs/2026-08-15/workbuddy-5.3.13_auto_craft_hi-en-v1_as-used_mac-arm64/README.md)。

## 一条结果如何确定身份

一个测试场景由下面这组变量共同确定：

```text
协议
× 输入
× Agent / 载体 / 版本
× 认证 / 计费 / 订阅
× 请求路由
× requested / observed model
× requested / observed effort
× 会话 / 工作区 / harness 状态
```

其中任何一项改变，都应视为另一个场景。相同场景由不同贡献者独立复测，则属于有价值的重复观察。

## 第一个标准输入

项目的第一个标准 test case 是：

```text
case_id: hi-en-v1
encoding: UTF-8
exact_input: hi
bytes_hex: 68 69
leading_whitespace: false
trailing_whitespace: false
```

后续可以增加中文问候、短问题、工具调用请求、仓库任务等其他输入。每种输入都必须保留精确原文、独立 case ID、字节数和 SHA-256；翻译或润色后的文本属于另一个 test case。

## 证据原则

项目采用三个包级证据等级：

- **Level A：机器记录 + 视觉证据。** 包含脱敏后的原生 usage/event 日志，以及足以连接配置、输入和回复的截图或录屏。
- **Level B：视觉证据。** 包含足以连接配置、输入和回复的截图或连续录屏，但没有可公开的机器记录。
- **Level C：自报数据。** 可以作为讨论线索或待复测场景，但在补充证据以前不进入有证据支持的比较数据集。

Level A 的视觉证据可以是公开脱敏图，也可以是维护者核对过、只登记哈希的私有原图。后一种必须另标 `visual_evidence_access: private_evidence`，其公开可复核性弱于公开脱敏图，原图哈希也不能被描述成公开证明。

证据等级不是 PR 门槛。能获得的证据应尽量提供；产品没有暴露、贡献者没有取得或公开会泄露隐私时，保留记录并标注 `not_exposed`、`not_provided`、`private_evidence` 或 `self_reported`。缺图不会让一次真实贡献自动失效，但会降低对应字段能够支持的结论强度。

无论使用哪一级，都遵守以下原则：

1. requested model/effort 与 observed model/effort 分开记录；
2. 订阅档位始终记录，但不预设它一定会造成差异；
3. 官方产品、官方 API、中转站和自部署结果分组展示；
4. 保留厂商原生 effort 和用量单位，不擅自归一化；
5. 机器日志与 UI 冲突时同时保留，不挑选更好看的一个；
6. 截图与日志能够提高可审计性，但不能被夸大成密码学证明；
7. 所有公开证据必须先脱敏，绝不提交 key、token、cookie、账号标识或私有内容。

完整规则见[贡献指南](CONTRIBUTING.zh-CN.md)。

## 当前状态

项目目前处于人工试运行阶段。维护者已经按照“外部贡献者”的方式完成四个样板，并继续用真实过程检查：

- 场景变量是否足够；
- 截图和日志能否对应到同一次 run；
- 脱敏流程是否现实；
- manifest 是否容易填写；
- PR 是否容易审核；
- 哪些字段实际上无法从产品中获得。

当前进度：

- [x] 中文版贡献协议与人工试运行 manifest
- [x] 第一个 `hi-en-v1` 三次重复样板
- [x] 第二个不同 Agent 样板：Claude Code / Fable 5 / high
- [x] 第三个 Claude Code / Opus 5 / high 样板及 mode 混杂审计
- [x] 第四个 WorkBuddy / Auto / craft 样板及自动路由、积分和全局上下文审计
- [x] 根据首个样板修订 protocol、证据分层和 token 口径
- [x] 根据第二至第四个样板增加 Codex／Claude／WorkBuddy 采集 adapter、厂商原生 token 口径、自动路由与 comparison 字段
- [ ] 机器可校验的正式 schema
- [x] 首版包结构与基础校验脚本
- [x] 自动生成的 Hi Tax Index 与 Pull Request 一致性检查
- [x] 外部贡献者最短路径、模板说明与 Pull Request 模板
- [ ] 自动采集与确定性脱敏辅助工具
- [x] 待测场景清单与贡献者实测指南
- [x] 场景认领、场景提议与数据更正 issue 模板
- [x] 许可、安全报告与开源仓库配置
- [ ] 图表与交互式可视化页面
- [x] 中英双语核心文档（英文为主）
- [ ] adapter 与流程复盘文档的英文版

## 仓库结构

当前结构：

```text
README.md             项目入口和基本说明
*.zh-CN.md            对应文档的中文版
RESULTS.md            自动生成的跨 Agent 汇总索引
CONTRIBUTING.md       贡献流程和证据规则
SECURITY.md           证据泄露的私密报告与撤下流程
LICENSE               Apache-2.0，覆盖 scripts/ 与 workflows
LICENSE-DATA          CC BY 4.0，覆盖数据与文档
prompts/              版本化的标准输入 case
templates/            场景与单次 attempt 模板
runs/                 已完成脱敏和核对的公开场景包
scripts/              汇总生成、包完整性、哈希和隐私线索检查
docs/                 方法说明和流程复盘
.github/               Pull Request 模板与自动一致性检查
```

正式 schema、自动采集和交互式可视化会在更多 Agent 样板完成后再定型，避免用第一家产品的字段绑死整个项目。

## 如何参与

第一次参与的贡献者，建议直接从[待测场景清单](docs/wanted-scenarios.zh-CN.md)认领一个具体任务，然后按[实测指南](docs/contributor-walkthrough.zh-CN.md)从头做到提交。

在这里贡献，也是一个真正去试用每个新 Agent 和新模型的结构化理由：每次 claim 都会把“我该去看看那个工具”变成一条可复现的公开观察；日积月累，这份清单会成长为一张由社区共同维护的真实 harness 覆盖地图。

私有试点受邀者在接受仓库邀请前，请先阅读[私有试点须知](docs/internal-pilot.zh-CN.md)。

如果你希望贡献一次测试：

1. 阅读[贡献指南](CONTRIBUTING.zh-CN.md)；
2. 选一份最接近的现有适配器——[Codex CLI](docs/adapters/codex-cli.zh-CN.md)、[Claude Code](docs/adapters/claude-code.zh-CN.md)、[WorkBuddy Desktop](docs/adapters/workbuddy-desktop.zh-CN.md)——其他 Agent 则走贡献指南里的通用采集路径；
3. 选择一个现有场景进行独立复测，或提出一个新组合；
4. 在执行前声明场景；相同设定至少顺序执行 3 次有效独立运行；
5. 按规范保存 `manifest.yaml`、精确输入、回复、截图和可用的机器日志；
6. 完成脱敏、哈希与检查清单；
7. 一个场景（包含全部重复运行）提交一个 Pull Request。

重复测试是受欢迎的。不同时间、不同版本、不同订阅和不同真实环境的独立观察，正是这个项目长期有意思的地方。

## 中英文架构

项目采用英文为主的双语文档：

- 英文（主版本）：`README.md`、`CONTRIBUTING.md`、`RESULTS.md` 以及不带语言后缀的 docs 页面；
- 中文：对应的 `*.zh-CN.md` 文件。

中英文文档共用协议版本、schema、英文机器字段和数据目录；它们不是两套数据体系。`docs/` 下的采集适配器与流程复盘目前仅有中文版，欢迎贡献翻译。测试输入的语言作为独立变量记录，不受文档语言影响。

## 许可

按文件性质分为两种许可：

- **数据与文档** —— `runs/`、`prompts/`、`templates/`、`docs/` 以及各 `*.md` 文件：[CC BY 4.0](LICENSE-DATA)。允许复用与改编（含商业用途），但必须署名。引用某条测量结果时，请同时标注场景 ID 和 commit，使数字可以回溯到一个已校验的场景包。
- **软件** —— `scripts/` 与 `.github/workflows/`：[Apache License 2.0](LICENSE)。

证据包中包含第三方 Agent 产品的截图。上述许可覆盖的是本项目自身的贡献——选择、编排、标注和测量数据——不包括各厂商的商标与界面内容，后者仅作为事实性研究记录出现。本项目与被观察的任何厂商没有隶属、认可或赞助关系。

提交 Pull Request 即表示你同意你的贡献以上述许可发布。

## 安全与隐私

在已公开的证据里发现了凭据、账号邮箱、session 标识或私有路径？**请私下报告** —— 见 [SECURITY.zh-CN.md](SECURITY.zh-CN.md)。不要开公开 issue，也不要把暴露的值粘贴到任何公开位置。涉及你自己材料的撤下请求一律接受。

## 如何正确理解结果

如果某次测试显示“发一句 `hi` 后额度下降 1%”，它严格表示：

> 在该次记录的账号、时间、Agent、版本、模型、effort、会话、路由和用量计条件下，界面显示了这一次变化。

它不自动表示：

- 这 1% 全部由 `hi` 的可见两个字符造成；
- 所有用户都会下降 1%；
- 另一个订阅档位一定相同或一定不同；
- 这 1% 能准确换算成某个 token 数；
- 中转站宣称的上游模型已经被独立证明；
- 同一产品未来版本仍会产生相同结果。

这种克制不会让项目变得无聊，反而会让每一次看似荒诞的 “Hi Tax” 更值得讨论。

---

一句 `hi` 很小，但它背后的 Agent 栈可能一点也不小。
