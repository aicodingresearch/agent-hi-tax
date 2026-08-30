# Contributing to Agent Hi Tax

**English** | [中文](CONTRIBUTING.zh-CN.md)

> Use the same tiny input to observe what a real agent harness actually loads, displays, and consumes.

Agent Hi Tax is a lightweight but as-verifiable-as-possible observation project. It is not a model capability benchmark, and it is not a general price list. What we record is one complete execution stack: the agent product and version, the model, effort, subscription or API routing, session state, workspace, rules, skills, MCP, hooks, caching, and the tokens, credits, quota, and latency the product actually exposes.

English is the primary language of this guide. The Chinese version, [CONTRIBUTING.zh-CN.md](CONTRIBUTING.zh-CN.md), shares the same protocol version, templates, and data directories; machine fields are English in both.

## Shortest path for external contributors

If you want to pick a concrete task first, or need more hands-on step-by-step guidance, see the [wanted scenarios list](docs/wanted-scenarios.md) and the [contributor walkthrough](docs/contributor-walkthrough.md).

For your first contribution, follow this order:

1. Fork and clone this repository, and create a new branch for one scenario.
2. Pick a collection adapter, or take the generic path. **Any agent product is in scope** — CLI, IDE, desktop, or web. Adapters exist today for [Codex CLI](docs/adapters/codex-cli.zh-CN.md) (Chinese), [Claude Code](docs/adapters/claude-code.zh-CN.md) (Chinese), and [WorkBuddy Desktop](docs/adapters/workbuddy-desktop.zh-CN.md) (Chinese); that list records the products already sampled, not the products we accept. If yours has no adapter, collect according to the generic semantics on this page, describe the product differences in your PR, and — optionally — include a first draft of `docs/adapters/<product>.md`.
3. Pin the scenario and launch command first, then execute at least 3 fresh attempts sequentially; do not change the model, effort, permission mode, or plugin state mid-test.
4. Keep raw screenshots and raw session/transcripts outside the Git repository at first; only redacted copies and minimal machine events may enter the PR.
5. Copy the [scenario template](templates/scenario-manifest.yaml) and the [attempt template](templates/attempt-result.yaml), and refer to whichever of the [four complete reference samples](runs/README.md) is closest to your product.
6. Generate hashes, run `./scripts/verify-all.sh`, and submit using the repository's Pull Request template.

Do not parse internal logs you do not understand just to chase Level A. If all you have is screenshots, honestly submit Level B; when a field cannot be obtained, use the fixed missing-value states. Unredacted original images, account information, and session identifiers must never be uploaded first with the expectation that maintainers will delete them later.

## The six most important rules

1. **Do at least 3 valid independent runs per scenario.** Three sequential executions, never in parallel; each run uses a new session and a new workspace, unless the scenario itself is declared warm or resumed.
2. **Scenario variables do not change.** If the agent, version, model, effort, subscription, routing, prompt, or any part of the harness changes, split it into another scenario.
3. **Collect environment evidence only once.** Within the same set of three runs, do not repeatedly screenshot the version, system, subscription, and fixed configuration.
4. **Each run captures only its own results.** Save the exact input and the complete reply, plus whatever native usage or machine events you can obtain.
5. **Evidence you can get should be provided; evidence you cannot get does not block.** Missing, not exposed, kept only as a private original, or conflicting evidence must all be explicitly labeled; never fill in fields with guesses.
6. **Never treat one total as cost.** Cached input, non-cached input, output, credits, and subscription percentages must be stored separately; without a published conversion formula, do not convert.

## What counts as one scenario

Scenario identity is jointly determined by these variables:

```text
protocol version × prompt case
× agent / carrier / exact version
× auth / subscription / billing channel / routing
× requested and observed model
× requested and observed effort
× operating system / architecture
× session / workspace / harness profile
× rules, plugins, skills, MCP, hooks, and permission mode
```

For example, any of the following changes requires splitting into a new scenario:

