# ZCode 3.10.2 × GLM-5.3-Flash × highest × hi

这是一次 Agent Hi Tax T-67 ZCode 首样场景的实测包。测试在 macOS arm64 上使用 ZCode 3.10.2，模型选择器固定为 `GLM-5.3-Flash`，effort 固定为产品原生标签 `最高`，模式固定为 `变更前确认`，每次在新的空目录和新任务中只发送一次 `hi`。

## 结果

三次顺序运行均有效，回复均为 ZCode 的简短问候。ZCode 界面显示的原生上下文用量分别为 28,585、28,614、28,595 / 1,000,000。该字段是产品界面显示的上下文占用，不能据此推导本次请求的输入、输出或订阅费用；产品未在本次界面中提供 token 分桶、cost 或单次额度消耗。

| attempt | status | model | effort | context usage displayed | UI latency | response |
| --- | --- | --- | ---: | ---: | ---: | --- |
| r1 | valid | GLM-5.3-Flash | 最高 | 28,585 / 1,000,000 | 7 s | Hi! I'm ZCode, ready to help... |
| r2 | valid | GLM-5.3-Flash | 最高 | 28,614 / 1,000,000 | 4 s | Hi! I'm ZCode, ready to help... |
| r3 | valid | GLM-5.3-Flash | 最高 | 28,595 / 1,000,000 | 4 s | Hi! I'm ZCode, ready to help... |

## 证据边界

证据等级为 C。公开包保留脱敏后的最小事件、提示词、回复和原生界面上下文用量；原始界面截图未进入仓库。r2 的回复曾包含本地工作目录，公开回复已用 `[redacted-local-path]` 替换，并在协议偏差中登记。

ZCode 没有现成仓库适配器，本包采用通用 GUI 语义。产品版本来自本机应用元数据，模型、effort、模式、回复和上下文用量来自产品界面。账号档位、token 分桶、cost、单次额度、工具调用明细和 harness 注入字段在本次测试中没有公开取得。

## 协议偏差

- 产品界面显示的是按秒取整的工作时长，因此没有伪造毫秒级 latency。
- r2 回复暴露了本地工作目录；保留该运行，公开文本只做隐私替换。
- 共享账户额度未测量，quota attribution 标为 `not_measured`。
- 运行期间保持模型、effort、模式、版本和空目录条件一致；三次测试顺序执行。

## 校验

本包按仓库通用流程生成，结果应通过 `verify-run-package.sh`；根目录索引由 `build-results-index.py` 重新生成。
