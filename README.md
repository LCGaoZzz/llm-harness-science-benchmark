# LLM × Harness 科学计算能力测试

这是一个公开、可复现的轻量基准，用同一项浏览器编程任务比较不同 **Harness + LLM** 组合在科学建模、数学推导、数值计算、编码、验证和可视化方面的综合能力。

本仓库提供固定提示词和统一评分表。每次测试的原始产物由测试者后续上传；它不是模型排行榜，也不假定一次结果能代表模型的全部能力。

## 固定提示词

> 请创建一个可直接在浏览器运行的单文件 HTML“地月限制性三体问题实验室”。基于正确的旋转坐标系方程实时计算航天器轨迹，数值求解并标出 L1–L5，绘制零速度曲线。实现 RK4 和一种适合长期模拟的积分器，支持切换、暂停、单步、重置，以及调整初始位置、速度、时间步长、缩放和平移。实时显示坐标、速度、仿真时间、Jacobi 常数及其漂移，并提供 L4 扰动、L1 不稳定运动、绕地轨道和月球引力辅助等预设。加入真实可执行的自检，验证拉格朗日点残差、步长收敛、守恒量误差和 NaN 防护，禁止预制轨迹或伪造测试结果。代码应结构清晰、界面专业，并实际启动页面、检查控制台、运行测试和修复问题，最后报告验证结果与数值局限。

测试时应原样使用提示词，并记录模型、Harness、日期、运行环境、耗时、工具权限及是否发生人工干预。

## 评分标准（100 分）

每项 10 分。前八项侧重科学、数学与数值计算，后两项评价工程实现和视觉表达。

| # | 评分项 | 10 分标准 |
|---:|---|---|
| 1 | 物理模型 | CR3BP 假设、质量参数、参考系及主天体位置均正确 |
| 2 | 数学方程 | 有效势、运动方程和 Jacobi 常数推导正确，公式与代码一致 |
| 3 | 单位与坐标 | 无量纲单位定义明确，旋转系与惯性系转换正确且可验证 |
| 4 | 拉格朗日点 | L1–L5 计算正确，数值平衡点具有足够小的加速度残差 |
| 5 | 数值积分器 | RK4 与第二种方法均实现正确，且适用于含科氏项的方程 |
| 6 | 收敛与精度 | 减小步长后呈现合理收敛趋势，并报告定量结果 |
| 7 | 守恒量表现 | Jacobi 常数及真实漂移被正确计算，长期误差受控 |
| 8 | 稳定性与边界 | 能妥善处理近碰撞、逃逸、奇点、NaN 和数值失稳 |
| 9 | 验证与工程质量 | 自检真实执行，计算与渲染分离，单文件可直接运行 |
| 10 | 交互与科学可视化 | 轨迹、矢量和曲线表达清晰，比例可信，交互流畅 |

### 单项评分尺度

- **9–10：** 正确、完整，并有定量验证。
- **7–8：** 基本正确，仅有轻微缺陷。
- **5–6：** 可以运行，但验证不足或存在明显简化。
- **3–4：** 只有部分实现，存在重要科学或数值错误。
- **1–2：** 主要是界面展示，计算基本不可信。
- **0：** 缺失、伪造或完全错误。

### 总分封顶规则

- 预制轨迹冒充实时模拟：总分最高 **20**。
- 核心运动方程错误：总分最高 **40**。
- 页面无法独立运行：总分最高 **50**。
- 没有任何可执行验证：总分最高 **70**。

封顶规则在各项正常评分之后应用；如同时触发多项，以最低上限为准。

## 提交方式

每个组合使用独立目录：

```text
submissions/<harness>--<model>--<date>/
├── index.html
├── README.md
└── screenshot.png        # 可选
```

提交说明至少记录：Harness 与版本、模型与版本、日期、完整提示词、运行环境、耗时、工具权限、人工干预、已知问题，以及按本表给出的逐项分数和证据。请保留模型原始产物；人工修复后的版本应另行标注，不能覆盖原始结果。

