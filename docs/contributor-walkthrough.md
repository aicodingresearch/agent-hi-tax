# Walkthrough: from claiming a task to submitting a PR

**English** | [中文](contributor-walkthrough.zh-CN.md)

> First-time contributors can simply work through this page from top to bottom. For rule details, [CONTRIBUTING](../CONTRIBUTING.md) is authoritative; this page turns it into a path you can walk end to end.

## What you will do, in one sentence

In an environment declared in advance and reviewable afterwards, send exactly the same small input (the standard case is [`hi`](../prompts/hi-en-v1.txt)) to an AI Agent, execute at least 3 sequential runs, and record, redact, and package everything actually consumed each time — tokens, credits, quota, latency — together with the environment evidence, then submit a Pull Request.

## Why this is worth doing

### This is a "zero-input probe" measurement of the Agent harness

Harness here means the entire system the Agent product wraps around the model: the system prompt, tool and MCP definitions, rules file loading, workspace probing, session and cache management, request routing. Ordinarily it is a black box — even if you have read parts of the open-source implementations, it is hard to quantify how much it actually injects into each request.

The design of this experiment turns the harness itself into the object under measurement. The visible input of `hi` is only 2 characters; yet the existing data already shows:

- In the Claude Code reference sample, plain input is only **2 tokens**, while the first request simultaneously created about **25K tokens** of cache;
- Across the six completed scenarios, per-run input context ranges between roughly **14K and 33K tokens**.

As user input approaches zero, these input tokens come almost entirely from the harness itself. Therefore:

- **A single scenario** = one direct measurement of the fixed overhead of a real harness;
- **The difference between two scenarios that differ in exactly one variable** = the marginal token cost of that specific harness component (one MCP server, one rules file, one effort tier, one permission mode);
- **Repeated observations of the same scenario over time** = a longitudinal record of harness evolution (product upgrades changing prompts, adding or removing tools).

In other words, every scenario package you submit is one weighing of a real harness at a moment in time. The group D tasks in the [wanted scenarios list](wanted-scenarios.md) are controlled comparisons designed along exactly these lines.

Along the way you will also confront the real differences in vendor metering semantics — for example, Codex's cached input is a subset of input, whereas Anthropic's three input buckets are additive. Working out these semantics is itself first-hand material for understanding harness billing and cache design.

### The data itself has public value

Complaints like "one hi cost me 1% of my quota" circulate everywhere in the community, but almost none come with reviewable evidence. This repository is turning rumor into data: a unified protocol, native semantics, tiered evidence, file hashes, automated verification. Every scenario package you contribute is one real record in this public dataset, which others can cite, replicate, or refute.

### This is a complete exercise in empirical research

Every part of the process corresponds to a standard move of empirical method:

- **Preregistration**: fix the scenario in the manifest before executing, ruling out "tuning while measuring";
- **Controlled variables**: only one variable may change at a time; any other change is split into a new scenario;
- **Tiered evidence**: every field is annotated with a status such as `verified` / `self_reported` / `not_exposed`, tying the strength of a conclusion to the strength of its evidence;
- **Honest handling of outliers**: failed attempts are kept and marked `invalid`; nothing is deleted, and you do not pick the three best-looking runs;
- **Reviewable packaging**: SHA-256 hashes + automated verification scripts + public redacted evidence.

This method is closer to the purpose of research training than any single number is.

## Before you start

### Pick a task

Open the [wanted scenarios list](wanted-scenarios.md) and pick an entry that matches the subscriptions, products, and devices you already have. For a first contribution, group A (replication) is recommended. **Do not buy a subscription for a task.**

### Claim it

Open an issue in the repository, titled `[Claim] T-xx one-line scenario description`, stating the planned Agent version, model, subscription plan, and estimated completion time.

### Spend 10 minutes memorizing the six rules

