# Runs

[English](README.md) | **中文**

`runs/` 保存已经完成脱敏和核对的公开测试场景。

本目录下的截图排除在 CC BY 授权之外（见 [LICENSE-DATA](../LICENSE-DATA)）；测量数据（`CSV`、`YAML`、`JSONL`）照常按 CC BY 4.0 发布。

每个场景至少包含 3 次有效独立运行。场景级环境、订阅和 harness 证据只保存一次；每次运行的回复、usage 和精简事件分别放在 `attempts/` 下。

[在 Hi Tax Index 中汇总比较全部场景](../RESULTS.zh-CN.md)。

当前已公开场景：

- [Codex CLI 0.147.0 / GPT-5.6 Sol / high / hi-en-v1 / macOS arm64](2026-08-14/codex-cli-0.147.0_gpt-5.6-sol_high_hi-en-v1_as-used_mac-arm64/README.md)
- [Claude Code 2.1.220 / Fable 5 / high / hi-en-v1 / macOS arm64](2026-08-15/claude-code-2.1.220_claude-fable-5_high_hi-en-v1_as-used_mac-arm64/README.md)
- [Claude Code 2.1.220 / Opus 5 / high / hi-en-v1 / macOS arm64](2026-08-15/claude-code-2.1.220_claude-opus-5_high_hi-en-v1_as-used_mac-arm64/README.md)
- [WorkBuddy 5.3.13 / Auto / craft / hi-en-v1 / macOS arm64](2026-08-15/workbuddy-5.3.13_auto_craft_hi-en-v1_as-used_mac-arm64/README.md)
- [Google Antigravity CLI 1.1.22 / Gemini 3.7 Flash / high / hi-en-v1 / Windows x64](2026-08-30/antigravity-cli-1.1.22_gemini-3.7-flash_high_hi-en-v1_as-used_windows-x64_beautyarbutin/README.md)
- [Codex CLI 0.147.0 / GPT-5.6 Sol / high / hi-en-v1 / Windows x64](2026-08-30/codex-cli-0.147.0_gpt-5.6-sol_high_hi-en-v1_as-used_windows-x64_beautyarbutin/README.md)

目录约定见[贡献指南](../CONTRIBUTING.zh-CN.md#场景包目录)。
