# 待测场景清单

[English](wanted-scenarios.md) | **中文**

> 每一条都是一个可以独立认领、独立完成、独立提交 Pull Request 的任务。

本页更新于 2026-08-30。已完成的场景见 [Hi Tax Index](../RESULTS.zh-CN.md)；逐步操作方法见[实测指南](contributor-walkthrough.zh-CN.md)。

## 怎么用这个清单

1. 先盘点自己手头有什么：哪个 Agent 产品、什么订阅档位、什么操作系统。**不要为了完成任务去购买订阅**；挑和现有资源匹配的任务。
2. **同等条件下，主流优先**：优先测主流、热度高的 harness 和模型——用户基数越大，一条可复核的观察能回答的疑问就越多；小众或长尾产品放在其后。
3. 在仓库开一个 issue 认领，标题写 `[Claim] T-xx 一句话场景描述`，正文写明计划使用的 Agent 版本、模型、订阅档位和预计完成时间。没有合适任务也可以在 issue 里提出新组合。
4. 同一个任务允许多人认领：不同人、不同设备、不同账号的独立复测本身就是有价值的贡献，只要在 issue 和 PR 里写清楚即可。目录命名自带你的 GitHub handle，同日复测不会冲突——见 [GitHub handle 后缀规则](../CONTRIBUTING.zh-CN.md#场景包目录)。
5. 认领后按[实测指南](contributor-walkthrough.zh-CN.md)逐步执行；规则细节以[贡献指南](../CONTRIBUTING.zh-CN.md)为准。
6. 一个任务对应一个场景、一个 PR。个别对照类任务（标注"2 场景"）会产出两个场景包，就提交两个 PR。

**关于版本**：清单里引用的产品版本是现有样板采集时的版本。你实际装到的多半更新——这不影响任务成立：版本不同就是一个新场景，同样有观察价值。请如实记录你安装的精确版本，不要刻意降级。

**难度说明**：

- ★ 有现成采集适配器和完整样板可照抄，改动最小；
- ★★ 有适配器，但要改变一个场景变量并保持其余不变；
- ★★★ 没有现成适配器，需要自己摸清产品的 usage 暴露方式和脱敏点。

一次贡献通常预留约 30 分钟。首次贡献建议预留约 1 小时，足以阅读文档、处理脱敏并完成一个场景。★★★ 任务和成对的对照类任务是例外，它们各自在下面标注了自己的工作量预期。

## 积分

清单上的每个任务都有一个分值，写在标题里，形如 `(N 分)`。

**这个数字是什么。** 它是对该任务*当前*能给数据集带来多少边际信息量的标价，仅此而已。它的用途是让你一眼看出缺口在哪、据此选题。积分是给贡献计价，不是给产品排名。这与 [README 明确不做的](../README.zh-CN.md#这不是什么)"简单排行榜"不冲突——那句话指的是把厂商和模型放在一起比高下，本项目依然不做。同一套价格对所有贡献者适用。

**什么时候发分。** PR 合并的那一刻，按本页当时显示的价格与计数确定。不预留额度，也不提前锁价。开测之前你可以对照本页和 open 的 claim issue 预判一个任务大概值多少，但这个预判不构成承诺。

**A 组递减，且每个季度重置。** 复测类任务随着同类工作的累积按 3 / 2 / 1 / 0 发分，计数在每个自然季度开始时重置，自 2026Q3 起算。计数所在的桶是*产品 × 模型 × effort × 平台 × 路由 × 订阅档位*，产品小版本在这里忽略不计。精确版本仍然要按[贡献指南](../CONTRIBUTING.zh-CN.md#什么算同一个场景)如实记录——那是数据层的场景身份，与计价用的桶无关。两个订阅名称或两个产品名称是否应归一到同一个桶，拿不准时由维护者在发分时裁定，并把裁定结果回写到本页。

**维护者的四个制度前参考样板不计分，也不占用任何递减名额。**它们是复测所对照的基线；所有复测计数都从零开始，下方台账从空表起步。

**pair 任务一次发分。** 标注"2 场景"的任务在两侧都合并之后，一次性发全额分。只完成单侧的，按该侧独立满足的档位计分。

**0 分不等于"不需要"。** 它只表示这一轮不再以积分招募这个任务。数据本身依然有价值，提交与独立复测一如既往受欢迎。

**唯一的加分项是可用的新产品适配器：+2。** 每个产品一次，条件是适配器文档已经合并，*并且*其中的采集命令与脱敏点被对应场景实际走通。没有证据等级加成；诚实标注混杂或缺失不会扣你的分。

**发分之前，维护者会核查可得的证据是否被遗漏了**，依据的是[贡献指南](../CONTRIBUTING.zh-CN.md#最重要的六条规则)已有的原则：能拿到的证据应当提供，拿不到不阻断。凡是本可采集却被主动省略的，补齐之后再发分。这只影响积分，不改变 PR 的接收标准。

**清单之外的组合**要先开一个 proposal issue。维护者回复前为 0 分；回复按固定 rubric 定价：3 分 = 已覆盖 harness 背后的兼容端点或模型替换；4 分 = 成熟的第三方 harness；6 分 = 真正全新的一方或独立 harness。

**边界情况由维护者裁定**，裁定结果回写到本页。

选题之前的三条自查：

- 证据能取到就不要改交纯自述——Level C 是留给产品确实不暴露该字段的情况。
- 新输入 case 要先开 issue，在动手测量之前就把精确字节、编码和 SHA-256 对齐。
- 小众或已停更的产品，先开 proposal 说明它能回答什么现有场景回答不了的问题。

### 计分示例

规则是抽象的，下面是它们兑现的样子。

| 发生了什么 | 得分 | 为什么 |
| --- | ---: | --- |
| T-01 的首个复测包合并——它所在的桶此前是空的 | 3 | 参考样板的第一次独立复测：这个数据集的首次可复现性检验 |
| 一周后另一位贡献者合并了同一组合 | 2 | 本季度同桶第 2 个；无需任何协调——以本页计数为准 |
| 这位贡献者接着合并 T-13（同配置，effort 改 medium） | 3 | effort 轴上一个新的单变量数据点 |
| T-31（MCP 开/关）两侧都合并 | 8，一次发 | 成对对照按一个任务计价，两侧落地后发放 |
| 成对任务只做成了一侧 | 按该侧自身档位（通常 0–3） | pair 价买的是对照本身，不是它的一半 |
| OpenCode 首样合并，且适配器被该场景实际走通 | 6 + 2 | 清单点名产品的首个样本；适配器是唯一可叠加的加分，每产品一次 |
| 只交了适配器文档，没有场景走通它 | +0 | +2 的条件是文档已合并且被真实场景走通 |
| 本季度同桶的第 4 个 T-01 复测 | 0——但照常合并 | 0 只表示本轮不再以积分招募；数据价值不变，计数下季度重置 |
| 提议测一个清单完全没点名的 Agent（T-23），维护者在回复中定价 4 分，包合并 | 4 | 清单外组合在 proposal 定价之前都是 0 分 |
| 复测某个新收录产品的首样 | 走 proposal 定价 | 清单上还没有这一项：维护者定价（通常照 A 组 3/2/1/0）并回写本页 |

---

## A. 入门：独立复测现有场景（难度 ★）

复测是最好的第一个任务：样板、适配器、字段全部有现成参照，你只需要严格执行并如实记录。这也是检验"这套数据是否可复现"的唯一方式。

### T-01 复测：Codex CLI × gpt-5.6-sol × high（3 分）

- **场景**：官方 Codex CLI（当前版本）× `gpt-5.6-sol` × `high` × ChatGPT 订阅 × fresh session × 空目录。
- **你需要**：任意档位的 ChatGPT 订阅（与样板的 Pro 20x 不同就如实记录）。
- **为什么优先**：现有样板只有维护者一人一机一次的观察；输入上下文是否稳定在约 13.95K tokens、缓存波动模式是否重现，都需要独立数据点。
- **参照**：[Codex CLI 适配器](adapters/codex-cli.zh-CN.md)、[现有样板](../runs/2026-08-14/codex-cli-0.147.0_gpt-5.6-sol_high_hi-en-v1_as-used_mac-arm64/README.md)。
- **积分**：3 / 2 / 1 / 0，随同一个桶内复测的累积而递减；计数每个自然季度重置。

### T-02 复测：Claude Code × Fable 5 × high（3 分）

- **场景**：官方 Claude Code（当前版本）× `claude-fable-5` × `high` × Claude 订阅 × fresh session。
- **你需要**：Claude Pro 或 Max 订阅。
- **为什么优先**：验证"普通 input 仅 2 tokens + 约 25K cache creation"的结构是否在其他账号和配置下重现；注意三次 attempt 保持同一 permission mode。
- **参照**：[Claude Code 适配器](adapters/claude-code.zh-CN.md)、[现有样板](../runs/2026-08-15/claude-code-2.1.220_claude-fable-5_high_hi-en-v1_as-used_mac-arm64/README.md)。
- **积分**：3 / 2 / 1 / 0，随同一个桶内复测的累积而递减；计数每个自然季度重置。

### T-03 复测：WorkBuddy × Auto（3 分）

- **场景**：WorkBuddy 桌面 IDE（当前版本）× `Auto` × fresh session × 独立空目录。
- **你需要**：WorkBuddy 账号（有积分显示）。
- **为什么优先**：Auto 路由的模型分布是逐次结果，样本越多越有意义；现有样板 3 次里出现了两个不同模型。这也是目前唯一做到 per-attempt 原生积分归因的产品，值得复现。
- **参照**：[WorkBuddy 适配器](adapters/workbuddy-desktop.zh-CN.md)、[现有样板](../runs/2026-08-15/workbuddy-5.3.13_auto_craft_hi-en-v1_as-used_mac-arm64/README.md)。
- **积分**：3 / 2 / 1 / 0，随同一个桶内复测的累积而递减；计数每个自然季度重置。

---

## B. 补全对比：已有产品的单变量扩展（难度 ★★）

每条任务只改变现有场景的一个变量，其余全部保持不变，是最容易产生"干净差值"的观察。

### T-11 去混杂补测：同一 permission mode 下的 Fable 5 vs Opus 5（2 场景）（8 分）

- **场景**：Claude Code × `high` × 同一 permission/footer mode 下分别测 `claude-fable-5` 和 `claude-opus-5`。
- **你需要**：Claude 订阅（Max 最好，可直接对照现有样板）。
- **为什么优先**：**这是当前数据集中最明确的待修复点。** 现有 Fable/Opus 对比被 footer mode 混杂（`bypass permissions on` vs `manual mode on`），342 tokens 的总输入差异目前不能归因于模型。把 mode 固定后重测两个模型，就能把这个混杂拆掉。
- **注意**：两个场景、两个 PR；manifest 里填写 comparison/confounder 字段。
- **回退条件**：Fable 5 可能因安全分类器回退到 Opus 5；每次 attempt 都必须记录实际 observed model。发生回退的 attempt 不得计为 Fable 侧样本，须标注并另行补测。
- **工作量**：两侧合计真实预期约 2–4 小时，上面的 30 分钟口径在这里不适用。

### T-10 Claude Code × Sonnet 5（`claude-sonnet-5`）× high（3 分）

- **场景**：Claude Code（当前版本）× Sonnet 5（`claude-sonnet-5`）× `high` × fresh session。
- **你需要**：Claude 订阅。
- **为什么优先**：补上 Sonnet 之后，同一 harness 下三个模型档位的 footprint 就能放在一起看：模型选择是否改变 system prompt 和工具定义的注入量。注意保持 permission mode 与你对照的样板一致。

### T-12 effort 阶梯：Claude Code × Fable 5 × medium（或 low）（3 分）

- **场景**：与现有 Fable 样板完全相同，只把 effort 从 `high` 换成 `medium` 或 `low`。
- **为什么优先**：effort 是产品明确暴露的档位，但它到底影响输入注入、输出长度还是仅影响推理，目前没有数据。

### T-13 effort 阶梯：Codex CLI × gpt-5.6-sol × medium（3 分）

- **场景**：与现有 Codex 样板完全相同，只把 effort 换成 `medium`。
- **为什么优先**：同 T-12，Codex 侧。

### T-14 订阅档位对照：Claude Pro（3 分）

- **场景**：与任一现有 Claude Code 样板同型，订阅从 Max 换成 Pro。
- **为什么优先**：预期 token footprint 与订阅档位无关——但"预期"需要证据。如果有差异，那是重要发现。

### T-15 订阅档位对照：ChatGPT Plus 或普通 Pro（3 分）

- **场景**：与现有 Codex 样板同型，订阅从 Pro 20x 换成 Plus 或普通 Pro。
- **为什么优先**：同 T-14，Codex 侧。

### T-16 Windows 平台复测（任选一个现有场景）（4 分）

- **场景**：任一现有场景，操作系统换成 Windows。
- **为什么优先**：全部现有数据都在 macOS arm64 上；harness 在不同平台注入的环境信息可能不同。预检命令用 Windows 等价物，其余流程不变。
- **积分**：4 分适用于每个产品的首个 Windows 包。

### T-17 WorkBuddy 固定单一模型 vs Auto（3 分）

- **场景**：WorkBuddy × 显式固定一个具体模型（如 GLM-5.2）× 其余与 Auto 样板相同。
- **为什么优先**：把"Auto 路由"和"模型本身"两个变量拆开；与 T-03 的 Auto 数据对照可以观察路由本身是否引入额外开销。

---

## C. 新产品：把更多 Agent harness 纳入观察（难度 ★★★）

新产品任务的价值最高，难度也最高：没有现成适配器，需要自己回答"这个产品把 usage 暴露在哪里、怎么脱敏"。先按[贡献指南](../CONTRIBUTING.zh-CN.md)的通用语义采集，把与三个现有适配器的差异写进 PR；欢迎按你写作的语言，顺手起草 `docs/adapters/<product>.md`（英文）或 `docs/adapters/<product>.zh-CN.md`（中文）初稿。

各产品计量单位五花八门（token、积分、premium requests、额度百分比）——**保留原生单位，不要换算**。

### T-20 Gemini CLI（已归档——消费级路径停止服务）（0 分）

- **状态**：Gemini CLI 的个人/免费与 Pro/Ultra 档已于 2026-06-18 停止请求服务（[官方公告](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)）；企业许可与付费 API key 路径仍保留。要按保留路径测量，须先开 proposal 定价。消费级首样已不可测，新预算见 T-24。
- **你需要**：Google 账号或 Gemini 订阅；确认产品暴露的 usage 字段。
- **为什么优先**：主流厂商中唯一完全缺席的一家；其免费/订阅额度模型与 token 暴露方式都值得首个样本。
- **积分**：0——个人/免费与 Pro/Ultra 档已于 2026-06-18 停止请求服务；企业许可与付费 API key 路径仍保留，须先开 proposal 定价。消费级首样已不可测，新预算见 T-24。

### T-21 Cursor（6 分）

- **你需要**：Cursor 订阅。
- **为什么优先**：典型的"积分/请求数"计费产品，IDE 载体，与 CLI 类产品的 harness 结构差异大。
- **风险注记**：OpenAI 已通知拟于 2026-11-12 停止向 Cursor 供应其模型；测量照常进行并记录实际模型构成，该任务与分值届时复评。
- **工作量**：真实预期约 2–4 小时——摸清 usage 暴露方式和脱敏点是耗时所在，上面的 30 分钟口径在这里不适用。

### T-22 GitHub Copilot IDE Chat（6 分）

- **你需要**：Copilot 订阅（个人或教育版均可，如实记录）。
- **为什么优先**：premium requests 是又一种原生计量单位；教育版账号也很普及，取材方便。
- **计费注记**：GitHub 自 2026-06-01 起切换为 AI Credits 计费，同时仍有部分 legacy premium-request 计划并存；必须记录账号所处的计费制度。
- **工作量**：真实预期约 2–4 小时——摸清 usage 暴露方式和脱敏点是耗时所在，上面的 30 分钟口径在这里不适用。

### T-24 Google Antigravity CLI（6 分）

- **场景**：Google Antigravity CLI（当前版本）× 产品默认模型或显式固定的模型 × fresh session × 空目录；如实记录订阅档位以及产品暴露的所有计量（tokens、compute units、额度比例）。
- **你需要**：拥有 Antigravity 访问权限的 Google 账号，任意档位均可。
- **为什么优先**：Google 的旗舰 Agent harness，也是 Gemini CLI 的继任者；其状态栏/usage 输出机器可读，多形态产品家族（CLI / 桌面端 / IDE）也为 T-35 对照铺路。目前是本清单最大的单一厂商缺口。
- **工作量**：真实预期约 2–4 小时——摸清 usage 暴露方式和脱敏点是耗时所在，上面的 30 分钟口径在这里不适用。

### T-25 GitHub Copilot CLI（6 分）

- **场景**：GitHub Copilot CLI（当前版本）× 默认模型或固定模型 × fresh session × 空目录。
- **你需要**：Copilot 订阅（个人或教育版均可）。
- **为什么优先**：这是与 T-22 已覆盖的 Copilot IDE Chat 不同的 harness——CLI/SDK 形态按每次模型调用报告 usage，因此仅发一次 `hi` 就能揭示 harness 是否暗中发起额外模型调用；Copilot 生态也是业界规模最大的生态之一。
- **计费注记**：GitHub 自 2026-06-01 起切换为 AI Credits 计费，同时仍有部分 legacy premium-request 计划并存；必须记录账号所处的计费制度。
- **工作量**：真实预期约 2–4 小时——摸清 usage 暴露方式和脱敏点是耗时所在，上面的 30 分钟口径在这里不适用。

### T-26 OpenCode（6 分）

- **场景**：OpenCode（当前版本）× 显式固定一个 provider 和模型（BYOK 或其托管网关）× fresh session × 空目录；按真实配置归类 route 并在 PR 中说明。
- **你需要**：安装 OpenCode，并拥有至少一个模型 provider 的 API 访问权限。
- **为什么优先**：领先的开源 Agent CLI；其 session 记录会暴露每次调用的 tokens、cost、cache 和 reasoning——包括 session-title model 等辅助调用，这正是本项目要测量的 hidden tax。其 BYOK 设计也使它成为 T-36 的天然载体。
- **工作量**：真实预期约 2–4 小时——摸清 usage 暴露方式和脱敏点是耗时所在，上面的 30 分钟口径在这里不适用。

### T-27 xAI Grok Build（6 分）

- **场景**：xAI Grok Build（当前版本）× 固定一个 Grok 模型 × fresh session × 空目录；headless JSON 输出是天然的机器证据。
- **你需要**：SuperGrok 订阅或 xAI API key；如实记录 route。
- **为什么优先**：以第一方 harness 补上 Grok 模型家族的缺口；usage 输出完全机器可读（逐模型调用、cache buckets，以及 API 路径下的总成本数字），也能实际检验 CONTRIBUTING 中的派生货币成本规则。
- **产品形态注记**：本任务指 terminal 版 Grok Build。xAI 于 2026-08-19 新增的 web/mobile “Build” 是不同 surface，不属本任务，可另行 proposal。
- **工作量**：真实预期约 2–4 小时——摸清 usage 暴露方式和脱敏点是耗时所在，上面的 30 分钟口径在这里不适用。

### T-28 Kiro（6 分）

- **场景**：Kiro（当前版本）× 一个预先声明的 surface（IDE 或 CLI）× 产品默认模型或显式固定的模型 × fresh session × 空目录；把每次交互结束时显示的 credit 作为原生单位记录。
- **你需要**：Kiro 账号。
- **为什么优先**：AWS 的主力 agentic IDE/CLI，也是 Amazon Q Developer 的指定后继；后者已宣布于 2027-04-30 结束支持，并从 2026-05-15 起停止新订阅。Kiro 的 credit 计量精确到 0.01，单次交互结束即显示本次消耗，但官方明确按 request 计费、没有 token 级回执——保留 credit 原生单位即可。同一订阅覆盖 IDE、CLI 和 Web 多个 surface，天然适配 T-35。
- **积分**：Kiro harness 首样 6 分。
- **工作量**：真实预期约 2–4 小时——摸清 usage 暴露方式和脱敏点是耗时所在，上面的 30 分钟口径在这里不适用。

### T-29 Meta Muse Code（6 分）

- **场景**：Meta Muse Code（当前 beta）× Muse Spark 1.2 × fresh session × 空目录；记录实际选择的定价档，并保留涵盖 model call、tool run、approval 与 edit 的本地 event log。
- **你需要**：Meta 开发者账号。
- **为什么优先**：Meta 于 2026-08-05 发布的一方 terminal coding agent，本地证据透明度很高。“Contributor 数据换低价”档目前仅有二手报道，官方价目尚未复核；如选用，须在包内注明档位证据状态。标准档 vs Contributor 档的对照实验，待官方价目可核后再另立任务。
- **积分**：Meta Muse Code harness 首样 6 分。
- **工作量**：真实预期约 2–4 小时——摸清 usage 暴露方式和脱敏点是耗时所在，上面的 30 分钟口径在这里不适用。

### T-23 自选：你日常在用的其他 Agent（4 分）

- **场景**：Cline、TraeCode、Aider、OpenHands、Zed，或其他你真实使用的 Agent 产品。
- **为什么优先**：真实用户的 as-used 配置最有现实意义。上面点名的产品，开一个 claim issue 就可以开工。其他产品先开 proposal 对齐，并确认按[场景身份规则](../CONTRIBUTING.zh-CN.md#什么算同一个场景)是一个新场景。
- **积分**：点名产品（Cline、TraeCode、Aider、OpenHands、Zed）每产品首样 4 分——无需事先批准，开 claim 即可开工。其他产品先开 proposal，维护者按上面的固定 3/4/6 分 rubric 定价，回复之前为 0 分。
- **原生 Agent 条件**：点名产品必须测其自身原生 Agent；在 host 内运行 Claude Code、Codex 或其他外部 Agent（例如由 Zed 或 OpenHands 作为 ACP client）属于该外部 Agent 的样本，而非 host 的样本。
- **工作量**：真实预期约 1–2 小时——工具本来就是你天天在用的，时间花在定位 usage 字段和脱敏点上，不是学产品；上面的 30 分钟口径仍不适用。

---

## D. Harness 变量专题：直接给 harness 的组成部分"称重"（难度 ★★）

如果你的研究方向是 Agent harness 本身，这一组任务和研究最直接相关：同一产品、同一模型下做一组开/关对照，**差值直接对应 harness 某个具体组件的边际 token 成本**。背景见[实测指南·为什么值得做](contributor-walkthrough.zh-CN.md#二为什么值得做)。

### T-31 MCP 开 / 关对照（2 场景）（8 分）

- **场景**：同一产品、同一模型和 effort，分别在"配置了某个 MCP server"和"移除该 MCP"两种状态下各做 3 次。选工具数量多的 MCP server 效果更明显。
- **有效条件**：MCP 侧的 schema 必须非空，且确实注册了工具。
- **为什么优先**：MCP 工具定义即使从未被调用，也会进入上下文影响 input tokens——这是"工具定义成本"的直接测量，harness 研究里最常被引用的问题之一。
- **工作量**：两侧合计真实预期约 2–4 小时，上面的 30 分钟口径在这里不适用。

### T-32 规则文件有 / 无对照（2 场景）（8 分）

- **场景**：空目录 vs 只含一份内容固定、公开可复现的 `AGENTS.md`（或 `CLAUDE.md`）的目录，其余不变。规则文件 fixture 随 PR 公开，harness profile 用 `custom`。
- **为什么优先**：测量规则文件注入的边际成本，以及产品是否原文注入、截断或改写。
- **工作量**：两侧合计真实预期约 2–4 小时，上面的 30 分钟口径在这里不适用。

### T-30 standard-clean vs as-used 同机对照（2 场景）（8 分）

- **场景**：同一台机器、同一产品和模型：先在你的真实配置（`as-used`）下做 3 次；再构造一个可核实的干净环境（如新建系统用户，确认无全局规则、MCP、插件）做 3 次 `standard-clean`。
- **为什么优先**：差值近似等于"你个人 harness 配置的全部固定开销"。
- **注意**：`standard-clean` 的门槛较高——[贡献指南](../CONTRIBUTING.zh-CN.md#三种-harness-profile)要求确实核实过才能用这个标签。无法完全确认就诚实用 `as-used`，或改做 T-31/T-32 这类单开关对照。
- **清单证据**：`as-used` 侧必须提交 rules/MCP/skills/memory 清单快照及其 hash。
- **工作量**：两侧合计真实预期约 2–4 小时，上面的 30 分钟口径在这里不适用。

### T-33 fresh vs resumed 会话（2 场景）（8 分）

- **场景**：同一产品和模型：一组正常 fresh；另一组先建立一个只含一次 `hi` 往返的会话、退出后 resume 再发 `hi`。
- **为什么优先**：观察会话恢复时历史注入和缓存读取的行为，目前完全没有数据。
- **工作量**：两侧合计真实预期约 2–4 小时，上面的 30 分钟口径在这里不适用。

### T-35 同一厂商，不同产品形态（2 场景）（8 分）

- **场景**：同一厂商、同一账号、同一固定模型、同一空工作区配置——一侧在形态 A（例如 CLI），另一侧在形态 B（桌面应用或 IDE 扩展）。自然的首选组合：Antigravity CLI vs Antigravity 桌面端/IDE；Codex CLI vs Codex IDE 扩展；Copilot CLI vs Copilot IDE Chat。
- **为什么优先**：backend 和模型保持不变时，注入 tokens 的任何差异都是纯粹的客户端形态 harness 差异——system prompt、tool schema、workspace bootstrap。同一产品的不同形态是否是“同一个东西”，是社区最常问的问题之一。
- **积分**：每个完整 pair 8 分，两侧都合并后发放；只完成一侧则按该侧自身满足的档位定价。
- **工作量**：两侧合计真实预期约 2–4 小时，上面的 30 分钟口径在这里不适用。

### T-36 同一模型，不同 harness（2 场景）（8 分）

- **场景**：通过 BYOK 或官方 API 固定一个完全相同的模型，再用两个不同 harness 跑标准协议（例如 Claude Code vs OpenCode，或 OpenCode vs Aider）；其余条件在产品允许的范围内尽量保持一致。也可以在同一模型上增加更多 harness——先在 claim 中固定 harness 清单。
- **为什么优先**：这是 T-62（harness 不变、backend 变化）的镜像：这里模型不变、harness 变化，因此 input-token 差值就是 harness 开销的直接正面对照——本项目的核心问题。社区传闻差距可达数十倍，但还没有统一协议下的数据。
- **积分**：每个完整 pair 8 分；claim 中声明的每个额外 harness 侧在合并后加 3 分。
- **工作量**：两侧合计真实预期约 2–4 小时，上面的 30 分钟口径在这里不适用。

### T-37 内置工具与 skills 开 / 关（2 场景）（8 分）

- **场景**：同一产品、模型和 effort；A 侧把产品内置 tools/skills/plugins 固定在一份有记录的清单，B 侧在产品允许的范围内尽量精简或禁用。两侧的 MCP 保持不变（关闭）——本任务隔离产品自身的 tool schema，T-31 则隔离外部 MCP。使用 `custom` harness profile，并公开精确清单。
- **有效条件**：必须证明开关确实改变了注入配置，而非仅改变 UI 开关。
- **为什么优先**：内置 tool 和 skill 定义会在你输入任何内容前进入上下文；它们吃掉了多少“免费”`hi`，是社区最关心的问题之一，且与外部 MCP 成本相互独立。
- **积分**：每个完整 pair 8 分，两侧都合并后发放。
- **工作量**：两侧合计真实预期约 2–4 小时，上面的 30 分钟口径在这里不适用。

### T-38 客户端回执 vs 厂商账单对账（每对 5 分）

- **场景**：同一场景执行标准 3 次协议，同时采集测量两侧：客户端/harness 自报回执（token、credit 或 cost）与厂商侧账单或 admin usage 记录（例如 GitHub AI Credits 用量、Kiro 账户页、腾讯 Credits 明细或 API 账单）；核对两者是否一致，并记录口径差异。
- **你需要**：一个能同时暴露 per-run 客户端回执和厂商侧账单或 admin usage 记录的产品与账号。
- **为什么优先**：各家 usage 语义正在分化——例如 GitHub 明确将 `ai_credits_used` 视为聚合指标，而非账单。本任务校准的是整个测量仪器，而不只是增加一个数据点。
- **积分**：每对 5 分，两侧证据齐全才发放。
- **工作量**：真实预期约 2–4 小时——同时采集并核对两处证据是耗时所在，上面的 30 分钟口径在这里不适用。

---

## E. 新输入 case（先开 issue 与维护者对齐）

### T-40 hi-zh-v1：中文「你好」（4 分）

- **场景**：任一已有 harness × 新输入 case「你好」。
- **注意**：新输入属于协议层变更——要先定义精确原文、编码、字节序列和 SHA-256，新建 `prompts/` 文件并确定 case ID。**先开 issue 讨论定稿，再开始测**；不要直接按自己的理解发一句中文就提交。
- **为什么优先**：输入语言是否影响 harness 注入（如语言检测、回复长度），是中英双语用户直接关心的问题。
- **积分**：4 分同时覆盖两半——新输入 case 的定义，以及使用它的首个场景包。

---

## F. 第三方中转站路由（难度 ★★–★★★）

Agent 的发行方和推理路由是两个变量：官方 Agent 也可以配置成走第三方网关（route 记 `third-party-gateway`）。中转站是社区里额度传闻最多、公开证据最少的一环——同名模型在中转站上的 token 计量、缓存行为和真实上游，目前几乎没有可复核的观察。规则见[贡献指南·官方产品、API 和中转站](../CONTRIBUTING.zh-CN.md#官方产品api-和中转站)。

这一组的统一注意事项：

- **只测你已经在用、信得过的中转站**；不要为了测试注册来路不明的服务，也不要把主力账号的 key 拿来做实验。
- 必须披露：中转站公开名称、公开域名、兼容协议、宣称的上游模型；endpoint 里的 secret、签名参数一律不提交。
- 中转站返回的模型名只能证明"它返回了这个标签"——manifest 里 claimed 与 observed 分开记录，不要下"证实是某厂模型"的结论。
- 倍率、积分、余额等计费显示保留原生单位；单人账号、无其他并发使用时，per-attempt 余额差是中转站少数能干净归因的计量，值得完整记录 before/after。
- 按主流优先原则：先测用户量大的中转站和主流模型标签（Claude、GPT 系列），再扩展到长尾组合。

### T-50 官方 API vs 中转站同名模型对照（2 场景）（8 分）

- **场景**：同一 harness、同一模型标签（如 `claude-sonnet-5` 或某个 GPT 型号）：一组走官方 API，一组走中转站，其余全部不变。
- **为什么优先**：直接回答"中转是否改变 token 计量与缓存行为"。差异可能来自网关改写请求、剥离缓存字段、注入自己的 system prompt——每一种都是 harness 研究关心的行为。官方 API 一侧同样如实记录（route `official-api`）。
- **工作量**：两侧合计真实预期约 2–4 小时，上面的 30 分钟口径在这里不适用。

### T-51 同一中转站的模型阶梯（每个模型一个场景）（3 分）

- **场景**：固定 harness 和中转站，分别测它宣称的几个不同上游模型（如 Claude、GPT、Gemini、DeepSeek 各一个场景）。
- **为什么优先**：横向看同一网关对不同上游的计量口径和延迟是否一致，顺带积累"宣称模型 vs 可观察行为"的公开记录。
- **积分**：每个模型场景 3 分，暂时限定在上面列出的这批模型清单内。

### T-52 不同中转站、同名模型对照（6 分）

- **场景**：同一 harness、同一模型标签，在两家不同中转站各做一组。
- **为什么优先**：如果两家对同名模型给出明显不同的 token/延迟分布，这本身就是值得公开的观察；一致则增强"标签可信"的间接证据。
- **积分**：无官方 anchor 的孤立双中转对照每对 6 分；若与已合并的 T-50 官方侧构成星形设计，则每新增一个中转侧加 3 分，须在 claim 中声明该星形设计。
- **工作量**：两侧合计真实预期约 2–4 小时，上面的 30 分钟口径在这里不适用。

---

## G. 中国模型生态：GLM、Kimi、MiniMax、千问、DeepSeek（难度 ★★–★★★）

现有数据里中国模型只以 WorkBuddy Auto 路由的形式出现过（GLM-5.2、DeepSeek-V4-Flash）。这些厂商都有自己的官方 Agent 载体或官方兼容端点，值得逐个纳入观察。产品形态迭代很快：以下以认领时的实际产品形态为准，精确版本、订阅和路由归类如实记录，路由归类拿不准就在 PR 里描述实际链路。

同组多个选项时，先挑你判断当前热度最高、用户最多的那个组合。

### T-60 Qwen Code CLI × 千问（6 分）

- **场景**：官方 Qwen Code CLI × 默认或显式固定的千问模型 × 官方账号额度 × fresh session。
- **为什么优先**：官方开源 CLI harness，免费额度门槛低，适合作为 G 组的第一单；其 harness 与 Gemini CLI 同源，未来还能和 T-20 形成同构对照。
- **路径注记**：免费 OAuth 档已于 2026-04-15 停止；必须记录实际认证与计费路径（Coding Plan、API key 等），并将其视为计价桶的组成部分。

### T-61 Kimi Code CLI（6 分）

- **场景**：2026 年 5 月起的新 Kimi Code CLI（Node/TypeScript 重写版）× 固定 Kimi 模型 × fresh session。旧 Python `kimi-cli` 官方已不再维护，不得采集。
- **为什么优先**：Kimi 的订阅/额度模型与 token 暴露方式目前没有任何公开样本。

### T-62 GLM × Claude Code 兼容端点（3 分）

- **场景**：智谱官方 coding 订阅经其 Anthropic 兼容端点接入 Claude Code × 固定 GLM 模型，其余与现有 Claude Code 样板对齐。
- **为什么优先**：同一个 Claude Code harness，一边接 Anthropic 官方，一边接 GLM 官方端点——**harness 恒定、后端变化**的干净对照，可直接与现有 Claude Code 样板对比输入注入和缓存行为。claimed 与 observed 模型分开记录。按 rubric 这是后端替换（3 分），而非新 harness 首样；Z.ai 的一方 Agent 见 T-67 ZCode。

### T-63 MiniMax Code（6 分）

- **场景**：一方 MiniMax Code 产品（当前版本）× 默认或显式固定的 MiniMax 模型 × fresh session；如实记录产品形态与计量单位。
- **为什么优先**：MiniMax Code 的一方 Agent 形态和计量单位目前都没有样本。
- **积分**：一方 MiniMax Code 产品首样 6 分；仅把 MiniMax 模型接入第三方 harness（例如 × Claude Code）按 rubric 以 3 分走 proposal。

### T-65 DeepSeek（6 或 3 分）

- **场景**：DeepSeek 官方 Agent 产品（如有），或通过其官方兼容端点把固定的 DeepSeek 模型接入某个 harness × fresh session；产品形态与路由分类照实记录。
- **为什么优先**：使用最广的中国模型系列，但目前在本数据集中只以 WorkBuddy Auto 路由结果的身份出现过（某次 attempt 路由到 DeepSeek-V4-Flash）；其官方额度/计费模式与 token 暴露还没有任何专属样本。固定 DeepSeek 的场景也能与现有 Auto 观察形成对照。
- **积分**：一方 DeepSeek harness 首样 6 分；DeepSeek × Claude Code 兼容端点（官方 coding-agent 文档当前即此路径）按 3 分。认领时以实际产品形态裁定，并写入 claim。

### T-66 Tencent CodeBuddy Code（6 分）

- **场景**：Tencent CodeBuddy Code（当前版本）× 一个预先声明的一方 surface（插件、IDE 或 CodeBuddy Code CLI）× 默认或显式固定的模型 × fresh session × 空目录；如实记录原生 Credits 与共享额度范围。
- **你需要**：可访问任一一方 surface 的 Tencent CodeBuddy Code 账号。
- **为什么优先**：这是腾讯面向研发的一方产品；虽然与已测的 WorkBuddy 同属 Buddy 家族，却是不同产品面。官方计费明确 CodeBuddy Code 与 WorkBuddy 在同一账号下共享 Credits，因此 manifest 的 `quota_shared_scope` 必须如实标记该共享池。CLI 也暴露 `/cost`，并有成本管理文档；与 WorkBuddy 的同账号对照是后续高价值 pair，可另行 proposal。
- **积分**：Tencent CodeBuddy Code harness 首样 6 分。
- **工作量**：真实预期约 2–4 小时——摸清 usage 暴露方式、共享额度和脱敏点是耗时所在，上面的 30 分钟口径在这里不适用。

### T-67 ZCode（6 分）

- **场景**：ZCode（当前版本）× 固定一个模型 × 声明一个 Z.ai 订阅或计费路径 × fresh session × 空目录。
- **你需要**：拥有 ZCode 访问权限的 Z.ai 账号。
- **为什么优先**：Z.ai 自己的一方 coding agent 在 2026 年 8 月仍处于快速发版期。固定模型与订阅路径后，它与 T-62 构成天然对照：T-62 是把 GLM 接入 Claude Code 的 3 分兼容端点替换，这里则是一方 harness——直接比较一方 harness vs 端点替换。
- **积分**：ZCode harness 首样 6 分。
- **工作量**：真实预期约 2–4 小时——摸清 usage 暴露方式和脱敏点是耗时所在，上面的 30 分钟口径在这里不适用。

### T-64 本地自部署开源权重（难度 ★★★）（6 分）

- **场景**：开源权重（如 GLM、千问的开源版本）经 vLLM 或 Ollama 本地部署，接入任一开源 harness；route 记 `self-hosted`。
- **为什么优先**：这是唯一能同时看到"请求原文"和"计量"两端的路由——推理服务日志里的 prompt token 数可以与 harness 的注入逐字对账，是给 harness 称重最干净的方式。需要一定的本地部署经验和硬件。
- **积分**：6 分只适用于一套自部署栈，且需在认领 issue 里预先报价；默认不按栈的数量重复发放。
- **栈冻结条件**：必须冻结完整栈——model checkpoint/hash、量化、serving runtime 及版本、GPU、context 设置、sampling/tool 支持。后续更换量化或 runtime 属变量任务，走 proposal（2–3 分），不再按 6 分首样计。
- **工作量**：真实预期约 2–4 小时——摸清 usage 暴露方式和脱敏点是耗时所在，上面的 30 分钟口径在这里不适用。

---

## H. 新近发布的 harness（难度 ★★★）

本组收录 2026 年下半年新发布或出现新形态的产品线；按 rubric 定价，产品迭代快，以认领时的实际形态为准。

### T-70 Devin CLI（6 分）

- **场景**：Devin CLI（当前版本）× 产品默认模型或显式固定的模型 × fresh session × 空目录；如实记录订阅与原生 ACU 用量。
- **你需要**：拥有 Local/CLI 访问权限的 Devin 账号。
- **为什么优先**：在 Cognition 现行产品体系中，Windsurf 已于 2026-06-02 并入 Devin Desktop，Cascade 已弃用，不应再采旧产品。Devin Local 与 CLI 共享 next-generation harness，并以 ACU 计量；与 Devin Desktop 组成 T-35 同厂商 pair 是天然后续实验。
- **积分**：Devin CLI harness 首样 6 分。
- **工作量**：真实预期约 2–4 小时——摸清 usage 暴露方式和脱敏点是耗时所在，上面的 30 分钟口径在这里不适用。

### T-71 Mistral Vibe（条件式 4 分）

- **场景**：Mistral Vibe 2.23.3 或更高版本 × 显式固定一个 provider 和模型 × fresh session × 空目录；逐次采集 provider-reported token usage。
- **你需要**：安装 Mistral Vibe，并拥有能稳定暴露 per-run token usage 的 provider 访问权限。
- **为什么优先**：Mistral 官方 CLI 为清单补上一条成熟厂商 harness，但其本地计算的 USD 成本被官方明确标为 indicative。该金额只能记为 `indicative`，不得作为 canonical 货币成本。
- **积分**：仅当采集包证明能稳定取得逐次 provider-reported token usage 时发 4 分；不满足条件则按 proposal 处理。
- **工作量**：真实预期约 2–4 小时——证明逐次 token 回执及其语义是耗时所在，上面的 30 分钟口径在这里不适用。

### T-72 Warp Agent CLI（6 分）

- **场景**：Warp Agent CLI（当前版本）× 产品默认模型或显式固定的模型 × fresh session × 空目录；使用 `/usage` 记录 plan 与逐轮 credit 消耗。
- **你需要**：拥有 Agent CLI 访问权限的 Warp 账号，任意档位均可。
- **为什么优先**：2026-08-04 正式发布的 standalone Agent CLI 可在任意终端使用；自 2026-08-25 起，其 `/usage` 输出会在 per-turn credit 计费下显示 plan 与 credit 用量。勿采已弃用的 Oz 或旧 `warp-cli`，它们将被本产品取代。
- **积分**：Warp Agent CLI harness 首样 6 分；本任务替代 Warp 原先在 T-23 中的 4 分点名档。
- **工作量**：真实预期约 2–4 小时——摸清 usage 暴露方式和脱敏点是耗时所在，上面的 30 分钟口径在这里不适用。

---

## 想做清单之外的场景？

欢迎。开一个 issue 描述你的组合（产品 × 版本 × 模型 × effort × 订阅 × 路由 × 会话状态 × harness），对照[场景身份规则](../CONTRIBUTING.zh-CN.md#什么算同一个场景)确认它是一个新场景即可。清单会随认领和完成情况持续更新。

---

## 积分账本

维护者在合并时在这里追加一行。更正以追加冲销行的方式处理，历史行不改动。某位贡献者的累计分就是他名下各行之和。

| 日期 | 贡献者 | 任务 | PR | 积分 | 备注 |
| --- | --- | --- | --- | ---: | --- |
| 2026-08-30 | [@beautyarbutin](https://github.com/beautyarbutin) | T-16 | [#13](https://github.com/aicodingresearch/agent-hi-tax/pull/13) | 4 | 首个 Codex CLI Windows 包；维护者评审时由 T-01 重分类为 T-16 |
