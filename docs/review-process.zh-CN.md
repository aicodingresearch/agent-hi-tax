# PR 评审流程

[English](review-process.md) | **中文**

> 自动校验判断一个包是否规范，评审判断它是否诚实。

本页说明一个数据 Pull Request 开出来之后会发生什么：谁来读、被要求看哪些东西、意见不一致怎么办、一份评审意见必须写清哪些内容。采集和提交证据的规则仍以[贡献指南](../CONTRIBUTING.zh-CN.md)为准，本页只讲评审。

只给一个 PR URL 即可路由评审与合并后积分提交的 Agent 工作流，见 [Agent 评审与计分入口](agent-review-and-scoring.zh-CN.md)。

## 评审覆盖什么

每个 PR 都会先跑自动校验。`./scripts/verify-all.sh` 检查场景包结构、派生字段的算术、`SHA256SUMS`、文本中的隐私线索，以及生成的索引是否仍与数据一致——见[贡献指南「提交 Pull Request」一节](../CONTRIBUTING.zh-CN.md#提交-pull-request)。评审不重复这部分工作，绿色的检查标记也不构成对这份提交的任何意见。

评审存在的意义，是脚本做不到的四件事：

1. **脱敏。** 每一张已发布图片都要按原尺寸逐张打开目检。不得残留账号邮箱、账号 ID、Session 或 resume 标识、用户名、主机名、完整 home 路径；遮挡必须是完全不透明的，不能是模糊处理。看文件名或缩略图不算数。
2. **证据交叉一致。** 截图、`RESULTS.csv`、`manifest.yaml` 与脱敏后的事件记录，数值与时序必须互相吻合。usage 分桶、时间戳、attempt 数量、模型和 effort，在出现的每个地方都应当讲同一个故事。
3. **协议符合度。** 有效 attempts 之间的场景身份保持一致；[字段级状态](../CONTRIBUTING.zh-CN.md#字段级状态)——`not_exposed`、`not_provided`、`self_reported`、`conflicted` 等——是被诚实使用的，而不是用来把包装得"完整"；deviations 与混杂因素如实登记，而不是悄悄略去；目录名与 `scenario.id` 遵守 [GitHub handle 后缀规则](../CONTRIBUTING.zh-CN.md#场景包目录)。
4. **结论克制。** 包内 README 和 PR 正文都停留在证据能支撑的范围内。一个场景是对一套执行栈的一次观察，不是关于某个模型、某家厂商或某个价格的结论。

## 三级评审

| 级别 | 适用 | 配置与判定 |
| --- | --- | --- |
| **L1——默认** | 普通数据 PR | 至少 2 份独立评审（人工，或由人主导、AI 协助），外加维护者终审。两份 APPROVE：维护者合并并发放分值。任一 REQUEST_CHANGES：贡献者修改后由评审复看。 |
| **L2——升级** | 两份 Verdict 相左；★★★ 新产品的首个样本，没有可对照的参照样板；任何带 `private_evidence` 升级的包 | 追加第三份评审，来自与前两份不同的模型家族或不同的人。三取二形成判定，由维护者执行。 |
| **L3——维护者独占** | 协议文件改动（`prompts/`、`templates/`、`scripts/`，以及 [CODEOWNERS](../.github/CODEOWNERS) 中另行列出的路径）；计分争议；疑似不诚实；安全事件 | 不走多数决。维护者裁定，并按既有元规则把决定回写到相应清单上——定价与归一化的判断记录在它们发生的地方。 |

## 判定细则

- **"意见相左"指 Verdict 行不同。** 两份都是 REQUEST_CHANGES、但提出的问题完全不同，不算相左——那是两张清单，贡献者应当把两张都修掉。
- **每份评审都要写明所针对的 head commit。** force-push 或追加提交之后，受影响的评审针对新的 head 重做；针对旧树写下的判定不自动延续。
- **draft PR 不评审。** 评审从贡献者把 PR 转为 Ready for review 那一刻开始；明确要求评审一个 draft 也不改变这一点——针对移动中的 head 写下的判定注定要重做，而[贡献指南](../CONTRIBUTING.zh-CN.md#提交-pull-request)把自动核验和逐张复看截图放在这次状态切换之前，而不是之后。看 draft 并留下普通评论当然欢迎：那是评审前的沟通，不是 verdict，不计入任何门禁。
- **复审采用追加评论，不改写 verdict 历史。** 贡献者针对 verdict 推送 commit 或更新 PR 描述后，旧 verdict comment 保持不变；评审者在贡献者更新之后另发一条新的结构化 verdict，即使 head SHA 没有变化也一样。新评论在 `Supersedes` 中链接旧评论，说明复核了什么，并披露已经读过前序讨论。门禁以这条新评论作为该 reviewer 的当前 verdict，但它仍是同一份评审，不得重复计入 L1 独立评审数。旧 verdict 只允许修正不改变结论或 findings 的错字、链接或格式；维护者明确要求修正历史记录时，必须保留编辑说明。
- **目标响应时间约为 3 个工作日**，与 [SECURITY.md](../SECURITY.zh-CN.md) 里的响应窗口一致。

## 评审的独立性

两份评审并行派发，各自独立形成结论后再发布。不读 PR 评论区已有的评审意见，是[意见模板](#意见模板)中的一条硬要求，而不是礼节：看过他人意见之后写下的评审必须披露这一点，并且不计入两份独立评审的下限。明确要求由同一 reviewer 复审时，可以读取该 reviewer 自己的旧 verdict 与贡献者后续回复，因为这一步是在核验修订，不是在新增一份独立评审；follow-up 必须披露这一边界。

AI 协助的评审必须来自**不同的模型家族**。同一家族的两份评审算作一份，第二份不满足 L1 的下限。

## 意见模板

评审以结构化评论的形式发在 PR 下，骨架如下：

```text
Reviewed under: docs/review-process.md @ <template commit>

## Review verdict: APPROVE | REQUEST_CHANGES | PRIVACY-CONCERN-RAISED-PRIVATELY

Reviewed at head: <commit SHA>
Reviewer: <human name, or agent product + model + reasoning effort>
Date: <YYYY-MM-DD>
Supersedes (re-review only): <prior verdict comment URL>

| Dimension | Result |
| --- | --- |
| Redaction (published images eyeballed one by one) | pass / issues |
| Cross-evidence consistency (image ↔ CSV ↔ manifest ↔ events) | pass / issues |
| Protocol conformance (identity, field states, deviations) | pass / issues |
| Restraint of claims | pass / issues |

Blocking findings: <逐条写成 file:line；没有就写 "none">
Non-blocking suggestions: <可以为空>
Could not verify: <必填，见下>
Advisory (optional): <任务与分值判定建议，仅供维护者参考>
```

`<template commit>` 取本页最后一次改动的短哈希，在该 PR 的 base 分支上执行：

```sh
git log -1 --format=%h -- docs/review-process.md
```

有五条要求不是可选项：

- **评审评论的第一行必须声明所依据的评审模板版本**，以上述 commit 标识为准。本页后续改版不追溯已发布的评审：每份评审按它声明的版本裁定，除非维护者明确要求按新版复审。
- **发布自己的评审之前，不得阅读该 PR 评论区已有的任何评审意见，必须独立得出结论。** 评审基于 PR 的 diff 和文件本身进行，不打开 PR 会话页。如果你确实看到了他人的意见，必须在评论中披露：这份评审不计入两份独立评审的下限，只作参考。
- **复审必须另发新评论，并写明它 supersede 哪条旧 verdict。** 贡献者已经依据旧 verdict 行动后，不得把旧评论原地改成另一种结论。旧评论保留为贡献者回复的可见原因，新评论作为该 reviewer 的当前 verdict。
- **AI 协助的评审必须署明 agent 产品、具体模型和 reasoning effort。** 产品没有暴露模型或 effort 时写 `not exposed`，不要臆测。这与本仓对证据字段的诚实规则是同一条口径：拿不到的值就记为拿不到，绝不推断。
- **"Could not verify" 是必填栏。** 写清你这份评审实际能确立的边界。它至少包含只有贡献者才能核验的那一类主张——例如已发布图片与其脱敏所依据的私有原图之间的对应关系，或者提交之前是否还有被丢弃的 attempts。一份默默略过自身局限的评审是在夸大自己，而这正是本项目要求贡献者避免的那种失误。

## 隐私例外

如果你怀疑某个**已发布**文件泄漏了凭据、邮箱、Session 或 resume 标识、私有路径或私有内容，不要在 PR 里描述细节。不要复述该值，不要指出它在图上的位置，也不要开公开 issue。

只发一行：

```text
Privacy concern raised through the private channel.
```

Verdict 使用 `PRIVACY-CONCERN-RAISED-PRIVATELY`，细节按 [SECURITY.md](../SECURITY.zh-CN.md) 的私密渠道流程报告。评审的其余部分可以照常公开。公开描述泄漏所在的位置，本身就是一次披露；无论出错的是贡献者、另一位评审还是维护者，这一条都成立。

## 评审不裁定什么

评审是输入，不是裁决。合并、分值发放与登记、递减桶的归一化、台账更新，以及把 `private_evidence` 原图与其登记的哈希核对，都由维护者执行。评审可以在 Advisory 一行里给出分值意见，但它本身不具备效力。

AI 协助的评审只发结构化评论，不使用 GitHub 的正式 **Approve** 或 **Request changes** 按钮——那两个按钮记录的是一个具名的人对判断负责，而 agent 不是这样的主体。
