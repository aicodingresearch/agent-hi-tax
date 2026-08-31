# 参与 Agent Hi Tax

[English](CONTRIBUTING.md) | **中文**

> 用同一句小输入，观察一套真实 Agent harness 到底加载了什么、显示了什么、消耗了什么。

Agent Hi Tax 是一个轻松但尽量可复核的观察项目。它不是模型能力 benchmark，也不是通用价格表。我们记录的是一次完整执行栈：Agent 产品和版本、模型、effort、订阅或 API 路由、会话状态、工作区、规则、skills、MCP、hooks、缓存，以及产品实际暴露的 token、积分、额度和延迟。

本页为中文版，机器字段保持英文。英文主版本见 [CONTRIBUTING.md](CONTRIBUTING.md)；两个版本共用同一协议版本、模板和数据目录。

## 外部贡献者最短路径

想先挑一个具体任务，或需要更手把手的逐步指引，参见[待测场景清单](docs/wanted-scenarios.zh-CN.md)和[实测指南](docs/contributor-walkthrough.zh-CN.md)。

第一次参与时，按下面顺序即可：

1. Fork 并 clone 本仓库，为一个场景新建一个分支。
2. 选一份采集适配器，或走通用路径。**任何 Agent 产品都在范围内**：CLI、IDE、桌面端或网页端都可以。现有适配器覆盖 [Codex CLI](docs/adapters/codex-cli.zh-CN.md)、[Claude Code](docs/adapters/claude-code.zh-CN.md) 和 [WorkBuddy Desktop](docs/adapters/workbuddy-desktop.zh-CN.md)，这份清单记录的是已经采过样的产品，不是本项目接受的产品范围。你的产品没有适配器时，按本页通用语义采集，在 PR 中说明产品差异，也欢迎顺手起草一份 `docs/adapters/<产品>.md`。
3. 先固定场景和 launch command，再顺序执行至少 3 次 fresh attempt；不要边测边改模型、effort、权限模式或插件状态。
4. 原始截图和原始 session/transcript 先留在 Git 仓库外；只有脱敏副本和最小机器事件可以进入 PR。
5. 复制[场景模板](templates/scenario-manifest.yaml)、[单次模板](templates/attempt-result.yaml)，并参考与自己产品最接近的[六个已公开场景包](runs/README.zh-CN.md)。
6. 生成哈希，运行 `./scripts/verify-all.sh`，再使用仓库的 Pull Request 模板提交。

不必为了追求 Level A 而解析不理解的内部日志。只有截图时可以诚实提交 Level B；字段拿不到就使用固定缺失状态。未经脱敏的原图、账号信息和 session 标识绝不能先上传、再等待维护者删除。

## 最重要的六条规则

1. **一个场景至少做 3 次有效独立运行。** 三次顺序执行，不并行；每次使用新会话和新工作区，除非场景本身声明为 warm 或 resumed。
2. **场景变量不变。** Agent、版本、模型、effort、订阅、路由、prompt 和 harness 任何一项改变，都应拆成另一个场景。
3. **环境证据只采一次。** 同一组三次运行不必重复截图版本、系统、订阅和固定配置。
4. **每次运行只采本次结果。** 保存精确输入与完整回复，以及能够取得的原生 usage 或机器事件。
5. **能拿到的证据应当提供，拿不到不阻断。** 缺失、未暴露、只保留私有原图或证据冲突都必须明确标注；不能用猜测补字段。
6. **不把一个 total 当成成本。** Cached input、非缓存 input、output、积分和订阅百分比要分开保存；没有公开换算公式就不换算。

## 什么算同一个场景

场景身份由下面这些变量共同确定：

```text
协议版本 × prompt case
× Agent / 载体 / 精确版本
× 认证 / 订阅 / 计费通道 / 路由
× requested 与 observed model
× requested 与 observed effort
× 操作系统 / 架构
× 会话 / 工作区 / harness profile
× 规则、plugins、skills、MCP、hooks 和权限模式
```

例如，下面任意变化都要拆成新场景：

