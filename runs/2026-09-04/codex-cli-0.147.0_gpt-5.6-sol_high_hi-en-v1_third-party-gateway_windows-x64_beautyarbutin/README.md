# T-50：Codex CLI × gpt-5.6-sol × high × IKUN Family

这是 T-50 的中转站侧预注册包，使用 Codex CLI 0.147.0，在 Windows 11 x64 上通过 IKUN Family 网关请求 `gpt-5.6-sol`，effort 固定为 `high`。

- 任务：T-50
- Issue：[aicodingresearch/agent-hi-tax#96](https://github.com/aicodingresearch/agent-hi-tax/issues/96)
- 路由：`third-party-gateway`（IKUN Family，`api.ikungod.online`）
- 标准输入：`hi-en-v1`，文件内容严格为两个 UTF-8 字节 `hi`
- 计划运行：R1、R2、R3，均为独立 fresh 会话，先完成本中转站侧，再建立官方 API 侧；两侧不交替

## 正式结果

三次正式运行均在独立空目录和 fresh session 中完成，每次只发送一次 \`hi\`。退出界面提供了精确 usage：

| Attempt | Input | Cached input | Output | Total |
|---|---:|---:|---:|---:|
| R1 | 844 | 0 | 14 | 858 |
| R2 | 12,492 | 3,968 | 12 | 12,504 |
| R3 | 13,132 | 3,328 | 14 | 13,146 |

R1 明显低于 R2/R3，但没有观察到错误配置、额外交互或失败，因此按协议保留为有效异常值；没有追加 R4，也没有挑选或替换样本。三次的网关额度均未公开提供，quota 字段统一为 \`not_provided\`，不对网关余额变化作归因。

此前误在 \`preflight\` 目录发送过一次 \`hi\`，该 probe 已标为 \`invalid\`，仅作诊断证据，不计入上述三次结果。API key 只在本机私有环境变量中提供，绝不进入仓库。
