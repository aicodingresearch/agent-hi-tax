# Runs

**English** | [中文](README.zh-CN.md)

`runs/` holds public test scenarios that have been redacted and checked.

Screenshots in this directory are excluded from the CC BY grant (see [LICENSE-DATA](../LICENSE-DATA)); measurement data (`CSV`, `YAML`, and `JSONL`) remain licensed under CC BY 4.0.

Each scenario contains at least 3 valid independent runs. Scenario-level environment, subscription, and harness evidence is stored only once; each run's reply, usage, and trimmed events live separately under `attempts/`.

[Compare all scenarios together in the Hi Tax Index](../RESULTS.md).

Current reference samples:

- [Codex CLI 0.147.0 / GPT-5.6 Sol / high / hi-en-v1 / macOS arm64](2026-08-14/codex-cli-0.147.0_gpt-5.6-sol_high_hi-en-v1_as-used_mac-arm64/README.md)
- [Claude Code 2.1.220 / Fable 5 / high / hi-en-v1 / macOS arm64](2026-08-15/claude-code-2.1.220_claude-fable-5_high_hi-en-v1_as-used_mac-arm64/README.md)
- [Claude Code 2.1.220 / Opus 5 / high / hi-en-v1 / macOS arm64](2026-08-15/claude-code-2.1.220_claude-opus-5_high_hi-en-v1_as-used_mac-arm64/README.md)
- [WorkBuddy 5.3.13 / Auto / craft / hi-en-v1 / macOS arm64](2026-08-15/workbuddy-5.3.13_auto_craft_hi-en-v1_as-used_mac-arm64/README.md)

Directory conventions are in the [contributing guide](../CONTRIBUTING.md#run-package-layout).
