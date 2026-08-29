# 实测指南：从领任务到提交 PR

[English](contributor-walkthrough.md) | **中文**

> 第一次参与的贡献者照着本页从上往下做即可。规则细节以[贡献指南](../CONTRIBUTING.zh-CN.md)为准，本页负责把它变成一条能走完的路。

## 一、你要做的事，一句话

在一个事先声明、事后可复核的环境里，向一个 AI Agent 发送完全相同的一句小输入（标准 case 是 [`hi`](../prompts/hi-en-v1.txt)），顺序执行至少 3 次，把每次实际发生的消耗——token、积分、额度、延迟——连同环境证据完整记录、脱敏、打包，提交一个 Pull Request。

## 二、为什么值得做

### 1. 这是对 Agent harness 的一次"零输入探针"测量

这里说的 harness，指的是 Agent 产品包在模型外面的整套系统：system prompt、工具与 MCP 定义、规则文件加载、工作区探测、会话与缓存管理、请求路由。平时它是黑盒——即使读过部分开源实现，也很难量化"它到底往每次请求里注入了多少东西"。

这个实验的设计恰好把 harness 变成被测对象。`hi` 的可见输入只有 2 个字符；但已有数据显示：

- Claude Code 样板里，普通 input 只有 **2 tokens**，首次请求却同时创建了约 **25K tokens** 的缓存；
- 四个已完成场景的单次输入上下文在约 **1.4 万到 3.3 万 tokens** 之间。

当用户输入趋近于零时，这些输入 token 几乎全部来自 harness 本身。因此：

- **单个场景** = 某个真实 harness 固定开销的一次直接测量；
- **两个只差一个变量的场景之差** = harness 中那个具体组件（一个 MCP server、一份规则文件、一个 effort 档位、一种权限模式）的边际 token 成本；
- **同一场景随时间的重复观察** = harness 演进（产品升级改 prompt、增删工具）的纵向记录。

换句话说，你交上来的每一个场景包，都是给某个真实 harness 在某个时刻"称了一次重"。[待测场景清单](wanted-scenarios.zh-CN.md)的 D 组任务就是按这个思路设计的对照实验。

顺带你还会直面各厂商计量口径的真实差异——例如 Codex 的 cached input 是 input 的子集，而 Anthropic 的三个 input 桶是相加关系。搞清这些口径，本身就是理解 harness 计费与缓存设计的第一手材料。

### 2. 这些数据本身有公共价值

"发一句 hi 掉了 1% 额度"这类抱怨在社区里到处流传，但几乎没有一条带着可复核的证据。这个仓库在把传闻变成数据：统一协议、原生口径、分层证据、文件哈希、自动校验。你的每一个场景包都是这个公共数据集的一条真实记录，别人可以引用、复测、推翻。

### 3. 这是一次完整的实证研究训练

流程里的每个环节都对应实证方法的一个标准动作：

- **预注册**：先在 manifest 里固定场景，再开始执行，杜绝"边测边调"；
- **控制变量**：一次只允许一个变量变化，其他任何变化都拆成新场景；
- **证据分层**：每个字段标注 `verified` / `self_reported` / `not_exposed` 等状态，结论强度与证据强度挂钩；
- **诚实处理异常值**：跑废的 attempt 标 `invalid` 保留，不删除、不挑好看的三次；
- **可复核打包**：SHA-256 哈希 + 自动校验脚本 + 公开脱敏证据。

这套方法比任何一个具体数字都更接近研究训练的目的。

## 三、开始之前

### 1. 挑一个任务

打开[待测场景清单](wanted-scenarios.zh-CN.md)，按你手头的订阅、产品和设备挑一条。第一次做建议从 A 组（复测）开始。**不要为了任务去买订阅。**

### 2. 认领

在仓库开一个 issue，标题 `[Claim] T-xx 一句话场景描述`，写明计划的 Agent 版本、模型、订阅档位和预计完成时间。

### 3. 花 10 分钟记住六条规则

