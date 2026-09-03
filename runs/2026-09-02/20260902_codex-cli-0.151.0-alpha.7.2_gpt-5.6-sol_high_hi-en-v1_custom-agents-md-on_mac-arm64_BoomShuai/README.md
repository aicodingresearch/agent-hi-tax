# Codex CLI 0.151.0-alpha.7.2 / GPT-5.6 Sol / high / AGENTS.md rules ON

This package is the rules-ON side of the T-32 same-machine paired comparison claimed in [Issue #64](https://github.com/aicodingresearch/agent-hi-tax/issues/64). Its sibling scenario is `20260902_codex-cli-0.151.0-alpha.7.2_gpt-5.6-sol_high_hi-en-v1_custom-agents-md-off_mac-arm64_BoomShuai`.

## Scenario

- Prompt: `hi-en-v1`, exactly `hi` as two UTF-8 bytes
- Agent: first-party OpenAI Codex CLI 0.151.0-alpha.7.2
- Model and effort: `gpt-5.6-sol`, `high`
- Account: ChatGPT Pro subscription login
- System: macOS 26.6 build 25G72, arm64
- Session: three valid fresh sessions, executed sequentially as complete same-index pairs
- Workspace: three separate non-Git directories containing only the unchanged public `AGENTS.md` fixture
- Sandbox and approval: `workspace-write`, restricted network, approval policy `never`
- Harness profile: `custom`
- Intended pair variable: root-workspace `AGENTS.md` present=true
- Common harness: all configured MCP servers disabled, 11 plugins, 202 model-visible skill entries, empty global `AGENTS.md`, and one local notification hook
- Evidence level: Level A; every valid attempt has a minimized native event record and a public terminal screenshot connecting configuration, exact input, reply, usage, exit status, and post-run workspace state

The public fixture is 874 UTF-8 bytes, 16 lines, has a final LF, and SHA-256 `f9a80f05c0b9e7981ccb512fb7f955a7d1c5760eddd7b5919ef3d5538919d2a8`. Retained model-input rollouts contain the exact fixture once on every ON run and zero times on every OFF run. The normalized ON injection wrapper hash is `bf3e29f7ffc8c73851a1200fe0b08c26ac6daeac6a5a18897db36f9d3abc0873`.

## Results

| Attempt | Input incl. cached | Cached | Non-cached | Output | Context total | CLI total excl. cached | Latency | Visual evidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| R2 | 20,655 | 11,008 | 9,647 | 11 | 20,666 | 9,658 | 3,267 ms | public |
| R3 | 20,655 | 11,008 | 9,647 | 11 | 20,666 | 9,658 | 1,786 ms | public |
| R4 | 20,655 | 11,008 | 9,647 | 11 | 20,666 | 9,658 | 2,229 ms | public |

All three valid attempts on this side reported 20,655 input tokens including cached input. The side median was 11,008 cached, 9,647 non-cached, 11 output, 20,666 context total, and 9,658 CLI total excluding cached input.

Codex reports cached input as a subset of input:

```text
non_cached_input_tokens
  = input_tokens_including_cached - cached_input_tokens

context_total_tokens
  = input_tokens_including_cached + output_tokens

cli_total_excluding_cached
  = non_cached_input_tokens + output_tokens
```

These are native per-turn fields, not ChatGPT subscription quota or API price.

## Paired result

Across r2-r4, ON minus OFF for `input_tokens_including_cached` was `[220, 220, 220]`; side medians were 20,655 ON and 20,435 OFF. The directly supported observation is therefore a repeatable +220-token delta in this Codex native field for this exact public fixture, build, model, account configuration, and prompt.

The fixture itself occurs byte-for-byte once inside a 945-byte normalized model-input wrapper on ON and never on OFF. After removing only that fixture-bearing content item and normalizing equal-shaped workspace paths, all six rollouts share non-fixture role/content SHA-256 `5d4835ebc49f343dd58294d2c87cb014f7c51e29956cb2174ca75fa9c6db3e33`, base-instructions SHA-256 `a91357a1cd2727a0be06d461248d6e3a7274746e38108f548a3adf2cc2430415`, and the same 202-skill inventory hash.

The earlier `codex debug prompt-input` diagnostic used a different record shape and produced common-projection SHA-256 `f0722794b99fa98b79aafd1540d31d9ef735ad4a7a1025c044cbaf0d21aca28d`; the retained target rollouts produced `5d4835ebc49f343dd58294d2c87cb014f7c51e29956cb2174ca75fa9c6db3e33`. Equality is tested within each evidence surface, so these two cross-surface serialization hashes are not expected to match.

The cached ON-minus-OFF deltas were `[-256, 0, -256]`; non-cached deltas were `[476, 220, 476]`. Output wording varied naturally, so context-total deltas were `[217, 218, 217]`. These secondary differences are retained but not attributed beyond the observed pair. No tool or hook model call occurred.

This does not establish a universal byte-to-token conversion, does not show how every `AGENTS.md` is transformed, and does not generalize to other files, Codex versions, models, prompts, or billing metrics. Latency is descriptive only. OFF-r2 and OFF-r4 emitted disclosed non-fatal startup/transport diagnostics, so no latency contrast is interpreted causally.

The complete private local-config byte hash changed during every target process. The fixed launch parameters and model-visible controls listed above were independently verified and remained equal, but no claim is made that unrelated private config bytes stayed unchanged.

The sibling OFF package retains invalid r1. It failed locally during argument parsing before any model request, so ON-r1 was not started; the amended complete valid pairs are r2-r4.

## Evidence

The package publishes the exact prompt and corrected launch command, pair and side preregistrations, pre-target amendment, public fixture, public-safe preflight, model-input projection audit, skill-name inventory, paired analysis, workspace and post-run audits, minimized native events, exact replies, three public attempt captures, a public subscription-plan screenshot, privacy/visual audits, and complete hashes.

Raw exec streams, complete local rollouts, local configuration, absolute paths, and session identifiers remain outside Git. Their safe hash registry is in `evidence/private-evidence.md`; no public claim depends solely on those hashes because public machine records and screenshots are included.

## Protocol record

The original planned order was OFF-r1, ON-r1, OFF-r2, ON-r2, OFF-r3, ON-r3. OFF-r1 failed before any model request because this CLI build rejected the original placement of the approval option. Before the first target request, an amendment retained r1 as invalid, changed only the spelling to `--config approval_policy=never`, created r4 workspaces, and fixed the valid order as OFF-r2, ON-r2, OFF-r3, ON-r3, OFF-r4, ON-r4.

All valid runs then followed that order with fresh processes and independent workspaces. No result was replaced or selected by token value. Every retained valid rollout contains exactly one target user message equal to `hi`, one assistant reply, one final usage record, and no tool call.
