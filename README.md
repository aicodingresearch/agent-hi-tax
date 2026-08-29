# Agent Hi Tax

**English** | [中文](README.zh-CN.md)

> Observing the full-stack cost of a single `hi`.

Some people have noticed that after sending nothing but a `hi` to an AI agent, their subscription quota dropped by 1% or even more.

That may come from model inference, or from the rules, tools, skills, MCP, workspace context, session history, caching strategy, or billing rounding the agent loads at startup. Agent Hi Tax wants to do one simple, interesting thing: record these real observations under a single, uniform set of rules.

We are in no hurry to decide which agent is "best". First we take a smaller question seriously:

> In a well-defined, reviewable environment, when the exact same input is sent, what actually happens — and what does it consume?

[View the Hi Tax Index: a combined comparison of all agent scenarios](RESULTS.md) | [Contribute via the shortest path](CONTRIBUTING.md#shortest-path-for-external-contributors)

## What this is

Agent Hi Tax is a community-maintained, evidence-based repository for observing AI agent consumption.

Any agent product is in scope — CLI, IDE, desktop, or web, first-party or third-party, official subscription or self-hosted. The products already sampled are simply where we started; there is no fixed list of accepted agents.

Every test records a complete scenario, including:

- which agent and which carrier were used;
- the exact version of the agent;
- which model was used;
- the reasoning effort or thinking tier;
- Plus, Pro, Max, Team, API, or another billing method;
- official subscription, official API, third-party gateway, or local self-hosted routing;
- a fresh, warm, or resumed session;
- workspace, rule files, tools, plugins, skills, MCP, and hooks;
- the exact input, the visible reply, and latency;
- tokens, credits, quota percentage, request counts, or other native consumption units;
- before/after screenshots, machine logs, and file hashes.

A run can be reduced to the following chain:

```text
exact input
  → agent product and harness
  → session, rules, tools, and workspace context
  → model, effort, and request routing
  → reply, tokens, credits, quota, and latency
  → redacted evidence package
```

The "Tax" here is a tongue-in-cheek name for the observable overhead a minimal input incurs when passing through a full agent system; it does not refer to a tax in any legal or financial sense.

## What this is not

This project is not:

- a benchmark of model intelligence or coding ability;
- a general price list for model APIs;
- a simple leaderboard across vendors;
- a tool for back-deriving exact token counts from subscription quota percentages;
- a system that provides absolute guarantees of authenticity for screenshots, logs, or contributor identity.

A single result describes the complete execution stack at that moment; it cannot be automatically generalized into "this underlying model always needs this many tokens".

Different native units must not be forcibly mixed either. Tokens, subscription percentages, credits, request counts, and currency should be presented separately, and converted only when a public, precise conversion basis exists.

## The first reference sample

The first reference sample is complete: official Codex CLI 0.147.0, `gpt-5.6-sol`, `high`, ChatGPT Pro 20x, macOS arm64, an `as-used` harness, running 3 consecutive fresh-session tests with the exact same `hi`.

![Codex CLI first hi-en-v1 reference sample reply](runs/2026-08-14/codex-cli-0.147.0_gpt-5.6-sol_high_hi-en-v1_as-used_mac-arm64/attempts/r3/response.png)

| Metric | R1 | R2 | R3 |
| --- | ---: | ---: | ---: |
| Input (incl. cached input) | 13,950 | 13,950 | 13,950 |
| Cached input | 5,888 | 0 | 9,984 |
| Output | 14 | 13 | 14 |
| Context total | 13,964 | 13,963 | 13,964 |
| Total under the CLI's display semantics (non-cached input + output) | 8,076¹ | 13,963 | 3,980 |

The most interesting finding is not any single isolated number, but this: the input context of the same harness is stable at about 13.95K tokens, while automatic caching makes the CLI-displayed total fluctuate widely. That total cannot be read directly as subscription quota cost.

¹ R1 did not save an exit-screen screenshot; this value is deterministically derived from public event fields. R2 and R3 have both event records and private original exit screenshots.

See the [full reference sample, raw semantics, and public evidence](runs/2026-08-14/codex-cli-0.147.0_gpt-5.6-sol_high_hi-en-v1_as-used_mac-arm64/README.md), and the [process revisions from the first round of real testing](docs/first-sample-lessons.zh-CN.md) (Chinese).

## The second reference sample

The second reference sample uses official Claude Code 2.1.220, `claude-fable-5`, `high`, Claude Max, macOS arm64, and an `as-used` harness that keeps the real user configuration, likewise executing 3 sequential fresh-session `hi` runs.

| Metric | R1 | R2 | R3 |
| --- | ---: | ---: | ---: |
| Native plain input | 2 | 2 | 2 |
| Cache creation input | 25,441 | 25,006 | 25,006 |
| Cache read input | 0 | 0 | 0 |
| Derived total input | 25,443 | 25,008 | 25,008 |
| Native output | 30 | 37 | 37 |
| Context total | 25,473 | 25,045 | 25,045 |
| UI whole-second duration | 5 s | 8 s | 6 s |

The visible reply was identical across all three runs: `Hi! What can I help you with today?`. The most striking "Hi Tax": the plain input behind two visible characters is only 2 tokens, yet the first request also created a roughly 25K one-hour cache.

Claude's three input fields are additive, unlike the first Codex sample, where cached input is a subset of input. The project accordingly upgraded the attempt template and validator, and no longer tries to explain one vendor's total with another vendor's.

See the [full Claude Code reference sample](runs/2026-08-15/claude-code-2.1.220_claude-fable-5_high_hi-en-v1_as-used_mac-arm64/README.md), and the [second round of process revisions](docs/second-sample-lessons.zh-CN.md) (Chinese).

## The third reference sample and the latest process lessons

The third reference sample keeps Claude Code 2.1.220 and `high` effort, but switches the model to `claude-opus-5`. The three derived total inputs were 24,837, 24,666, and 24,600 tokens, and the replies showed three short text variants.

This sample's most important contribution is not the inter-model delta, but a confounding variable discovered in the screenshots: the Fable sample's footer reads `bypass permissions on`, while the Opus sample's reads `manual mode on`. The 342-token difference in median total input between the two is therefore explicitly marked `mode-confounded` and cannot be attributed to the model. The contribution process accordingly gained a three-run consistency check on permission/footer mode, plus comparison/confounder fields in the manifest.

See the [full Opus reference sample and public redacted evidence](runs/2026-08-15/claude-code-2.1.220_claude-opus-5_high_hi-en-v1_as-used_mac-arm64/README.md).

## The fourth reference sample: WorkBuddy Auto routing

The fourth reference sample uses the WorkBuddy 5.3.13 desktop IDE with the fixed selection `Auto / 日常办公 / 允许完全访问` (Auto / everyday office / allow full access), manually submitting `hi` in three independent empty directories and fresh sessions.

| Metric | R1 | R2 | R3 |
| --- | ---: | ---: | ---: |
| Actual model | GLM-5.2 | GLM-5.2 | DeepSeek-V4-Flash |
| Input (incl. cached) | 32,119 | 33,043 | 33,193 |
| Cached input | 9,920 | 9,920 | 8,960 |
| Output | 382 | 436 | 631 |
| Context total | 32,501 | 33,479 | 33,824 |
| WorkBuddy credits | 4.46 | 4.66 | 0.74 |
| Event duration | 11.628 s | 8.470 s | 7.893 s |

It brought two new methodological lessons. First, when `Auto` is the fixed selection, the requested model is a scenario variable, while the actually routed model is a per-run result. Second, an empty directory is not an empty harness: R2 still read the global Git identity, and R3 even treated the workspace basename as task semantics. The public evidence has been deterministically redacted.

See the [full WorkBuddy reference sample, credit cross-check, and public visual evidence](runs/2026-08-15/workbuddy-5.3.13_auto_craft_hi-en-v1_as-used_mac-arm64/README.md).

## How a result is identified

A test scenario is jointly determined by this set of variables:

```text
protocol
× input
× agent / carrier / version
× auth / billing / subscription
× request routing
× requested / observed model
× requested / observed effort
× session / workspace / harness state
```

A change in any one of them should be treated as a different scenario. The same scenario independently replicated by different contributors counts as a valuable repeated observation.

## The first standard input

The project's first standard test case is:

```text
case_id: hi-en-v1
encoding: UTF-8
exact_input: hi
bytes_hex: 68 69
leading_whitespace: false
trailing_whitespace: false
```

Other inputs — a Chinese greeting, a short question, a tool-call request, a repository task — can be added later. Every input must keep its exact original text, its own case ID, byte count, and SHA-256; translated or polished text is a different test case.

## Evidence principles

The project uses three package-level evidence levels:

- **Level A: machine records + visual evidence.** Includes redacted native usage/event logs, plus screenshots or recordings sufficient to connect configuration, input, and reply.
- **Level B: visual evidence.** Includes screenshots or a continuous recording sufficient to connect configuration, input, and reply, but no publishable machine records.
- **Level C: self-reported data.** Can serve as a discussion lead or a scenario awaiting replication, but does not enter the evidence-backed comparison dataset until evidence is added.

Level A visual evidence can be public redacted images, or private originals that a maintainer has checked and for which only hashes are registered. The latter must additionally be marked `visual_evidence_access: private_evidence`; its public reviewability is weaker than that of public redacted images, and the original-image hashes must not be described as public proof.

Evidence level is not a PR gate. Provide whatever evidence you can obtain; when the product does not expose it, the contributor did not capture it, or publishing it would leak private information, keep the record and mark it `not_exposed`, `not_provided`, `private_evidence`, or `self_reported`. A missing screenshot does not automatically invalidate a genuine contribution, but it does lower the strength of the conclusions the corresponding fields can support.

Whichever level applies, the following principles hold:

1. record requested model/effort and observed model/effort separately;
2. always record the subscription plan, without presupposing that it must make a difference;
3. present official-product, official-API, third-party-gateway, and self-hosted results in separate groups;
4. keep vendors' native effort and usage units; do not normalize on your own;
5. when machine logs conflict with the UI, keep both; do not pick the better-looking one;
6. screenshots and logs improve auditability, but must not be overstated as cryptographic proof;
7. all public evidence must be redacted first; never commit keys, tokens, cookies, account identifiers, or private content.

Full rules are in the [contributing guide](CONTRIBUTING.md).

## Current status

The project is currently in a manual pilot phase. The maintainer has completed four reference samples following the "external contributor" path, and keeps using the real process to check:

- whether the scenario variables are sufficient;
- whether screenshots and logs can be tied to the same run;
- whether the redaction process is realistic;
- whether the manifest is easy to fill in;
- whether PRs are easy to review;
- which fields are in practice unobtainable from the product.

Current progress:

- [x] Chinese contribution protocol and manual-pilot manifest
- [x] First `hi-en-v1` reference sample with 3 repeats
- [x] Second sample on a different agent: Claude Code / Fable 5 / high
- [x] Third sample: Claude Code / Opus 5 / high, with a mode-confounding audit
- [x] Fourth sample: WorkBuddy / Auto / craft, with auto-routing, credit, and global-context audits
- [x] Protocol, evidence tiering, and token semantics revised after the first sample
- [x] Codex / Claude / WorkBuddy capture adapters, vendor-native token semantics, auto-routing, and comparison fields added after samples two through four
- [ ] Machine-verifiable formal schema
- [x] First version of the package layout and basic validation scripts
- [x] Auto-generated Hi Tax Index and pull request consistency checks
- [x] Shortest path for external contributors, template notes, and pull request template
- [ ] Automated capture and deterministic redaction helpers
- [x] Wanted-scenario list and contributor walkthrough
- [x] Scenario-claim, proposal, and data-correction issue templates
- [x] Licensing, security reporting, and open-source repository setup
- [ ] Charts and an interactive visualization page
- [x] Bilingual core documentation (English-primary)
- [ ] English versions of adapter docs and process retrospectives

## Repository layout

Current layout:

```text
README.md             project entry point and basic overview
*.zh-CN.md            Chinese versions of the corresponding documents
RESULTS.md            auto-generated cross-agent summary index
CONTRIBUTING.md       contribution process and evidence rules
SECURITY.md           private reporting for leaked evidence and takedowns
LICENSE               Apache-2.0, covering scripts/ and workflows
LICENSE-DATA          CC BY 4.0, covering data and documentation
prompts/              versioned standard input cases
templates/            scenario and per-attempt templates
runs/                 public scenario packages, redacted and checked
scripts/              index generation, package integrity, hash, and privacy-lead checks
docs/                 method notes and process retrospectives
.github/              pull request template and automated consistency checks
```

The formal schema, automated capture, and interactive visualization will be finalized only after more agent samples are complete, to avoid locking the whole project into the fields of the first product.

## How to participate

First-time contributors are encouraged to claim a concrete task directly from the [wanted-scenario list](docs/wanted-scenarios.md), then follow the [contributor walkthrough](docs/contributor-walkthrough.md) from start to submission.

Private-pilot invitees should read the [internal pilot notes](docs/internal-pilot.md) before accepting the repository invitation.

If you would like to contribute a test:

1. read the [contributing guide](CONTRIBUTING.md);
2. pick whichever existing adapter is closest — [Codex CLI](docs/adapters/codex-cli.zh-CN.md) (Chinese), [Claude Code](docs/adapters/claude-code.zh-CN.md) (Chinese), [WorkBuddy Desktop](docs/adapters/workbuddy-desktop.zh-CN.md) (Chinese) — or, for any other agent, the generic capture path in the contributing guide;
3. choose an existing scenario to replicate independently, or propose a new combination;
4. declare the scenario before executing; run at least 3 valid independent runs sequentially with identical settings;
5. save `manifest.yaml`, the exact input, the reply, screenshots, and any available machine logs as specified;
6. complete redaction, hashing, and the checklist;
7. submit one pull request per scenario (including all its repeated runs).

Replication is welcome. Independent observations at different times, with different versions, subscriptions, and real environments, are exactly what makes this project interesting over the long run.

## Languages

The project is bilingual with English as the primary language:

- English (primary): `README.md`, `CONTRIBUTING.md`, `RESULTS.md`, and docs without a language suffix;
- Chinese: the parallel `*.zh-CN.md` files.

Both languages share the same protocol version, schema, English machine fields, and data directories — one data system, not two. The capture adapters and process retrospectives under `docs/` are currently Chinese-only; translations are welcome. The language of a test input is an independent recorded variable, unaffected by documentation language.

## License

Two licenses, split by what the file is:

- **Data and documentation** — `runs/`, `prompts/`, `templates/`, `docs/`, and the `*.md` files: [CC BY 4.0](LICENSE-DATA). Reuse and adaptation are permitted, including commercially, with attribution. When citing a measurement, cite the scenario ID and the commit as well, so the number can be traced to a verified package.
- **Software** — `scripts/` and `.github/workflows/`: [Apache License 2.0](LICENSE).

Evidence packages contain screenshots of third-party agent products. Those licenses cover this project's own contribution — the selection, arrangement, annotation, and measurement data — not the vendors' trademarks or interface content, which appear here for factual research reporting. This project is not affiliated with, endorsed by, or sponsored by any observed vendor.

By opening a pull request you agree that your contribution is published under these licenses.

## Security and privacy

Found a credential, account email, session identifier, or private path in published evidence? **Report it privately** — see [SECURITY.md](SECURITY.md). Do not open a public issue and do not paste the exposed value anywhere public. Takedown requests for your own material are granted.

## How to interpret results correctly

If a test shows "quota dropped by 1% after sending a single `hi`", it strictly means:

> Under the account, time, agent, version, model, effort, session, routing, and usage-meter conditions of that recorded run, the interface displayed this one change.

It does not automatically mean:

- that the 1% was caused entirely by the two visible characters of `hi`;
- that all users will see a 1% drop;
- that another subscription tier must be the same, or must be different;
- that the 1% can be accurately converted into some token count;
- that the upstream model claimed by a third-party gateway has been independently verified;
- that a future version of the same product will still produce the same result.

This restraint does not make the project boring. On the contrary, it makes every seemingly absurd "Hi Tax" more worth discussing.

---

A single `hi` is small, but the agent stack behind it may not be small at all.
