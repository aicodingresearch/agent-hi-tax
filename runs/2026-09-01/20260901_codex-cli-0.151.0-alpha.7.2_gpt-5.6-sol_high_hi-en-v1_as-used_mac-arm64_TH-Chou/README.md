# Codex CLI 0.151.0-alpha.7.2 / GPT-5.6 Sol / high

This package is an independent T-01-style replication of the Codex CLI `hi-en-v1` scenario on macOS arm64.

## Scenario

- Prompt: `hi-en-v1`, exactly `hi` as two UTF-8 bytes
- Agent: first-party OpenAI Codex CLI 0.151.0-alpha.7.2
- Model: `gpt-5.6-sol`
- Reasoning effort: `high`
- Authentication and billing: ChatGPT subscription login; exact plan not exposed
- Route: first-party subscription, native protocol
- Session: three fresh sessions, sequentially executed
- Workspace: three separate empty non-Git directories
- Harness profile: `as-used`
- Evidence level: Level C; machine event records are included, visual evidence was not captured

## Results

| Attempt | Input incl. cached | Cached input | Non-cached input | Output | Reasoning output | Context total | CLI total excl. cached | Latency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| R1 | 20,959 | 11,008 | 9,951 | 15 | 0 | 20,974 | 9,966 | 2,163 ms |
| R2 | 20,756 | 11,008 | 9,748 | 32 | 17 | 20,788 | 9,780 | 3,455 ms |
| R3 | 20,756 | 11,008 | 9,748 | 31 | 16 | 20,787 | 9,779 | 2,656 ms |

The three valid runs used the same native model and effort. Input context was 20,756–20,959 tokens, with 11,008 cached input tokens in each run. The cached value is a subset of the input value; it is not added a second time. Subscription quota was not measured.

Visible replies were:

- R1: `Hi! 👋 有什么想一起做的吗？`
- R2: `Hi! 有什么我可以帮你的？`
- R3: `Hi! 有什么我可以帮你的？`

## Evidence and deviations

The public package contains the exact prompt, sanitized event logs, preflight transcription, result records, and hashes. Raw rollout files and account-related material remained outside the repository. The event logs retain only the target user message, final assistant message, model/effort, usage, and timestamps.

An initial interactive TUI probe was cancelled after no response. It is preserved as `attempts/r0/result.yaml` and excluded from the three valid repetitions. The first valid `exec` run used the same still-empty directory after the cancellation; the cancelled probe created no files. The successful repetitions used `codex exec --json` to obtain native machine-readable usage, and no screenshots were captured.