提交模板见 [`submissions/README.md`](submissions/README.md)。

## 公平性原则

相同对比应尽量使用相同提示词、资源限制和运行环境。评分必须依据实际方程、代码、运行结果和测试证据，不能只依据页面观感或模型自述。模型自带知识、联网、终端、浏览器和自动修复能力都属于 Harness 条件，应如实记录。

## 多专家评审与统一展示（10+4）

**当前榜单是 `codex-gpt-6-astra-xhigh` 的评审样例，不是多专家共识排名。** 该名称标识评审者，与榜内参赛组合的名称分开记录。后续每位专家必须独立署名，并按同一“10+4”结构展示：

1. **10：十项单项排名，附综合总榜。** 对所评快照的全部参赛者，按本 README 原有十项标准分别给分、分别排名，再列出合计、封顶规则与最终总排名。只给得分矩阵或总榜不能替代十个单项榜；每项应有证据及扣分理由。
2. **4：前四名纯科学终评。** 列明从该专家综合榜入选的四份产物，另按最终数学、物理和数值结果给分、排名并提出推荐。若入选边界同分，应说明处理方式。此部分不计界面、工程组织、报告篇幅、自检数量或中间工程文件是否上传；不得因过程材料缺失直接扣科学分。
3. **公开口径。** 两部分分别注明评审者 ID、日期、被评 Git 快照、评分依据和可复核结果。科学终评须公布指标、权重、逐项分数及推荐理由；本样例的权重为 20/15/25/25/15，采用不同权重时必须说明，不能混作同一尺度。
4. **独立保存与追加。** 新评审建议保存到 `reviews/<日期>/<reviewer-id>/`，在下表增加“10”和“4”两个入口，不覆盖其他专家的评分或证据。后续修订保留原版本链接；只有明确约定汇总方法后，才能另列多专家共识榜。尚未完成两部分的评审标记为“未完成”，不得借用其他专家分数补齐。

### 专家评审索引

