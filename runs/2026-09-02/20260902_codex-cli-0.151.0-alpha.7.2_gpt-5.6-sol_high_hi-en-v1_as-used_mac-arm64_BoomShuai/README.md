# Codex CLI 0.151.0-alpha.7.2 / GPT-5.6 Sol / high

This package is a T-01 observation of Codex CLI with `gpt-5.6-sol` at `high`
reasoning effort on macOS arm64. It was preregistered in
[Claim #51](https://github.com/aicodingresearch/agent-hi-tax/issues/51) and was
designed as a same-machine sibling for the contributor's
[medium-effort Draft PR #50](https://github.com/aicodingresearch/agent-hi-tax/pull/50).

## Scenario

- Prompt: `hi-en-v1`, exactly `hi` as two UTF-8 bytes
- Agent: first-party OpenAI Codex CLI 0.151.0-alpha.7.2
- Model: `gpt-5.6-sol`
- Reasoning effort: `high`
- Authentication and billing: ChatGPT Pro 20x subscription login, verified by a public pre-run account screenshot
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
| R1 | 20,421 | 11,008 | 9,413 | 14 | 0 | 20,435 | 9,427 | 2,342 ms |
| R2 | 20,421 | 11,008 | 9,413 | 14 | 0 | 20,435 | 9,427 | 1,863 ms |
| R3 | 20,421 | 11,008 | 9,413 | 14 | 0 | 20,435 | 9,427 | 1,671 ms |
| R4 | 20,421 | 11,008 | 9,413 | 13 | 0 | 20,434 | 9,426 | 1,668 ms |
| R5 | 20,421 | 11,008 | 9,413 | 14 | 0 | 20,435 | 9,427 | 2,408 ms |
| R6 | 20,421 | 11,008 | 9,413 | 14 | 0 | 20,435 | 9,427 | 1,940 ms |

R1-R3, R5, and R6 produced:

> Hi! What would you like to work on?

R4 produced:

> Hi! What are we working on today?

The alternate R4 greeting used 13 output tokens rather than 14. It is retained as a
valid observation and is not attributed to effort.

Codex reports cached input as a subset of input:

```text
non_cached_input_tokens
  = input_tokens_including_cached - cached_input_tokens

context_total_tokens
  = input_tokens_including_cached + output_tokens

cli_total_excluding_cached
  = non_cached_input_tokens + output_tokens
```

The CLI total is not interpreted as ChatGPT subscription quota cost. Subscription
quota was not measured.

## Same-machine effort pair

The medium sibling and this high package each contain six valid attempts. All twelve
reported exactly the same input-side values: 20,421 input including 11,008 cached,
9,413 non-cached, zero cache write, and zero reasoning output. High R4's alternate
greeting used 13 output tokens, yielding 20,434 context total and 9,426 CLI total;
the other eleven attempts used 14, 20,435, and 9,427 respectively. Both six-run
blocks have identical medians for every reported and derived token field.

Retained evidence showed the same CLI version, account, OS, route, prompt, empty
workspace profile, sandbox, approval mode, MCP, 11 plugins, empty `AGENTS.md`, and
202-skill inventory/hash. After projecting the ordered developer/user role/content
records and normalizing only the equal-shape attempt path, the model-visible input
hash was also identical across all twelve rollouts. The intended difference was
`medium` versus `high` effort.

This supports a narrow zero observed injected-input-footprint delta for this exact
`hi` case. The one greeting variation is retained and not attributed to effort. It
does not show that effort has no effect on hidden compute, subscription quota,
latency, longer outputs, or other prompts. Latency is not compared because the
blocks were sequential rather than randomized or interleaved. See
[paired-comparison-audit.txt](evidence/paired-comparison-audit.txt).

## Harness warning and config registry write

Each run emitted the same client warning that skill descriptions were shortened to
fit the skills context budget. All skills remained visible; each request completed
with one assistant message and no tool calls or approvals.

Codex also persisted a trusted-project registry entry for each new attempt path, so
the private whole-config hash changed. This path registry change is disclosed rather
than hidden. It did not change the normalized model-visible input, effective turn
context, workspace, inventory hashes, or any measured input-side token field.
Details are in [post-run-audit.txt](evidence/post-run-audit.txt).

## Evidence boundary

The public package contains the prompt, launch command, preregistration, public-safe
preflight and inventories, workspace checks, sanitized native events, result records,
subscription screenshot, audits, and hashes. Raw events, rollouts, session IDs, full
developer context, absolute paths, and the private config remained outside Git.

The subscription screenshot verifies only the plan. R1-R3 have no attempt images
because their background PTYs could not be reattached to a visible app terminal;
their native records remain public and valid. R4-R6 were added after the original
block, without replacing any run, specifically to collect visual evidence. Their
byte-identical public terminal-content captures show version, model, high effort,
exact `hi`, fresh/empty assertions, fixed command, full reply, native usage, and
exit 0. Together with the sanitized native records, they raise this package to
Level A.
