# OpenAI Codex CLI 0.149.1 / gpt-5.6-sol / high / ChatGPT Plus

This is a three-attempt replication of T-01 using the first-party Codex CLI with a ChatGPT Plus subscription.

## Scenario

- Prompt: `hi-en-v1`, exactly two UTF-8 bytes (`68 69`)
- Agent: OpenAI Codex CLI 0.149.1
- Model: `gpt-5.6-sol`
- Reasoning effort: `high`
- Authentication: ChatGPT subscription login
- Subscription: ChatGPT Plus
- OS: Linux x86_64; kernel/build recorded in `evidence/preflight.txt`
- Session: three fresh sessions, one prompt per session
- Workspace: three independent empty workspaces; absolute paths are withheld from the public package
- Harness profile: `as-used`
- Permission mode: `YOLO mode`

## Results

| Attempt | Input including cached | Cached input | Non-cached input | Output | Context total | CLI total excluding cached |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| R1 | 19,160 | 11,008 | 8,152 | 13 | 19,173 | 8,165 |
| R2 | 19,160 | 11,008 | 8,152 | 13 | 19,173 | 8,165 |
| R3 | 17,609 | 9,984 | 7,625 | 22 | 17,631 | 7,647 |

R1 and R2 displayed `total=8,165 input=8,152 (+ 11,008 cached) output=13`. R3 displayed `total=7,647 input=7,625 (+ 9,984 cached) output=22 (reasoning 9)`. In this display, the parenthesized cached value is added to the displayed non-cached input to obtain the full input context.

```text
R1/R2: input_tokens_including_cached = 8,152 + 11,008 = 19,160
R1/R2: context_total_tokens = 19,160 + 13 = 19,173
R1/R2: cli_total_excluding_cached = 8,152 + 13 = 8,165
R3: input_tokens_including_cached = 7,625 + 9,984 = 17,609
R3: context_total_tokens = 17,609 + 22 = 17,631
R3: cli_total_excluding_cached = 7,625 + 22 = 7,647
```

The three replies were:

- R1: `Hi! What can I help you with?`
- R2: `Hi! What can I help you with?`
- R3: `Hi! How can I help?`

## Evidence and limitations

This package is Level B: it contains public visual evidence and exact reply text, but no sanitized machine event logs. Per-attempt timestamps and latency were not retained and are marked `not_exposed`. Quota before/after was not measured and is excluded from the results.

The environment screenshot confirms Codex CLI 0.149.1, `gpt-5.6-sol`, `high`, and the R3 workspace. The subscription screenshot confirms ChatGPT Plus. Detailed plugins, skills, MCP, hooks, and network state were not captured and are not inferred.