- Codex CLI 换成 Codex 桌面端；
- Agent 或插件升级版本；
- `medium` 换成 `high`；
- Plus 换成 Pro，或 Pro 换成 Pro 20x；
- 官方订阅换成官方 API 或第三方中转站；
- macOS 换成 Windows；
- fresh session 换成 resume；
- 空目录换成带 `AGENTS.md` 的仓库；
- 开关某个 skill、MCP、plugin 或会调用模型的 hook。

自动缓存命中通常是运行结果，不是贡献者可控的场景变量。只要缓存策略没有人为改变，应把每次命中量分别记录，而不是因为命中量不同就拆场景。

自动模型路由采用相同原则：当贡献者固定选择产品的 `Auto`，requested model `Auto` 是场景变量，实际路由模型是逐次结果；三次路由到不同模型时仍属于同一个 Auto 场景。贡献者必须逐次记录 actual model，并避免把积分或 token 差异解释成同一底层模型的波动。显式固定具体模型时，模型变化才需要拆场景或标记为执行错误。

## 三种 harness profile

每个场景必须选择一种 profile：

- `standard-clean`：新会话、空工作区，没有贡献者增加的项目规则、MCP、plugins、skills 或 hooks。只有确实核实过才能使用。
- `as-used`：贡献者平时真实配置。它很有现实价值，但必须列出已知规则、skills、MCP、plugins 和 hooks。
- `custom`：专门设计的固定 fixture 或配置。可公开时提供 fixture 和不可变 commit。

不要为了贴上 `standard-clean` 标签而删除个人配置。无法完全确认全局配置时，诚实使用 `as-used`。

## 标准输入

首个标准 case 是 [`hi-en-v1`](prompts/hi-en-v1.txt)：

```text
可见内容：hi
编码：UTF-8
字节：68 69
字节数：2
SHA-256：8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4
前导空白：无
尾随空白：无
```

Enter/Return 只负责提交，不属于 prompt。不要大写、补标点或加换行。

可以贡献其他输入，但每种精确输入必须有独立 case ID、原文文件、编码、字节数和 SHA-256。翻译、润色或添加一个标点都属于另一个 case。

## 证据如何分层

### 包级等级

- **Level A — 机器记录 + 视觉证据：** 有脱敏后的原生 usage/event 记录，同时有能够连接配置、输入和回复的截图或录屏。
- **Level B — 视觉证据：** 有足够截图或连续录屏，但产品没有可用的机器记录。
- **Level C — 自报数据：** 缺少可以公开复核的核心证据，可保留为待复测观察，但不进入“已验证字段”的比较。

Level A 的视觉证据可以公开，也可以由维护者私下核对后只发布哈希。私有视觉证据必须设置 `visual_evidence_access: private_evidence`，并逐字段使用 `private_evidence`；它仍说明机器记录与视觉原件同时存在，但公开可复核性弱于发布脱敏图，哈希本身也不是公开证明。

### 字段级状态

包级等级不能掩盖单个字段的缺口。对关键字段分别使用：

- `verified`：有公开证据支持；
- `private_evidence`：维护者核对过原件，但原件因隐私没有公开，只公开哈希或脱敏转录；
- `self_reported`：贡献者声明，缺少独立公开证据；
- `not_exposed`：产品没有暴露；
- `not_provided`：产品可能暴露，但本次没有取得；
- `conflicted`：两个来源相互冲突，两个值都保留；
- `not_applicable`：不适用于本场景。

证据不齐不会自动阻断 PR。它只会限制这条记录能支持的结论。例如，没有订阅截图仍可记录 token 日志，但订阅档位只能标为 `self_reported`；共享额度受到其他会话污染时，session token 仍可有效，额度差值则必须排除。

## 哪些证据只需采一次

同一场景的三次重复，共用一组场景级证据：

- Agent 版本命令或产品 build；
- 操作系统、版本、架构和 UTC 时间；
- 订阅档位、倍率或计费方式；
- 请求路由：官方订阅、官方 API、中转站或自部署；
- 模型和 effort 的启动配置；
- harness profile，以及规则、plugins、skills、MCP、hooks 和权限模式清单；
- CLI 启动界面或网页配置页。

一张截图能够证明多项信息时可以一图多用。不要为了三次重复而截三套相同环境图。

以 Codex CLI 为例，预检命令可以是：

```sh
command -v codex
codex --version
sw_vers
uname -m
date -u '+%Y-%m-%dT%H:%M:%SZ'
```

