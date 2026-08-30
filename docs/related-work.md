# Related work

**English** | [中文](related-work.zh-CN.md)

## hibench

[hibench](https://hibench.dev) is an open-source benchmark of coding-agent default context footprints. It starts each agent in a fresh, empty Git repository, points it at a local recorder with a dummy key so no upstream model is called, sends `Hi`, captures the first outbound request, and counts every field with `o200k_base`. Its current public dataset covers 16 agents and 1,132 versions, with one canonical capture per release.

hibench measures the intercepted default request footprint with a dummy key and no upstream call; Agent Hi Tax measures what real products actually meter, report, and charge on real accounts — and reconciles those surfaces.

The two projects are complementary. Agent Hi Tax covers dimensions that hibench intentionally does not: real accounts and subscriptions, credits and billing ledgers, observed routing, differences between subscription tiers, and Chinese-ecosystem or newer-form-factor product lines that are not yet on the hibench roster.

## Load-bearing evaluation

[Claw-SWE-Bench](https://arxiv.org/abs/2606.12344), with its [open-source reference implementation](https://github.com/opensquilla/claw-swe-bench), evaluates agent-harness capability and cost under controlled conditions with real coding workloads. Agent Hi Tax observes the orthogonal minimal-interaction, no-load side: what the product consumes before a substantive task begins.

## Research context

The broader literature now treats the harness as a hidden variable. [The Scaffold Effect in Coding Agents](https://arxiv.org/abs/2607.22585) reports up to a 40x difference in tokens per solved task for the same model across harnesses. [Prompt-Induced Waste](https://arxiv.org/abs/2608.01347) studies how prompt wording and harness design change end-to-end reasoning cost, while [A²E](https://arxiv.org/abs/2608.07346) provides an end-to-end auditing engine for harness capabilities and execution traces. At the request boundary, [Systima's July 2026 Claude Code versus OpenCode comparison](https://systima.ai/blog/claude-code-vs-opencode-token-overhead) measured roughly 33K versus 7K tokens of initial context in an empty environment.

That the harness is a hidden variable is now a shared conclusion. Agent Hi Tax adds real-account native metering, reconciliation across reporting surfaces, and longitudinal observation.

## Naming

"Hi Tax" is the project brand. The formal schema and papers use neutral terms such as *baseline footprint*, *harness-mediated consumption*, and *native metering*; `tax` and `waste` are not statistical variables.
