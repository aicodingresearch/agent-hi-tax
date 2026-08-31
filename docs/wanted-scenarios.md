# Wanted scenarios

**English** | [中文](wanted-scenarios.zh-CN.md)

> Each entry is a task that can be claimed independently, completed independently, and submitted as its own Pull Request.

Last updated: 2026-08-30. Completed scenarios are listed in the [Hi Tax Index](../RESULTS.md); for step-by-step instructions see the [contributor walkthrough](contributor-walkthrough.md).

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

For the one-PR-URL Agent workflow that calculates an award after merge and submits the bilingual ledger update, see [Agent entry point for PR review and points](agent-review-and-scoring.md).

Every task on this list carries a point value, written into its title as `(N pts)`.

**What the number means.** It is a price on how much marginal information that task adds to the dataset *right now* — nothing more. It exists so you can see at a glance where the gaps are and choose accordingly. Points price contributions; they do not rank products. This is not the "simple leaderboard across vendors" that the [README rules out](../README.md#what-this-is-not) — that phrase refers to comparing vendors and models against each other, which this project still does not do. The same prices apply to every contributor.

**When points are awarded.** At the moment a PR is merged, using the price and the count shown on this page at that moment. Nothing is reserved and no price is locked in advance. Before you start testing you can read this page together with the open claim issues to estimate what a task is likely to be worth, but that estimate is not a commitment.

**Group A decays, and the decay resets every quarter.** Non-anchor replication tasks pay 3 / 2 / 1 / 0 points as identical work accumulates; anchors use the separate rate below. The count resets at the start of each natural quarter, beginning with 2026Q3. The bucket the count runs in is *product × model × effort × platform × route × subscription tier*; product point releases are ignored for this purpose. You still record the exact version, as [CONTRIBUTING](../CONTRIBUTING.md#what-counts-as-one-scenario) requires — that is scenario identity at the data layer, and it has nothing to do with the pricing bucket. When it is unclear whether two subscription names or two product names normalize into the same bucket, the maintainer decides at the time of the award and writes the decision back onto this page.

**The maintainer's four pre-system reference samples neither earn points nor occupy any decay slot.** They are the baseline that replications are measured against; every replication count starts from zero, and the ledger below starts empty.

**Paired tasks pay once.** A task marked "2 scenarios" pays its full value once, after both sides have been merged. If you complete only one side, it is priced at whatever tier that side satisfies on its own.

**0 points does not mean "not wanted".** It means only that this round of the task is no longer being recruited with points. The data is still valuable, and submissions and independent replications are as welcome as they have always been.

**The only general task bonus is a usable new product adapter: +2.** It is awarded once per product, when the adapter documentation has been merged *and* its collection commands and redaction points have actually been walked through by the corresponding scenario. The narrow probe add-on rule below applies only to sibling L1/L2 packages. There is no bonus for evidence tier, and honestly labelling a package as mixed or incomplete costs you nothing.

**Before awarding, the maintainer checks whether available evidence was left out**, following the principle already stated in [CONTRIBUTING](../CONTRIBUTING.md#the-six-most-important-rules): evidence you can get should be provided, evidence you cannot get does not block. Where something was omitted that could have been collected, the points are awarded once it has been filled in. This affects points only; it does not change the bar for accepting a PR.

**Combinations that are not on this list** need a proposal issue first. Before the maintainer replies they are worth 0 points; the reply prices them by a fixed rubric: 3 pts = a compatible endpoint or model substitution behind an already-covered harness; 4 pts = a mature third-party harness; 6 pts = a genuinely new first-party or independent harness.

**Edge cases are decided by the maintainer**, and the decision is written back onto this page.

### Probe add-ons

The definitions of two new standard inputs, L1 and L2, are being finalized through the Group E process; see T-41 and T-42. Once a definition is final, a sibling L1 or L2 package added by the same contributor, in the same time window and under the same anchor combination, earns +1 point each. A sibling package may state that it reuses scenario-level environment evidence from the same batch.

`hi` remains the only required input. L1 and L2 are entirely optional, and no submission will be down-scored or rejected for lacking L1 or L2 — probe add-ons only add points and never become a gate.

Three checks before you pick a task:

- If the evidence can be obtained, do not submit a self-report instead — Level C is for products that genuinely do not expose the field.
- A new input case needs an issue first, agreeing on the exact bytes, encoding, and SHA-256 before you measure anything.
- For a niche or no-longer-maintained product, open a proposal explaining what it can answer that no existing scenario can.

### Worked examples

Rules are abstract; here is how they cash out.

| What happened | Points | Why |
| --- | ---: | --- |
| First merged replication of T-01 — its anchor bucket was empty | 5 | First independent replication of anchor 1: the dataset's first reproducibility check |
| A second contributor merges the same anchor combination a week later | 3 | Second in the anchor bucket this quarter; no coordination needed — the count on this page decides |
| That contributor then merges T-13 (same setup, effort medium) | 3 | A new single-variable point on the effort axis |
| Both sides of T-31 (MCP on/off) merged | 8, once | A paired comparison pays as one task, after both sides land |
| Only one side of a paired task ever lands | that side's own tier (usually 0–3) | The pair price buys the comparison, not half of it |
| First OpenCode sample, plus an adapter the scenario actually walked through | 6 + 2 | First sample of a listed product; the adapter is the only general stackable task bonus, once per product |
| An adapter document alone, with no scenario exercising it | +0 | The +2 requires the adapter to be merged and walked through by a real scenario |
| A fourth same-bucket T-01 replication in the same quarter | 1 | Anchor pricing keeps the fourth slot at 1; the count resets next quarter |
| Proposing an agent that is not named anywhere on this list (T-23); the maintainer prices it at 4 in the reply; the package merges | 4 | Off-list combinations are worth 0 until priced in a proposal reply |
| Replicating a newly added product's first sample | priced via proposal | Not on this list yet: the maintainer prices it (often like group A, 3/2/1/0) and writes it back here |

## Anchor combinations

Anchors are long-running objects of longitudinal observation, and quarterly repeat measurements are encouraged. Retesting an anchor is a **standing claim path**: it does not need a corresponding task on this list; open a claim issue and name the anchor number. The maintainer owns this list and may expand it.

**Anchor identity rules.** An anchor's long-term identity is Agent × effort. The model column records that product's current flagship or default model, not a permanently pinned value; when the product's flagship changes, the maintainer updates the value and notes the effective quarter in the table. A model transition does not break the time series: every round still records requested and observed models under the normal protocol. In a transition quarter, contributors are encouraged to make one **old/new overlap measurement** when the old model remains selectable: measure one package for each combination in the same time window. The two packages occupy different pricing buckets and each receives the anchor rate; their within-window difference is used to separate the model-attributable component from harness drift.

The current model values below are effective from **2026Q3**; future changes will carry their own effective quarter in this table.

| No. | Agent | Anchored model (current value) | Effort |
| ---: | --- | --- | --- |
| 1 | Codex CLI | `gpt-5.6-sol` | `high` |
| 2 | Claude Code | `claude-opus-5` | `high` |
| 3 | Google Antigravity CLI | Product default | Default |
| 4 | GitHub Copilot CLI | Product default | Default |
| 5 | Cursor | Mainline model (pin it and state it in the claim) | Default |
| 6 | OpenCode | One mainstream model (pin it when claiming) | Default |
| 7 | Tencent WorkBuddy | `Auto` | `craft` |
| 8 | ZCode | Mainline GLM model | Default |
| 9 | DeepSeek line | Mainline DeepSeek model (either a first-party harness or compatible endpoint; record it accurately) | Default |
| 10 | Local self-hosted | One frozen set of weights and stack | Default |

**Anchor pricing.** Retests of an anchor combination pay 5 / 3 / 2 / 1 points, resetting each natural quarter. This price takes precedence over any task's default price. Non-anchor combinations keep their current prices; no long-tail price is reduced in this round.

---

## A. Getting started: independently replicate an existing scenario (difficulty ★)

Replication is the best first task: the reference sample, the adapter, and the fields all have existing references to follow — you only need to execute strictly and record honestly. It is also the only way to test whether this dataset is reproducible.

### T-01 Replication: Codex CLI × gpt-5.6-sol × high (3 pts)

- **Scenario**: official Codex CLI (current version) × `gpt-5.6-sol` × `high` × ChatGPT subscription × fresh session × empty directory.
- **You need**: a ChatGPT subscription at any tier (if it differs from the reference sample's Pro 20x, record that honestly).
- **Why this is a priority**: the existing reference sample is one observation by one maintainer, on one machine, once; whether the input context stays stable at about 13.95K tokens, and whether the cache fluctuation pattern reproduces, both need independent data points.
- **References**: [Codex CLI adapter (Chinese)](adapters/codex-cli.zh-CN.md), [existing reference sample](../runs/2026-08-14/codex-cli-0.147.0_gpt-5.6-sol_high_hi-en-v1_as-used_mac-arm64/README.md).
- **Points**: this combination is anchor 1, so it pays the anchor rate of 5 / 3 / 2 / 1, resetting each natural quarter; that rate takes precedence over this task's default price.

### T-02 Replication: Claude Code × Fable 5 × high (3 pts)

- **Scenario**: official Claude Code (current version) × `claude-fable-5` × `high` × Claude subscription × fresh session.
- **You need**: a Claude Pro or Max subscription.
- **Why this is a priority**: verify whether the structure of "plain input only 2 tokens + about 25K cache creation" reproduces under other accounts and configurations; keep the same permission mode across all three attempts.
- **References**: [Claude Code adapter (Chinese)](adapters/claude-code.zh-CN.md), [existing reference sample](../runs/2026-08-15/claude-code-2.1.220_claude-fable-5_high_hi-en-v1_as-used_mac-arm64/README.md).
- **Points**: the Fable combination remains priced by this task at 3 / 2 / 1 / 0, decaying as replications of the same bucket accumulate and resetting each natural quarter. The longitudinal anchor is Claude Code × Opus 5 (anchor 2).

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
- **Fallback condition**: Fable 5 may fall back to Opus 5 because of the safety classifier; every attempt must record the actual observed model. An attempt that falls back cannot count as a Fable-side sample: label it and run a replacement attempt.
- **Effort**: expect about 2–4 hours of real work across both sides; the 30-minute figure above does not apply here.

### T-10 Claude Code × Sonnet 5 (`claude-sonnet-5`) × high (3 pts)

- **Scenario**: Claude Code (current version) × Sonnet 5 (`claude-sonnet-5`) × `high` × fresh session.
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

### T-20 Gemini CLI (archived — consumer path sunset) (0 pts)

- **Status**: On 2026-06-18, Gemini CLI stopped serving requests for individual/free and Pro/Ultra tiers ([official announcement](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)); enterprise licenses and paid API key paths remain available. To measure one of those retained paths, open a proposal for pricing first. The consumer first sample can no longer be measured; the new budget is T-24.
- **You need**: a Google account or Gemini subscription; confirm which usage fields the product exposes.
- **Why this is a priority**: the only major vendor completely absent so far; its free/subscription quota model and its token exposure are both worth a first sample.
- **Points**: 0 — request service for individual/free and Pro/Ultra tiers ended on 2026-06-18; enterprise licenses and paid API key paths remain available and require a proposal for pricing. The consumer first sample is no longer measurable; see T-24 for the new budget.

### T-21 Cursor (6 pts)

- **You need**: a Cursor subscription.
- **Why this is a priority**: a typical product billed in "credits/request counts", an IDE carrier, with a harness structure very different from CLI products.
- **Risk note**: OpenAI has notified Cursor that it plans to stop supplying its models on 2026-11-12; continue measuring as normal and record the actual model mix. This task and its point value will be reviewed then.
- **Effort**: expect about 2–4 hours of real work — working out the usage exposure and the redaction points is what takes the time; the 30-minute figure above does not apply here.

### T-22 GitHub Copilot IDE Chat (6 pts)

- **You need**: a Copilot subscription (individual or education both fine; record honestly).
- **Why this is a priority**: premium requests are yet another native metering unit; education accounts are also widespread, making material easy to obtain.
- **Billing note**: GitHub moved to AI Credits billing on 2026-06-01 while some legacy premium-request plans remain; record which billing system applies to the account.
- **Effort**: expect about 2–4 hours of real work — working out the usage exposure and the redaction points is what takes the time; the 30-minute figure above does not apply here.

### T-24 Google Antigravity CLI (6 pts)

- **Scenario**: Google Antigravity CLI (current version) × the product default or an explicitly pinned model × fresh session × empty directory; record the subscription tier and whatever the product exposes (tokens, compute units, quota fraction) honestly.
- **You need**: a Google account with Antigravity access, any tier.
- **Why this is a priority**: Google's flagship agent harness and the successor to Gemini CLI; its statusline/usage output is machine-readable, and its multi-surface family (CLI / desktop / IDE) also sets up the T-35 comparison. Currently the largest single-vendor gap in this list.
- **Effort**: expect about 2–4 hours of real work — working out the usage exposure and the redaction points is what takes the time; the 30-minute figure above does not apply here.

### T-25 GitHub Copilot CLI (6 pts)

- **Scenario**: GitHub Copilot CLI (current version) × default or pinned model × fresh session × empty directory.
- **You need**: a Copilot subscription (individual or education both fine).
- **Why this is a priority**: a different harness from the Copilot IDE Chat already covered by T-22 — the CLI/SDK surface reports usage per model call, so a single `hi` can reveal whether the harness makes hidden extra model calls; the Copilot ecosystem is among the largest in the industry.
- **Billing note**: GitHub moved to AI Credits billing on 2026-06-01 while some legacy premium-request plans remain; record which billing system applies to the account.
- **Effort**: expect about 2–4 hours of real work — working out the usage exposure and the redaction points is what takes the time; the 30-minute figure above does not apply here.

### T-26 OpenCode (6 pts)

- **Scenario**: OpenCode (current version) × one explicitly pinned provider and model (BYOK or its hosted gateway) × fresh session × empty directory; classify the route per your actual setup and explain it in the PR.
- **You need**: an OpenCode install plus API access to at least one model provider.
- **Why this is a priority**: the leading open-source agent CLI; its session records expose tokens, cost, cache, and reasoning per call — including auxiliary calls such as the session-title model, which is exactly the kind of hidden tax this project measures. Its BYOK design also makes it the natural carrier for T-36.
- **Effort**: expect about 2–4 hours of real work — working out the usage exposure and the redaction points is what takes the time; the 30-minute figure above does not apply here.

### T-27 xAI Grok Build (6 pts)

- **Scenario**: xAI Grok Build (current version) × a pinned Grok model × fresh session × empty directory; the headless JSON output is the natural machine evidence.
- **You need**: a SuperGrok subscription or an xAI API key; record the route honestly.
- **Why this is a priority**: fills the Grok model-family gap with a first-party harness; usage output is fully machine-readable (per-model calls, cache buckets, and on the API path a total cost figure), which also exercises the derived monetary cost rule in CONTRIBUTING.
- **Surface note**: this task covers the terminal version of Grok Build. The web/mobile "Build" added by xAI on 2026-08-19 is a different surface and is out of scope; propose it separately.
- **Effort**: expect about 2–4 hours of real work — working out the usage exposure and the redaction points is what takes the time; the 30-minute figure above does not apply here.

### T-28 Kiro (6 pts)

- **Scenario**: Kiro (current version) × one declared surface (IDE or CLI) × the product default or an explicitly pinned model × fresh session × empty directory; record the credit shown when each interaction ends as the native unit.
- **You need**: a Kiro account.
- **Why this is a priority**: AWS's flagship agentic IDE/CLI and the designated successor to Amazon Q Developer, whose end of support is announced for 2027-04-30 and whose new subscriptions stop on 2026-05-15. Kiro meters credits to 0.01 and shows each interaction's charge immediately, while officially billing per request without a token-level receipt — keep credits as the native unit. One subscription spans IDE, CLI, and web surfaces, naturally setting up T-35.
- **Points**: 6 pts for the first Kiro harness sample.
- **Effort**: expect about 2–4 hours of real work — working out the usage exposure and the redaction points is what takes the time; the 30-minute figure above does not apply here.

### T-29 Meta Muse Code (6 pts)

- **Scenario**: Meta Muse Code (current beta) × Muse Spark 1.2 × fresh session × empty directory; record the selected pricing tier and preserve the local event log covering model calls, tool runs, approvals, and edits.
- **You need**: a Meta developer account.
- **Why this is a priority**: Meta's first-party terminal coding agent, released on 2026-08-05, offers unusually transparent local evidence. A lower-priced "Contributor" data-exchange tier has only secondary reporting and no verified official price sheet; if you use it, state the tier evidence status in the package. A standard-vs-Contributor comparison should become a separate task only after the official pricing can be verified.
- **Points**: 6 pts for the first Meta Muse Code harness sample.
- **Effort**: expect about 2–4 hours of real work — working out the usage exposure and the redaction points is what takes the time; the 30-minute figure above does not apply here.

### T-23 Your pick: another Agent you use day to day (4 pts)

- **Scenario**: Cline, TraeCode, Aider, OpenHands, Zed, or another Agent product you genuinely use.
- **Why this is a priority**: the as-used configurations of real users have the most real-world relevance. For one of the products named above, open a claim issue and start. For any other product, open a proposal first and align on it, having confirmed under the [scenario identity rules](../CONTRIBUTING.md#what-counts-as-one-scenario) that it is a new scenario.
- **Points**: 4 pts for the first merged sample of each named product (Cline, TraeCode, Aider, OpenHands, Zed) — no prior approval needed; claim and start. Any other product needs a proposal first: the maintainer prices it under the fixed 3/4/6-point rubric above, and it is worth 0 before that reply.
- **Native-agent condition**: Named products must be measured on their own native agent; running Claude Code, Codex, or another external agent inside a host (for example via Zed or OpenHands acting as an ACP client) is a sample of that external agent, not of the host.
- **Effort**: expect about 1–2 hours — you already use the tool every day, so the time goes into locating the usage fields and the redaction points, not into learning the product; the 30-minute figure above still does not apply.

---

## D. Harness variable studies: weighing the components of the harness directly (difficulty ★★)

If your research interest is the Agent harness itself, this group of tasks is the most directly relevant: a set of on/off comparisons under the same product and the same model, where **the difference corresponds directly to the marginal token cost of one specific harness component**. Background: [contributor walkthrough — Why this is worth doing](contributor-walkthrough.md#why-this-is-worth-doing).

### T-31 MCP on/off comparison (2 scenarios) (8 pts)

- **Scenario**: same product, same model and effort, 3 attempts each in two states: "with a specific MCP server configured" and "with that MCP removed". Choosing an MCP server with many tools makes the effect clearer.
- **Validity condition**: the MCP side's schema must be non-empty, with tools actually registered.
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
- **Inventory evidence**: the `as-used` side must submit a rules/MCP/skills/memory inventory snapshot and its hash.
- **Effort**: expect about 2–4 hours of real work across both sides; the 30-minute figure above does not apply here.

### T-33 fresh vs resumed session (2 scenarios) (8 pts)

- **Scenario**: same product and model: one group as normal fresh runs; for the other group, first create a session containing only one `hi` round trip, exit, then resume and send `hi` again.
- **Why this is a priority**: observes how history injection and cache reads behave when a session is resumed; there is currently no data at all.
- **Effort**: expect about 2–4 hours of real work across both sides; the 30-minute figure above does not apply here.

### T-35 Same vendor, different surface (2 scenarios) (8 pts)

- **Scenario**: same vendor, same account, same pinned model, same empty-workspace setup — one scenario on surface A (for example the CLI), one on surface B (the desktop app or IDE extension). Natural first pairs: Antigravity CLI vs Antigravity desktop/IDE; Codex CLI vs the Codex IDE extension; Copilot CLI vs Copilot IDE Chat.
- **Why this is a priority**: with backend and model held constant, any difference in injected tokens is pure client-surface harness difference — system prompt, tool schema, workspace bootstrap. Whether different surfaces of the same product are "the same thing" is one of the most-asked questions in the community.
- **Points**: 8 pts per completed pair, after both sides merge; a single side is priced at whatever tier it satisfies on its own.
- **Effort**: expect about 2–4 hours of real work across both sides; the 30-minute figure above does not apply here.

### T-36 Same model, different harness (2 scenarios) (8 pts)

- **Scenario**: pin one exact model via BYOK or the official API, then run the standard protocol through two different harnesses (for example Claude Code vs OpenCode, or OpenCode vs Aider); everything else held as close as the products allow. Optionally add further harnesses on the same model — fix the harness list in your claim first.
- **Why this is a priority**: the mirror image of T-62 (harness constant, backend varying): here the model is constant and the harness varies, so the input-token delta is a direct head-to-head measurement of harness overhead — the project's core question. Community anecdotes put the spread at up to tens of times, with no uniform-protocol data.
- **Points**: 8 pts per completed pair; +3 pts for each additional harness side declared in the claim, after it merges.
- **Effort**: expect about 2–4 hours of real work across both sides; the 30-minute figure above does not apply here.

### T-37 Built-in tools and skills on/off (2 scenarios) (8 pts)

- **Scenario**: same product, model, and effort; side A with the product's built-in tools/skills/plugins at a fixed, documented set, side B with them minimized or disabled as far as the product allows. MCP stays unchanged (off) on both sides — this task isolates the product's own tool schema, where T-31 isolates external MCP. Use the `custom` harness profile and publish the exact inventory.
- **Validity condition**: prove that the switch actually changed the injected configuration, rather than merely changing a UI toggle.
- **Why this is a priority**: built-in tool and skill definitions enter the context before you type anything; how much of the "free" `hi` they eat is a top community question, separate from external MCP cost.
- **Points**: 8 pts per completed pair, after both sides merge.
- **Effort**: expect about 2–4 hours of real work across both sides; the 30-minute figure above does not apply here.

### T-38 Receipt vs vendor billing reconciliation (5 pts per pair)

- **Scenario**: run the standard three-attempt protocol for one scenario while collecting both sides of the measurement: the client/harness-reported receipt (tokens, credits, or cost) and the vendor billing or admin usage record (for example GitHub AI Credits usage, a Kiro account page, Tencent Credits detail, or an API bill); reconcile them and document any semantic difference.
- **You need**: a product and account that expose both a per-run client receipt and a vendor-side billing or admin usage record.
- **Why this is a priority**: usage semantics are diverging across vendors — GitHub, for example, explicitly treats `ai_credits_used` as an aggregate metric rather than a bill. This task calibrates the whole measurement instrument, not merely one more data point.
- **Points**: 5 pts per pair, awarded only when both evidence sides are complete.
- **Effort**: expect about 2–4 hours of real work — collecting and reconciling both evidence surfaces is what takes the time; the 30-minute figure above does not apply here.

---

## E. New input cases (open an issue first to align with the maintainers)

### T-40 hi-zh-v1: Chinese "你好" (4 pts)

- **Scenario**: any existing harness × the new input case "你好".
- **Note**: a new input is a protocol-level change — the exact original text, encoding, byte sequence, and SHA-256 must be defined first, with a new `prompts/` file created and a case ID decided. **Open an issue to finalize this before measuring**; do not just send a Chinese sentence as you understand it and submit.
- **Why this is a priority**: whether the input language affects harness injection (e.g. language detection, reply length) is a question of direct interest to bilingual Chinese/English users.
- **Points**: 4 pts covers both halves — the new input case definition and the first scenario package that uses it.

### T-41 Probe L1: exact-reply case (4 pts)

- **Scenario**: define a fixed instruction-style input intended to make the agent reply with exactly `OK` and use no tools. The exact bytes, encoding, and SHA-256 must first be aligned with the maintainers in an issue, then written into `prompts/`. The first package consists of 3 standard runs under any anchor combination.
- **Why this is a priority**: `hi` is a greeting, and products branch in how they handle greetings. L1 constrains the output to the shortest form and minimizes semantic branching, making it a purer ruler for harness injection than `hi`; the two cases serve as controls for each other.
- **Points**: 4 pts covers the case definition and first package. Later packages follow the +1 probe add-on rule.

### T-42 Probe L2: fixed file-read case (4 pts)

- **Scenario**: define a minimal fixed task: place a byte-for-byte fixed small fixture file in the workspace, then ask the agent to read it and return a specified field. First align the fixture's and input's exact bytes in an issue, then publish them with the case definition. The first package consists of 3 standard runs under any anchor combination.
- **Why this is a priority**: neither `hi` nor L1 triggers a tool. L2 measures the marginal cost of one deterministic tool call, separating tool-definition cost (measured by T-31 and T-37) from tool-invocation cost.
- **Points**: as for T-41, 4 pts covers the case definition and first package; later packages follow the +1 probe add-on rule.

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

### T-52 Different gateways, same model label (6 pts)

- **Scenario**: same harness, same model label, one group each on two different gateways.
- **Why this is a priority**: if the two gateways show clearly different token/latency distributions for the same model label, that is itself an observation worth publishing; if they agree, it strengthens the indirect evidence that the label is credible.
- **Points**: 6 pts per pair for an isolated two-gateway comparison without an official anchor. If it forms a star design with an already merged T-50 official side, each additional gateway side is +3 pts; declare the star in the claim.
- **Effort**: expect about 2–4 hours of real work across both sides; the 30-minute figure above does not apply here.

---

## G. Chinese model ecosystem: GLM, Kimi, MiniMax, Qwen, DeepSeek (difficulty ★★–★★★)

In the existing data, Chinese models have only appeared through WorkBuddy's Auto routing (GLM-5.2, DeepSeek-V4-Flash). These vendors all have official Agent carriers or official compatible endpoints of their own, and are worth bringing under observation one by one. Product forms iterate quickly: treat the actual product form at the time you claim as authoritative, record the exact version, subscription, and route classification honestly, and if the route classification is unclear, describe the actual chain in the PR.

When a group offers multiple options, pick the combination you judge to be the most popular with the most users right now.

### T-60 Qwen Code CLI × Qwen (6 pts)

- **Scenario**: official Qwen Code CLI × default or explicitly pinned Qwen model × official account quota × fresh session.
- **Why this is a priority**: an official open-source CLI harness with a low free-quota barrier, well suited as the first entry in group G; its harness shares a common origin with Gemini CLI, so it can later form a structurally matched comparison with T-20.
- **Route note**: the free OAuth tier ended on 2026-04-15; record the actual authentication and billing route (Coding Plan, API key, etc.), which is part of the pricing bucket.

### T-61 Kimi Code CLI (6 pts)

- **Scenario**: the new Kimi Code CLI introduced in May 2026 (the Node/TypeScript rewrite) × a pinned Kimi model × fresh session. The old Python `kimi-cli` is no longer officially maintained and must not be used.
- **Why this is a priority**: there is currently no public sample at all of Kimi's subscription/quota model or its token exposure.

### T-62 GLM × Claude Code compatible endpoint (3 pts)

- **Scenario**: Zhipu's official coding subscription connected to Claude Code via its Anthropic-compatible endpoint × pinned GLM model, everything else aligned with the existing Claude Code reference samples.
- **Why this is a priority**: the same Claude Code harness, connected to Anthropic's official service on one side and GLM's official endpoint on the other — a clean **harness-constant, backend-varying** comparison, directly comparable with the existing Claude Code reference samples on input injection and cache behavior. Record claimed and observed models separately. Under the rubric this is a backend substitution (3 pts), not a new-harness first sample; for Z.ai's first-party agent, see T-67 ZCode.

### T-63 MiniMax Code (6 pts)

- **Scenario**: the first-party MiniMax Code product (current version) × default or explicitly pinned MiniMax model × fresh session; record the actual product form and metering units.
- **Why this is a priority**: there are no samples yet of MiniMax Code's first-party Agent form or its metering units.
- **Points**: 6 pts for the first sample of the first-party MiniMax Code product. Connecting a MiniMax model to a third-party harness (for example, × Claude Code) follows the rubric at 3 pts through a proposal.

### T-65 DeepSeek (6 or 3 pts)

- **Scenario**: DeepSeek's official agent product if one exists, or a pinned DeepSeek model connected to a harness via its official compatible endpoint × fresh session; record the actual product form and the route classification honestly.
- **Why this is a priority**: the most widely used Chinese model family, yet so far it has only appeared in this dataset as a WorkBuddy Auto routing outcome (DeepSeek-V4-Flash in one attempt); its official quota/billing model and token exposure have no dedicated sample. A pinned-DeepSeek scenario also gives the existing Auto observation something to be compared against.
- **Points**: 6 pts for the first sample of a first-party DeepSeek harness; 3 pts for DeepSeek × Claude Code via the compatible endpoint (the current official coding-agent documentation uses this route). The actual product form determines the price when claimed and must be written into the claim.

### T-66 Tencent CodeBuddy Code (6 pts)

- **Scenario**: Tencent CodeBuddy Code (current version) × one declared first-party surface (plugin, IDE, or CodeBuddy Code CLI) × default or explicitly pinned model × fresh session × empty directory; record the native Credits and the shared-quota scope honestly.
- **You need**: a Tencent CodeBuddy Code account with access to one of its first-party surfaces.
- **Why this is a priority**: this is Tencent's first-party development product and a different product surface from the already measured WorkBuddy, despite belonging to the same Buddy family. Official billing makes CodeBuddy Code and WorkBuddy share Credits under the same account, so `quota_shared_scope` must identify that pool. The CLI also exposes `/cost` and has cost-management documentation; a same-account comparison with WorkBuddy is a high-value follow-up pair that can be proposed separately.
- **Points**: 6 pts for the first Tencent CodeBuddy Code harness sample.
- **Effort**: expect about 2–4 hours of real work — working out the usage exposure, shared quota, and redaction points is what takes the time; the 30-minute figure above does not apply here.

### T-67 ZCode (6 pts)

- **Scenario**: ZCode (current version) × one pinned model × one declared Z.ai subscription or billing route × fresh session × empty directory.
- **You need**: a Z.ai account with ZCode access.
- **Why this is a priority**: Z.ai's own first-party coding agent was still shipping rapidly in August 2026. With the model and subscription route pinned, it forms a natural comparison against T-62, which puts GLM behind Claude Code as a 3-point compatible-endpoint substitution: first-party harness vs endpoint substitution.
- **Points**: 6 pts for the first ZCode harness sample.
- **Effort**: expect about 2–4 hours of real work — working out the usage exposure and the redaction points is what takes the time; the 30-minute figure above does not apply here.

### T-64 Locally self-hosted open weights (difficulty ★★★) (6 pts)

- **Scenario**: open weights (e.g. the open versions of GLM or Qwen) deployed locally via vLLM or Ollama, connected to any open-source harness; record the route as `self-hosted`.
- **Why this is a priority**: this is the only route where both ends — "the raw request" and "the metering" — are visible at the same time: the prompt token counts in the inference server logs can be reconciled word for word against the harness's injection, the cleanest way of weighing the harness. Requires some local deployment experience and hardware.
- **Points**: 6 pts applies to one self-hosted stack, priced in advance in your claim issue; further stacks are not priced by default.
- **Stack freeze**: freeze the entire stack — model checkpoint/hash, quantization, serving runtime and version, GPU, context settings, and sampling/tool support. A later quantization or runtime change is a variable task that needs a proposal (2–3 pts), not another 6-point first sample.
- **Effort**: expect about 2–4 hours of real work — working out the usage exposure and the redaction points is what takes the time; the 30-minute figure above does not apply here.

---

## H. Recently shipped harnesses (difficulty ★★★)

This group covers product lines newly released or newly surfaced in the second half of 2026. Prices follow the rubric; products are moving quickly, so the actual form at claim time is authoritative.

### T-70 Devin CLI (6 pts)

- **Scenario**: Devin CLI (current version) × the product default or an explicitly pinned model × fresh session × empty directory; record the subscription and native ACU usage honestly.
- **You need**: a Devin account with Local/CLI access.
- **Why this is a priority**: in Cognition's current product line, Windsurf joined Devin Desktop on 2026-06-02 and Cascade is deprecated, so old-product captures are out of scope. Devin Local and CLI share the next-generation harness and meter in ACUs; a T-35 same-vendor pair with Devin Desktop is a natural follow-up.
- **Points**: 6 pts for the first Devin CLI harness sample.
- **Effort**: expect about 2–4 hours of real work — working out the usage exposure and the redaction points is what takes the time; the 30-minute figure above does not apply here.

### T-71 Mistral Vibe (conditional 4 pts)

- **Scenario**: Mistral Vibe version 2.23.3 or later × one explicitly pinned provider and model × fresh session × empty directory; collect provider-reported token usage for every run.
- **You need**: a Mistral Vibe install plus provider access that can expose stable per-run token usage.
- **Why this is a priority**: Mistral's official CLI adds a mature-vendor harness to the list, but its locally calculated USD cost is explicitly indicative. Record that amount only as `indicative`, never as canonical monetary cost.
- **Points**: 4 pts only if the package proves that stable provider-reported token usage can be collected per run; otherwise handle it through a proposal.
- **Effort**: expect about 2–4 hours of real work — proving the per-run token receipt and its semantics is what takes the time; the 30-minute figure above does not apply here.

### T-72 Warp Agent CLI (6 pts)

- **Scenario**: Warp Agent CLI (current version) × the product default or an explicitly pinned model × fresh session × empty directory; use `/usage` to record plan and per-turn credit consumption.
- **You need**: a Warp account with Agent CLI access, any tier.
- **Why this is a priority**: the standalone Agent CLI released on 2026-08-04 works in any terminal, and since 2026-08-25 its `/usage` output exposes plan and credit usage under per-turn credit billing. Do not collect the deprecated Oz or old `warp-cli`, which this product replaces.
- **Points**: 6 pts for the first Warp Agent CLI harness sample; this replaces Warp's former 4-point named slot in T-23.
- **Effort**: expect about 2–4 hours of real work — working out the usage exposure and the redaction points is what takes the time; the 30-minute figure above does not apply here.

---

## Want to do a scenario not on this list?

Welcome. Open an issue describing your combination (product × version × model × effort × subscription × route × session state × harness), and check against the [scenario identity rules](../CONTRIBUTING.md#what-counts-as-one-scenario) that it is a new scenario. The list is continuously updated as tasks are claimed and completed.

---

## Points ledger

The maintainer appends one row here when a PR is merged. Corrections are handled by appending an offsetting row; historical rows are never edited. A contributor's total is the sum of their rows.

| Date | Contributor | Task | PR | Points | Note |
| --- | --- | --- | --- | ---: | --- |
| 2026-08-30 | [@beautyarbutin](https://github.com/beautyarbutin) | T-16 | [#13](https://github.com/aicodingresearch/agent-hi-tax/pull/13) | 4 | First Codex CLI Windows package; claimed as T-01 ([#7](https://github.com/aicodingresearch/agent-hi-tax/issues/7)), priced once at the highest qualifying tier (T-16) |
| 2026-08-30 | [@beautyarbutin](https://github.com/beautyarbutin) | T-24 | [#20](https://github.com/aicodingresearch/agent-hi-tax/pull/20) | 6 | First Google Antigravity CLI sample and first Antigravity CLI Windows package; priced once at the higher T-24 tier, with no T-16 stacking |
| 2026-08-31 | [@AHMEDALATTAR416](https://github.com/AHMEDALATTAR416) | T-62 | [#25](https://github.com/aicodingresearch/agent-hi-tax/pull/25) | 3 | GLM official Anthropic-compatible endpoint behind Claude Code; claimed as T-62 ([#16](https://github.com/aicodingresearch/agent-hi-tax/issues/16)) and priced as a backend substitution, with no T-16 stacking because the package changes more than the platform |