Windows 或其他 Agent 使用等价的原生命令。公开转录时把 home 路径改成 `~`，不要公开用户名、主机名、邮箱或账号 ID。

## 每次 attempt 要采什么

每次有效运行至少记录：

- 唯一 attempt 编号；
- fresh、warm 或 resumed 状态；
- 精确 prompt；
- 完整可见回复；
- 开始和完成时间，以及计时方法；
- 产品暴露的原生 usage 字段；
- 错误、超时、工具调用和人工批准；
- 如果要主张额度变化，本次 before/after 观察及其归因状态。

推荐的最小视觉证据是一张包含输入和完整回复的截图。usage 可以用退出界面截图、产品 usage 页面、provider receipt 或脱敏机器日志证明。产品拿不到某一项时标注，不要求伪造一个“完整”截图。

三次顺序运行的延迟数值只作描述性元数据记录，不支持跨产品的延迟比较结论：延迟受时段、负载与缓存影响。若要比较，需另行采用跨时间块随机交错的实验设计；本协议不承载该类结论。

## 标准执行流程

### 1. 固定场景

复制 [`templates/scenario-manifest.yaml`](templates/scenario-manifest.yaml)，先填写能够确定的场景变量和计划重复次数。固定 launch command；三个 attempt 不要临时改参数。

如果测试共享订阅百分比、团队额度或中转站余额，应先暂停会使用同一计量池的其他任务。无法暂停也可以测试，但额度归因必须标成 `contaminated`。

### 2. 在被测工作区之外准备证据目录

截图、转录和私有原图不要放进被测空目录。建议使用仓库外临时证据目录，全部运行结束并脱敏后再复制公开文件到 Git。

所有采集都必须是人工正常使用官方界面或客户端：不得拦截或解密流量、不得自动化操作消费者账户、不得逆向或修改客户端，也不得绕过速率或额度限制。方法与各产品条款的对照见 [docs/tos-review.zh-CN.md](docs/tos-review.zh-CN.md)。

### 3. 只做一次环境预检

执行版本、系统、架构和 UTC 时间命令，保存一张预检截图。另保存订阅、模型、effort 和启动界面证据。检查 hooks 是否会额外调用模型；如果会，它就是 harness 的一部分，不能隐去。

MCP 即使没有实际调用，也可能因为工具定义进入上下文而影响 input tokens，因此要记录启动状态。`AGENTS.md`、skills、plugins 和其他规则同理。

已经写好的采集适配器见[Codex CLI](docs/adapters/codex-cli.zh-CN.md)、[Claude Code](docs/adapters/claude-code.zh-CN.md)和[WorkBuddy Desktop](docs/adapters/workbuddy-desktop.zh-CN.md)。其他 Agent 同样欢迎：用该产品自己的等价命令，按上面的通用语义采集，并在 PR 中说明它暴露的字段与这几份适配器的差异。适配器只标准化采集动作，不要求贡献者为了测试关闭已有的代理、sandbox 或账号安全措施；这些设置属于场景，保持不变并如实记录即可。

### 4. 顺序执行至少三次

对 R1、R2、R3 依次执行：

1. 新建一个独立工作区；空目录场景要确认目录为空且不是 Git 仓库。
2. 启动一个新会话。fresh 场景不得先退出再 resume。
3. 在第一次模型请求前确认模型和 effort。产品本地的 `/status` 一类命令可以使用，但不要发送额外聊天消息。
4. 同时确认 footer、permission 或 execution mode 没有在三个 attempt 之间变化；发生变化就建立新场景或明确标成混杂。
5. 只发送一次精确 prompt。
6. 回复完成后，截图保存输入与完整回复。
7. 正常退出并保存原生 usage；能够取得时保留原始事件日志。
8. 本次结束后再开始下一次，不并行运行三个 attempt。

如果某次误输入、resume、改参数、目录不空、网络失败或发生了额外交互，把它保留并标为 `invalid` 或 `error`，说明原因，然后追加新 attempt，直到有至少 3 次有效运行。不要删除异常值，也不要只挑最省 token 的三次。

### 5. 生成公开场景包

