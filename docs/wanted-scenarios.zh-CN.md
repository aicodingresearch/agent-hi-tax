# 待测场景清单

[English](wanted-scenarios.md) | **中文**

> 每一条都是一个可以独立认领、独立完成、独立提交 Pull Request 的任务。

本页更新于 2026-08-28。已完成的场景见 [Hi Tax Index](../RESULTS.zh-CN.md)；逐步操作方法见[实测指南](contributor-walkthrough.zh-CN.md)。

## 怎么用这个清单

1. 先盘点自己手头有什么：哪个 Agent 产品、什么订阅档位、什么操作系统。**不要为了完成任务去购买订阅**；挑和现有资源匹配的任务。
2. **同等条件下，主流优先**：优先测主流、热度高的 harness 和模型——用户基数越大，一条可复核的观察能回答的疑问就越多；小众或长尾产品放在其后。
3. 在仓库开一个 issue 认领，标题写 `[Claim] T-xx 一句话场景描述`，正文写明计划使用的 Agent 版本、模型、订阅档位和预计完成时间。没有合适任务也可以在 issue 里提出新组合。
4. 同一个任务允许多人认领：不同人、不同设备、不同账号的独立复测本身就是有价值的贡献，只要在 issue 和 PR 里写清楚即可。同日目录冲突时，请遵循 [GitHub handle 后缀规则](../CONTRIBUTING.zh-CN.md#场景包目录)。
5. 认领后按[实测指南](contributor-walkthrough.zh-CN.md)逐步执行；规则细节以[贡献指南](../CONTRIBUTING.zh-CN.md)为准。
6. 一个任务对应一个场景、一个 PR。个别对照类任务（标注"2 场景"）会产出两个场景包，就提交两个 PR。

**关于版本**：清单里引用的产品版本是现有样板采集时的版本。你实际装到的多半更新——这不影响任务成立：版本不同就是一个新场景，同样有观察价值。请如实记录你安装的精确版本，不要刻意降级。

**难度说明**：

- ★ 有现成采集适配器和完整样板可照抄，改动最小；
- ★★ 有适配器，但要改变一个场景变量并保持其余不变；
- ★★★ 没有现成适配器，需要自己摸清产品的 usage 暴露方式和脱敏点。

通常预留 30–60 分钟；熟练后约 30 分钟。首次阅读文档、处理脱敏或测试没有现成适配器的产品时可能更久。

---

## A. 入门：独立复测现有场景（难度 ★）

复测是最好的第一个任务：样板、适配器、字段全部有现成参照，你只需要严格执行并如实记录。这也是检验"这套数据是否可复现"的唯一方式。

### T-01 复测：Codex CLI × gpt-5.6-sol × high

- **场景**：官方 Codex CLI（当前版本）× `gpt-5.6-sol` × `high` × ChatGPT 订阅 × fresh session × 空目录。
- **你需要**：任意档位的 ChatGPT 订阅（与样板的 Pro 20x 不同就如实记录）。
- **为什么优先**：现有样板只有维护者一人一机一次的观察；输入上下文是否稳定在约 13.95K tokens、缓存波动模式是否重现，都需要独立数据点。
- **参照**：[Codex CLI 适配器](adapters/codex-cli.zh-CN.md)、[现有样板](../runs/2026-08-14/codex-cli-0.147.0_gpt-5.6-sol_high_hi-en-v1_as-used_mac-arm64/README.md)。

### T-02 复测：Claude Code × Fable 5 × high

- **场景**：官方 Claude Code（当前版本）× `claude-fable-5` × `high` × Claude 订阅 × fresh session。
- **你需要**：Claude Pro 或 Max 订阅。
- **为什么优先**：验证"普通 input 仅 2 tokens + 约 25K cache creation"的结构是否在其他账号和配置下重现；注意三次 attempt 保持同一 permission mode。
- **参照**：[Claude Code 适配器](adapters/claude-code.zh-CN.md)、[现有样板](../runs/2026-08-15/claude-code-2.1.220_claude-fable-5_high_hi-en-v1_as-used_mac-arm64/README.md)。

### T-03 复测：WorkBuddy × Auto

- **场景**：WorkBuddy 桌面 IDE（当前版本）× `Auto` × fresh session × 独立空目录。
- **你需要**：WorkBuddy 账号（有积分显示）。
- **为什么优先**：Auto 路由的模型分布是逐次结果，样本越多越有意义；现有样板 3 次里出现了两个不同模型。这也是目前唯一做到 per-attempt 原生积分归因的产品，值得复现。
- **参照**：[WorkBuddy 适配器](adapters/workbuddy-desktop.zh-CN.md)、[现有样板](../runs/2026-08-15/workbuddy-5.3.13_auto_craft_hi-en-v1_as-used_mac-arm64/README.md)。

---

## B. 补全对比：已有产品的单变量扩展（难度 ★★）

每条任务只改变现有场景的一个变量，其余全部保持不变，是最容易产生"干净差值"的观察。

### T-11 去混杂补测：同一 permission mode 下的 Fable 5 vs Opus 5（2 场景）

- **场景**：Claude Code × `high` × 同一 permission/footer mode 下分别测 `claude-fable-5` 和 `claude-opus-5`。
- **你需要**：Claude 订阅（Max 最好，可直接对照现有样板）。
- **为什么优先**：**这是当前数据集中最明确的待修复点。** 现有 Fable/Opus 对比被 footer mode 混杂（`bypass permissions on` vs `manual mode on`），342 tokens 的总输入差异目前不能归因于模型。把 mode 固定后重测两个模型，就能把这个混杂拆掉。
- **注意**：两个场景、两个 PR；manifest 里填写 comparison/confounder 字段。

### T-10 Claude Code × Sonnet 5 × high

- **场景**：Claude Code（当前版本）× `claude-sonnet-5` × `high` × fresh session。
- **你需要**：Claude 订阅。
- **为什么优先**：补上 Sonnet 之后，同一 harness 下三个模型档位的 footprint 就能放在一起看：模型选择是否改变 system prompt 和工具定义的注入量。注意保持 permission mode 与你对照的样板一致。

### T-12 effort 阶梯：Claude Code × Fable 5 × medium（或 low）

- **场景**：与现有 Fable 样板完全相同，只把 effort 从 `high` 换成 `medium` 或 `low`。
- **为什么优先**：effort 是产品明确暴露的档位，但它到底影响输入注入、输出长度还是仅影响推理，目前没有数据。

### T-13 effort 阶梯：Codex CLI × gpt-5.6-sol × medium

- **场景**：与现有 Codex 样板完全相同，只把 effort 换成 `medium`。
- **为什么优先**：同 T-12，Codex 侧。

### T-14 订阅档位对照：Claude Pro

- **场景**：与任一现有 Claude Code 样板同型，订阅从 Max 换成 Pro。
- **为什么优先**：预期 token footprint 与订阅档位无关——但"预期"需要证据。如果有差异，那是重要发现。

### T-15 订阅档位对照：ChatGPT Plus 或普通 Pro

- **场景**：与现有 Codex 样板同型，订阅从 Pro 20x 换成 Plus 或普通 Pro。
- **为什么优先**：同 T-14，Codex 侧。

### T-16 Windows 平台复测（任选一个现有场景）

- **场景**：任一现有场景，操作系统换成 Windows。
- **为什么优先**：全部现有数据都在 macOS arm64 上；harness 在不同平台注入的环境信息可能不同。预检命令用 Windows 等价物，其余流程不变。

### T-17 WorkBuddy 固定单一模型 vs Auto

- **场景**：WorkBuddy × 显式固定一个具体模型（如 GLM-5.2）× 其余与 Auto 样板相同。
- **为什么优先**：把"Auto 路由"和"模型本身"两个变量拆开；与 T-03 的 Auto 数据对照可以观察路由本身是否引入额外开销。

---

## C. 新产品：把更多 Agent harness 纳入观察（难度 ★★★）

新产品任务的价值最高，难度也最高：没有现成适配器，需要自己回答"这个产品把 usage 暴露在哪里、怎么脱敏"。先按[贡献指南](../CONTRIBUTING.zh-CN.md)的通用语义采集，把与三个现有适配器的差异写进 PR；欢迎按你写作的语言，顺手起草 `docs/adapters/<product>.md`（英文）或 `docs/adapters/<product>.zh-CN.md`（中文）初稿。

各产品计量单位五花八门（token、积分、premium requests、额度百分比）——**保留原生单位，不要换算**。

### T-20 Gemini CLI

- **你需要**：Google 账号或 Gemini 订阅；确认产品暴露的 usage 字段。
- **为什么优先**：主流厂商中唯一完全缺席的一家；其免费/订阅额度模型与 token 暴露方式都值得首个样本。

### T-21 Cursor

- **你需要**：Cursor 订阅。
- **为什么优先**：典型的"积分/请求数"计费产品，IDE 载体，与 CLI 类产品的 harness 结构差异大。

### T-22 GitHub Copilot（CLI 或 IDE Chat）

- **你需要**：Copilot 订阅（个人或教育版均可，如实记录）。
- **为什么优先**：premium requests 是又一种原生计量单位；教育版账号也很普及，取材方便。

### T-23 自选：你日常在用的其他 Agent

- **场景**：Cline、Qwen Code、iFlow、Trae 或其他你真实使用的 Agent 产品。
- **为什么优先**：真实用户的 as-used 配置最有现实意义。先开 issue 描述组合，确认按[场景身份规则](../CONTRIBUTING.zh-CN.md#什么算同一个场景)是一个新场景即可开工。

---

## D. Harness 变量专题：直接给 harness 的组成部分"称重"（难度 ★★）

如果你的研究方向是 Agent harness 本身，这一组任务和研究最直接相关：同一产品、同一模型下做一组开/关对照，**差值直接对应 harness 某个具体组件的边际 token 成本**。背景见[实测指南·为什么值得做](contributor-walkthrough.zh-CN.md#二为什么值得做)。

### T-31 MCP 开 / 关对照（2 场景）

- **场景**：同一产品、同一模型和 effort，分别在"配置了某个 MCP server"和"移除该 MCP"两种状态下各做 3 次。选工具数量多的 MCP server 效果更明显。
- **为什么优先**：MCP 工具定义即使从未被调用，也会进入上下文影响 input tokens——这是"工具定义成本"的直接测量，harness 研究里最常被引用的问题之一。

### T-32 规则文件有 / 无对照（2 场景）

- **场景**：空目录 vs 只含一份内容固定、公开可复现的 `AGENTS.md`（或 `CLAUDE.md`）的目录，其余不变。规则文件 fixture 随 PR 公开，harness profile 用 `custom`。
- **为什么优先**：测量规则文件注入的边际成本，以及产品是否原文注入、截断或改写。

### T-30 standard-clean vs as-used 同机对照（2 场景）

- **场景**：同一台机器、同一产品和模型：先在你的真实配置（`as-used`）下做 3 次；再构造一个可核实的干净环境（如新建系统用户，确认无全局规则、MCP、插件）做 3 次 `standard-clean`。
- **为什么优先**：差值近似等于"你个人 harness 配置的全部固定开销"。
- **注意**：`standard-clean` 的门槛较高——[贡献指南](../CONTRIBUTING.zh-CN.md#三种-harness-profile)要求确实核实过才能用这个标签。无法完全确认就诚实用 `as-used`，或改做 T-31/T-32 这类单开关对照。

### T-33 fresh vs resumed 会话（2 场景）

- **场景**：同一产品和模型：一组正常 fresh；另一组先建立一个只含一次 `hi` 往返的会话、退出后 resume 再发 `hi`。
- **为什么优先**：观察会话恢复时历史注入和缓存读取的行为，目前完全没有数据。

### T-34 干净的额度归因（任选载体）

- **场景**：任选一个现有场景重做，测试期间暂停同账号、同额度池的一切其他用量，记录每次 attempt 前后的额度/百分比显示。
- **为什么优先**：现有 Codex 样板的额度归因是 `contaminated`，Claude 样板是 `not_measured`。对订阅百分比额度做出首个干净的 per-attempt 归因，就能开始回答项目最初的问题："一句 hi 到底吃掉多少额度"。WorkBuddy 样板的积分归因可作方法参照。

---

## E. 新输入 case（先开 issue 与维护者对齐）

### T-40 hi-zh-v1：中文「你好」

- **场景**：任一已有 harness × 新输入 case「你好」。
- **注意**：新输入属于协议层变更——要先定义精确原文、编码、字节序列和 SHA-256，新建 `prompts/` 文件并确定 case ID。**先开 issue 讨论定稿，再开始测**；不要直接按自己的理解发一句中文就提交。
- **为什么优先**：输入语言是否影响 harness 注入（如语言检测、回复长度），是中英双语用户直接关心的问题。

---

## F. 第三方中转站路由（难度 ★★–★★★）

Agent 的发行方和推理路由是两个变量：官方 Agent 也可以配置成走第三方网关（route 记 `third-party-gateway`）。中转站是社区里额度传闻最多、公开证据最少的一环——同名模型在中转站上的 token 计量、缓存行为和真实上游，目前几乎没有可复核的观察。规则见[贡献指南·官方产品、API 和中转站](../CONTRIBUTING.zh-CN.md#官方产品api-和中转站)。

这一组的统一注意事项：

- **只测你已经在用、信得过的中转站**；不要为了测试注册来路不明的服务，也不要把主力账号的 key 拿来做实验。
- 必须披露：中转站公开名称、公开域名、兼容协议、宣称的上游模型；endpoint 里的 secret、签名参数一律不提交。
- 中转站返回的模型名只能证明"它返回了这个标签"——manifest 里 claimed 与 observed 分开记录，不要下"证实是某厂模型"的结论。
- 倍率、积分、余额等计费显示保留原生单位；单人账号、无其他并发使用时，per-attempt 余额差是中转站少数能干净归因的计量，值得完整记录 before/after。
- 按主流优先原则：先测用户量大的中转站和主流模型标签（Claude、GPT 系列），再扩展到长尾组合。

### T-50 官方 API vs 中转站同名模型对照（2 场景）

- **场景**：同一 harness、同一模型标签（如 `claude-sonnet-5` 或某个 GPT 型号）：一组走官方 API，一组走中转站，其余全部不变。
- **为什么优先**：直接回答"中转是否改变 token 计量与缓存行为"。差异可能来自网关改写请求、剥离缓存字段、注入自己的 system prompt——每一种都是 harness 研究关心的行为。官方 API 一侧同样如实记录（route `official-api`）。

### T-51 同一中转站的模型阶梯（每个模型一个场景）

- **场景**：固定 harness 和中转站，分别测它宣称的几个不同上游模型（如 Claude、GPT、Gemini、DeepSeek 各一个场景）。
- **为什么优先**：横向看同一网关对不同上游的计量口径和延迟是否一致，顺带积累"宣称模型 vs 可观察行为"的公开记录。

### T-52 不同中转站、同名模型对照

- **场景**：同一 harness、同一模型标签，在两家不同中转站各做一组。
- **为什么优先**：如果两家对同名模型给出明显不同的 token/延迟分布，这本身就是值得公开的观察；一致则增强"标签可信"的间接证据。

---

## G. 中国模型生态：GLM、Kimi、MiniMax、千问（难度 ★★–★★★）

现有数据里中国模型只以 WorkBuddy Auto 路由的形式出现过（GLM-5.2、DeepSeek-V4-Flash）。这些厂商都有自己的官方 Agent 载体或官方兼容端点，值得逐个纳入观察。产品形态迭代很快：以下以认领时的实际产品形态为准，精确版本、订阅和路由归类如实记录，路由归类拿不准就在 PR 里描述实际链路。

同组多个选项时，先挑你判断当前热度最高、用户最多的那个组合。

### T-60 Qwen Code CLI × 千问

- **场景**：官方 Qwen Code CLI × 默认或显式固定的千问模型 × 官方账号额度 × fresh session。
- **为什么优先**：官方开源 CLI harness，免费额度门槛低，适合作为 G 组的第一单；其 harness 与 Gemini CLI 同源，未来还能和 T-20 形成同构对照。

### T-61 Kimi × 官方载体

- **场景**：Kimi 官方 CLI，或 Kimi 订阅接入官方支持的兼容 harness × 固定 Kimi 模型。
- **为什么优先**：Kimi 的订阅/额度模型与 token 暴露方式目前没有任何公开样本。

### T-62 GLM × Claude Code 兼容端点（官方 Coding 订阅）

- **场景**：智谱官方 coding 订阅经其 Anthropic 兼容端点接入 Claude Code × 固定 GLM 模型，其余与现有 Claude Code 样板对齐。
- **为什么优先**：同一个 Claude Code harness，一边接 Anthropic 官方，一边接 GLM 官方端点——**harness 恒定、后端变化**的干净对照，可直接与现有 Claude Code 样板对比输入注入和缓存行为。claimed 与 observed 模型分开记录。

### T-63 MiniMax × 官方载体或兼容端点

- **场景**：MiniMax 官方 Agent 产品，或其 M 系列模型经官方兼容端点接入 harness × fresh session。
- **为什么优先**：MiniMax 的 Agent 产品形态和计量单位都还没有样本；载体选择（官方产品 vs 兼容 harness）本身也值得在 PR 里说明。

### T-64 本地自部署开源权重（难度 ★★★）

- **场景**：开源权重（如 GLM、千问的开源版本）经 vLLM 或 Ollama 本地部署，接入任一开源 harness；route 记 `self-hosted`。
- **为什么优先**：这是唯一能同时看到"请求原文"和"计量"两端的路由——推理服务日志里的 prompt token 数可以与 harness 的注入逐字对账，是给 harness 称重最干净的方式。需要一定的本地部署经验和硬件。

---

## 想做清单之外的场景？

欢迎。开一个 issue 描述你的组合（产品 × 版本 × 模型 × effort × 订阅 × 路由 × 会话状态 × harness），对照[场景身份规则](../CONTRIBUTING.zh-CN.md#什么算同一个场景)确认它是一个新场景即可。清单会随认领和完成情况持续更新。
