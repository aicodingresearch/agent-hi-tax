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

1. 在此 as-used 配置（含 bypassPermissions 及权限白名单）下，Claude Code harness 注入约 23.5K tokens（输入 `hi` 前已加载）；该数值取决于具体配置和后端，非 Claude Code 通用常量
2. R2 和 R3 命中了缓存（cache_read: 19,840 tokens），首次观察到跨会话服务端 prompt cache 命中
3. 与 Fable 5 样板对比：后端变化（GLM vs Claude）为意图变量，但版本（2.1.119 vs 2.1.220）、OS（Windows vs macOS）及账户/路由均不同，比较受混杂

## 参考

- 参考样板：[Claude Code Fable 5](../2026-08-15_claude-code-2.1.220_claude-fable-5_high_hi-en-v1_as-used_mac-arm64/README.md)
- 任务编号：T-62