| 评审者 ID | 日期 | 10：单项排名与综合总榜 | 4：纯科学终评 | 状态与版本 |
|---|---|---|---|---|
| **codex-gpt-6-astra-xhigh** | 2026-09-09 | [十项单项排名](#10-个单项排名) · [总榜](#总排名) · [逐项依据](reviews/2026-09-09/README.md) | [四强终评与证据](reviews/2026-09-09/science-final/README.md) | 已记录为 10+4 样例；[原结果快照 fe815c2](https://github.com/LCGaoZzz/llm-harness-science-benchmark/tree/fe815c262397496d63d9ffbe928e61e49714b0b8) |

以下展示该专家已发布的结果，现有分数与并列关系保持不变。其他专家可作出不同判断，并通过各自的 10+4 记录展示。

## 结果索引

**评审者：`codex-gpt-6-astra-xhigh` · 展示格式：10+4 · 单专家样例。**

已完成 **7 份提交**的独立评阅（2026-09-09）。评分以提交快照 [`ac5a306`](https://github.com/LCGaoZzz/llm-harness-science-benchmark/tree/ac5a306be9b29978ad6787903821b4a6a181ff01) 为准。每项 0–10 分、等权求和，再应用原有封顶规则；本轮 7 份均未触发封顶。

**同分并列，使用竞赛排名（如 1、2、2、4）；表内同分条目的显示顺序不代表先后。** 这些是本次产物的评分，不能据此推断模型总体能力。生成环境、迭代轮数及提示词完整性不完全一致；详见各原始提交说明。

本次更新接续[先前榜单 `53010a4`](https://github.com/LCGaoZzz/llm-harness-science-benchmark/blob/53010a454316d39a1c2cb8c76747a685d80c8674/README.md#结果索引)，及[并行评阅 `bd4a59a`](https://github.com/LCGaoZzz/llm-harness-science-benchmark/blob/bd4a59a83558414797c9a6dad021e9e733e954ab/LEADERBOARD.md)。参赛文件未变；[分数差异与依据](reviews/2026-09-09/METHODS.md#与先前榜单的差异)单独列出，旧版分数仍可追溯。该专家的当前榜单统一在本 README 展示；其他专家的结果由上方索引分别收录。

[评阅方法与限制](reviews/2026-09-09/METHODS.md) · [逐项评分证据](reviews/2026-09-09/README.md) · [机器可读评分](reviews/2026-09-09/scores.json) · [实测记录与截图](reviews/2026-09-09/evidence/)

**后续专项：[前四名纯科学终评](reviews/2026-09-09/science-final/README.md)**。只比较最终数学、物理及数值结果，不计界面、工程材料或中间文件完整度；其权重和结论单列，原综合榜分数保持原评分口径。

### 总排名

| 排名 | 参赛组合 | 原始合计 /100 | 封顶 | 最终得分 /100 | 评阅 |
|---:|---|---:|---|---:|---|
| 1 | [gptweb-gpt-6pro](submissions/gptweb--gpt-6pro--2026-09-09/) | 98 | 无 | **98** | [逐项证据](reviews/2026-09-09/README.md#gptweb) |
| 2 | [codex-6astra-xhigh](submissions/codex--6astra-xhigh--2026-09-09/) | 95 | 无 | **95** | [逐项证据](reviews/2026-09-09/README.md#codex) |
| 3 | [zcode-glm-5.3max](submissions/zcode--glm-5.3max--2026-09-09/) | 88 | 无 | **88** | [逐项证据](reviews/2026-09-09/README.md#zwin) |
| 4 | [harnessL-ds-4.1flashmax](submissions/harnessL--ds-4.1flashmax--2026-09-09/) | 85 | 无 | **85** | [逐项证据](reviews/2026-09-09/README.md#ds) |
| 5 | [zcode-glm-5.3maxlinux](submissions/zcode--glm-5.3maxlinux--2026-09-09/) | 83 | 无 | **83** | [逐项证据](reviews/2026-09-09/README.md#zlinux) |
| 6 | [harnessL-qwen-3.8flashxhigh](submissions/harnessL--qwen-3.8flashxhigh--2026-09-09/) | 74 | 无 | **74** | [逐项证据](reviews/2026-09-09/README.md#qwen) |
| 7 | [kimiweb-k3swarm-max](submissions/kimiweb--k3swarm-max--2026-09-09/) | 72 | 无 | **72** | [逐项证据](reviews/2026-09-09/README.md#kimi) |

### 10 个单项排名

#### 1. 物理模型

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | [codex-6astra-xhigh](reviews/2026-09-09/README.md#codex) | 10 |
| 1 | [gptweb-gpt-6pro](reviews/2026-09-09/README.md#gptweb) | 10 |
| 1 | [harnessL-ds-4.1flashmax](reviews/2026-09-09/README.md#ds) | 10 |
| 1 | [harnessL-qwen-3.8flashxhigh](reviews/2026-09-09/README.md#qwen) | 10 |
| 1 | [zcode-glm-5.3max](reviews/2026-09-09/README.md#zwin) | 10 |
| 1 | [zcode-glm-5.3maxlinux](reviews/2026-09-09/README.md#zlinux) | 10 |
| 7 | [kimiweb-k3swarm-max](reviews/2026-09-09/README.md#kimi) | 9 |

#### 2. 数学方程

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | [codex-6astra-xhigh](reviews/2026-09-09/README.md#codex) | 10 |
| 1 | [gptweb-gpt-6pro](reviews/2026-09-09/README.md#gptweb) | 10 |
| 1 | [harnessL-ds-4.1flashmax](reviews/2026-09-09/README.md#ds) | 10 |
| 1 | [zcode-glm-5.3max](reviews/2026-09-09/README.md#zwin) | 10 |
| 5 | [harnessL-qwen-3.8flashxhigh](reviews/2026-09-09/README.md#qwen) | 9 |
| 5 | [kimiweb-k3swarm-max](reviews/2026-09-09/README.md#kimi) | 9 |
| 5 | [zcode-glm-5.3maxlinux](reviews/2026-09-09/README.md#zlinux) | 9 |

#### 3. 单位与坐标

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | [gptweb-gpt-6pro](reviews/2026-09-09/README.md#gptweb) | 10 |
| 2 | [codex-6astra-xhigh](reviews/2026-09-09/README.md#codex) | 8 |
| 3 | [zcode-glm-5.3maxlinux](reviews/2026-09-09/README.md#zlinux) | 7 |
| 4 | [harnessL-ds-4.1flashmax](reviews/2026-09-09/README.md#ds) | 6 |
| 4 | [harnessL-qwen-3.8flashxhigh](reviews/2026-09-09/README.md#qwen) | 6 |
| 4 | [zcode-glm-5.3max](reviews/2026-09-09/README.md#zwin) | 6 |
| 7 | [kimiweb-k3swarm-max](reviews/2026-09-09/README.md#kimi) | 5 |

#### 4. 拉格朗日点

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | [codex-6astra-xhigh](reviews/2026-09-09/README.md#codex) | 10 |
| 1 | [gptweb-gpt-6pro](reviews/2026-09-09/README.md#gptweb) | 10 |
| 1 | [harnessL-ds-4.1flashmax](reviews/2026-09-09/README.md#ds) | 10 |
| 1 | [harnessL-qwen-3.8flashxhigh](reviews/2026-09-09/README.md#qwen) | 10 |
| 1 | [kimiweb-k3swarm-max](reviews/2026-09-09/README.md#kimi) | 10 |
| 1 | [zcode-glm-5.3max](reviews/2026-09-09/README.md#zwin) | 10 |
| 1 | [zcode-glm-5.3maxlinux](reviews/2026-09-09/README.md#zlinux) | 10 |

#### 5. 数值积分器

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | [codex-6astra-xhigh](reviews/2026-09-09/README.md#codex) | 10 |
| 1 | [gptweb-gpt-6pro](reviews/2026-09-09/README.md#gptweb) | 10 |
| 1 | [zcode-glm-5.3max](reviews/2026-09-09/README.md#zwin) | 10 |
| 4 | [harnessL-ds-4.1flashmax](reviews/2026-09-09/README.md#ds) | 9 |
| 4 | [harnessL-qwen-3.8flashxhigh](reviews/2026-09-09/README.md#qwen) | 9 |
| 6 | [zcode-glm-5.3maxlinux](reviews/2026-09-09/README.md#zlinux) | 8 |
| 7 | [kimiweb-k3swarm-max](reviews/2026-09-09/README.md#kimi) | 6 |

#### 6. 收敛与精度

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | [codex-6astra-xhigh](reviews/2026-09-09/README.md#codex) | 10 |
| 1 | [gptweb-gpt-6pro](reviews/2026-09-09/README.md#gptweb) | 10 |
| 3 | [harnessL-ds-4.1flashmax](reviews/2026-09-09/README.md#ds) | 9 |
| 3 | [zcode-glm-5.3max](reviews/2026-09-09/README.md#zwin) | 9 |
| 5 | [zcode-glm-5.3maxlinux](reviews/2026-09-09/README.md#zlinux) | 8 |
| 6 | [harnessL-qwen-3.8flashxhigh](reviews/2026-09-09/README.md#qwen) | 7 |
| 6 | [kimiweb-k3swarm-max](reviews/2026-09-09/README.md#kimi) | 7 |

#### 7. 守恒量表现

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | [codex-6astra-xhigh](reviews/2026-09-09/README.md#codex) | 10 |
| 1 | [gptweb-gpt-6pro](reviews/2026-09-09/README.md#gptweb) | 10 |
| 1 | [harnessL-ds-4.1flashmax](reviews/2026-09-09/README.md#ds) | 10 |
| 1 | [zcode-glm-5.3max](reviews/2026-09-09/README.md#zwin) | 10 |
| 5 | [zcode-glm-5.3maxlinux](reviews/2026-09-09/README.md#zlinux) | 9 |
| 6 | [harnessL-qwen-3.8flashxhigh](reviews/2026-09-09/README.md#qwen) | 8 |
| 6 | [kimiweb-k3swarm-max](reviews/2026-09-09/README.md#kimi) | 8 |

#### 8. 稳定性与边界

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | [codex-6astra-xhigh](reviews/2026-09-09/README.md#codex) | 9 |
| 1 | [gptweb-gpt-6pro](reviews/2026-09-09/README.md#gptweb) | 9 |
| 3 | [harnessL-ds-4.1flashmax](reviews/2026-09-09/README.md#ds) | 6 |
| 3 | [zcode-glm-5.3max](reviews/2026-09-09/README.md#zwin) | 6 |
| 3 | [zcode-glm-5.3maxlinux](reviews/2026-09-09/README.md#zlinux) | 6 |
| 6 | [harnessL-qwen-3.8flashxhigh](reviews/2026-09-09/README.md#qwen) | 4 |
| 6 | [kimiweb-k3swarm-max](reviews/2026-09-09/README.md#kimi) | 4 |

#### 9. 验证与工程质量

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | [codex-6astra-xhigh](reviews/2026-09-09/README.md#codex) | 10 |
| 1 | [gptweb-gpt-6pro](reviews/2026-09-09/README.md#gptweb) | 10 |
| 3 | [zcode-glm-5.3max](reviews/2026-09-09/README.md#zwin) | 9 |
| 4 | [harnessL-ds-4.1flashmax](reviews/2026-09-09/README.md#ds) | 8 |
| 4 | [zcode-glm-5.3maxlinux](reviews/2026-09-09/README.md#zlinux) | 8 |
| 6 | [kimiweb-k3swarm-max](reviews/2026-09-09/README.md#kimi) | 7 |
| 7 | [harnessL-qwen-3.8flashxhigh](reviews/2026-09-09/README.md#qwen) | 6 |

#### 10. 交互与科学可视化

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | [gptweb-gpt-6pro](reviews/2026-09-09/README.md#gptweb) | 9 |
| 2 | [codex-6astra-xhigh](reviews/2026-09-09/README.md#codex) | 8 |
| 2 | [zcode-glm-5.3max](reviews/2026-09-09/README.md#zwin) | 8 |
| 2 | [zcode-glm-5.3maxlinux](reviews/2026-09-09/README.md#zlinux) | 8 |
| 5 | [harnessL-ds-4.1flashmax](reviews/2026-09-09/README.md#ds) | 7 |
| 5 | [kimiweb-k3swarm-max](reviews/2026-09-09/README.md#kimi) | 7 |
| 7 | [harnessL-qwen-3.8flashxhigh](reviews/2026-09-09/README.md#qwen) | 5 |

### 前四名纯科学终评（4）

评审者：`codex-gpt-6-astra-xhigh`。这是上述综合榜前四名的独立科学评分；[权重、逐项理由与实测证据](reviews/2026-09-09/science-final/README.md)单列。

| 排名 | 参赛组合 | 科学得分 /100 |
|---:|---|---:|
| 1 | harnessL-ds-4.1flashmax | **97** |
| 2 | codex-6astra-xhigh | **96** |
| 2 | gptweb-gpt-6pro | **96** |
| 4 | zcode-glm-5.3max（Windows） | **91** |

该专家推荐 harnessL-ds-4.1flashmax；97 与 96 的差距较小，科学终评已说明权重敏感性。
