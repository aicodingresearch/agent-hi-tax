# Antigravity CLI status-line instrumentation

Antigravity CLI 1.1.23 supports a command-backed status line that receives a product-native JSON state object on standard input. This scenario uses that documented interface as a passive local observer.

Official documentation:

- <https://antigravity.google/docs/cli/statusline/>
- <https://antigravity.google/docs/cli/commands/usage/>

Frozen capture-script SHA-256:

```text
e04087dc9110807ee89d05a121c1dd59a7b59af0d0a936e34532ac2687de06f5
```

The command makes no network or model request and does not modify the prompt or model context. Its terminal output contains token numbers only. Unmodified payloads remain outside Git.

Each attempt publishes two snapshots produced by the same explicit allowlist:

- `pre-prompt.sanitized.jsonl` is the first complete pre-prompt state after product, plan, model, and quota metadata became available. It has zero total input/output tokens and supports that attempt's exact `quota.before` values.
- `events.sanitized.jsonl` is the final after-response state. It supports the attempt's token counts and exact `quota.after` values.

Both retain product, version, model, effort, plan tier, the native `context_window` fields, and native quota fractions/reset times. They omit the raw fields `cwd`, `session_id`, `conversation_id`, `transcript_path`, `workspace`, `email`, `terminal_width`, `agent_state`, and `sandbox`.

The first launch-only preflight exposed an automatic update from preregistered 1.1.22 to 1.1.23. No prompt was sent. The observed version and frozen settings were replacement-preregistered before the formal attempts, as recorded in [preregistration-replacement-1.1.23.txt](preregistration-replacement-1.1.23.txt).