所有运行结束后，复制模板并按[场景包目录](#场景包目录)整理。原始日志只提取与本场景有关的最小事件；保留时间、模型、effort、usage 和回复，移除账号、绝对路径、会话恢复标识和无关内容。

不要从空白文件猜测产品字段。请复制最接近的完整样板，再替换为自己的证据和数据：

- [Codex CLI 0.147.0 / GPT-5.6 Sol / high](runs/2026-08-14/codex-cli-0.147.0_gpt-5.6-sol_high_hi-en-v1_as-used_mac-arm64/README.md)
- [Claude Code 2.1.220 / Fable 5 / high](runs/2026-08-15/claude-code-2.1.220_claude-fable-5_high_hi-en-v1_as-used_mac-arm64/README.md)
- [Claude Code 2.1.220 / Opus 5 / high](runs/2026-08-15/claude-code-2.1.220_claude-opus-5_high_hi-en-v1_as-used_mac-arm64/README.md)
- [WorkBuddy 5.3.13 / Auto / craft](runs/2026-08-15/workbuddy-5.3.13_auto_craft_hi-en-v1_as-used_mac-arm64/README.md)

如果参照样板与当前产品版本不一致，记录差异，不要为了“看起来一致”而修改原生字段含义。

### 6. 生成哈希并校验

最终编辑和脱敏完成后，在场景目录生成 `SHA256SUMS`，再运行：

```sh
cd runs/YYYY-MM-DD/<scenario-id>
find . -type f ! -name SHA256SUMS -print0 \
  | LC_ALL=C sort -z \
  | xargs -0 shasum -a 256 > SHA256SUMS
cd -

./scripts/verify-run-package.sh runs/YYYY-MM-DD/<scenario-id>
python3 scripts/build-results-index.py
./scripts/verify-all.sh
```

Linux 没有 `shasum` 时可使用 `sha256sum`。任何公开文件变化后都要重新生成哈希。汇总页由全部场景的 manifest 与 `RESULTS.csv` 自动生成，一条命令同时产出英文 [RESULTS.md](RESULTS.md) 与中文 [RESULTS.zh-CN.md](RESULTS.zh-CN.md)；新增或修改场景后必须重建，Pull Request 会用 `verify-all.sh` 检查两者是否漂移。

## Token 与额度口径

不同产品的 `total` 可能不是同一件事。应优先保留原生字段和来源，再明确写出派生公式。

Codex CLI 0.147.0 的首个样板使用以下字段：

- `input_tokens_including_cached`：事件日志报告的全部 input，cached input 是其中的子集；
- `cached_input_tokens`：缓存命中的 input；
- `non_cached_input_tokens`：全部 input 减 cached input；
- `output_tokens`：事件日志报告的 output；
- `context_total_tokens`：全部 input 加 output；
- `cli_total_excluding_cached`：该版本退出界面的口径，即非缓存 input 加 output。

不要把 cached input 再加到 `input_tokens_including_cached` 上，否则会重复计算。也不要把 `cli_total_excluding_cached`、API 标价或订阅百分比中的任何一个称为“真实成本”，除非产品公开了精确换算关系。

Claude Code 2.1.220 的第二个样板使用 Anthropic 原生字段：

- `input_tokens`：原生普通输入桶；
- `cache_creation_input_tokens`：本次创建缓存的输入桶；
- `cache_read_input_tokens`：本次读取缓存的输入桶；
- `total_input_tokens`：以上三项相加的派生总输入；
- `output_tokens`：原生输出；
- `context_total_tokens`：派生总输入再加 output。

这三个 Anthropic 输入桶是相加关系，不能把 cache creation/read 当作 `input_tokens` 的子集。Anthropic 的公开 usage 说明也明确用三项之和计算总输入，参见 [Anthropic 官方定价与 usage 字段说明](https://docs.anthropic.com/en/docs/about-claude/pricing)。

因此跨 Agent 数据层采用“原生字段 + 明确派生公式”，不采用一个名为 `total` 的无来源通用字段。某产品不适用的厂商字段写 `not_applicable`，没有暴露的字段写 `not_exposed`。

额度、积分或余额还要记录：原始显示值、单位、重置周期、观察时间和共享范围。若同一账户、API project、团队或中转站余额还有其他活动，使用：

```yaml
quota:
  attribution: contaminated
```

污染的是共享额度差值，不一定污染当前 session 自己的机器 token 记录。

### 派生金额——仅在存在精确公开价格时

当路由为 `official-api` 时，应同时计算每次 attempt 的金额：把每个原生 usage 桶分别乘以厂商公布的对应单价——input、cache write、cache read、output 通常价格不同，绝不能用一个统一单价一把乘。在场景包中记录：价目页链接、查看日期、所用各桶单价、计算公式、币种和每次 attempt 的金额。金额只作为派生字段，与原生 token 字段并存、绝不取而代之：价格会变，留下快照才能让这个数字日后可复核。`third-party-gateway` 为可选：中转站若公开价目表，可按同样方式计算并标注“按中转站自报价目”——其可信度与中转站的其他声称同级。订阅、积分体系与 `self-hosted` 一律写 `not_applicable`；这正是上文“不自行换算”规则所保护的边界。

### 测量面与归因

既有 `usage.source` 字段记录测量面：`client-reported`、`provider-reported`、`billing-ledger` 或 `self-reported`。不同测量面的数值必须分别呈现，不得混成一个数字。

解释一项测量时，使用以下四档归因等级之一：

- `directly-observed`：直接观测到请求内容；
- `delta-attributed`：由开关某项条件产生的差值归因；
- `inferred`：归因来自推断，而非直接观测；
- `not-identifiable`：现有证据无法识别归因。

凡跨场景或跨测量面的结论，必须在包 README 或 PR 说明中声明所依赖的归因等级。这不改模板，也不新增必填字段。

哈希证明文件在生成哈希后未被改动，不证明测量解释正确；两者不可混同。

## 官方产品、API 和中转站

Agent 的发行方与推理路由是两个变量。官方 Agent 也可能配置成走第三方网关。

路由统一分为：

- `first-party-subscription`
- `first-party-product`：官方 Agent 产品自带账号或积分体系，而非按座席的模型订阅或裸 API key（例如 WorkBuddy）
- `official-api`
- `third-party-gateway`
- `self-hosted`

第三方网关还应披露公开名称、公开域名、兼容协议、所宣称上游模型、可观察到的模型、缓存、fallback 和路由设置。不要提交 endpoint 中的 secret、签名参数或凭据。中转站返回的模型名称只能证明它返回了这个标签，不能单独证明上游厂商。

## 场景包目录

一个场景包含共享环境与全部 attempts：

```text
runs/YYYY-MM-DD/<scenario-id>/
  README.md
  manifest.yaml
  prompt.txt
  launch-command.txt             # CLI 场景适用
  RESULTS.csv
  SHA256SUMS
  evidence/
    environment.png              # 场景级，只需一次
    subscription.png             # 适用且可取得时
    preflight.txt
    private-evidence.md           # 只登记私有原件哈希，不放原件
  attempts/
    r1/
      result.yaml
      response.txt                # 精确回复字节
      response.png
      events.sanitized.jsonl      # 可取得时
    r2/
      ...
    r3/
      ...
```

每个新提交的场景包，都在目录名与 manifest 的 `scenario.id` 末尾追加 `_<github-handle>`（例如 `..._mac-arm64_alice`）。这使包路径从构造上就不会冲突，同日同场景的多人复测无需任何协调。现有四个参考样板先于此规则，保持原名。

场景字段模板见 [`templates/scenario-manifest.yaml`](templates/scenario-manifest.yaml)，单次结果模板见 [`templates/attempt-result.yaml`](templates/attempt-result.yaml)，模板选择和可选字段说明见 [`templates/README.zh-CN.md`](templates/README.zh-CN.md)。六个完整实例统一列在 [`runs/README.zh-CN.md`](runs/README.zh-CN.md)。

## 隐私与脱敏

绝对不要提交：

- API key、access token、cookie、authorization header 或中转站凭据；
- 账号邮箱、账号 ID、支付信息；
- Codex Session ID、resume 命令或其他会话恢复标识；
- 本机用户名、主机名、完整 home 路径；
- 私有仓库内容、私人规则正文或无关聊天历史；
- 带 secret 或签名参数的 URL。

截图可裁剪，必要时使用完全不透明色块并展平。不要用可逆模糊。脱敏不能改变用量数字、事件顺序或关键时间。

视觉证据有两条合规路径：

1. **公开脱敏图：** 贡献者自己制作不透明遮挡副本，逐张目视检查；原图留在本机，PR 只提交脱敏副本、遮挡说明和原图／副本哈希。
2. **暂不公开视觉证据：** 原图继续留在贡献者本机，不上传到公开 Issue、PR、网盘或聊天附件。先提交非敏感数据并标 `not_provided`；只有维护者已经通过双方同意的私密渠道核对过原件，才可以改标 `private_evidence` 并登记哈希。

`private_evidence` 表示维护者确实看过原件，不等于“贡献者电脑上可能还有一张图”。如果没有既定私密渠道，不要临时把原图发送给陌生账号，也不要在公开 PR 中询问应该遮哪一块。

如果原图只能私下保留，可以在 `private-evidence.md` 登记 SHA-256 和未公开原因。这个哈希只提供后续核对锚点，不等于公开证明。

凭据一旦进入 Git 历史，下一次提交删除并不够；应立即轮换或吊销，并联系维护者清理历史。

如果你在**已经公开**的证据里发现这类内容——无论是你自己的还是别人的——请按 [SECURITY.zh-CN.md](SECURITY.zh-CN.md) 的流程私下报告。不要开公开 issue，也不要在任何公开位置复述被暴露的值。自己报告自己的失误不会被追究；第一天修掉的泄露，远好过一年后才被发现的泄露。

## 贡献的许可

提交 Pull Request 即表示你同意：你提交的测量数据与文字按 [CC BY 4.0](LICENSE-DATA) 发布；你提交的**截图不进入 CC BY 授权范围**，仅作为事实性研究报告发布。软件贡献（`scripts/`、`.github/workflows/`）按 [Apache License 2.0](LICENSE) 发布。你保留自己贡献部分的著作权，不需要签署 CLA。

只提交你有权公开的证据。第三方产品界面的截图作为事实性研究记录出现在这里；私有仓库、内部工具或他人账号的截图不属于此列——请裁剪或重新截取。如果你所在单位限制公开与工作中所用产品有关的材料，请在提交之前解决，而不是提交之后。

## 提交 Pull Request

一个 PR 只放一个场景和它的全部重复运行。PR 中说明：

- 场景一句话摘要；
- 有效、无效和错误 attempts 数量；
- 证据等级与缺失字段；
- 任何协议偏差；
- 校验脚本输出；
- 为什么共享额度可归因，或为什么被标为 contaminated。

仓库的 [Pull Request 模板](.github/pull_request_template.md)已经包含这些字段和提交前检查项。建议先开 Draft PR，等自动验证通过并完成截图目视检查后再标记 Ready for review。自动验证只能检查结构、算术、哈希和文本隐私线索，不能证明截图遮挡正确，也不能替代人工核对。

审核重点是内部一致性、字段状态、脱敏和是否避免过度结论，不是要求每个产品都暴露完全相同的数据。

每个数据 PR 都会收到**至少两份独立评审**，人工或 AI 协助；AI 协助的评审会署明所用的 agent 产品、模型与 effort。评审以结构化评论的形式发在 PR 下，流程与意见模板见 [docs/review-process.zh-CN.md](docs/review-process.zh-CN.md)。两份意见相左时追加第三份。合并、分值发放与最终把关由维护者负责，目标响应时间约 3 个工作日。

提交前检查：

- [ ] 相同场景至少有 3 次有效独立运行；
- [ ] 三次使用同一 prompt、模型、effort、版本、路由和 harness；
- [ ] 环境证据没有无意义地重复三套；
- [ ] 每次 prompt、完整回复和原生 usage 已尽量保存；
- [ ] cached input 没有被重复相加；
- [ ] 共享额度污染已标注；
- [ ] 缺失或冲突字段已使用固定状态；
- [ ] 公开文件没有凭据、邮箱、绝对 home 路径或会话恢复标识；
- [ ] `SHA256SUMS` 是最后生成的；
- [ ] 已重建根级索引（`RESULTS.md` 与 `RESULTS.zh-CN.md`）；
- [ ] `verify-all.sh` 通过。

重复测试非常欢迎。不同贡献者、不同设备、不同订阅和不同时间的独立复测，正是这个项目逐渐变得有价值的方式。
