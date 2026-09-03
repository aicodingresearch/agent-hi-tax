# Codex CLI 0.151.0-alpha.7.2 / GPT-5.6 Sol / medium

This package is a T-13 observation of Codex CLI with `gpt-5.6-sol` at `medium` reasoning effort on macOS arm64. It was preregistered in [Claim #49](https://github.com/aicodingresearch/agent-hi-tax/issues/49).

## Scenario

- Prompt: `hi-en-v1`, exactly `hi` as two UTF-8 bytes
- Agent: first-party OpenAI Codex CLI 0.151.0-alpha.7.2
- Model: `gpt-5.6-sol`
- Reasoning effort: `medium`
- Authentication and billing: ChatGPT Pro 20x subscription login, verified post-collection by a public account screenshot
- Route: first-party subscription, native protocol
- Session: six fresh sessions, sequentially executed in an original and a supplemental block
- Workspace: six separate empty non-Git directories, still empty after each run
- Valid-run surface: official `codex exec --json`
- Sandbox and approval: `workspace-write`, restricted filesystem/network, approval policy `never`
- Harness profile: `as-used`
- Harness inventory: one enabled MCP server (`node_repl`), 11 enabled plugins, 202 model-visible skill entries, an empty global `AGENTS.md`, and one local notification hook
- Evidence level: Level A; native machine events cover R1-R6 and public terminal screenshots connect configuration, input, reply, and usage for supplemental R4-R6

## Results

| Attempt | Input incl. cached | Cached input | Non-cached input | Output | Reasoning output | Context total | CLI total excl. cached | Latency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| R1 | 20,421 | 11,008 | 9,413 | 14 | 0 | 20,435 | 9,427 | 1,727 ms |
| R2 | 20,421 | 11,008 | 9,413 | 14 | 0 | 20,435 | 9,427 | 3,761 ms |
| R3 | 20,421 | 11,008 | 9,413 | 14 | 0 | 20,435 | 9,427 | 1,883 ms |
| R4 | 20,421 | 11,008 | 9,413 | 14 | 0 | 20,435 | 9,427 | 2,898 ms |
| R5 | 20,421 | 11,008 | 9,413 | 14 | 0 | 20,435 | 9,427 | 1,611 ms |
| R6 | 20,421 | 11,008 | 9,413 | 14 | 0 | 20,435 | 9,427 | 2,161 ms |

All six valid runs produced the same visible reply:

> Hi! What would you like to work on?

The native input, cached input, non-cached input, output, reasoning output, and context total were identical across all six attempts. Latency varied and is retained only as descriptive metadata.

Codex reports cached input as a subset of input:

```text
non_cached_input_tokens
  = input_tokens_including_cached - cached_input_tokens

context_total_tokens
  = input_tokens_including_cached + output_tokens

cli_total_excluding_cached
  = non_cached_input_tokens + output_tokens
```

The CLI total is not interpreted as ChatGPT subscription quota cost. Subscription quota was not measured. The public [subscription screenshot](evidence/subscription.png) shows Pro at USD 200/month; OpenAI's public pricing documentation identifies that tier as Pro 20x. This post-collection account evidence does not change any native token value.

## Harness warning

Each `exec` run emitted the same local client warning: skill descriptions were shortened to fit the skills context budget. Codex reported that all skills remained visible with shortened descriptions. The warning is retained in every `result.yaml`; the target request still completed successfully, with one assistant message and no tool calls or approvals.

This is part of the measured `as-used` harness rather than a reason to discard the attempts. The full public-safe name inventory is in [available-skill-names.txt](evidence/available-skill-names.txt).

The preregistration and initial preflight recorded 199 skill names because the first public-safe parser truncated names at the first colon and collapsed namespaced siblings. Post-run inspection of each retained rollout found the same 202 unique full names and the same inventory hash in R1–R6. This is a measurement-extraction correction, not a runtime configuration change; details are in [post-run-audit.txt](evidence/post-run-audit.txt).

## Evidence and deviations

The public package contains the exact prompt, launch command, preregistration record, public-safe preflight and harness inventory, workspace checks, sanitized event logs, result records, subscription screenshot, visual-evidence audit, and hashes. Raw `exec` JSONL and rollout files remained outside Git. Public events retain only version, model, effort, the exact target `hi`, final reply, timestamps, and native usage.

An initial TUI preflight was cancelled before any target model request because the host PTY did not render a usable interface. It is preserved as `attempts/r0/result.yaml` and excluded from the six valid repetitions. Before R1, the valid-run surface was fixed to official `codex exec --json` and held constant through the original R1-R3 block. The same command and harness were reused for supplemental R4-R6.

R1-R3 have no attempt screenshots because their background PTYs could not be reattached to a visible app terminal. They remain valid machine-record attempts. R4-R6 were added after the original block, without replacing any run, specifically to collect public visual evidence. Their byte-identical public terminal-content captures show version, model, medium effort, exact `hi`, fresh/empty assertions, fixed command, full reply, native usage, and exit 0. This combination of native events and public visual evidence raises the package to Level A.

## Same-machine effort pair

The same-machine [high-effort sibling PR #53](https://github.com/aicodingresearch/agent-hi-tax/pull/53) now contains six matching attempts. Across all twelve rollouts, version, account, OS, route, prompt, workspace profile, sandbox, approval mode, MCP, plugins, `AGENTS.md`, skill inventory, and normalized model-visible inputs were held constant apart from effort.

Every attempt reported 20,421 input including 11,008 cached, 9,413 non-cached, zero cache write, and zero reasoning output. High R4 produced a different 13-token greeting; the other eleven replies used 14 output tokens. Both six-run blocks still have identical medians for every token field. The supported conclusion is therefore a zero observed injected-input-footprint delta for this exact `hi` case; the one greeting variation is retained and not attributed to effort. Hidden compute, quota, latency, longer outputs, and other prompts remain outside that conclusion.