- Codex CLI swapped for the Codex desktop app;
- an agent or plugin version upgrade;
- `medium` swapped for `high`;
- Plus swapped for Pro, or Pro swapped for Pro 20x;
- an official subscription swapped for the official API or a third-party gateway;
- macOS swapped for Windows;
- a fresh session swapped for a resume;
- an empty directory swapped for a repository containing `AGENTS.md`;
- toggling any skill, MCP, plugin, or hook that invokes a model.

Automatic cache hits are usually run results, not contributor-controlled scenario variables. As long as the caching policy was not deliberately changed, record each run's hit volume separately instead of splitting scenarios just because hit volumes differ.

Automatic model routing follows the same principle: when the contributor deliberately selects the product's `Auto`, the requested model `Auto` is the scenario variable and the actually routed model is a per-run result; three runs routed to different models still belong to the same Auto scenario. Contributors must record the actual model for each run, and avoid interpreting credit or token differences as fluctuation of the same underlying model. Only when a specific model is explicitly pinned does a model change require splitting the scenario or being marked as an execution error.

## Three harness profiles

Every scenario must choose one profile:

- `standard-clean`: new session, empty workspace, with no contributor-added project rules, MCP, plugins, skills, or hooks. Use it only if you have actually verified this.
- `as-used`: the contributor's real everyday configuration. It has genuine real-world value, but the known rules, skills, MCP, plugins, and hooks must be listed.
- `custom`: a purpose-built fixed fixture or configuration. When it can be made public, provide the fixture and an immutable commit.

Do not delete personal configuration just to earn the `standard-clean` label. When you cannot fully verify your global configuration, honestly use `as-used`.

## The standard input

The first standard case is [`hi-en-v1`](prompts/hi-en-v1.txt):

```text
Visible content: hi
Encoding: UTF-8
Bytes: 68 69
Byte count: 2
SHA-256: 8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4
Leading whitespace: none
Trailing whitespace: none
```

Enter/Return only submits; it is not part of the prompt. Do not capitalize, add punctuation, or append a newline.

Other inputs are welcome, but each exact input must have its own case ID, source text file, encoding, byte count, and SHA-256. A translation, a rewording, or a single added punctuation mark is a different case.

## Evidence tiers

### Package-level tiers

- **Level A — machine records + visual evidence:** redacted native usage/event records, together with screenshots or a screen recording that connect the configuration, the input, and the reply.
- **Level B — visual evidence:** sufficient screenshots or a continuous recording, but the product offers no usable machine records.
- **Level C — self-reported data:** the core publicly re-verifiable evidence is missing; it may be kept as an observation awaiting replication, but it does not enter comparisons among `verified` fields.

Level A visual evidence may be published, or it may be checked privately by maintainers with only hashes published. Private visual evidence must set `visual_evidence_access: private_evidence` and use `private_evidence` on a per-field basis; it still indicates that machine records and visual originals coexist, but its public re-verifiability is weaker than publishing redacted images, and the hash itself is not public proof.

### Field-level states

A package-level tier must not mask gaps in individual fields. For key fields, use separately:

- `verified`: supported by public evidence;
- `private_evidence`: a maintainer checked the original, but the original was not published for privacy reasons; only a hash or a redacted transcript is public;
- `self_reported`: a contributor claim without independent public evidence;
- `not_exposed`: the product does not expose it;
- `not_provided`: the product may expose it, but it was not obtained this time;
- `conflicted`: two sources contradict each other; both values are kept;
- `not_applicable`: not applicable to this scenario.

Incomplete evidence does not automatically block a PR. It only limits the conclusions this record can support. For example, token logs can still be recorded without a subscription screenshot, but the subscription tier can then only be marked `self_reported`; when shared quota is contaminated by other sessions, the session's own tokens can still be valid while the quota delta must be excluded.

## Evidence you only collect once

The three repetitions of one scenario share a single set of scenario-level evidence:

- the agent version command or product build;
- operating system, version, architecture, and UTC time;
- subscription tier, multiplier, or billing method;
- request routing: official subscription, official API, gateway, or self-hosted;
- the launch configuration for model and effort;
- the harness profile, plus the inventory of rules, plugins, skills, MCP, hooks, and permission mode;
- the CLI launch screen or the web configuration page.

When one screenshot proves several items, it can serve several purposes. Do not capture three identical sets of environment screenshots just because there are three repetitions.

