# Codex CLI 0.151.0-alpha.7.2 / GPT-5.6 Sol / high / fresh

This package is the `fresh` side of the T-33 same-machine paired comparison claimed in [Issue #67](https://github.com/aicodingresearch/agent-hi-tax/issues/67). Its sibling scenario is `20260903_codex-cli-0.151.0-alpha.7.2_gpt-5.6-sol_high_hi-en-v1_custom-session-resumed-one-hi_mac-arm64_BoomShuai`.

## Scenario

- Prompt: `hi-en-v1`, exactly `hi` as two UTF-8 bytes
- Agent: first-party OpenAI Codex CLI 0.151.0-alpha.7.2
- Model and effort: `gpt-5.6-sol`, `high`
- Account: ChatGPT Pro subscription login
- System: macOS 26.6 build 25G72, arm64
- Session state: `fresh`; prior human chat turns at the measured target: 0
- Workspace: the same preregistered empty non-Git path within each pair, reused sequentially and empty after every phase
- Sandbox and approval: `workspace-write` with `network_access=false`, approval policy `never`
- Harness: custom; all configured MCP servers disabled, 11 plugins, 202 model-visible skills, empty global `AGENTS.md`, no project rules, and one local notification hook
- Evidence: Level A; each attempt has safe native events plus a public terminal image connecting state, exact input, reply, usage, exit status, and workspace checks

Each attempt is a new session with zero prior human chat turns.

## Target results

| Attempt | Seed input (setup only) | Target input incl. cached | Target cached | Target non-cached | Target output | Target context total | Target latency | Visual evidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| R1 | not applicable | 20,428 | 11,264 | 9,164 | 14 | 20,442 | 2,346 ms | public |
| R2 | not applicable | 20,428 | 11,264 | 9,164 | 13 | 20,441 | 3,045 ms | public |
| R3 | not applicable | 20,428 | 11,264 | 9,164 | 14 | 20,442 | 1,972 ms | public |

Target medians were 20,428 input tokens including cached input, 11,264 cached, 9,164 non-cached, 14 output, and 20,442 context total.

Codex reports cached input as a subset of input:

```text
non_cached_input_tokens = input_tokens_including_cached - cached_input_tokens
context_total_tokens = input_tokens_including_cached + output_tokens
cli_total_excluding_cached = non_cached_input_tokens + output_tokens
```

These native fields are not ChatGPT quota charges or API prices.

## Paired result

| Pair | Fresh input | Resumed target input | Input delta | Fresh cached | Resumed cached | Cached delta | Fresh non-cached | Resumed non-cached |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| R1 | 20,428 | 20,448 | +20 | 11,264 | 20,224 | +8,960 | 9,164 | 224 |
| R2 | 20,428 | 20,449 | +21 | 11,264 | 20,224 | +8,960 | 9,164 | 225 |
| R3 | 20,428 | 20,449 | +21 | 11,264 | 20,224 | +8,960 | 9,164 | 225 |

Across r1-r3, resumed-minus-fresh input deltas were `[+20, +21, +21]`; the side medians were 20,428 fresh and 20,449 resumed. Cached input increased by exactly 8,960 in every pair, from 11,264 to 20,224, while non-cached input fell by `[8,940, 8,939, 8,939]` tokens. Cache-write input and reasoning output remained zero.

The supported observation is that one prior `hi` roundtrip plus explicit session recovery added only 20-21 tokens to the native input field in this exact harness, while substantially more of that input was served from cache. Cached tokens are a subset, so the 8,960-token cached increase must not be added again to total input or interpreted as a billing reduction.

Every resumed rollout preserved the seed rollout as an exact prefix, used the same withheld private thread identifier, and contained exactly two human `hi` messages, two assistant replies, two matching turn contexts, and zero tool calls. Base instructions SHA-256 `a91357a1cd2727a0be06d461248d6e3a7274746e38108f548a3adf2cc2430415`, fixed turn-context projection SHA-256 `62171cbbeaaa61ef8159d4470555e2c2f01d292cc5cd31f900a7e1e8443c114c`, and normalized initial role/content SHA-256 `ceb80661a56b7c8c68ff0b88783d31572284b156c41a61a1c5ef9624c5ed6339` were equal across all six formal targets/seeds.

Reply wording and output tokens varied naturally; context-total deltas were `[+20, +29, +24]`. Resumed target latency was descriptively lower in these three pairs, but the fixed order was not randomized, one fresh run had startup diagnostics, and provider cache state is not independently controlled. No latency effect is claimed.

The complete local config byte hash changed during each fresh process and did not change during the resumed wrappers. Effective model-visible controls and inventories remained equal, but unrelated private config bytes are not claimed fixed. Fresh r3 emitted non-fatal model-list-refresh-timeout and plugin-MCP transport-closed diagnostics, then completed with native usage and exit 0. Latency is descriptive.

This result does not generalize to longer histories, other session contents, other builds, models, accounts, or billing metrics. The separate preflight mechanics probe used different diagnostic text and is excluded from all formal values.

## Evidence

The package publishes exact prompt and safe launch syntax, pair and side preregistrations, preflight records, skill inventory, resume-mechanics preflight summary, paired analysis, workspace and post-run audits, minimized events, exact target replies, three public terminal captures, a public ChatGPT Pro screenshot, privacy/visual audits, and full hashes.

Raw CLI streams, complete rollouts, local configuration, absolute paths, and all session identifiers remain outside Git. Their retained-original hashes are listed in `evidence/private-evidence.md`; no target usage or reply claim depends only on a private hash.

## Protocol record

The preregistered execution order was fresh-r1, resumed-seed-r1, resumed-target-r1, then the same sequence for r2 and r3. All phases ran sequentially. No attempt was replaced or selected by wording or token value, and all six targets were valid.