完整版见[贡献指南](../CONTRIBUTING.zh-CN.md#最重要的六条规则)，速记版：

1. 一个场景至少 3 次有效独立运行，顺序执行不并行；
2. 场景变量中途不许变，变了就是另一个场景；
3. 环境证据只采一次，不用截三套；
4. 每次运行只采本次结果：精确输入、完整回复、原生 usage；
5. 拿得到的证据要提供，拿不到就用固定缺失状态标注，不猜；
6. 不把一个 total 当成本：cached input、非缓存 input、output、积分、百分比分开存，不擅自换算。

### 4. 检查你需要的东西

- 一台 macOS、Windows 或 Linux 机器（如实记录系统与架构）；
- 被测 Agent 产品 + 有效的订阅或 API 访问；
- git 和 GitHub 账号；
- `python3`（运行校验脚本）；
- **一段约 30 分钟不被打断的时间**：一次贡献通常约 30 分钟即可完成；首次贡献建议预留约 1 小时，足以阅读文档、处理脱敏并完成一个场景。三次运行必须顺序完成，中途别切换配置、别升级软件。

## 四、动手：一步步做

### 第 0 步：Fork、clone、建分支

在 GitHub 上 fork [aicodingresearch/agent-hi-tax](https://github.com/aicodingresearch/agent-hi-tax)，然后：

```sh
git clone https://github.com/<你的用户名>/agent-hi-tax.git
cd agent-hi-tax
git checkout -b run/<产品>-<模型>-<日期>
```

一个分支只放一个场景。

### 第 1 步：选采集适配器（或走通用路径）

目前已经写好的适配器，选与你产品最接近的一份，通读一遍：

- [Codex CLI](adapters/codex-cli.zh-CN.md)
- [Claude Code](adapters/claude-code.zh-CN.md)
- [WorkBuddy Desktop](adapters/workbuddy-desktop.zh-CN.md)

这份清单只代表采样已经走到哪里，不限制可以提交哪些 Agent：**任何 Agent 产品都欢迎**。你的产品没有适配器时，按[贡献指南](../CONTRIBUTING.zh-CN.md)的通用语义采集，把产品差异记下来写进 PR；有余力的话顺手起草一份 `docs/adapters/<产品>.md`，下一个测同款产品的人就有路可循。适配器不要求你关闭已有代理、sandbox 或账号安全设置——它们属于场景的一部分，保持原样并如实记录。

### 第 2 步：固定场景（这一步就是"预注册"）

复制 [`templates/scenario-manifest.yaml`](../templates/scenario-manifest.yaml)，填写所有能确定的场景变量：产品与精确版本、模型、effort、订阅与路由、操作系统、harness profile（大多数人应诚实选 `as-used` 并列出已知规则、skills、MCP、plugins、hooks）、计划重复次数，并固定 launch command。

**从这一刻起，模型、effort、版本、权限模式、插件状态都不许再动。** 动了任何一项，就是另一个场景。

如果你要主张额度变化（quota before/after），现在就暂停同账号、同额度池的其他一切使用；做不到就把额度归因标 `contaminated`（session 自身的 token 记录仍然有效）。

### 第 3 步：在仓库外建一个证据目录

```sh
mkdir -p ~/hi-tax-evidence/<场景名>
```

原始截图、原始 session/transcript **永远不直接进 Git**。先全部收进这个目录，最后一步才把脱敏副本复制进仓库。

### 第 4 步：环境预检（只做一次）

在正式运行前，采集一次场景级证据：

1. 运行版本与环境命令并保存输出（macOS 示例，其他系统用等价命令）：

   ```sh
   command -v <agent>
   <agent> --version
   sw_vers
   uname -m
   date -u '+%Y-%m-%dT%H:%M:%SZ'
   ```

2. 截图保存：订阅档位页面、模型与 effort 配置、启动界面；
3. 记录 harness 清单：规则文件、skills、MCP、plugins、hooks、权限模式。注意 MCP 即使不被调用，工具定义也会进入上下文，必须记录启动状态；会调用模型的 hook 也是 harness 的一部分，不能隐去。

同一组三次运行共用这一套环境证据，不要重复截三份。

### 第 5 步：顺序执行 3 次

对 R1、R2、R3，每次严格按这张执行卡：

1. 新建一个独立的空工作区目录（确认为空且不是 Git 仓库）；
2. 启动一个全新会话（fresh 场景不得退出后 resume）；
3. 发送 prompt 之前确认模型和 effort（可以用产品自带的 `/status` 类命令，但不要发额外聊天消息）；
4. 确认 footer / permission mode 与前几次一致——不一致就停下，要么标为混杂，要么另立场景；
5. 只发送一次精确输入 `hi`（两个小写字母，不带标点、空格和换行；Enter 只负责提交）；
6. 回复完成后，截一张包含输入和完整回复的图，存到证据目录；
7. 记录开始/结束时间与计时方法；正常退出并保存产品暴露的原生 usage（退出界面截图、usage 页面或事件日志）；
8. 本次完全结束后，再开始下一次。

**跑废了怎么办**：误输入、手滑 resume、目录不空、网络失败、发生额外交互——都不用慌。把这次保留并标为 `invalid` 或 `error`，写明原因，然后追加新的 attempt，直到凑满 3 次有效运行。**不要删除异常值，也不要挑数据最好看的三次。**

### 第 6 步：整理场景包

在 `runs/YYYY-MM-DD/<scenario-id>/` 下建立如下结构（详见[贡献指南·场景包目录](../CONTRIBUTING.zh-CN.md#场景包目录)）：

如果目标目录已存在，或同日同场景已被其他贡献者认领，请在目录名与 manifest 的 `scenario.id` 末尾同时追加 `_<github-handle>`（例如 `..._mac-arm64_alice`）。

```text
runs/YYYY-MM-DD/<scenario-id>/
  README.md
  manifest.yaml
  prompt.txt
  launch-command.txt        # CLI 场景适用
  RESULTS.csv
  SHA256SUMS                # 最后一步生成
  evidence/                 # 场景级证据（脱敏后）
  attempts/r1 r2 r3/        # 每次的 result.yaml、response.txt、response.png、精简事件日志
```

**不要从空白模板开始猜字段。** 从[四个完整样板](../runs/README.zh-CN.md)里挑与你产品最接近的一个，整包复制后逐项替换成自己的数据。厂商原生字段的含义不要为了"看起来一致"而修改；不适用写 `not_applicable`，没暴露写 `not_exposed`，没拿到写 `not_provided`。

### 第 7 步：脱敏

红线——以下内容绝对不能出现在任何提交文件里：

- API key、token、cookie、authorization header、中转站凭据；
- 账号邮箱、账号 ID、支付信息；
- session ID、resume 命令等会话恢复标识；
- 本机用户名、主机名、完整 home 路径（转录里把 home 改写成 `~`）；
- 私有仓库内容、私人规则正文、无关聊天历史。

截图处理规则：裁剪或用**完全不透明色块**遮挡后展平导出；不要用马赛克或高斯模糊（可逆）。脱敏不能改动用量数字、事件顺序和关键时间。每张公开图逐张目视检查一遍。

不想公开某张原图也可以：原图留在本机，对应字段标 `not_provided` 先提交；后续维护者通过私密渠道核对后可升级为 `private_evidence`。**绝不要先上传原图再等人删。**

### 第 8 步：生成哈希并校验

所有公开文件定稿后（任何再编辑都要重新生成）：

```sh
cd runs/YYYY-MM-DD/<scenario-id>
find . -type f ! -name SHA256SUMS -print0 \
  | LC_ALL=C sort -z \
  | xargs -0 shasum -a 256 > SHA256SUMS
cd -

./scripts/verify-run-package.sh runs/YYYY-MM-DD/<scenario-id>
```

Linux 上没有 `shasum` 可用 `sha256sum`。脚本报错就按提示修，修完重新生成哈希再跑。

### 第 9 步：重建汇总索引

```sh
python3 scripts/build-results-index.py
./scripts/verify-all.sh
```

两条都通过、`RESULTS.md` 与 `RESULTS.zh-CN.md` 已更新，才算打包完成。CI 会检查索引是否与场景包漂移。

### 第 10 步：提交 Pull Request

```sh
git add runs/ RESULTS.md RESULTS.zh-CN.md
git commit -m "data: add <场景一句话描述> sample"
git push -u origin <分支名>
```

到 GitHub 开一个 **Draft PR**（一个 PR 只放一个场景），按 [PR 模板](../.github/pull_request_template.md)填写：场景摘要、有效/无效 attempts 数、证据等级与缺失字段、协议偏差、校验输出、额度归因说明。等自动校验通过、截图逐张目视复查完，再标记 Ready for review，并在认领 issue 里留个链接。

## 五、提交之后会发生什么

CI 自动检查包结构、算术一致性、哈希和文本隐私线索；维护者人工 review 的重点是内部一致性、字段状态、脱敏质量和结论是否克制——**不会**因为你的产品暴露的字段比别人少而拒收。

常见返工点，提交前自己先扫一遍：

- cached input 被重复相加（注意你的厂商是"子集"口径还是"相加"口径）；
- 截图漏遮邮箱、用户名或 session ID；
- `SHA256SUMS` 不是最后生成的（改了文件没重新生成）；
- 忘记重建根级索引（`RESULTS.md` 与 `RESULTS.zh-CN.md`）；
- 把共享额度差值直接说成"这次 hi 的成本"而没有归因说明。

## 六、常见问题

**我只有 API key，没有订阅，能做吗？**
能。路由如实标 `official-api`，这本身就是一个有价值的场景变量。

**数据看起来"不对劲"或"不好看"，还要交吗？**
要。异常值是数据，不是错误。三次之间的波动、意外的缓存行为、和现有样板不一致的结果，往往比"正常"数据更有讨论价值——如实记录并在 PR 里指出即可。

**某个字段产品根本不显示怎么办？**
用固定状态：`not_exposed`（产品没暴露）、`not_provided`（可能有但这次没拿到）、`conflicted`（两个来源打架，两个都保留）。缺字段不阻断 PR，只影响这条记录能支持的结论强度。

**只有截图、没有机器日志，够吗？**
够。那是 Level B 证据，诚实标注即可。不要为了凑 Level A 去解析自己不理解的内部日志。

**我的 Agent 三次路由到了不同模型？**
如果你固定选的是产品的 `Auto`，这是正常结果：requested model 记 `Auto`，每次的实际模型逐次记录，仍属同一场景。显式固定了模型却发生漂移，才需要标记执行错误或拆场景。

**三次做完发现版本和认领时写的不一样？**
如实记录实际版本即可，在 PR 里说明。版本以实测为准，不需要重做。

**大概要花多久？**
通常约 30 分钟。首次贡献建议预留约 1 小时，足以阅读文档、处理脱敏并完成一个场景。三次运行本身很快，时间主要花在证据整理上。

## 七、提交前最后自查

- [ ] 同一场景至少 3 次有效独立运行，顺序执行；
- [ ] 三次的 prompt、模型、effort、版本、路由、permission mode、harness 完全一致；
- [ ] 环境证据只有一套，attempt 证据每次一套；
- [ ] 缺失/冲突字段全部用固定状态标注，没有猜测值；
- [ ] cached input 没有按错误口径重复相加；
- [ ] 共享额度污染已标注；
- [ ] 公开文件无凭据、邮箱、用户名、home 路径、会话恢复标识；截图逐张目视检查过；
- [ ] `SHA256SUMS` 是最后生成的；
- [ ] `RESULTS.md` 与 `RESULTS.zh-CN.md` 已重建，`./scripts/verify-all.sh` 通过；
- [ ] PR 模板填写完整，一个 PR 只有一个场景。

---

做完一单，欢迎回到[待测场景清单](wanted-scenarios.zh-CN.md)领下一单——或者提出你自己的场景组合。
