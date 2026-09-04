# Agent 评审与计分入口

[English](agent-review-and-scoring.md) | **中文**

> 目标：给一个具备相应能力的 Agent 一项动作和一个 Agent Hi Tax Pull Request URL，它就能自行发现仓库规则，完成独立评审；或在 PR 合并后计算积分并提交台账更新，不再需要提供本地路径或复制整段操作说明。

本页是路由入口，不替代详细规则。[贡献指南](../CONTRIBUTING.zh-CN.md)、PR base 分支上的[评审流程](review-process.zh-CN.md)和适用版本的[任务与积分页](wanted-scenarios.zh-CN.md)仍是权威口径。

## 最小输入约定

唯一可变输入是本仓库的一个 PR URL，再配一个动作：

```text
按仓库的 Agent 评审入口评审 <PR URL>，并发布 verdict comment。
```

或者，在 PR 合并之后：

```text
按仓库的 Agent 计分入口为 <已合并 PR URL> 计算积分并提交台账更新。
```

如果用户只提供 URL，不附动作，则按权威 PR 状态自动路由：

- open 且非 draft 的 PR 进入评审动作；
- merged PR 进入计分动作；
- draft PR 或 closed 但未合并的 PR 只报告“尚不适用”，Agent 停止，不发布 comment，也不修改仓库。

### draft PR 一律不评审

评审资格取决于 PR 本身的状态，而不是评审是被怎样发起的。**draft PR 在任何调用方式下都不具备评审资格**——只给 URL 的自动路由、下文的建议评审输入，或人类明确点名该 PR 的指令，都一样。Agent 报告 draft 状态，写明唯一的解除条件（由贡献者把 PR 转为 Ready for review），然后停止：不发布 comment，不修改仓库。在 draft 上发布 verdict、再在评论里声明“这是 draft”并不是可接受的替代做法——那条路仍然把一份 verdict 留在了记录上，事后还要靠人工把它从门禁里剔除。

