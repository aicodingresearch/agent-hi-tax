# Antigravity CLI status-line instrumentation

Antigravity CLI 1.1.22 supports a command-backed status line that receives a product-native JSON state object on standard input. This scenario uses that documented interface as a passive local observer.

Official documentation:

- <https://antigravity.google/docs/cli/statusline/>
- <https://antigravity.google/docs/cli/commands/usage/>

Frozen capture-script SHA-256:

```text
31f0a32cf143405c298a98d9a8ceb762b123432ece623364d8bf2231d490906e
```

The command makes no network or model request and does not modify the prompt or model context. Its terminal output contains token numbers only. Unmodified payloads remain outside Git.

Each public `events.sanitized.jsonl` is a single after-response snapshot produced by an explicit allowlist. It retains product, version, model, effort, plan tier, the native `context_window` fields, and native quota fractions/reset times. It omits the raw fields `cwd`, `session_id`, `conversation_id`, `transcript_path`, `workspace`, `email`, `terminal_width`, `agent_state`, and `sandbox`.

The first Windows preflight exposed a literal-quote `-File` parsing problem. The command was corrected and the settings hash was re-frozen before any formal prompt, as recorded in [preregistration-statusline-replacement.txt](preregistration-statusline-replacement.txt).