Taking Codex CLI as an example, the preflight commands can be:

```sh
command -v codex
codex --version
sw_vers
uname -m
date -u '+%Y-%m-%dT%H:%M:%SZ'
```

On Windows or with other agents, use the equivalent native commands. When publishing transcripts, replace home paths with `~`; do not publish usernames, hostnames, email addresses, or account IDs.

## What to capture per attempt

Each valid run records at least:

- a unique attempt number;
- fresh, warm, or resumed state;
- the exact prompt;
- the complete visible reply;
- start and completion times, plus the timing method;
- the native usage fields the product exposes;
- errors, timeouts, tool calls, and manual approvals;
- if a quota change is being claimed, this run's before/after observations and their attribution state.

The recommended minimum visual evidence is one screenshot containing the input and the complete reply. Usage can be proven with an exit-screen screenshot, the product's usage page, a provider receipt, or a redacted machine log. When the product does not surface an item, label it; there is no requirement to fabricate a "complete" screenshot.

Latency values from the three sequential runs are descriptive metadata only. They do not support cross-product latency comparisons: latency is affected by time of day, load, and caching. Such a comparison requires a separate design with randomized interleaving across time blocks; this protocol does not support that class of conclusion.

## Standard execution flow

### 1. Pin the scenario

Copy [`templates/scenario-manifest.yaml`](templates/scenario-manifest.yaml) and first fill in the scenario variables you can determine and the planned repetition count. Pin the launch command; do not tweak parameters across the three attempts.

If you are testing shared subscription percentages, team quota, or gateway balances, first pause other tasks that draw on the same metering pool. You can still test if pausing is impossible, but the quota attribution must then be marked `contaminated`.

### 2. Prepare an evidence directory outside the workspace under test

Do not put screenshots, transcripts, or private originals into the empty directory under test. Use a temporary evidence directory outside the repository, and copy the public files into Git only after all runs have finished and redaction is complete.

All collection must be ordinary human use of the official interface or client: do not intercept or decrypt traffic, automate consumer accounts, reverse-engineer or modify the client, or bypass rate or quota limits. See [docs/tos-review.md](docs/tos-review.md) for the comparison between this method and each product's terms.

### 3. Run the environment preflight once

Run the version, system, architecture, and UTC time commands, and save one preflight screenshot. Also save evidence of the subscription, model, effort, and launch screen. Check whether hooks make additional model calls; if they do, they are part of the harness and must not be hidden.

Even when MCP is never actually invoked, its tool definitions may enter the context and affect input tokens, so record its startup state. The same applies to `AGENTS.md`, skills, plugins, and other rules.

For agent-specific commands, see the collection adapters written so far: [Codex CLI](docs/adapters/codex-cli.zh-CN.md) (Chinese), [Claude Code](docs/adapters/claude-code.zh-CN.md) (Chinese), and [WorkBuddy Desktop](docs/adapters/workbuddy-desktop.zh-CN.md) (Chinese). Any other agent is equally welcome: use the product's own equivalent of these commands, follow the generic semantics above, and state in your PR where the product's exposed fields differ. Adapters only standardize the collection actions; they do not require contributors to disable existing proxies, sandboxes, or account security measures for the sake of testing. Those settings are part of the scenario — keep them unchanged and record them truthfully.

### 4. Execute at least three sequential attempts

For R1, R2, and R3 in turn:

1. Create a separate new workspace; for empty-directory scenarios, confirm the directory is empty and is not a Git repository.
2. Start a new session. Fresh scenarios must not exit and then resume.
3. Confirm the model and effort before the first model request. Product-local commands such as `/status` may be used, but do not send extra chat messages.
4. Also confirm that the footer, permission, or execution mode does not change across the three attempts; if it does, create a new scenario or explicitly mark the run as confounded.
5. Send the exact prompt exactly once.
6. After the reply completes, screenshot the input and the complete reply.
7. Exit normally and save the native usage; keep the raw event log when obtainable.
8. Finish this run before starting the next; do not run the three attempts in parallel.

