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

提示词不需要复制规则正文，不需要给绝对本地路径，也不能包含 token、邮箱或其他凭据。Agent 必须从 URL 和仓库状态自行解析 owner、仓库、PR 编号、head SHA、base SHA、贡献者、任务或认领、检查状态和变更文件。

该约定假设 Agent 能够：

- 读取 PR、Git 仓库、GitHub API，以及关联的 claim 或 proposal；
- checkout 或以其他方式检查精确的 PR head；
- 按原尺寸打开每一张公开图片；
- 运行仓库校验命令；
- 评审时发布 issue-style PR comment；
- 计分时创建分支、commit、push 并创建 PR。

缺少必要能力或权限时，Agent 必须报告准确边界并停止；不得推断未检查的证据，也不得声称已经发布实际未发布的 comment、commit 或 PR。

## 动作一：评审 PR

Agent 按以下顺序执行：

1. 解析 PR URL，记录当前 head SHA、base SHA、作者、变更文件、draft 状态、CI checks 和可合并状态。评审对象是精确 head，不是会移动的分支名。
2. 在读取任何已有 review 或 PR 会话评论之前，从 PR 的 base 分支读取：`CONTRIBUTING.zh-CN.md`、`docs/review-process.zh-CN.md`、`.github/CODEOWNERS`、`docs/wanted-scenarios.zh-CN.md` 中的适用任务，以及关联 claim 或 proposal。读取 PR 正文、diff 和提交文件，但在本评审发布前不得打开其他评审者的 findings。
3. 在 PR head 运行 `./scripts/verify-all.sh`。绿色检查只构成结构证据，绝不替代评审。
4. 按原尺寸逐张打开全部公开图片。先检查脱敏，再交叉核对图片、`RESULTS.csv`、`manifest.yaml`、attempt result、events 或 usage 记录、哈希、包 README 与 PR 声称。
5. 按 L1/L2/L3 规则独立形成 verdict。AI 协助评审必须写出 Agent 产品、准确模型和 reasoning effort；没有暴露的值写 `not exposed`，不得猜测。
6. 在 `Advisory` 中给出积分建议：注明任务、候选分值、叠加或不叠加判断，以及证据边界。它只是建议，最终发分和登记由维护者裁定。
7. 使用 `docs/review-process.zh-CN.md` 的结构化模板发布 verdict comment。AI 评审只发 comment，绝不使用 GitHub 的正式 **Approve** 或 **Request changes**。
8. 发布之后，Agent 才可以读取其他 verdict comment，并汇报总门禁：独立评审数量、CODEOWNER 正式批准、CI、threads 解决状态和 merge state。PR head 变化后必须重新评审。

若疑似出现敏感信息泄露，遵守 `docs/review-process.zh-CN.md` 的隐私例外：不得在公开位置复述该值或指出位置，细节通过私密渠道报告。

### 评审完成输出

Agent 汇报：

- 被评审的 head SHA 与模板 commit；
- verdict 与评审 comment URL；
- 校验结果和证据边界；
- 积分建议；
- 尚未满足的项目流程与 GitHub 机械门禁。

## 动作二：计算并提交积分

该动作只在目标 PR 已合并后开始。只有批准或仍处于 open 状态都不够。

1. 解析已合并 PR URL，记录合并时间、merge commit、贡献者、场景身份、任务或认领、route、证据等级和交付文件。
2. 读取 PR 合并时版本的 `docs/wanted-scenarios.zh-CN.md` 中的积分规则和台账。读取 claim 或 proposal 及评审 Advisory，但重新计算分值；评审建议只是输入，不是裁决。
3. 匹配所有可能适用的任务和计价桶。执行递减、pair 完成条件、proposal 定价、adapter 与 probe 加分，以及已有叠加规则。不得默默叠加两个普通任务分值。确有歧义时，只向维护者询问一个明确裁决，并把裁决写入台账备注。
4. 核实是否遗漏了本可取得的证据。诚实使用 `self_reported`、`not_exposed` 或标注 confounded 本身不扣分；能够提供却主动省略的证据按积分规则推迟发分。
5. 在 `docs/wanted-scenarios.md` 和 `docs/wanted-scenarios.zh-CN.md` 各追加一行。记录日期、贡献者、任务、已合并 PR、分值、必要时关联 claim 或 proposal，并用足够的备注保存归一化与不叠加裁决。历史台账行绝不修改；更正通过追加冲销行完成。
6. 从最新 `main` 创建工作分支，运行 `./scripts/verify-all.sh` 和 `git diff --check`，只提交台账文件，push 分支并创建 PR。绝不直接 push `main`，也不得使用 admin bypass 跳过 PR、CI 或评审门禁。
7. 汇报台账 commit 与 PR URL。该 PR 正常合并后，再确认中英文台账行已进入 `main`，并确认工作区没有本任务产生的未提交文件。

### 计分完成输出

Agent 汇报：

- 发放的任务与积分，以及叠加或递减依据；
- 已合并的源 PR 与贡献者；
- 中英文台账准确行；
- 校验结果；
- 台账 commit 与 PR URL；
- 尚待维护者裁决的事项。

## 边界

- 一个 PR URL 足以定位目标，但不构成修改无关设置、权限、secret、分支、Issue 或其他 PR 的授权。
- 评审与计分是两个独立动作。评审 Advisory 不会自动更新台账；源 PR 已合并也不等于已经发分，中英文台账更新合并后才完成登记。
- GitHub 正式批准、最终合并、积分裁定和私有证据核对由维护者完成。Agent 只通过评审 comment 与正常 PR 提供输入和仓库变更。