这不是新增限制，而是两条既有规则的推论。[每份评审都要写明所针对的 head commit 和实际覆盖的场景内容](review-process.zh-CN.md#判定细则)；只有自动化证明所有已提交场景包的目录树完全不变时，APPROVE 才能跨 head 沿用，而 draft 尚未到达这个稳定边界。[贡献指南](../CONTRIBUTING.zh-CN.md#提交-pull-request)还要求贡献者在自动核验通过、且逐张复看过截图之后才转 Ready for review——早于该时点评审，等于把评审精力花在贡献者本人尚未交付的检查上。

维护者当然可以看 draft 并留言。那属于评审前的沟通：只发普通评论，不发结构化 verdict comment，也不计入任何评审门禁。

这里有两类不同的 URL。**目标 PR URL** 标识要处理的对象，足以自动路由；**本 runbook URL** 只标识操作规则，不标识目标。如果用户只给了 runbook URL，且上下文不能唯一确定一个 PR，Agent 必须询问目标 PR URL，不得猜测。

### 建议的评审输入

只给 URL 仍然有效，但建议在评审 prompt 中同时登记 reviewer 的实际运行配置：

```text
动作：独立评审并发布 verdict comment
目标 PR：https://github.com/aicodingresearch/agent-hi-tax/pull/<编号>
评审 Agent：<产品，例如 Claude Code 或 Codex>
评审模型：<准确模型，例如 claude-opus-5 或 gpt-5.6-sol>
Reasoning effort：<准确 effort，例如 xhigh>
Independence key：agent:<model-family>

按本仓库的 Agent 评审与计分入口执行。评审当前精确 head；在发布本次
独立 verdict 前，不得读取已有评审评论或其他 reviewer findings。只发布
comment，不使用 GitHub 的正式 Approve 或 Request changes。
```

Agent 产品、模型、effort 和 Independence key 必须描述真实运行环境。把它们写进 prompt 不会切换或配置运行时。用户填写的身份与产品实际暴露值冲突时，Agent 必须报告不一致并使用观察值；拿不到时写 `not exposed`，不得照抄或猜测。

合并后计分建议使用：

```text
动作：计算积分并提交中英文台账更新
目标 PR：https://github.com/aicodingresearch/agent-hi-tax/pull/<已合并编号>

按本仓库的 Agent 评审与计分入口执行。重新计算资格与分值，先检查已有
台账行或待合并台账 PR；outcome 不是 RECORDED 时不得修改仓库。
```

提示词不需要复制规则正文，不需要给绝对本地路径，也不能包含 token、邮箱或其他凭据。Agent 必须从 URL 和仓库状态自行解析 owner、仓库、PR 编号、head SHA、base SHA、贡献者、任务或认领、检查状态和变更文件。

该约定假设 Agent 能够：

- 读取 PR、Git 仓库、GitHub API，以及关联的 claim 或 proposal；
- checkout 或以其他方式检查精确的 PR head；
- 按原尺寸打开每一张公开图片；
- 运行仓库校验命令；
- 评审时发布 issue-style PR comment；
- 计分时创建分支、commit、push 并创建 PR。

缺少必要能力或权限时，Agent 必须报告准确边界并停止；不得推断未检查的证据，也不得声称已经发布实际未发布的 comment、commit 或 PR。

## PR 类型分诊

执行任一动作前，先按交付行为分型，不按作者身份分型：

- **场景数据 PR**：新增或修改 `runs/` 下的场景包及其生成索引。使用数据评审维度和 L1/L2 流程；合并后可能符合计分条件。
- **协议、治理、软件或文档 PR**：修改规则、prompts、templates、scripts、workflows、安全策略、流程文档或普通文档，但不交付场景。权威评审流程要求时走 L3，否则走维护者主导的代码/文档评审；通常不获得场景积分。
- **积分台账 PR**：主要为一个已经合并的源 PR 新增或更正积分台账。由维护者评审台账操作本身；台账 PR 绝不因“登记积分”而再次获得积分。
- **混合 PR**：同时交付以上多类内容。普通组合应合并所有适用评审维度并采用风险最高的决策路径；如果场景提交同时修改受保护协议路径，则不按混合 PR 直接评审，必须先把协议修改拆成单独 PR。

场景数据 PR 的 L1 要求两份独立结构化评审，L2 按规则升级。L3 和维护者主导的非数据评审不会仅因它是 open PR 就自动获得“两份评审多数制”要求。所有类型仍分别受 GitHub 正式批准、CI 和 thread resolution 机械门禁约束。

## 动作一：评审 PR

Agent 按以下顺序执行：

1. 解析 PR URL，记录当前 head SHA、base SHA、作者、变更文件、draft 状态、CI checks 和可合并状态。评审对象是精确 head，不是会移动的分支名。
2. 初次独立评审时，在读取任何已有 review 或 PR 会话评论之前，从 PR 的 base 分支读取：`CONTRIBUTING.zh-CN.md`、`docs/review-process.zh-CN.md`、`.github/CODEOWNERS`、`docs/wanted-scenarios.zh-CN.md` 中的适用任务，以及关联 claim 或 proposal。读取 PR 正文、diff 和提交文件，但在本评审发布前不得打开其他评审者的 findings。明确要求由同一 reviewer 复审时，先解析当前 PR 状态，再读取该 reviewer 的旧 verdict 和核验修订所需的贡献者回复；必须披露这一点，且不得声称新增了一份独立评审。
3. 按 [PR 类型分诊](#pr-类型分诊)分类，再选择评审维度：
   - 场景数据：脱敏、证据交叉一致、协议符合度、结论克制；
   - 协议/软件/文档：行为正确性、与权威规则的冲突、中英文和链接一致性、可执行性与安全边界；
   - 积分台账：源 PR 资格、重新计算的分值与不叠加依据、中英文 append-only 一致性和防重复、校验结果；
   - 允许的混合 PR：合并全部适用维度，并明确写出决策级别；如果把场景数据与受保护协议路径混在一起，则停止并要求拆成两个 PR，不发布 verdict。
4. 在 PR head 运行 `./scripts/verify-packages.sh`（若该 PR 改动了生成的索引，则运行 `./scripts/verify-all.sh`），再运行变更文件需要的专项检查。绿色检查只构成结构证据，绝不替代评审。
5. 对发布证据的场景数据或允许的混合 PR，按原尺寸逐张打开全部公开图片，再交叉核对图片、`RESULTS.csv`、`manifest.yaml`、attempt result、events 或 usage 记录、哈希、包 README 与 PR 声称。不得把数据包检查表强套在没有发布场景证据的 PR 上。
6. 按适用级别独立形成 verdict。AI 协助评审必须写出 Agent 产品、准确模型和 reasoning effort；没有暴露的值写 `not exposed`，不得猜测。
7. 对符合条件的场景数据交付，在 `Advisory` 中给出任务、候选分值、叠加或不叠加判断及证据边界。仅协议、文档、软件或台账的 PR 写 `points: not_applicable`，除非已有明确计价任务。
8. 发布适用的结构化 verdict comment。场景数据评审使用 `docs/review-process.zh-CN.md` 模板。非数据评审保留版本、verdict、head、reviewer、日期、findings、verification、`Could not verify` 和 Advisory 字段，但使用上述对应维度，不得在数据证据表里伪造 `n/a` 行。AI 评审只发 comment，绝不使用 GitHub 的正式 **Approve** 或 **Request changes**。
9. 贡献者更新后的复审必须保留旧 verdict comment，并在更新之后另发新的结构化 follow-up；绝不通过编辑旧评论来改变其 verdict 或 findings。新评论在 `Supersedes` 中链接旧 verdict，写明本次复核的状态（包括 head 不变、只更新 PR 描述的情况），并披露已经读过前序讨论。它仍属于同一个 reviewer，不得重复计入 L1 独立评审数。
10. 发布之后，Agent 才可以读取其他 verdict comment，并按当前 PR 类型汇报总门禁：所需独立评审、CODEOWNER 正式批准、CI、threads 解决状态和 merge state。单纯 head 变化不再要求复审：只有自动化证明所有已提交场景包目录树不变时才沿用 APPROVE；场景包内容变化时，原 Reviewer 仍须发布新 verdict。汇总时，每个 reviewer 对被评审状态只采用最新且有效的 superseding verdict，旧评论继续保留为历史。

若疑似出现敏感信息泄露，遵守 `docs/review-process.zh-CN.md` 的隐私例外：不得在公开位置复述该值或指出位置，细节通过私密渠道报告。

### 评审完成输出

Agent 汇报：

- 被评审的 head SHA 与模板 commit；
- verdict 与评审 comment URL；
- 校验结果和证据边界；
- 积分建议或 `not_applicable`；
- 尚未满足的项目流程与 GitHub 机械门禁。

## 动作二：计算并提交积分

该动作只在目标 PR 已合并后开始。只有批准或仍处于 open 状态都不够。

1. 解析已合并 PR URL，记录合并时间、merge commit、贡献者、交付文件和 PR 类型。
2. 在计算或写入之前先做幂等检查：
   - 在当前中英文台账中搜索准确的源 PR；
   - 在 open 的台账更新 PR 中搜索是否已有该源 PR 的待合并记录；
   - 两份台账已有匹配行时返回 `ALREADY_RECORDED` 并停止；
   - 已有对应台账 PR 时返回 `ALREADY_PENDING` 和其 URL 并停止；
   - 中英文台账不一致时返回 `LEDGER_INCONSISTENT`，请求维护者裁决，不再追加普通行。
3. 执行资格出口。积分台账 PR 返回 `NOT_APPLICABLE`，防止工作流给自己计分。没有明确计价场景交付的协议、治理、软件或文档 PR 也返回 `NOT_APPLICABLE`。制度前明确排除的参考样板继续不计分；作者身份本身不是排除条件。
4. 对符合条件的场景或混合交付，记录场景身份、任务或认领、route、证据等级和交付文件。读取源 PR 合并时版本的 `docs/wanted-scenarios.zh-CN.md` 中的积分规则和台账。读取 claim 或 proposal 及评审 Advisory，但重新计算分值；评审建议只是输入，不是裁决。
5. 匹配所有可能适用的任务和计价桶。执行递减、pair 完成条件、proposal 定价、adapter 与 probe 加分，以及已有叠加规则。不得默默叠加两个普通任务分值。`docs/wanted-scenarios.md` 的首次贡献保底放在最后执行，在其余全部调整之后取下限。确有歧义时返回 `NEEDS_MAINTAINER_DECISION`，只问维护者一个具体问题；未得到答复前不创建台账变更。
6. 核实是否遗漏了本可取得的证据。诚实使用 `self_reported`、`not_exposed` 或标注 confounded 本身不扣分。能够提供却主动省略证据时返回 `AWARD_DEFERRED`，写清需要补什么，暂不追加台账行。唯一的例外是首次贡献保底：贡献者的首个已合并场景包一律按不低于 1 分登记，本条核查不对它暂缓——把遗漏写进台账备注即可。
7. 只有前述检查得到“符合条件且尚未登记”的分值后，才在 `docs/wanted-scenarios.md` 和 `docs/wanted-scenarios.zh-CN.md` 各追加一行。记录日期、贡献者、任务、已合并 PR、分值、必要时关联 claim 或 proposal，并用足够的备注保存归一化与不叠加裁决。历史台账行绝不修改；更正通过追加冲销行完成。
8. 从最新 `main` 创建工作分支，运行 `./scripts/verify-packages.sh` 和 `git diff --check`，只提交台账文件，push 分支并创建 PR。绝不直接 push `main`，也不得使用 admin bypass 跳过 PR、CI 或评审门禁。
9. 汇报台账 commit 与 PR URL。该 PR 正常合并后，再确认中英文台账行已进入 `main`，并确认工作区没有本任务产生的未提交文件。

### 计分完成输出

Agent 汇报：

- outcome：`RECORDED`、`ALREADY_RECORDED`、`ALREADY_PENDING`、`NOT_APPLICABLE`、`AWARD_DEFERRED`、`NEEDS_MAINTAINER_DECISION` 或 `LEDGER_INCONSISTENT`；
- 发放的任务与积分，以及叠加或递减依据；
- 已合并的源 PR 与贡献者；
- 中英文台账准确行；
- 校验结果；
- 台账 commit 与 PR URL；
- 尚待维护者裁决的事项。

outcome 不是 `RECORDED` 时，省略不适用字段，不创建 commit 或 PR。

## 契约验收用例

本 runbook 合并后，不在 prompt 中重复操作说明，用以下测试验证最小输入契约：

1. 只给一个 open 场景数据 PR URL。Agent 必须正确分为数据 PR、保持评审独立、使用数据维度，并发布一份带正确版本的 verdict。
2. 只给一个 open 协议/文档或台账 PR URL。Agent 必须使用非数据维度，不套数据证据表，不声称自动适用 L1 两份评审，并把积分标为 `not_applicable`。
3. 给一个已发布 REQUEST_CHANGES verdict 的 PR，再让贡献者推送新 head，或只更新 PR 描述。同一 reviewer 必须保留旧 verdict 不变，并在贡献者更新之后另发一条 superseding verdict；门禁只能把该 reviewer 计数一次。
4. 给一个 draft PR URL，先只给 URL，再附上明确要求评审并发布 verdict 的指令。两次 Agent 都必须报告 draft 状态并停止，不得发布任何 comment；明确指令不得解锁一份“带免责声明的 verdict”。
5. 只给一个尚无台账行、也无待合并台账 PR 的合格 merged 场景 PR URL。Agent 必须只计算一次，并只创建一个中英文台账更新 PR。
6. 在台账 PR open 时和合并后，再次给同一个 merged 场景 PR URL。outcome 必须分别是 `ALREADY_PENDING` 和 `ALREADY_RECORDED`，不得产生重复行或重复 PR。
7. 只给一个 merged 积分台账 PR 或无计价文档 PR URL。outcome 必须是 `NOT_APPLICABLE`，不得修改仓库。

引入本页时使用的 bootstrap prompt 不能证明“只给 URL”契约已经通过；只有合并后的上述测试才算验收。

## 边界

- 一个 PR URL 足以定位目标，但不构成修改无关设置、权限、secret、分支、Issue 或其他 PR 的授权。
- 评审与计分是两个独立动作。评审 Advisory 不会自动更新台账；源 PR 已合并也不等于已经发分，中英文台账更新合并后才完成登记。
- 台账 PR 只登记另一个 PR 的分值，绝不是新的计分目标；每次写入前必须先做幂等检查。
- GitHub 正式批准、最终合并、积分裁定和私有证据核对由维护者完成。Agent 只通过评审 comment 与正常 PR 提供输入和仓库变更。
