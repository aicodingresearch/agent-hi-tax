# Codex CLI 0.151.0-alpha.7.2 / GPT-5.6 Sol / high / node_repl MCP ON

This package is the MCP-ON side of the T-31 same-machine paired comparison claimed in [Issue #54](https://github.com/aicodingresearch/agent-hi-tax/issues/54). Its sibling scenario is `20260902_codex-cli-0.151.0-alpha.7.2_gpt-5.6-sol_high_hi-en-v1_custom-mcp-node-repl-off_mac-arm64_BoomShuai`.

## Scenario

- Prompt: `hi-en-v1`, exactly `hi` as two UTF-8 bytes
- Agent: first-party OpenAI Codex CLI 0.151.0-alpha.7.2
- Model and effort: `gpt-5.6-sol`, `high`
- Account: ChatGPT Pro subscription login
- System: macOS 26.6 build 25G72, arm64
- Session: six valid fresh sessions, run sequentially in an original and a supplemental block
- Workspace: six separate empty non-Git directories, still empty after each run
- Sandbox and approval: `workspace-write`, restricted network, approval policy `never`
- Harness profile: `custom`
- Intended pair variable: `node_repl` MCP enabled=true
- Common harness: 11 plugins, 202 model-visible skill entries, empty global `AGENTS.md`, and one local notification hook
- Evidence level: Level A; native events cover every valid attempt and public terminal captures connect command/configuration, exact input, reply, usage, and exit status for r5-r7

The ON side directly queried the native MCP server before collection: protocol 2025-06-18 returned three registered tools (`js`, `js_add_node_module_dir`, and `js_reset`), each with a nonempty object input schema. The canonical tool record hash is `3ff64c325e18992b39da03e361b06ca830b26b4e8b0447f46d3f2d0f72c68ca6`. The OFF side was disabled with a per-launch override and confirmed disabled before each run.

## Results

| Attempt | Input incl. cached | Cached | Non-cached | Output | Context total | CLI total excl. cached | Latency | Visual evidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| R1 | 20,435 | 11,264 | 9,171 | 14 | 20,449 | 9,185 | 6,084 ms | machine only |
| R2 | 20,435 | 11,008 | 9,427 | 13 | 20,448 | 9,440 | 2,234 ms | machine only |
| R3 | 20,435 | 11,264 | 9,171 | 14 | 20,449 | 9,185 | 2,307 ms | machine only |
| R5 | 20,435 | 11,264 | 9,171 | 14 | 20,449 | 9,185 | 2,357 ms | public |
| R6 | 20,435 | 11,264 | 9,171 | 14 | 20,449 | 9,185 | 2,449 ms | public |
| R7 | 20,435 | 11,008 | 9,427 | 14 | 20,449 | 9,441 | 2,181 ms | public |

All six valid attempts on this side reported 20,435 input tokens including cached input. The side median was 11,264 cached, 9,171 non-cached, 14 output, 20,449 context total, and 9,185 CLI total excluding cached input.

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

Across all six same-index pairs, ON minus OFF for `input_tokens_including_cached` was `[0, 0, 0, 0, 0, 0]`. Both side medians were 20,435. The three registered MCP schemas therefore produced a zero observed delta in this Codex native input field for this exact configuration and prompt.

That observation does not establish that tool schemas have no backend cost. It cannot distinguish schema exclusion from the reported metric, caching, transport behavior, or another implementation detail. It also does not generalize to other MCP servers, Codex versions, models, prompts, or tool calls.

The cached/non-cached split matched in five pairs. In r7, ON reported 11,008 cached while OFF reported 11,264, with the total input still identical. Output wording varied naturally from 13 to 15 tokens. Side medians for output and context total remained equal. No MCP or other tool call occurred. Latency is retained descriptively and is not causally attributed to MCP registration.

All retained rollouts shared one base-instructions hash, one normalized developer/user role-content hash, and one 202-skill inventory hash. The role-content projection intentionally excludes separately transported tool schemas; the direct MCP probe and per-attempt state checks establish the intended schema difference.

An additional ON-side r4 is retained as invalid: the standalone Terminal could not find `codex`, exited 127, produced an empty native event stream, and sent no model request. The script was fixed before any subsequent target request.

## Evidence

The package publishes the exact prompt and fixed launch command, pair and side preregistrations, the amended supplemental plan, public-safe preflight, MCP state and schema summary, skill-name inventory, paired analysis, workspace and post-run audits, sanitized events, exact response text, three public valid-attempt terminal captures, a public subscription-plan screenshot, visual/privacy audits, and complete hashes.

Raw exec streams, full local rollouts, local configuration, absolute paths, and session identifiers remained outside Git. Their safe hash registry is in `evidence/private-evidence.md`.

## Protocol record

The original pair ran in order ON-r1, OFF-r1, ON-r2, OFF-r2, ON-r3, OFF-r3. After that block, a supplemental visual plan was registered. The valid visual pair ran ON-r5, OFF-r5, ON-r6, OFF-r6, ON-r7, OFF-r7. No original observation was replaced, and no result was selected by token value.

Original r1-r3 used piped stdin and emitted a local notice while reading EOF after the command argument. The retained rollouts contain exactly one target user message equal to `hi`; r5-r7 used a native Terminal and emitted no stderr. Base instructions and normalized model-visible developer/user inputs were identical across all 12 valid pair runs.
