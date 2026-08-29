# Wanted scenarios

**English** | [中文](wanted-scenarios.zh-CN.md)

> Each entry is a task that can be claimed independently, completed independently, and submitted as its own Pull Request.

Last updated: 2026-08-28. Completed scenarios are listed in the [Hi Tax Index](../RESULTS.md); for step-by-step instructions see the [contributor walkthrough](contributor-walkthrough.md).

## How to use this list

1. Start by taking stock of what you already have: which Agent product, which subscription plan, which operating system. **Do not buy a subscription just to complete a task**; pick tasks that match your existing resources.
2. **All else being equal, mainstream first**: prioritize mainstream, high-traffic harnesses and models — the larger the user base, the more questions a single reviewable observation can answer; niche or long-tail products come after.
3. Open an issue in the repository to claim a task, titled `[Claim] T-xx one-line scenario description`, stating in the body the planned Agent version, model, subscription plan, and estimated completion time. If no task fits, you can also propose a new combination in an issue.
4. Multiple people may claim the same task: independent replications by different people, on different devices, with different accounts are themselves valuable contributions, as long as this is stated clearly in the issue and the PR. For same-date directory conflicts, follow the [GitHub-handle suffix rule](../CONTRIBUTING.md#run-package-layout).
5. After claiming, follow the [contributor walkthrough](contributor-walkthrough.md) step by step; for rule details, [CONTRIBUTING](../CONTRIBUTING.md) is authoritative.
6. One task corresponds to one scenario and one PR. A few comparison tasks (marked "2 scenarios") produce two scenario packages — submit two PRs.

**About versions**: the product versions referenced in this list are the versions in use when the existing reference samples were collected. The version you actually install will most likely be newer — this does not invalidate the task: a different version is a new scenario and is just as worth observing. Record the exact version you installed honestly; do not deliberately downgrade.

**Difficulty**:

- ★ An existing collection adapter and a complete reference sample can be copied directly; minimal changes required;
- ★★ An adapter exists, but you need to change one scenario variable while keeping everything else fixed;
- ★★★ No existing adapter; you need to work out for yourself how the product exposes usage and where the redaction points are.

Allow 30–60 minutes for a typical contribution; practiced contributors can often finish in about 30 minutes. A first pass through the documentation, redaction work, or a product without an existing adapter may take longer.

---

## A. Getting started: independently replicate an existing scenario (difficulty ★)

Replication is the best first task: the reference sample, the adapter, and the fields all have existing references to follow — you only need to execute strictly and record honestly. It is also the only way to test whether this dataset is reproducible.

### T-01 Replication: Codex CLI × gpt-5.6-sol × high

- **Scenario**: official Codex CLI (current version) × `gpt-5.6-sol` × `high` × ChatGPT subscription × fresh session × empty directory.
- **You need**: a ChatGPT subscription at any tier (if it differs from the reference sample's Pro 20x, record that honestly).
- **Why this is a priority**: the existing reference sample is one observation by one maintainer, on one machine, once; whether the input context stays stable at about 13.95K tokens, and whether the cache fluctuation pattern reproduces, both need independent data points.
- **References**: [Codex CLI adapter (Chinese)](adapters/codex-cli.zh-CN.md), [existing reference sample](../runs/2026-08-14/codex-cli-0.147.0_gpt-5.6-sol_high_hi-en-v1_as-used_mac-arm64/README.md).

### T-02 Replication: Claude Code × Fable 5 × high

- **Scenario**: official Claude Code (current version) × `claude-fable-5` × `high` × Claude subscription × fresh session.
- **You need**: a Claude Pro or Max subscription.
- **Why this is a priority**: verify whether the structure of "plain input only 2 tokens + about 25K cache creation" reproduces under other accounts and configurations; keep the same permission mode across all three attempts.
- **References**: [Claude Code adapter (Chinese)](adapters/claude-code.zh-CN.md), [existing reference sample](../runs/2026-08-15/claude-code-2.1.220_claude-fable-5_high_hi-en-v1_as-used_mac-arm64/README.md).

### T-03 Replication: WorkBuddy × Auto

- **Scenario**: WorkBuddy desktop IDE (current version) × `Auto` × fresh session × separate empty directory.
- **You need**: a WorkBuddy account (with credit display).
- **Why this is a priority**: which models the Auto route picks is a per-attempt outcome, so more samples mean more meaning; the existing reference sample saw two different models across 3 attempts. This is also currently the only product that achieves native per-attempt credit attribution, which is worth reproducing.
- **References**: [WorkBuddy adapter (Chinese)](adapters/workbuddy-desktop.zh-CN.md), [existing reference sample](../runs/2026-08-15/workbuddy-5.3.13_auto_craft_hi-en-v1_as-used_mac-arm64/README.md).

---

## B. Filling out comparisons: single-variable extensions of existing products (difficulty ★★)

Each task changes exactly one variable of an existing scenario and keeps everything else fixed — the observations most likely to produce a clean difference.

### T-11 De-confounding follow-up: Fable 5 vs Opus 5 under the same permission mode (2 scenarios)

- **Scenario**: Claude Code × `high` × measure `claude-fable-5` and `claude-opus-5` separately under the same permission/footer mode.
- **You need**: a Claude subscription (Max is best, allowing direct comparison with the existing reference samples).
- **Why this is a priority**: **This is the most clearly identified fix needed in the current dataset.** The existing Fable/Opus comparison is confounded by footer mode (`bypass permissions on` vs `manual mode on`); the 342-token difference in total input currently cannot be attributed to the model. Re-measuring both models with the mode held fixed removes this confounder.
- **Note**: two scenarios, two PRs; fill in the comparison/confounder fields in the manifest.

### T-10 Claude Code × Sonnet 5 × high

- **Scenario**: Claude Code (current version) × `claude-sonnet-5` × `high` × fresh session.
- **You need**: a Claude subscription.
- **Why this is a priority**: once Sonnet is added, the footprints of three model tiers under the same harness can be viewed side by side: does model choice change how much system prompt and tool definition content is injected? Keep the permission mode consistent with the reference sample you are comparing against.

### T-12 Effort ladder: Claude Code × Fable 5 × medium (or low)

- **Scenario**: identical to the existing Fable reference sample, except effort changes from `high` to `medium` or `low`.
- **Why this is a priority**: effort is a tier the product explicitly exposes, but whether it affects input injection, output length, or only reasoning — there is currently no data.

### T-13 Effort ladder: Codex CLI × gpt-5.6-sol × medium

- **Scenario**: identical to the existing Codex reference sample, except effort changes to `medium`.
- **Why this is a priority**: same as T-12, on the Codex side.

### T-14 Subscription tier comparison: Claude Pro

- **Scenario**: same shape as any existing Claude Code reference sample, with the subscription changed from Max to Pro.
- **Why this is a priority**: the token footprint is expected to be independent of subscription tier — but "expected" needs evidence. If there is a difference, that is an important finding.

### T-15 Subscription tier comparison: ChatGPT Plus or regular Pro

- **Scenario**: same shape as the existing Codex reference sample, with the subscription changed from Pro 20x to Plus or regular Pro.
- **Why this is a priority**: same as T-14, on the Codex side.

### T-16 Windows platform replication (pick any existing scenario)

- **Scenario**: any existing scenario, with the operating system changed to Windows.
- **Why this is a priority**: all existing data was collected on macOS arm64; a harness may inject different environment information on different platforms. Use Windows equivalents for the preflight commands; everything else stays the same.

### T-17 WorkBuddy with a single pinned model vs Auto

- **Scenario**: WorkBuddy × one explicitly pinned specific model (e.g. GLM-5.2) × everything else identical to the Auto reference sample.
- **Why this is a priority**: it separates the two variables "Auto routing" and "the model itself"; compared against the Auto data from T-03, it can show whether the routing itself introduces extra overhead.

---

## C. New products: bringing more Agent harnesses under observation (difficulty ★★★)

New-product tasks have the highest value and the highest difficulty: there is no existing adapter, and you need to answer for yourself where this product exposes usage and how to redact it. Start by collecting under the generic semantics in [CONTRIBUTING](../CONTRIBUTING.md), and describe the differences from the three existing adapters in your PR; drafting a first version of `docs/adapters/<product>.md` along the way is welcome.

Products use wildly varied metering units (tokens, credits, premium requests, quota percentages) — **keep the native units, do not convert**.

### T-20 Gemini CLI

- **You need**: a Google account or Gemini subscription; confirm which usage fields the product exposes.
- **Why this is a priority**: the only major vendor completely absent so far; its free/subscription quota model and its token exposure are both worth a first sample.

### T-21 Cursor

- **You need**: a Cursor subscription.
- **Why this is a priority**: a typical product billed in "credits/request counts", an IDE carrier, with a harness structure very different from CLI products.

### T-22 GitHub Copilot (CLI or IDE Chat)

- **You need**: a Copilot subscription (individual or education both fine; record honestly).
- **Why this is a priority**: premium requests are yet another native metering unit; education accounts are also widespread, making material easy to obtain.

### T-23 Your pick: another Agent you use day to day

- **Scenario**: Cline, Qwen Code, iFlow, Trae, or another Agent product you genuinely use.
- **Why this is a priority**: the as-used configurations of real users have the most real-world relevance. Open an issue first describing the combination; once you have confirmed under the [scenario identity rules](../CONTRIBUTING.md#what-counts-as-one-scenario) that it is a new scenario, you can start.

---

## D. Harness variable studies: weighing the components of the harness directly (difficulty ★★)

If your research interest is the Agent harness itself, this group of tasks is the most directly relevant: a set of on/off comparisons under the same product and the same model, where **the difference corresponds directly to the marginal token cost of one specific harness component**. Background: [contributor walkthrough — Why this is worth doing](contributor-walkthrough.md#why-this-is-worth-doing).

### T-31 MCP on/off comparison (2 scenarios)

- **Scenario**: same product, same model and effort, 3 attempts each in two states: "with a specific MCP server configured" and "with that MCP removed". Choosing an MCP server with many tools makes the effect clearer.
- **Why this is a priority**: MCP tool definitions enter the context and affect input tokens even when they are never called — this is a direct measurement of "tool definition cost", one of the most frequently cited questions in harness research.

### T-32 Rules file present/absent comparison (2 scenarios)

- **Scenario**: an empty directory vs a directory containing only one fixed-content, publicly reproducible `AGENTS.md` (or `CLAUDE.md`); everything else unchanged. The rules file fixture is published with the PR; use `custom` for the harness profile.
- **Why this is a priority**: measures the marginal cost of rules file injection, and whether the product injects it verbatim, truncates it, or rewrites it.

### T-30 standard-clean vs as-used comparison on the same machine (2 scenarios)

- **Scenario**: same machine, same product and model: first do 3 attempts under your real configuration (`as-used`); then construct a verifiably clean environment (e.g. a newly created system user, confirmed free of global rules, MCP, plugins) and do 3 `standard-clean` attempts.
- **Why this is a priority**: the difference approximates "the entire fixed overhead of your personal harness configuration".
- **Note**: the bar for `standard-clean` is high — [CONTRIBUTING](../CONTRIBUTING.md#three-harness-profiles) requires that you have actually verified the environment before using this label. If you cannot fully confirm it, honestly use `as-used`, or switch to a single-switch comparison like T-31/T-32.

### T-33 fresh vs resumed session (2 scenarios)

- **Scenario**: same product and model: one group as normal fresh runs; for the other group, first create a session containing only one `hi` round trip, exit, then resume and send `hi` again.
- **Why this is a priority**: observes how history injection and cache reads behave when a session is resumed; there is currently no data at all.

### T-34 Clean quota attribution (any carrier)

- **Scenario**: redo any existing scenario, pausing all other usage on the same account and the same quota pool during the test, and recording the quota/percentage display before and after each attempt.
- **Why this is a priority**: quota attribution in the existing Codex reference sample is `contaminated`, and `not_measured` in the Claude sample. Producing the first clean per-attempt attribution for subscription percentage quotas would begin to answer the project's original question: "how much quota does one hi actually consume?" The credit attribution in the WorkBuddy reference sample can serve as a methodological reference.

---

## E. New input cases (open an issue first to align with the maintainers)

### T-40 hi-zh-v1: Chinese "你好"

- **Scenario**: any existing harness × the new input case "你好".
- **Note**: a new input is a protocol-level change — the exact original text, encoding, byte sequence, and SHA-256 must be defined first, with a new `prompts/` file created and a case ID decided. **Open an issue to finalize this before measuring**; do not just send a Chinese sentence as you understand it and submit.
- **Why this is a priority**: whether the input language affects harness injection (e.g. language detection, reply length) is a question of direct interest to bilingual Chinese/English users.

---

## F. Third-party gateway routing (difficulty ★★–★★★)

The Agent's distributor and the inference route are two separate variables: an official Agent can also be configured to go through a third-party gateway (record the route as `third-party-gateway`). Gateways are the corner of the community with the most quota rumors and the least public evidence — for a same-named model on a gateway, the token metering, cache behavior, and true upstream currently have almost no reviewable observations. Rules: [CONTRIBUTING — First-party products, official APIs, and gateways](../CONTRIBUTING.md#first-party-products-official-apis-and-gateways).

Shared notes for this group:

- **Only test gateways you already use and trust**; do not sign up for services of unknown origin just to test them, and do not use the key of your main account for experiments.
- Must be disclosed: the gateway's public name, public domain, compatible protocol, and claimed upstream models; secrets and signature parameters in the endpoint are never committed.
- A model name returned by a gateway only proves "it returned this label" — record claimed and observed separately in the manifest, and do not conclude "confirmed to be a certain vendor's model".
- Keep billing displays such as multipliers, credits, and balances in native units; with a single-user account and no other concurrent usage, the per-attempt balance difference is one of the few gateway metrics that can be attributed cleanly — worth recording before/after in full.
- Following the mainstream-first principle: test high-traffic gateways and mainstream model labels (Claude, GPT series) first, then extend to long-tail combinations.

### T-50 Official API vs gateway, same model label (2 scenarios)

- **Scenario**: same harness, same model label (e.g. `claude-sonnet-5` or some GPT model): one group through the official API, one group through a gateway, everything else unchanged.
- **Why this is a priority**: directly answers "does relaying change token metering and cache behavior". Differences could come from the gateway rewriting requests, stripping cache fields, or injecting its own system prompt — each of these is a behavior harness research cares about. Record the official API side just as honestly (route `official-api`).

### T-51 Model ladder on a single gateway (one scenario per model)

- **Scenario**: fix the harness and the gateway, and separately measure several of the different upstream models it claims (e.g. one scenario each for Claude, GPT, Gemini, DeepSeek).
- **Why this is a priority**: a horizontal view of whether one gateway's metering semantics and latency are consistent across different upstreams, while also building a public record of "claimed model vs observable behavior".

### T-52 Different gateways, same model label

- **Scenario**: same harness, same model label, one group each on two different gateways.
- **Why this is a priority**: if the two gateways show clearly different token/latency distributions for the same model label, that is itself an observation worth publishing; if they agree, it strengthens the indirect evidence that the label is credible.

---

## G. Chinese model ecosystem: GLM, Kimi, MiniMax, Qwen (difficulty ★★–★★★)

In the existing data, Chinese models have only appeared through WorkBuddy's Auto routing (GLM-5.2, DeepSeek-V4-Flash). These vendors all have official Agent carriers or official compatible endpoints of their own, and are worth bringing under observation one by one. Product forms iterate quickly: treat the actual product form at the time you claim as authoritative, record the exact version, subscription, and route classification honestly, and if the route classification is unclear, describe the actual chain in the PR.

When a group offers multiple options, pick the combination you judge to be the most popular with the most users right now.

### T-60 Qwen Code CLI × Qwen

- **Scenario**: official Qwen Code CLI × default or explicitly pinned Qwen model × official account quota × fresh session.
- **Why this is a priority**: an official open-source CLI harness with a low free-quota barrier, well suited as the first entry in group G; its harness shares a common origin with Gemini CLI, so it can later form a structurally matched comparison with T-20.

### T-61 Kimi × official carrier

- **Scenario**: the official Kimi CLI, or a Kimi subscription connected to an officially supported compatible harness × pinned Kimi model.
- **Why this is a priority**: there is currently no public sample at all of Kimi's subscription/quota model or its token exposure.

### T-62 GLM × Claude Code compatible endpoint (official coding subscription)

- **Scenario**: Zhipu's official coding subscription connected to Claude Code via its Anthropic-compatible endpoint × pinned GLM model, everything else aligned with the existing Claude Code reference samples.
- **Why this is a priority**: the same Claude Code harness, connected to Anthropic's official service on one side and GLM's official endpoint on the other — a clean **harness-constant, backend-varying** comparison, directly comparable with the existing Claude Code reference samples on input injection and cache behavior. Record claimed and observed models separately.

### T-63 MiniMax × official carrier or compatible endpoint

- **Scenario**: MiniMax's official Agent product, or its M-series models connected to a harness via an official compatible endpoint × fresh session.
- **Why this is a priority**: there are no samples yet of MiniMax's Agent product form or its metering units; the carrier choice itself (official product vs compatible harness) is also worth explaining in the PR.

### T-64 Locally self-hosted open weights (difficulty ★★★)

- **Scenario**: open weights (e.g. the open versions of GLM or Qwen) deployed locally via vLLM or Ollama, connected to any open-source harness; record the route as `self-hosted`.
- **Why this is a priority**: this is the only route where both ends — "the raw request" and "the metering" — are visible at the same time: the prompt token counts in the inference server logs can be reconciled word for word against the harness's injection, the cleanest way of weighing the harness. Requires some local deployment experience and hardware.

---

## Want to do a scenario not on this list?

Welcome. Open an issue describing your combination (product × version × model × effort × subscription × route × session state × harness), and check against the [scenario identity rules](../CONTRIBUTING.md#what-counts-as-one-scenario) that it is a new scenario. The list is continuously updated as tasks are claimed and completed.