If a run involved a mistyped input, a resume, a parameter change, a non-empty directory, a network failure, or any extra interaction, keep it and mark it `invalid` or `error`, explain why, then append new attempts until there are at least 3 valid runs. Do not delete outliers, and do not keep only the three runs that used the fewest tokens.

### 5. Assemble the public scenario package

After all runs have finished, copy the templates and organize everything according to the [run package layout](#run-package-layout). From the raw logs, extract only the minimal events relevant to this scenario; keep times, model, effort, usage, and the reply, and remove accounts, absolute paths, session-resume identifiers, and unrelated content.

Do not guess product fields from a blank file. Copy the closest complete reference sample, then replace it with your own evidence and data:

- [Codex CLI 0.147.0 / GPT-5.6 Sol / high](runs/2026-08-14/codex-cli-0.147.0_gpt-5.6-sol_high_hi-en-v1_as-used_mac-arm64/README.md)
- [Claude Code 2.1.220 / Fable 5 / high](runs/2026-08-15/claude-code-2.1.220_claude-fable-5_high_hi-en-v1_as-used_mac-arm64/README.md)
- [Claude Code 2.1.220 / Opus 5 / high](runs/2026-08-15/claude-code-2.1.220_claude-opus-5_high_hi-en-v1_as-used_mac-arm64/README.md)
- [WorkBuddy 5.3.13 / Auto / craft](runs/2026-08-15/workbuddy-5.3.13_auto_craft_hi-en-v1_as-used_mac-arm64/README.md)

If the reference sample does not match your current product version, record the differences; do not change the meaning of native fields to make things "look consistent".

### 6. Generate hashes and verify

Once final edits and redaction are complete, generate `SHA256SUMS` in the scenario directory, then run:

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

On Linux without `shasum`, use `sha256sum`. Regenerate the hashes after any public file changes. The index pages [RESULTS.md](RESULTS.md) (English) and `RESULTS.zh-CN.md` (Chinese) are generated automatically from every scenario's manifest and `RESULTS.csv`; a single run of `python3 scripts/build-results-index.py` writes both. They must be rebuilt after adding or modifying a scenario, and the Pull Request check uses `verify-all.sh` to verify that neither has drifted.

## Token and quota semantics

A `total` from one product may not be the same thing as a `total` from another. Prefer preserving the native fields and their sources, then state derived formulas explicitly.

The first reference sample, Codex CLI 0.147.0, uses these fields:

- `input_tokens_including_cached`: all input reported by the event log; cached input is a subset of it;
- `cached_input_tokens`: cache-hit input;
- `non_cached_input_tokens`: all input minus cached input;
- `output_tokens`: output reported by the event log;
- `context_total_tokens`: all input plus output;
- `cli_total_excluding_cached`: the semantics of that version's exit screen, i.e. non-cached input plus output.

Do not add cached input on top of `input_tokens_including_cached` again — that double-counts. And do not call any of `cli_total_excluding_cached`, the API list price, or the subscription percentage the "true cost" unless the product has published an exact conversion.

The second reference sample, Claude Code 2.1.220, uses Anthropic's native fields:

- `input_tokens`: the native plain input bucket;
- `cache_creation_input_tokens`: the input bucket for cache created in this run;
- `cache_read_input_tokens`: the input bucket for cache read in this run;
- `total_input_tokens`: the derived total input, the sum of the three fields above;
- `output_tokens`: native output;
- `context_total_tokens`: derived total input plus output.

These three Anthropic input buckets are additive; do not treat cache creation/read as subsets of `input_tokens`. Anthropic's public usage documentation also explicitly computes total input as the sum of the three — see [Anthropic's official pricing and usage field documentation](https://docs.anthropic.com/en/docs/about-claude/pricing).

The cross-agent data layer therefore uses "native fields plus explicit derived formulas", not a source-less generic field named `total`. Write `not_applicable` for vendor fields that do not apply to a product, and `not_exposed` for fields the product does not expose.

For quota, credits, or balances, also record: the raw displayed value, the unit, the reset cycle, the observation time, and the sharing scope. If the same account, API project, team, or gateway balance has other activity, use:

```yaml
quota:
  attribution: contaminated
```

What is contaminated is the shared quota delta; it does not necessarily contaminate the current session's own machine token records.

### Derived monetary cost — only where an exact public price exists

When the route is `official-api`, also compute the monetary cost of each attempt: multiply each native usage bucket by the vendor's published price for that bucket — input, cache write, cache read, and output are usually priced differently, so never apply one flat rate. Record in the scenario package: the price-page link, the date you read it, the per-bucket prices used, the formula, the currency, and the resulting amount per attempt. Keep the amount as a derived field alongside — never in place of — the native token fields: prices change, and the snapshot is what keeps the number auditable later. For a `third-party-gateway` this is optional: if the gateway publishes a price table you may compute the same way, labelled as gateway-published pricing — exactly as trustworthy as the gateway's other claims. For subscriptions, credit systems, and `self-hosted` routes, write `not_applicable`; that is precisely what the no-conversion rule above protects.

### Measurement surface and attribution

The existing `usage.source` field records the measurement surface: `client-reported`, `provider-reported`, `billing-ledger`, or `self-reported`. Values from different measurement surfaces must be presented separately, not mixed into one figure.

Use one of four attribution levels when interpreting a measurement:

- `directly-observed`: the request contents were observed directly;
- `delta-attributed`: attribution comes from the difference produced by switching a condition on and off;
- `inferred`: the attribution is inferred rather than directly observed;
- `not-identifiable`: the available evidence cannot identify the attribution.

Any conclusion that crosses scenarios or measurement surfaces must state the attribution level it relies on, in the package README or PR description. This does not change the templates or add a required field.

A hash proves that a file was not changed after it was hashed; it does not prove that the measurement was interpreted correctly. Do not conflate the two.

## First-party products, official APIs, and gateways

The agent's publisher and the inference routing are two separate variables. Even an official agent can be configured to go through a third-party gateway.

Routing is uniformly classified as one of:

- `first-party-subscription`
- `first-party-product`: an official Agent product with its own account or credit system, rather than a per-seat model subscription or a bare API key (for example, WorkBuddy)
- `official-api`
- `third-party-gateway`
- `self-hosted`

A third-party gateway should additionally disclose its public name, public domain, compatible protocol, claimed upstream model, observable model, caching, fallback, and routing settings. Do not submit secrets, signature parameters, or credentials from endpoints. A model name returned by a gateway only proves that it returned that label; on its own it does not prove the upstream vendor.

## Run package layout

One scenario package contains the shared environment and all attempts:

```text
runs/YYYY-MM-DD/<scenario-id>/
  README.md
  manifest.yaml
  prompt.txt
  launch-command.txt             # CLI scenarios only
  RESULTS.csv
  SHA256SUMS
  evidence/
    environment.png              # scenario-level, only once
    subscription.png             # when applicable and obtainable
    preflight.txt
    private-evidence.md           # registers hashes of private originals only, no originals
  attempts/
    r1/
      result.yaml
      response.txt                # exact reply bytes
      response.png
      events.sanitized.jsonl      # when obtainable
    r2/
      ...
    r3/
      ...
```

Every newly submitted scenario package appends `_<github-handle>` to both the directory name and the manifest's `scenario.id` (for example, `..._mac-arm64_alice`). This makes package paths collision-free by construction, so several contributors replicating the same scenario on the same date need no coordination at all. The four existing reference samples predate this rule and keep their original names.

The scenario field template is [`templates/scenario-manifest.yaml`](templates/scenario-manifest.yaml), the per-attempt result template is [`templates/attempt-result.yaml`](templates/attempt-result.yaml), and template selection plus optional-field notes are in [`templates/README.md`](templates/README.md). The four complete examples are listed together in [`runs/README.md`](runs/README.md).

## Privacy and redaction

Never submit:

- API keys, access tokens, cookies, authorization headers, or gateway credentials;
- account email addresses, account IDs, payment information;
- Codex session IDs, resume commands, or other session-resume identifiers;
- local usernames, hostnames, full home paths;
- private repository contents, the text of private rules, or unrelated chat history;
- URLs containing secrets or signature parameters.

Screenshots may be cropped; when necessary, use fully opaque blocks and flatten the image. Do not use reversible blurring. Redaction must not change usage numbers, event order, or key timestamps.

There are two compliant paths for visual evidence:

1. **Published redacted images:** the contributor makes opaquely masked copies and visually inspects each one; the originals stay on the contributor's machine, and the PR contains only the redacted copies, a masking description, and the hashes of the originals and the copies.
2. **Visual evidence withheld for now:** the originals stay on the contributor's machine and are not uploaded to public issues, PRs, cloud drives, or chat attachments. Submit the non-sensitive data first and mark `not_provided`; only after a maintainer has checked the originals through a mutually agreed private channel may the state be changed to `private_evidence` with the hashes registered.

`private_evidence` means a maintainer has actually seen the original; it does not mean "there might still be an image somewhere on the contributor's computer". If no established private channel exists, do not improvise by sending originals to unfamiliar accounts, and do not ask in a public PR which part should be masked.

If an original can only be kept privately, register its SHA-256 and the reason for non-publication in `private-evidence.md`. This hash only provides an anchor for later verification; it is not public proof.

Once a credential enters Git history, deleting it in the next commit is not enough: rotate or revoke it immediately, and contact the maintainers to clean the history.

If you find something like this in evidence that is **already published** — yours or anyone else's — report it privately through the process in [SECURITY.md](SECURITY.md). Do not open a public issue, and do not repeat the exposed value anywhere public. Reporting your own mistake carries no penalty; a leak fixed on day one is far better than one discovered a year later.

## Licensing of your contribution

By opening a pull request you agree that your contributed measurement data and text are published under [CC BY 4.0](LICENSE-DATA). Screenshots you contribute are **outside the CC BY grant** and are published only for factual research reporting. Software contributions (`scripts/`, `.github/workflows/`) are published under the [Apache License 2.0](LICENSE). You keep the copyright in what you contribute; there is no CLA to sign.

Only submit evidence you are entitled to publish. Screenshots of a third-party product's interface are reproduced here for factual research reporting; screenshots of private repositories, internal tools, or someone else's account are not — crop or reshoot instead. If your employer restricts publishing material about a product you use at work, resolve that before submitting, not after.

## Submitting a Pull Request

One PR contains one scenario and all of its repeated runs. In the PR, state:

- a one-sentence scenario summary;
- the counts of valid, invalid, and error attempts;
- the evidence tier and any missing fields;
- any protocol deviations;
- the verification script output;
- why the shared quota is attributable, or why it was marked contaminated.

The repository's [Pull Request template](.github/pull_request_template.md) already includes these fields and the pre-submission checklist. We recommend opening a Draft PR first and marking it Ready for review only after automated verification passes and the screenshots have been visually inspected. Automated verification can only check structure, arithmetic, hashes, and textual privacy clues; it cannot prove that screenshot masking is correct and does not replace human review.

Review focuses on internal consistency, field states, redaction, and whether overclaiming was avoided — not on requiring every product to expose exactly the same data.

Every data PR receives **at least two independent reviews**, human or AI-assisted; an AI-assisted review names the agent product, the model, and the effort it was performed with. Reviews are posted as structured comments on the PR — the process and the verdict template are in [docs/review-process.md](docs/review-process.md). When the two verdicts disagree, a third review is added. Merging, awarding points, and the final read are the maintainer's; the target response time is about 3 working days.

Pre-submission checklist:

- [ ] The same scenario has at least 3 valid independent runs;
- [ ] All three used the same prompt, model, effort, version, routing, and harness;
- [ ] Environment evidence was not pointlessly duplicated three times;
- [ ] Each attempt's prompt, complete reply, and native usage were saved wherever possible;
- [ ] Cached input was not double-counted;
- [ ] Shared quota contamination is labeled;
- [ ] Missing or conflicting fields use the fixed states;
- [ ] Public files contain no credentials, email addresses, absolute home paths, or session-resume identifiers;
- [ ] `SHA256SUMS` was generated last;
- [ ] The root `RESULTS.md` and `RESULTS.zh-CN.md` indexes have been rebuilt;
- [ ] `verify-all.sh` passes.

Replications are very welcome. Independent replications by different contributors, on different devices, with different subscriptions, and at different times are exactly how this project gradually becomes valuable.
