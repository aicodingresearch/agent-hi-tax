# Wanted scenarios

**English** | [中文](wanted-scenarios.zh-CN.md)

> Each entry is a task that can be claimed independently, completed independently, and submitted as its own Pull Request.

Last updated: 2026-08-29. Completed scenarios are listed in the [Hi Tax Index](../RESULTS.md); for step-by-step instructions see the [contributor walkthrough](contributor-walkthrough.md).

## How to use this list

1. Start by taking stock of what you already have: which Agent product, which subscription plan, which operating system. **Do not buy a subscription just to complete a task**; pick tasks that match your existing resources.
2. **All else being equal, mainstream first**: prioritize mainstream, high-traffic harnesses and models — the larger the user base, the more questions a single reviewable observation can answer; niche or long-tail products come after.
3. Open an issue in the repository to claim a task, titled `[Claim] T-xx one-line scenario description`, stating in the body the planned Agent version, model, subscription plan, and estimated completion time. If no task fits, you can also propose a new combination in an issue.
4. Multiple people may claim the same task: independent replications by different people, on different devices, with different accounts are themselves valuable contributions, as long as this is stated clearly in the issue and the PR. Directory names carry your own GitHub handle, so same-date replications never collide — see the [GitHub-handle suffix rule](../CONTRIBUTING.md#run-package-layout).
5. After claiming, follow the [contributor walkthrough](contributor-walkthrough.md) step by step; for rule details, [CONTRIBUTING](../CONTRIBUTING.md) is authoritative.
6. One task corresponds to one scenario and one PR. A few comparison tasks (marked "2 scenarios") produce two scenario packages — submit two PRs.

**About versions**: the product versions referenced in this list are the versions in use when the existing reference samples were collected. The version you actually install will most likely be newer — this does not invalidate the task: a different version is a new scenario and is just as worth observing. Record the exact version you installed honestly; do not deliberately downgrade.

**Difficulty**:

- ★ An existing collection adapter and a complete reference sample can be copied directly; minimal changes required;
- ★★ An adapter exists, but you need to change one scenario variable while keeping everything else fixed;
- ★★★ No existing adapter; you need to work out for yourself how the product exposes usage and where the redaction points are.

Allow about 30 minutes for a typical contribution. For a first contribution, allow about 1 hour, which is enough to read the documentation, handle redaction, and complete one scenario. The ★★★ tasks and the paired comparison tasks are the exceptions; each of them carries its own estimate below.

## Points

Every task on this list carries a point value, written into its title as `(N pts)`.

**What the number means.** It is a price on how much marginal information that task adds to the dataset *right now* — nothing more. It exists so you can see at a glance where the gaps are and choose accordingly. Points price contributions; they do not rank products. This is not the "simple leaderboard across vendors" that the [README rules out](../README.md#what-this-is-not) — that phrase refers to comparing vendors and models against each other, which this project still does not do. The same prices apply to every contributor.

**When points are awarded.** At the moment a PR is merged, using the price and the count shown on this page at that moment. Nothing is reserved and no price is locked in advance. Before you start testing you can read this page together with the open claim issues to estimate what a task is likely to be worth, but that estimate is not a commitment.

**Group A decays, and the decay resets every quarter.** The replication tasks pay 3 / 2 / 1 / 0 points as identical work accumulates, and the count resets at the start of each natural quarter, beginning with 2026Q3. The bucket the count runs in is *product × model × effort × platform × route × subscription tier*; product point releases are ignored for this purpose. You still record the exact version, as [CONTRIBUTING](../CONTRIBUTING.md#what-counts-as-one-scenario) requires — that is scenario identity at the data layer, and it has nothing to do with the pricing bucket. When it is unclear whether two subscription names or two product names normalize into the same bucket, the maintainer decides at the time of the award and writes the decision back onto this page.

**The maintainer's four pre-system reference samples neither earn points nor occupy any decay slot.** They are the baseline that replications are measured against; every replication count starts from zero, and the ledger below starts empty.

**Paired tasks pay once.** A task marked "2 scenarios" pays its full value once, after both sides have been merged. If you complete only one side, it is priced at whatever tier that side satisfies on its own.

**0 points does not mean "not wanted".** It means only that this round of the task is no longer being recruited with points. The data is still valuable, and submissions and independent replications are as welcome as they have always been.

**The only bonus is a usable new product adapter: +2.** It is awarded once per product, when the adapter documentation has been merged *and* its collection commands and redaction points have actually been walked through by the corresponding scenario. There is no bonus for evidence tier, and honestly labelling a package as mixed or incomplete costs you nothing.

**Before awarding, the maintainer checks whether available evidence was left out**, following the principle already stated in [CONTRIBUTING](../CONTRIBUTING.md#the-six-most-important-rules): evidence you can get should be provided, evidence you cannot get does not block. Where something was omitted that could have been collected, the points are awarded once it has been filled in. This affects points only; it does not change the bar for accepting a PR.

**Combinations that are not on this list** need a proposal issue first. The maintainer prices them in the reply; before that reply they are worth 0 points.

**Edge cases are decided by the maintainer**, and the decision is written back onto this page.

Three checks before you pick a task:

- If the evidence can be obtained, do not submit a self-report instead — Level C is for products that genuinely do not expose the field.
- A new input case needs an issue first, agreeing on the exact bytes, encoding, and SHA-256 before you measure anything.
- For a niche or no-longer-maintained product, open a proposal explaining what it can answer that no existing scenario can.

### Worked examples

Rules are abstract; here is how they cash out.

| What happened | Points | Why |
| --- | ---: | --- |
| First merged replication of T-01 — its bucket was empty | 3 | First independent replication of a reference sample: the dataset's first reproducibility check |
| A second contributor merges the same combination a week later | 2 | Second in the same bucket this quarter; no coordination needed — the count on this page decides |
| That contributor then merges T-13 (same setup, effort medium) | 3 | A new single-variable point on the effort axis |
| Both sides of T-31 (MCP on/off) merged | 8, once | A paired comparison pays as one task, after both sides land |
| Only one side of a paired task ever lands | that side's own tier (usually 0–3) | The pair price buys the comparison, not half of it |
| First Gemini CLI sample, plus an adapter the scenario actually walked through | 6 + 2 | First sample of a listed product; the adapter bonus is the only stackable bonus, once per product |
| An adapter document alone, with no scenario exercising it | +0 | The +2 requires the adapter to be merged and walked through by a real scenario |
| A fourth same-bucket T-01 replication in the same quarter | 0 — and still merged | 0 only means "not recruited with points this round"; the data keeps its value, and the count resets next quarter |
| Proposing an agent that is not named anywhere on this list (T-23); the maintainer prices it at 4 in the reply; the package merges | 4 | Off-list combinations are worth 0 until priced in a proposal reply |
| Replicating a newly added product's first sample | priced via proposal | Not on this list yet: the maintainer prices it (often like group A, 3/2/1/0) and writes it back here |

---

## A. Getting started: independently replicate an existing scenario (difficulty ★)

Replication is the best first task: the reference sample, the adapter, and the fields all have existing references to follow — you only need to execute strictly and record honestly. It is also the only way to test whether this dataset is reproducible.

### T-01 Replication: Codex CLI × gpt-5.6-sol × high (3 pts)

- **Scenario**: official Codex CLI (current version) × `gpt-5.6-sol` × `high` × ChatGPT subscription × fresh session × empty directory.
- **You need**: a ChatGPT subscription at any tier (if it differs from the reference sample's Pro 20x, record that honestly).
- **Why this is a priority**: the existing reference sample is one observation by one maintainer, on one machine, once; whether the input context stays stable at about 13.95K tokens, and whether the cache fluctuation pattern reproduces, both need independent data points.
- **References**: [Codex CLI adapter (Chinese)](adapters/codex-cli.zh-CN.md), [existing reference sample](../runs/2026-08-14/codex-cli-0.147.0_gpt-5.6-sol_high_hi-en-v1_as-used_mac-arm64/README.md).
- **Points**: 3 / 2 / 1 / 0, decaying as replications of the same bucket accumulate; the count resets each natural quarter.

### T-02 Replication: Claude Code × Fable 5 × high (3 pts)

- **Scenario**: official Claude Code (current version) × `claude-fable-5` × `high` × Claude subscription × fresh session.
- **You need**: a Claude Pro or Max subscription.
- **Why this is a priority**: verify whether the structure of "plain input only 2 tokens + about 25K cache creation" reproduces under other accounts and configurations; keep the same permission mode across all three attempts.
- **References**: [Claude Code adapter (Chinese)](adapters/claude-code.zh-CN.md), [existing reference sample](../runs/2026-08-15/claude-code-2.1.220_claude-fable-5_high_hi-en-v1_as-used_mac-arm64/README.md).
- **Points**: 3 / 2 / 1 / 0, decaying as replications of the same bucket accumulate; the count resets each natural quarter.

### T-03 Replication: WorkBuddy × Auto (3 pts)

- **Scenario**: WorkBuddy desktop IDE (current version) × `Auto` × fresh session × separate empty directory.
- **You need**: a WorkBuddy account (with credit display).
- **Why this is a priority**: which models the Auto route picks is a per-attempt outcome, so more samples mean more meaning; the existing reference sample saw two different models across 3 attempts. This is also currently the only product that achieves native per-attempt credit attribution, which is worth reproducing.
- **References**: [WorkBuddy adapter (Chinese)](adapters/workbuddy-desktop.zh-CN.md), [existing reference sample](../runs/2026-08-15/workbuddy-5.3.13_auto_craft_hi-en-v1_as-used_mac-arm64/README.md).
- **Points**: 3 / 2 / 1 / 0, decaying as replications of the same bucket accumulate; the count resets each natural quarter.

---

## B. Filling out comparisons: single-variable extensions of existing products (difficulty ★★)

Each task changes exactly one variable of an existing scenario and keeps everything else fixed — the observations most likely to produce a clean difference.

### T-11 De-confounding follow-up: Fable 5 vs Opus 5 under the same permission mode (2 scenarios) (8 pts)

- **Scenario**: Claude Code × `high` × measure `claude-fable-5` and `claude-opus-5` separately under the same permission/footer mode.
- **You need**: a Claude subscription (Max is best, allowing direct comparison with the existing reference samples).
- **Why this is a priority**: **This is the most clearly identified fix needed in the current dataset.** The existing Fable/Opus comparison is confounded by footer mode (`bypass permissions on` vs `manual mode on`); the 342-token difference in total input currently cannot be attributed to the model. Re-measuring both models with the mode held fixed removes this confounder.
- **Note**: two scenarios, two PRs; fill in the comparison/confounder fields in the manifest.
- **Effort**: expect about 2–4 hours of real work across both sides; the 30-minute figure above does not apply here.

### T-10 Claude Code × Sonnet 5 × high (3 pts)

- **Scenario**: Claude Code (current version) × `claude-sonnet-5` × `high` × fresh session.
- **You need**: a Claude subscription.
- **Why this is a priority**: once Sonnet is added, the footprints of three model tiers under the same harness can be viewed side by side: does model choice change how much system prompt and tool definition content is injected? Keep the permission mode consistent with the reference sample you are comparing against.

### T-12 Effort ladder: Claude Code × Fable 5 × medium (or low) (3 pts)

- **Scenario**: identical to the existing Fable reference sample, except effort changes from `high` to `medium` or `low`.
- **Why this is a priority**: effort is a tier the product explicitly exposes, but whether it affects input injection, output length, or only reasoning — there is currently no data.

### T-13 Effort ladder: Codex CLI × gpt-5.6-sol × medium (3 pts)

- **Scenario**: identical to the existing Codex reference sample, except effort changes to `medium`.
- **Why this is a priority**: same as T-12, on the Codex side.

### T-14 Subscription tier comparison: Claude Pro (3 pts)

- **Scenario**: same shape as any existing Claude Code reference sample, with the subscription changed from Max to Pro.
- **Why this is a priority**: the token footprint is expected to be independent of subscription tier — but "expected" needs evidence. If there is a difference, that is an important finding.

### T-15 Subscription tier comparison: ChatGPT Plus or regular Pro (3 pts)

- **Scenario**: same shape as the existing Codex reference sample, with the subscription changed from Pro 20x to Plus or regular Pro.
- **Why this is a priority**: same as T-14, on the Codex side.

### T-16 Windows platform replication (pick any existing scenario) (4 pts)

- **Scenario**: any existing scenario, with the operating system changed to Windows.
- **Why this is a priority**: all existing data was collected on macOS arm64; a harness may inject different environment information on different platforms. Use Windows equivalents for the preflight commands; everything else stays the same.
- **Points**: 4 pts for the first Windows package of each product.

### T-17 WorkBuddy with a single pinned model vs Auto (3 pts)

- **Scenario**: WorkBuddy × one explicitly pinned specific model (e.g. GLM-5.2) × everything else identical to the Auto reference sample.
- **Why this is a priority**: it separates the two variables "Auto routing" and "the model itself"; compared against the Auto data from T-03, it can show whether the routing itself introduces extra overhead.

---

## C. New products: bringing more Agent harnesses under observation (difficulty ★★★)

New-product tasks have the highest value and the highest difficulty: there is no existing adapter, and you need to answer for yourself where this product exposes usage and how to redact it. Start by collecting under the generic semantics in [CONTRIBUTING](../CONTRIBUTING.md), and describe the differences from the three existing adapters in your PR; in the language you write, drafting `docs/adapters/<product>.md` (English) or `docs/adapters/<product>.zh-CN.md` (Chinese) along the way is welcome.

Products use wildly varied metering units (tokens, credits, premium requests, quota percentages) — **keep the native units, do not convert**.

### T-20 Gemini CLI (6 pts)

- **You need**: a Google account or Gemini subscription; confirm which usage fields the product exposes.
- **Why this is a priority**: the only major vendor completely absent so far; its free/subscription quota model and its token exposure are both worth a first sample.
- **Effort**: expect about 2–4 hours of real work — working out the usage exposure and the redaction points is what takes the time; the 30-minute figure above does not apply here.

### T-21 Cursor (6 pts)

- **You need**: a Cursor subscription.
- **Why this is a priority**: a typical product billed in "credits/request counts", an IDE carrier, with a harness structure very different from CLI products.
- **Effort**: expect about 2–4 hours of real work — working out the usage exposure and the redaction points is what takes the time; the 30-minute figure above does not apply here.

### T-22 GitHub Copilot (CLI or IDE Chat) (6 pts)

- **You need**: a Copilot subscription (individual or education both fine; record honestly).
- **Why this is a priority**: premium requests are yet another native metering unit; education accounts are also widespread, making material easy to obtain.
- **Effort**: expect about 2–4 hours of real work — working out the usage exposure and the redaction points is what takes the time; the 30-minute figure above does not apply here.

### T-23 Your pick: another Agent you use day to day (4 pts)

- **Scenario**: Cline, iFlow, Trae, or another Agent product you genuinely use.
- **Why this is a priority**: the as-used configurations of real users have the most real-world relevance. For one of the products named above, open a claim issue and start. For any other product, open a proposal first and align on it, having confirmed under the [scenario identity rules](../CONTRIBUTING.md#what-counts-as-one-scenario) that it is a new scenario.
- **Points**: 4 pts for the first merged sample of each named product (Cline, iFlow, Trae) — no prior approval needed; claim and start. Any other product needs a proposal first: the maintainer prices it at 3–6 pts in the reply, and it is worth 0 before that reply.
- **Effort**: expect about 1–2 hours — you already use the tool every day, so the time goes into locating the usage fields and the redaction points, not into learning the product; the 30-minute figure above still does not apply.

---

## D. Harness variable studies: weighing the components of the harness directly (difficulty ★★)

If your research interest is the Agent harness itself, this group of tasks is the most directly relevant: a set of on/off comparisons under the same product and the same model, where **the difference corresponds directly to the marginal token cost of one specific harness component**. Background: [contributor walkthrough — Why this is worth doing](contributor-walkthrough.md#why-this-is-worth-doing).

### T-31 MCP on/off comparison (2 scenarios) (8 pts)

- **Scenario**: same product, same model and effort, 3 attempts each in two states: "with a specific MCP server configured" and "with that MCP removed". Choosing an MCP server with many tools makes the effect clearer.
- **Why this is a priority**: MCP tool definitions enter the context and affect input tokens even when they are never called — this is a direct measurement of "tool definition cost", one of the most frequently cited questions in harness research.
- **Effort**: expect about 2–4 hours of real work across both sides; the 30-minute figure above does not apply here.

### T-32 Rules file present/absent comparison (2 scenarios) (8 pts)

- **Scenario**: an empty directory vs a directory containing only one fixed-content, publicly reproducible `AGENTS.md` (or `CLAUDE.md`); everything else unchanged. The rules file fixture is published with the PR; use `custom` for the harness profile.
- **Why this is a priority**: measures the marginal cost of rules file injection, and whether the product injects it verbatim, truncates it, or rewrites it.
- **Effort**: expect about 2–4 hours of real work across both sides; the 30-minute figure above does not apply here.

### T-30 standard-clean vs as-used comparison on the same machine (2 scenarios) (8 pts)

- **Scenario**: same machine, same product and model: first do 3 attempts under your real configuration (`as-used`); then construct a verifiably clean environment (e.g. a newly created system user, confirmed free of global rules, MCP, plugins) and do 3 `standard-clean` attempts.
- **Why this is a priority**: the difference approximates "the entire fixed overhead of your personal harness configuration".
- **Note**: the bar for `standard-clean` is high — [CONTRIBUTING](../CONTRIBUTING.md#three-harness-profiles) requires that you have actually verified the environment before using this label. If you cannot fully confirm it, honestly use `as-used`, or switch to a single-switch comparison like T-31/T-32.
- **Effort**: expect about 2–4 hours of real work across both sides; the 30-minute figure above does not apply here.

### T-33 fresh vs resumed session (2 scenarios) (8 pts)

- **Scenario**: same product and model: one group as normal fresh runs; for the other group, first create a session containing only one `hi` round trip, exit, then resume and send `hi` again.
- **Why this is a priority**: observes how history injection and cache reads behave when a session is resumed; there is currently no data at all.
- **Effort**: expect about 2–4 hours of real work across both sides; the 30-minute figure above does not apply here.

---

## E. New input cases (open an issue first to align with the maintainers)

### T-40 hi-zh-v1: Chinese "你好" (4 pts)

- **Scenario**: any existing harness × the new input case "你好".
- **Note**: a new input is a protocol-level change — the exact original text, encoding, byte sequence, and SHA-256 must be defined first, with a new `prompts/` file created and a case ID decided. **Open an issue to finalize this before measuring**; do not just send a Chinese sentence as you understand it and submit.
- **Why this is a priority**: whether the input language affects harness injection (e.g. language detection, reply length) is a question of direct interest to bilingual Chinese/English users.
- **Points**: 4 pts covers both halves — the new input case definition and the first scenario package that uses it.

---

## F. Third-party gateway routing (difficulty ★★–★★★)

The Agent's distributor and the inference route are two separate variables: an official Agent can also be configured to go through a third-party gateway (record the route as `third-party-gateway`). Gateways are the corner of the community with the most quota rumors and the least public evidence — for a same-named model on a gateway, the token metering, cache behavior, and true upstream currently have almost no reviewable observations. Rules: [CONTRIBUTING — First-party products, official APIs, and gateways](../CONTRIBUTING.md#first-party-products-official-apis-and-gateways).

Shared notes for this group:

- **Only test gateways you already use and trust**; do not sign up for services of unknown origin just to test them, and do not use the key of your main account for experiments.
- Must be disclosed: the gateway's public name, public domain, compatible protocol, and claimed upstream models; secrets and signature parameters in the endpoint are never committed.
- A model name returned by a gateway only proves "it returned this label" — record claimed and observed separately in the manifest, and do not conclude "confirmed to be a certain vendor's model".
- Keep billing displays such as multipliers, credits, and balances in native units; with a single-user account and no other concurrent usage, the per-attempt balance difference is one of the few gateway metrics that can be attributed cleanly — worth recording before/after in full.
- Following the mainstream-first principle: test high-traffic gateways and mainstream model labels (Claude, GPT series) first, then extend to long-tail combinations.

### T-50 Official API vs gateway, same model label (2 scenarios) (8 pts)

- **Scenario**: same harness, same model label (e.g. `claude-sonnet-5` or some GPT model): one group through the official API, one group through a gateway, everything else unchanged.
- **Why this is a priority**: directly answers "does relaying change token metering and cache behavior". Differences could come from the gateway rewriting requests, stripping cache fields, or injecting its own system prompt — each of these is a behavior harness research cares about. Record the official API side just as honestly (route `official-api`).
- **Effort**: expect about 2–4 hours of real work across both sides; the 30-minute figure above does not apply here.

### T-51 Model ladder on a single gateway (one scenario per model) (3 pts)

- **Scenario**: fix the harness and the gateway, and separately measure several of the different upstream models it claims (e.g. one scenario each for Claude, GPT, Gemini, DeepSeek).
- **Why this is a priority**: a horizontal view of whether one gateway's metering semantics and latency are consistent across different upstreams, while also building a public record of "claimed model vs observable behavior".
- **Points**: 3 pts per model scenario, for now limited to the model list named above.

### T-52 Different gateways, same model label (8 pts)

- **Scenario**: same harness, same model label, one group each on two different gateways.
- **Why this is a priority**: if the two gateways show clearly different token/latency distributions for the same model label, that is itself an observation worth publishing; if they agree, it strengthens the indirect evidence that the label is credible.
- **Points**: 8 pts paid once, after both gateway sides have been merged.
- **Effort**: expect about 2–4 hours of real work across both sides; the 30-minute figure above does not apply here.

---

## G. Chinese model ecosystem: GLM, Kimi, MiniMax, Qwen, DeepSeek (difficulty ★★–★★★)

In the existing data, Chinese models have only appeared through WorkBuddy's Auto routing (GLM-5.2, DeepSeek-V4-Flash). These vendors all have official Agent carriers or official compatible endpoints of their own, and are worth bringing under observation one by one. Product forms iterate quickly: treat the actual product form at the time you claim as authoritative, record the exact version, subscription, and route classification honestly, and if the route classification is unclear, describe the actual chain in the PR.

When a group offers multiple options, pick the combination you judge to be the most popular with the most users right now.

### T-60 Qwen Code CLI × Qwen (6 pts)

- **Scenario**: official Qwen Code CLI × default or explicitly pinned Qwen model × official account quota × fresh session.
- **Why this is a priority**: an official open-source CLI harness with a low free-quota barrier, well suited as the first entry in group G; its harness shares a common origin with Gemini CLI, so it can later form a structurally matched comparison with T-20.

### T-61 Kimi × official carrier (6 pts)

- **Scenario**: the official Kimi CLI, or a Kimi subscription connected to an officially supported compatible harness × pinned Kimi model.
- **Why this is a priority**: there is currently no public sample at all of Kimi's subscription/quota model or its token exposure.

### T-62 GLM × Claude Code compatible endpoint (official coding subscription) (6 pts)

- **Scenario**: Zhipu's official coding subscription connected to Claude Code via its Anthropic-compatible endpoint × pinned GLM model, everything else aligned with the existing Claude Code reference samples.
- **Why this is a priority**: the same Claude Code harness, connected to Anthropic's official service on one side and GLM's official endpoint on the other — a clean **harness-constant, backend-varying** comparison, directly comparable with the existing Claude Code reference samples on input injection and cache behavior. Record claimed and observed models separately.

### T-63 MiniMax × official carrier or compatible endpoint (6 pts)

- **Scenario**: MiniMax's official Agent product, or its M-series models connected to a harness via an official compatible endpoint × fresh session.
- **Why this is a priority**: there are no samples yet of MiniMax's Agent product form or its metering units; the carrier choice itself (official product vs compatible harness) is also worth explaining in the PR.

### T-65 DeepSeek × official carrier or compatible endpoint (6 pts)

- **Scenario**: DeepSeek's official agent product if one exists, or a pinned DeepSeek model connected to a harness via its official compatible endpoint × fresh session; record the actual product form and the route classification honestly.
- **Why this is a priority**: the most widely used Chinese model family, yet so far it has only appeared in this dataset as a WorkBuddy Auto routing outcome (DeepSeek-V4-Flash in one attempt); its official quota/billing model and token exposure have no dedicated sample. A pinned-DeepSeek scenario also gives the existing Auto observation something to be compared against.

### T-64 Locally self-hosted open weights (difficulty ★★★) (6 pts)

- **Scenario**: open weights (e.g. the open versions of GLM or Qwen) deployed locally via vLLM or Ollama, connected to any open-source harness; record the route as `self-hosted`.
- **Why this is a priority**: this is the only route where both ends — "the raw request" and "the metering" — are visible at the same time: the prompt token counts in the inference server logs can be reconciled word for word against the harness's injection, the cleanest way of weighing the harness. Requires some local deployment experience and hardware.
- **Points**: 6 pts applies to one self-hosted stack, priced in advance in your claim issue; further stacks are not priced by default.
- **Effort**: expect about 2–4 hours of real work — working out the usage exposure and the redaction points is what takes the time; the 30-minute figure above does not apply here.

---

## Want to do a scenario not on this list?

Welcome. Open an issue describing your combination (product × version × model × effort × subscription × route × session state × harness), and check against the [scenario identity rules](../CONTRIBUTING.md#what-counts-as-one-scenario) that it is a new scenario. The list is continuously updated as tasks are claimed and completed.

---

## Points ledger

The maintainer appends one row here when a PR is merged. Corrections are handled by appending an offsetting row; historical rows are never edited. A contributor's total is the sum of their rows.

| Date | Contributor | Task | PR | Points | Note |
| --- | --- | --- | --- | ---: | --- |
