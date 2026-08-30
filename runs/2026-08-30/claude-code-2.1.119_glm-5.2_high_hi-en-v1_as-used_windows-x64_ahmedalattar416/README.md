# Claude Code × GLM-5.2 × Windows 11 测试

- **场景**：Claude Code 2.1.119 × GLM-5.2 × high effort × third-party-gateway (Z.ai) × Windows 11
- **标准输入**：`hi-en-v1`
- **测试日期**：2026-08-30
- **贡献者**：[@AHMEDALATTAR416](https://github.com/AHMEDALATTAR416)

## 三次运行结果

| 指标 | R1 | R2 | R3 |
|------|------:|------:|------:|
| input_tokens | 23,552 | 3,712 | 3,712 |
| cache_read_input_tokens | 0 | 19,840 | 19,840 |
| output_tokens | 11 | 12 | 11 |
| 总输入 | 23,552 | 23,552 | 23,552 |
| 上下文总量 | 23,563 | 23,564 | 23,563 |

## 关键发现

1. Claude Code harness 固定注入约 23.5K tokens（输入 `hi` 前已加载）
2. R2 和 R3 命中了缓存（cache_read: 19,840 tokens）
3. 与 Fable 5 样板对比：Harness 恒定，后端变化（GLM vs Claude）
4. 版本差异：2.1.119 vs 参考样板的 2.1.220

## 参考

- 参考样板：[Claude Code Fable 5](../2026-08-15_claude-code-2.1.220_claude-fable-5_high_hi-en-v1_as-used_mac-arm64/README.md)
- 任务编号：T-62 T-16