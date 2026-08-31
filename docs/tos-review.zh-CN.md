# 服务条款自查

[English](tos-review.md) | **中文**

本页是维护者的**自查记录，不是法律意见**。本页逐产品记录条款版本、与测量相关的条款要点，以及本项目实际采集方式的对照。如发现偏差，请按 [SECURITY.zh-CN.md](../SECURITY.zh-CN.md) 中的私密渠道联系维护者；撤下机制见该页。

## 统一采集方式

对所有产品，维护者均以人工正常方式使用官方界面或客户端，发送最小输入，并记录产品自己显示或写盘的用量。本项目不自动化操作消费者账户，不拦截或解密网络流量，不逆向或修改客户端，也不绕过速率或额度限制。截图经不透明脱敏后才发布。每条公开测量均附带完整复现信息：协议、产品版本、配置和原始单位。

## 产品矩阵

| 产品 / 厂商 | 账户类型 | 条款版本与查阅日期 | 相关条款要点 | 本项目做法对照 | 定性 |
| --- | --- | --- | --- | --- | --- |
| Codex CLI / OpenAI | ChatGPT 订阅登录（个人账户） | [使用条款](https://openai.com/policies/row-terms-of-use/) 2026-01-01 生效；[分享与发布政策](https://openai.com/policies/sharing-publication-policy/) 2022-11-14 更新；2026-08-30 查阅 | 在已核对的个人使用条款中，未发现针对 benchmark 结果发布的事前批准要求。条款禁止自动或程序化提取、逆向工程以及绕过速率限制或其他限制。分享政策通常允许在人工审查并明确披露 AI 生成的前提下分享自己的提示词和回复；其研究部分欢迎与 OpenAI API 有关的研究出版物。OpenAI 保留服务本身的权利，名称和标志的使用受其品牌指南约束。 | 维护者人工启动一次官方 CLI 会话，发送最小提示词，只记录 CLI 自己显示或保存的用量；不自动化操作账户、不拦截流量、不逆向，也不绕过限制。回复明确标识为 AI 输出；脱敏截图仍排除在本项目的 CC BY 授权之外。 | compatible |
| Claude Code / Anthropic | Claude 订阅登录（个人账户） | [消费者服务条款](https://www.anthropic.com/legal/consumer-terms) 2025-10-08 生效；[Anthropic 条款更新公告](https://www.anthropic.com/news/updates-to-our-consumer-terms)确认消费者条款覆盖以 Free、Pro 或 Max 账户使用 Claude Code 的场景；2026-08-30 查阅 | 在已核对的消费者条款中，未发现针对 benchmark 结果发布的事前批准要求。条款禁止爬取、抓取或以其他方式收集服务数据，禁止逆向工程，禁止在 API key 或明确许可以外通过自动化或非人工方式访问，也禁止绕过保护措施。Anthropic 及其提供方保留服务本身的权利。 | 维护者人工操作官方 Claude Code 客户端完成一次最小请求，只记录客户端自己显示或保存的用量。本项目不爬取服务、不自动化操作消费者账户、不检查流量、不逆向客户端，也不绕过保护措施；截图仍排除在本项目的 CC BY 授权之外。 | compatible |
| WorkBuddy / 腾讯 | 个人账户 | [官方用户协议入口](https://rule.tencent.com/rule/202603180001)（未检索到版本与生效日期）；[WorkBuddy 官网](https://www.workbuddy.cn/home)（链接到该入口）；2026-08-30 查阅 | **未检索到。** WorkBuddy 官网链接到腾讯用户协议入口，但本次查阅时无法从公开页面取得协议正文与版本。因此，本页不推断该产品对 benchmark 发布、自动化访问或提取、逆向工程、界面与商标使用的具体要求。 | 已有样本由维护者人工操作官方桌面客户端，发送最小提示词，只记录界面显示或客户端写盘的用量。这符合统一采集方式，但因协议正文不可用，逐项对照尚不完整。 | needs care - 下次采样或数据发布前须取得并核对登录时展示的协议，且界面截图继续排除在 CC BY 授权之外 |
| Google Antigravity CLI / Google | Google AI Pro 订阅登录（个人 Google 账户） | [Google 服务条款](https://policies.google.com/terms?hl=zh-CN) 2026-07-30 生效；[生成式 AI 附加条款](https://policies.google.com/terms/generative-ai?hl=zh-CN) 2023-08-09 最后修改（页面说明该条款自 2024-05-22 起不再适用，签署协议明确引用该条款的商业合作伙伴除外）；[Antigravity 附加条款](https://antigravity.google/terms)（版本与生效日期 not retrieved）；[Antigravity 套餐说明](https://antigravity.google/docs/plans)链接个人账户条款并列明 Google AI Pro；2026-08-31 查阅 | 在已核对条款中，未发现针对 benchmark 结果发布的事前批准要求。Google 服务条款禁止滥用、干扰服务、绕过保护措施、为提取专有信息而逆向工程、违反机器可读指令的自动访问，以及用生成内容开发机器学习技术。Antigravity 条款要求用户对 Agent 行为负责，并禁止通过第三方产品、软件、工具或服务访问该服务。生成式 AI 附加条款按其页面自身说明不再适用于本次个人账户使用，因此不把旧条款作为本场景的适用依据。 | 已有样本由贡献者人工操作官方 Antigravity CLI，完成三次最小提示词请求。产品文档明确支持的 status-line 脚本接收官方 CLI 主动传入的状态 JSON，公开内容只保留白名单内的 token 与额度字段；脚本不单独认证，也不通过第三方客户端访问 Antigravity。本项目未自动化操作账户、拦截流量、逆向客户端、绕过保护措施或用输出训练模型；脱敏界面截图继续排除在 CC BY 授权之外。 | compatible |

**每个新产品的首样 PR 应随场景包提出一行本矩阵。** 维护者在合并时将该行并入本页。矩阵行缺失不阻断 PR，但会在数据发布前补齐。