Full version in [CONTRIBUTING](../CONTRIBUTING.md#the-six-most-important-rules); the short version:

1. A scenario needs at least 3 valid independent runs, executed sequentially, not in parallel;
2. Scenario variables must not change midway; if one changes, it is another scenario;
3. Environment evidence is collected once; no need to screenshot three sets;
4. Each run collects only that run's results: the exact input, the full reply, the native usage;
5. Provide the evidence you can obtain; mark what you cannot with the fixed missing statuses — do not guess;
6. Never treat a total as the cost: store cached input, non-cached input, output, credits, and percentages separately, and do not convert on your own.

### Check what you need

- A macOS, Windows, or Linux machine (record the OS and architecture honestly);
- The Agent product under test + a valid subscription or API access;
- git and a GitHub account;
- `python3` (to run the verification scripts);
- **An uninterrupted block of about 30 minutes**: a typical contribution can usually be completed in about 30 minutes; for a first contribution, allow about 1 hour, which is enough to read the documentation, handle redaction, and complete one scenario. The three runs must be completed sequentially; do not switch configurations or upgrade software midway.

## Hands on: step by step

### Step 0: Fork, clone, branch

Fork [aicodingresearch/agent-hi-tax](https://github.com/aicodingresearch/agent-hi-tax) on GitHub, then:

```sh
git clone https://github.com/<your-username>/agent-hi-tax.git
cd agent-hi-tax
git checkout -b run/<product>-<model>-<date>
```

One branch holds one scenario.

### Step 1: Choose a collection adapter (or take the generic path)

Adapters written so far — pick the one closest to your product and read it through:

- [Codex CLI (Chinese)](adapters/codex-cli.zh-CN.md)
- [Claude Code (Chinese)](adapters/claude-code.zh-CN.md)
- [WorkBuddy Desktop (Chinese)](adapters/workbuddy-desktop.zh-CN.md)

This list is where sampling has reached, not a restriction on which agents may be submitted: **any agent product is welcome**. If yours has no adapter, collect under the generic semantics in [CONTRIBUTING](../CONTRIBUTING.md), note the product differences for your PR, and — if you feel like it — draft `docs/adapters/<product>.md` as you go, so the next person testing that product has a path to follow. Adapters do not require you to disable existing proxies, sandboxes, or account security settings — they are part of the scenario; leave them as they are and record them honestly.

### Step 2: Fix the scenario (this step is the "preregistration")

Copy [`templates/scenario-manifest.yaml`](../templates/scenario-manifest.yaml) and fill in every scenario variable you can determine: product and exact version, model, effort, subscription and route, operating system, harness profile (most people should honestly choose `as-used` and list the known rules, skills, MCP, plugins, hooks), the planned number of repetitions, and fix the launch command.

**From this moment on, the model, effort, version, permission mode, and plugin state must not change.** Change any one of them, and it is another scenario.

If you intend to claim quota changes (quota before/after), pause all other usage on the same account and the same quota pool now; if you cannot, mark the quota attribution `contaminated` (the session's own token records remain valid).

### Step 3: Create an evidence directory outside the repository

```sh
mkdir -p ~/hi-tax-evidence/<scenario-name>
```

Raw screenshots and raw session/transcript files **never go into Git directly**. Collect everything into this directory first; only in the final step are redacted copies placed into the repository.

### Step 4: Environment preflight (once only)

Before the formal runs, collect the scenario-level evidence once:

1. Run the version and environment commands and save the output (macOS example; use equivalent commands on other systems):

   ```sh
   command -v <agent>
   <agent> --version
   sw_vers
   uname -m
   date -u '+%Y-%m-%dT%H:%M:%SZ'
   ```

2. Save screenshots: the subscription plan page, the model and effort configuration, the launch screen;
3. Record the harness inventory: rules files, skills, MCP, plugins, hooks, permission mode. Note that MCP tool definitions enter the context even when never called, so their enabled state must be recorded; hooks that call a model are also part of the harness and must not be omitted.

All three runs in the group share this one set of environment evidence; do not screenshot it three times.

### Step 5: Execute 3 sequential runs

For R1, R2, R3, follow this execution card strictly each time:

1. Create a new, separate, empty workspace directory (confirm it is empty and not a Git repository);
2. Start a brand-new session (in fresh scenarios you must not exit and resume);
3. Confirm the model and effort before sending the prompt (a product's built-in `/status`-style command is fine, but do not send extra chat messages);
4. Confirm the footer / permission mode matches the previous runs — if it does not, stop: either mark it as confounded or split off a new scenario;
5. Send the exact input `hi` exactly once (two lowercase letters, no punctuation, spaces, or newline; Enter only submits);
6. After the reply completes, take one screenshot containing the input and the full reply, and save it to the evidence directory;
7. Record the start/end times and the timing method; exit normally and save the native usage the product exposes (exit-screen screenshot, usage page, or event log);
8. Only after this run has fully finished, start the next one.

**If a run goes wrong**: a mistyped input, an accidental resume, a non-empty directory, a network failure, an extra interaction — no need to panic. Keep the attempt, mark it `invalid` or `error`, state the reason, then append new attempts until you have 3 valid runs. **Do not delete outliers, and do not pick the three best-looking runs.**

### Step 6: Assemble the scenario package

Under `runs/YYYY-MM-DD/<scenario-id>/`, build the following structure (details in [CONTRIBUTING — run package layout](../CONTRIBUTING.md#run-package-layout)):

Every newly submitted scenario package appends `_<github-handle>` to both the directory name and the manifest's `scenario.id` (for example, `..._mac-arm64_alice`). This makes package paths collision-free by construction, so several contributors replicating the same scenario on the same date need no coordination at all. The four existing reference samples predate this rule and keep their original names.

```text
runs/YYYY-MM-DD/<scenario-id>/
  README.md
  manifest.yaml
  prompt.txt
  launch-command.txt        # CLI scenarios only
  RESULTS.csv
  SHA256SUMS                # generated in the final step
  evidence/                 # scenario-level evidence (redacted)
  attempts/r1 r2 r3/        # per attempt: result.yaml, response.txt, response.png, trimmed event log
```

**Do not guess fields from a blank template.** Pick the one of the [six published scenario packages](../runs/README.md) closest to your product, copy the whole package, and replace each item with your own data. Do not change the meaning of vendor-native fields to "look consistent"; write `not_applicable` where a field does not apply, `not_exposed` where the product does not expose it, `not_provided` where it was not obtained.

### Step 7: Redaction

Red lines — the following must never appear in any submitted file:

- API keys, tokens, cookies, authorization headers, gateway credentials;
- Account email addresses, account IDs, payment information;
- Session IDs, resume commands, and other session-restore identifiers;
- Local usernames, hostnames, full home paths (rewrite home as `~` in transcripts);
- Private repository content, private rules text, unrelated chat history.

Screenshot handling rules: crop, or cover with a **fully opaque block**, then flatten and export; do not use mosaic or Gaussian blur (reversible). Redaction must not alter usage numbers, event order, or key timestamps. Visually inspect every public image, one by one.

Not wanting to publish a particular original image is fine too: keep the original on your machine, mark the corresponding field `not_provided`, and submit; later, once a maintainer has verified it through a private channel, it can be upgraded to `private_evidence`. **Never upload an original first and then wait for someone to delete it.**

### Step 8: Generate hashes and verify

After all public files are final (any further edit requires regenerating):

```sh
cd runs/YYYY-MM-DD/<scenario-id>
find . -type f ! -name SHA256SUMS -print0 \
  | LC_ALL=C sort -z \
  | xargs -0 shasum -a 256 > SHA256SUMS
cd -

./scripts/verify-run-package.sh runs/YYYY-MM-DD/<scenario-id>
```

On Linux, where `shasum` is unavailable, use `sha256sum`. If the script reports errors, fix them as instructed, regenerate the hashes, and run it again.

### Step 9: Verify every package

```sh
./scripts/verify-packages.sh
```

Packaging is complete once this passes. Do not rebuild or commit the root-level `RESULTS.md` and `RESULTS.zh-CN.md` — they are generated from the scenario packages and refreshed on `main` after your PR merges. The PR check shows you the rows your scenario will add.

### Step 10: Submit the Pull Request

```sh
git add runs/
git commit -m "data: add <one-line scenario description> sample"
git push -u origin <branch-name>
```

Open a **Draft PR** on GitHub (one PR holds one scenario) and fill in the [PR template](../.github/pull_request_template.md): scenario summary, valid/invalid attempt counts, evidence level and missing fields, protocol deviations, verification output, quota attribution notes. Only after automated verification passes and every screenshot has been visually re-checked, mark it Ready for review, and leave a link in your claim issue.

## What happens after you submit

CI automatically checks package structure, arithmetic consistency, hashes, and textual privacy clues; maintainer review focuses on internal consistency, field statuses, redaction quality, and whether the conclusions are restrained — a PR will **not** be rejected because your product exposes fewer fields than others.

Common rework items — scan for these yourself before submitting:

- cached input double-counted (check whether your vendor uses "subset" or "additive" semantics);
- screenshots with an unredacted email address, username, or session ID;
- `SHA256SUMS` not generated last (files edited without regenerating);
- committing the generated root-level indexes (`RESULTS.md` and `RESULTS.zh-CN.md`), which are maintained on `main`;
- stating a shared-quota difference as "the cost of this hi" without an attribution note.

## FAQ

**I only have an API key, no subscription. Can I take part?**
Yes. Record the route honestly as `official-api`; that is itself a valuable scenario variable.

**The data looks "off" or "unflattering" — should I still submit it?**
Yes. Outliers are data, not mistakes. Variance across the three runs, unexpected cache behavior, or results that disagree with the existing reference samples are often more worth discussing than "normal" data — record them honestly and point them out in the PR.

**What if the product simply does not display a field?**
Use the fixed statuses: `not_exposed` (the product does not expose it), `not_provided` (it may exist but was not obtained this time), `conflicted` (two sources disagree; keep both). Missing fields do not block a PR; they only affect the strength of the conclusions this record can support.

**I only have screenshots, no machine logs. Is that enough?**
Yes. That is Level B evidence; just label it honestly. Do not parse internal logs you do not understand just to reach Level A.

**My Agent routed to different models on the three runs?**
If what you deliberately selected was the product's `Auto`, that is a normal outcome: record the requested model as `Auto` and the actual model per attempt; it remains one scenario. Only when you explicitly pinned a model and it still drifted do you need to flag an execution error or split the scenario.

**After the three runs, the version differs from what I wrote when claiming?**
Just record the actual version and explain it in the PR. The measured version is authoritative; there is no need to redo the runs.

**Roughly how long will it take?**
Usually about 30 minutes. For a first contribution, allow about 1 hour, which is enough to read the documentation, handle redaction, and complete one scenario. The three runs themselves are quick; most of the time goes into organizing the evidence.

## Final self-check before submitting

- [ ] At least 3 valid independent runs of the same scenario, executed sequentially;
- [ ] The prompt, model, effort, version, route, permission mode, and harness are identical across the three runs;
- [ ] Exactly one set of environment evidence, and one set of attempt evidence per run;
- [ ] All missing/conflicting fields annotated with the fixed statuses, with no guessed values;
- [ ] cached input not double-counted under the wrong semantics;
- [ ] shared-quota contamination annotated;
- [ ] Public files free of credentials, email addresses, usernames, home paths, and session-restore identifiers; every screenshot visually inspected;
- [ ] `SHA256SUMS` generated last;
- [ ] `RESULTS.md` and `RESULTS.zh-CN.md` left untouched, `./scripts/verify-packages.sh` passing;
- [ ] PR template filled in completely, one scenario per PR.

---

Once you have finished one, come back to the [wanted scenarios list](wanted-scenarios.md) to claim the next — or propose a scenario combination of your own.
