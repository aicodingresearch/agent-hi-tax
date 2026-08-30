# 相关工作

[English](related-work.md) | **中文**

## hibench

[hibench](https://hibench.dev) 是一个测量 coding agent 默认上下文 footprint 的开源基准。它让每个 Agent 从 fresh 空 Git 仓库启动，使用 dummy key 指向本地 recorder、因而不调用上游模型，发送 `Hi`，截获首个出站请求，并统一用 `o200k_base` 对所有字段计数。其当前公开数据集覆盖 16 个 Agent、1,132 个版本，每个 release 保留一个 canonical capture。

hibench 用 dummy key、在不调用上游的条件下测量被截获的默认请求 footprint；Agent Hi Tax 测量的是真实产品在真实账户下实际计量、报告与收费的量，并对账这些测量面。

两个项目彼此互补。Agent Hi Tax 覆盖 hibench 有意不测的维度：真实账户与订阅、credits 与账单台账、observed 路由、订阅档位差异，以及尚未进入 hibench 名单的中国生态或新形态产品线。

## 有负载评测

[Claw-SWE-Bench](https://arxiv.org/abs/2606.12344) 及其[开源参考实现](https://github.com/opensquilla/claw-swe-bench)，在统一条件和真实编码负载下评测 Agent harness 的能力与成本。Agent Hi Tax 观察的是与之正交的最小交互、空载侧：产品在实质任务开始之前消耗了什么。

## 学术语境

更广泛的研究现在已经把 harness 视为隐藏变量。[The Scaffold Effect in Coding Agents](https://arxiv.org/abs/2607.22585) 报告了同一模型跨 harness 的每成功任务 token 差异可达 40 倍。[Prompt-Induced Waste](https://arxiv.org/abs/2608.01347) 研究 prompt 表述与 harness 设计如何改变端到端推理成本，[A²E](https://arxiv.org/abs/2608.07346) 则提供了面向 harness 能力与执行轨迹的端到端审计引擎。在请求边界上，[Systima 于 2026 年 7 月所做的 Claude Code 与 OpenCode 对比](https://systima.ai/blog/claude-code-vs-opencode-token-overhead)，测得空环境初始上下文约为 33K 与 7K tokens。

“harness 是隐藏变量”如今已是共同结论。Agent Hi Tax 的增量在于真实账户的原生计量、跨报告面的对账与纵向观察。

## 命名

“Hi Tax”是项目品牌名。正式 schema 与论文使用 *baseline footprint*、*harness-mediated consumption*、*native metering* 等中性术语；`tax` 和 `waste` 不作为统计变量。
