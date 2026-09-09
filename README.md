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

**以下按评审者独立收录，尚未形成多专家共识排名。** `codex-gpt-6-astra-xhigh` 提供首份完整样例。评审者 ID 与榜内参赛组合名称分开记录；每位专家均按同一“10+4”结构展示：

1. **10：十项单项排名，附综合总榜。** 对所评快照的全部参赛者，按本 README 原有十项标准分别给分、分别排名，再列出合计、封顶规则与最终总排名。只给得分矩阵或总榜不能替代十个单项榜；每项应有证据及扣分理由。
2. **4：前四名纯科学终评。** 列明从该专家综合榜入选的四份产物，另按最终数学、物理和数值结果给分、排名并提出推荐。若入选边界同分，应说明处理方式。此部分不计界面、工程组织、报告篇幅、自检数量或中间工程文件是否上传；不得因过程材料缺失直接扣科学分。
3. **公开口径。** 两部分分别注明评审者 ID、日期、被评 Git 快照、评分依据和可复核结果。科学终评须公布指标、权重、逐项分数及推荐理由；本样例的权重为 20/15/25/25/15，采用不同权重时必须说明，不能混作同一尺度。
4. **独立保存与追加。** 新评审建议保存到 `reviews/<日期>/<reviewer-id>/`，在下表增加“10”和“4”两个入口，不覆盖其他专家的评分或证据。自动生成时只更新本专家署名的标记区，不得改写整份 README。后续修订保留原版本链接；只有明确约定汇总方法后，才能另列多专家共识榜。尚未完成两部分的评审标记为“未完成”，不得借用其他专家分数补齐。

### 专家评审索引

| 评审者 ID | 日期 | 10：单项排名与综合总榜 | 4：纯科学终评 | 状态与版本 |
|---|---|---|---|---|
| **codex-gpt-6-astra-xhigh** | 2026-09-09 | [十项单项排名与总榜](reviews/2026-09-09/codex-gpt-6-astra-xhigh/README.md) · [逐项依据](reviews/2026-09-09/README.md) | [四强终评与证据](reviews/2026-09-09/science-final/README.md) | 已记录为 10+4 样例；[原结果快照 fe815c2](https://github.com/LCGaoZzz/llm-harness-science-benchmark/tree/fe815c262397496d63d9ffbe928e61e49714b0b8) |
| **gptweb-gpt-6-astra-pro** | 2026-09-09 | [十项单项排名与综合总榜](reviews/2026-09-09/gptweb-gpt-6-astra-pro/README.md#gptweb-gpt-6-astra-pro-ten) | [四强终评与证据](reviews/2026-09-09/gptweb-gpt-6-astra-pro/README.md#gptweb-gpt-6-astra-pro-four) | 10+4 已完整收录；十项为既有评分的独立复核，四强为新科学评分；[原始材料与来源](reviews/2026-09-09/gptweb-gpt-6-astra-pro/README.md#原始材料与导入核对) |
| **kimiweb-k3-swarmmax** | 2026-09-09 | [十项单项排名与综合总榜](reviews/2026-09-09/kimiweb-k3-swarmmax/README.md#ten) · [机器可读评分](reviews/2026-09-09/kimiweb-k3-swarmmax/scores.json) | [四强纯科学终评与推荐](reviews/2026-09-09/kimiweb-k3-swarmmax/README.md#four) | 已完成 10+4；首评归档 [SCOREBOARD.md](SCOREBOARD.md)（[648dcc3](https://github.com/LCGaoZzz/llm-harness-science-benchmark/tree/648dcc3)）；被评快照 [e45bd40](https://github.com/LCGaoZzz/llm-harness-science-benchmark/tree/e45bd407f12140758623eb2352360435874b2afa) |
| **zcode-glm-5.3max-win** | 2026-09-09 | [十项单项排名与总榜](reviews/2026-09-09/zcode-glm-5.3max-win/README.md) · [机器可读评分](reviews/2026-09-09/zcode-glm-5.3max-win/scores.json) | [四强纯科学终评](reviews/2026-09-09/zcode-glm-5.3max-win/science-final/README.md) | 已完成 10+4；被评快照 [ac5a306](https://github.com/LCGaoZzz/llm-harness-science-benchmark/tree/ac5a306be9b29978ad6787903821b4a6a181ff01) |

以下依次展示各专家的 10+4 记录，原有分数与并列关系保持不变。并行提交 648dcc3 的 SCOREBOARD.md 已登记为评审者 `kimiweb-k3-swarmmax` 的首评归档（其正式 10+4 记录见 reviews/2026-09-09/kimiweb-k3-swarmmax/）。各份记录分别注明评分来源与复核关系；其他专家可作出不同判断。

<!-- BEGIN REVIEW codex-gpt-6-astra-xhigh -->
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
<!-- END REVIEW codex-gpt-6-astra-xhigh -->

<!-- BEGIN REVIEW gptweb-gpt-6-astra-pro -->
## gptweb-gpt-6-astra-pro：10+4 评审记录

**评审者：`gptweb-gpt-6-astra-pro` · 2026-09-09 · 状态：10+4 已完整收录。**

评审者身份由仓库所有者在导入请求中指定，与参赛组合 `gptweb-gpt-6pro` 分开记录。两部分均评阅源快照 [`ac5a306`](https://github.com/LCGaoZzz/llm-harness-science-benchmark/tree/ac5a306be9b29978ad6787903821b4a6a181ff01)。

[完整署名记录与原始材料](reviews/2026-09-09/gptweb-gpt-6-astra-pro/README.md)。

<a id="gptweb-gpt-6-astra-pro-ten"></a>

### 10：十项单项排名与综合总榜

**评分来源：独立执行复核后，保留既有统一榜 [`faef8de`](https://github.com/LCGaoZzz/llm-harness-science-benchmark/blob/faef8de83fd70487b8986fe58c972dd403eb2176/README.md)。** 原包明确说明这不是另一套独立分值估计；本记录保留这一来源关系，不把相同分数当作两次独立评分。[原包说明](reviews/2026-09-09/gptweb-gpt-6-astra-pro/ten-category/README.md) · [独立复核报告](reviews/2026-09-09/gptweb-gpt-6-astra-pro/ten-category/repo/evaluations/2026-09-09-independent/REVIEW.md) · [原始十项分数](reviews/2026-09-09/gptweb-gpt-6-astra-pro/ten-category/repo/evaluations/2026-09-09-independent/scores.json) · [原有 70 项理由](https://github.com/LCGaoZzz/llm-harness-science-benchmark/blob/faef8de83fd70487b8986fe58c972dd403eb2176/reviews/2026-09-09/README.md)。

十项各 10 分，等权求和；本包七份均无封顶。同分采用竞赛排名，表内同分行的先后不表示优劣。

#### 综合总排名

| 排名 | 参赛组合 | 原始合计 /100 | 封顶 | 最终得分 /100 |
|---:|---|---:|---|---:|
| 1 | gptweb-gpt-6pro | 98 | 无 | **98** |
| 2 | codex-6astra-xhigh | 95 | 无 | **95** |
| 3 | zcode-glm-5.3max | 88 | 无 | **88** |
| 4 | harnessL-ds-4.1flashmax | 85 | 无 | **85** |
| 5 | zcode-glm-5.3maxlinux | 83 | 无 | **83** |
| 6 | harnessL-qwen-3.8flashxhigh | 74 | 无 | **74** |
| 7 | kimiweb-k3swarm-max | 72 | 无 | **72** |

#### 1. 物理模型

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 1 | harnessL-ds-4.1flashmax | 10 |
| 1 | harnessL-qwen-3.8flashxhigh | 10 |
| 1 | zcode-glm-5.3max | 10 |
| 1 | zcode-glm-5.3maxlinux | 10 |
| 7 | kimiweb-k3swarm-max | 9 |

#### 2. 数学方程

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 1 | harnessL-ds-4.1flashmax | 10 |
| 1 | zcode-glm-5.3max | 10 |
| 5 | harnessL-qwen-3.8flashxhigh | 9 |
| 5 | kimiweb-k3swarm-max | 9 |
| 5 | zcode-glm-5.3maxlinux | 9 |

#### 3. 单位与坐标

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | gptweb-gpt-6pro | 10 |
| 2 | codex-6astra-xhigh | 8 |
| 3 | zcode-glm-5.3maxlinux | 7 |
| 4 | harnessL-ds-4.1flashmax | 6 |
| 4 | harnessL-qwen-3.8flashxhigh | 6 |
| 4 | zcode-glm-5.3max | 6 |
| 7 | kimiweb-k3swarm-max | 5 |

#### 4. 拉格朗日点

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 1 | harnessL-ds-4.1flashmax | 10 |
| 1 | harnessL-qwen-3.8flashxhigh | 10 |
| 1 | kimiweb-k3swarm-max | 10 |
| 1 | zcode-glm-5.3max | 10 |
| 1 | zcode-glm-5.3maxlinux | 10 |

#### 5. 数值积分器

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 1 | zcode-glm-5.3max | 10 |
| 4 | harnessL-ds-4.1flashmax | 9 |
| 4 | harnessL-qwen-3.8flashxhigh | 9 |
| 6 | zcode-glm-5.3maxlinux | 8 |
| 7 | kimiweb-k3swarm-max | 6 |

#### 6. 收敛与精度

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 3 | harnessL-ds-4.1flashmax | 9 |
| 3 | zcode-glm-5.3max | 9 |
| 5 | zcode-glm-5.3maxlinux | 8 |
| 6 | harnessL-qwen-3.8flashxhigh | 7 |
| 6 | kimiweb-k3swarm-max | 7 |

#### 7. 守恒量表现

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 1 | harnessL-ds-4.1flashmax | 10 |
| 1 | zcode-glm-5.3max | 10 |
| 5 | zcode-glm-5.3maxlinux | 9 |
| 6 | harnessL-qwen-3.8flashxhigh | 8 |
| 6 | kimiweb-k3swarm-max | 8 |

#### 8. 稳定性与边界

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 9 |
| 1 | gptweb-gpt-6pro | 9 |
| 3 | harnessL-ds-4.1flashmax | 6 |
| 3 | zcode-glm-5.3max | 6 |
| 3 | zcode-glm-5.3maxlinux | 6 |
| 6 | harnessL-qwen-3.8flashxhigh | 4 |
| 6 | kimiweb-k3swarm-max | 4 |

#### 9. 验证与工程质量

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 3 | zcode-glm-5.3max | 9 |
| 4 | harnessL-ds-4.1flashmax | 8 |
| 4 | zcode-glm-5.3maxlinux | 8 |
| 6 | kimiweb-k3swarm-max | 7 |
| 7 | harnessL-qwen-3.8flashxhigh | 6 |

#### 10. 交互与科学可视化

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | gptweb-gpt-6pro | 9 |
| 2 | codex-6astra-xhigh | 8 |
| 2 | zcode-glm-5.3max | 8 |
| 2 | zcode-glm-5.3maxlinux | 8 |
| 5 | harnessL-ds-4.1flashmax | 7 |
| 5 | kimiweb-k3swarm-max | 7 |
| 7 | harnessL-qwen-3.8flashxhigh | 5 |

<a id="gptweb-gpt-6-astra-pro-four"></a>

### 4：前四名纯科学终评

本部分是该专家的新科学评分，入选四份与上述综合榜前四名一致，入选边界无同分。权重为数学正确性 **30**、数值结果质量 **35**、物理结果与科学解释 **25**、无效科学结果控制 **10**；与 `codex-gpt-6-astra-xhigh` 样例的五维权重不同，分数不直接平均。

| 排名 | 参赛组合 | 数学 /30 | 数值 /35 | 物理结果与科学解释 /25 | 无效结果控制 /10 | 科学总分 /100 |
|---:|---|---:|---:|---:|---:|---:|
| 1 | harnessL × ds-4.1flashmax | 30 | 35 | 23 | 8 | **96** |
| 2 | gptweb × gpt-6pro | 30 | 31 | 25 | 9 | **95** |
| 2 | Codex × 6astra-xhigh | 30 | 31 | 25 | 9 | **95** |
| 4 | zcode × glm-5.3max（Windows） | 30 | 32 | 21 | 8 | **91** |

**该专家推荐 harnessL × ds-4.1flashmax；GPT Web 与 Codex 并列第二。** 原报告认为 DS 的高阶固定步方法与自适应 GBS 在所测场景中提供了较强数值结果；也明确指出四份产物在足够小的步长下均可达到高精度，1 分差不代表统计显著性或专家投票概率。报告未因界面、工程组织或中间文件缺失扣科学分。

[原始科学结论与限制](reviews/2026-09-09/gptweb-gpt-6-astra-pro/science-final/SCIENCE_REVIEW.md) · [科学评分及逐项理由](reviews/2026-09-09/gptweb-gpt-6-astra-pro/science-final/scores.json)。
<!-- END REVIEW gptweb-gpt-6-astra-pro -->

<!-- BEGIN REVIEW kimiweb-k3-swarmmax -->
## kimiweb-k3-swarmmax：10+4 评审记录

**评审者：`kimiweb-k3-swarmmax` · 2026-09-09 · 状态：10+4 已完成。**

被评快照 [`e45bd40`](https://github.com/LCGaoZzz/llm-harness-science-benchmark/tree/e45bd407f12140758623eb2352360435874b2afa)（submissions 与 648dcc3 一致）。方法：无头执行底座实际加载每份 HTML 并真实触发其自检；从源码提取公式用 Python 独立复算（对照独立高精度真值）；一轮横向一致性校准。评审者 ID 与参赛组合 `kimiweb-k3swarm-max` 分开记录。

[完整评审记录（方法、封顶逐家判定、逐项证据）](reviews/2026-09-09/kimiweb-k3-swarmmax/README.md) · [机器可读评分](reviews/2026-09-09/kimiweb-k3-swarmmax/scores.json) · 首评归档 [SCOREBOARD.md](SCOREBOARD.md)

<a id="kimiweb-k3-swarmmax-ten"></a>

### 10：十项单项排名与综合总榜

每项 0–10 等权求和后应用封顶规则；7 份提交均**未触发**任何封顶规则（逐家证据见完整记录）。同分竞赛排名，表内同分行顺序不代表优劣。

#### 综合总排名

| 排名 | 参赛组合 | 原始合计 /100 | 封顶 | 最终得分 /100 |
|---:|---|---:|---|---:|
| 1 | [gptweb-gpt-6pro](submissions/gptweb--gpt-6pro--2026-09-09/) | 99 | 无 | **99** |
| 2 | [codex-6astra-xhigh](submissions/codex--6astra-xhigh--2026-09-09/) | 97.5 | 无 | **98.5** |
| 3 | [zcode-glm-5.3maxlinux](submissions/zcode--glm-5.3maxlinux--2026-09-09/) | 97.5 | 无 | **97.5** |
| 4 | [harnessL-ds-4.1flashmax](submissions/harnessL--ds-4.1flashmax--2026-09-09/) | 96.5 | 无 | **96.5** |
| 4 | [zcode-glm-5.3max](submissions/zcode--glm-5.3max--2026-09-09/) | 96.5 | 无 | **96.5** |
| 5 | [kimiweb-k3swarm-max](submissions/kimiweb--k3swarm-max--2026-09-09/) | 95 | 无 | **95** |
| 6 | [harnessL-qwen-3.8flashxhigh](submissions/harnessL--qwen-3.8flashxhigh--2026-09-09/) | 89 | 无 | **91** |

#### 1. 物理模型

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 1 | harnessL-ds-4.1flashmax | 10 |
| 1 | harnessL-qwen-3.8flashxhigh | 10 |
| 1 | kimiweb-k3swarm-max | 10 |
| 1 | zcode-glm-5.3max | 10 |
| 1 | zcode-glm-5.3maxlinux | 10 |

#### 2. 数学方程

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 1 | harnessL-ds-4.1flashmax | 10 |
| 1 | harnessL-qwen-3.8flashxhigh | 10 |
| 1 | kimiweb-k3swarm-max | 10 |
| 1 | zcode-glm-5.3max | 10 |
| 1 | zcode-glm-5.3maxlinux | 10 |

#### 3. 单位与坐标

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | gptweb-gpt-6pro | 9.5 |
| 2 | codex-6astra-xhigh | 9 |
| 2 | zcode-glm-5.3maxlinux | 9 |
| 3 | zcode-glm-5.3max | 8 |
| 4 | harnessL-ds-4.1flashmax | 7 |
| 4 | harnessL-qwen-3.8flashxhigh | 7 |
| 4 | kimiweb-k3swarm-max | 7 |

#### 4. 拉格朗日点

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 1 | harnessL-ds-4.1flashmax | 10 |
| 1 | harnessL-qwen-3.8flashxhigh | 10 |
| 1 | kimiweb-k3swarm-max | 10 |
| 1 | zcode-glm-5.3max | 10 |
| 1 | zcode-glm-5.3maxlinux | 10 |

#### 5. 数值积分器

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 1 | harnessL-ds-4.1flashmax | 10 |
| 1 | kimiweb-k3swarm-max | 10 |
| 1 | zcode-glm-5.3max | 10 |
| 1 | zcode-glm-5.3maxlinux | 10 |
| 2 | harnessL-qwen-3.8flashxhigh | 9.5 |

#### 6. 收敛与精度

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 1 | harnessL-ds-4.1flashmax | 10 |
| 1 | harnessL-qwen-3.8flashxhigh | 10 |
| 1 | kimiweb-k3swarm-max | 10 |
| 1 | zcode-glm-5.3max | 10 |
| 1 | zcode-glm-5.3maxlinux | 10 |

#### 7. 守恒量表现

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 1 | harnessL-ds-4.1flashmax | 10 |
| 1 | kimiweb-k3swarm-max | 10 |
| 1 | zcode-glm-5.3max | 10 |
| 1 | zcode-glm-5.3maxlinux | 10 |
| 2 | harnessL-qwen-3.8flashxhigh | 9.5 |

#### 8. 稳定性与边界

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 1 | harnessL-ds-4.1flashmax | 10 |
| 2 | kimiweb-k3swarm-max | 9 |
| 2 | zcode-glm-5.3max | 9 |
| 2 | zcode-glm-5.3maxlinux | 9 |
| 3 | harnessL-qwen-3.8flashxhigh | 8.5 |

#### 9. 验证与工程质量

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 1 | harnessL-ds-4.1flashmax | 10 |
| 1 | kimiweb-k3swarm-max | 10 |
| 1 | zcode-glm-5.3max | 10 |
| 1 | zcode-glm-5.3maxlinux | 10 |
| 2 | harnessL-qwen-3.8flashxhigh | 8 |

#### 10. 交互与科学可视化

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 9.5 |
| 1 | gptweb-gpt-6pro | 9.5 |
| 1 | harnessL-ds-4.1flashmax | 9.5 |
| 1 | zcode-glm-5.3max | 9.5 |
| 1 | zcode-glm-5.3maxlinux | 9.5 |
| 2 | kimiweb-k3swarm-max | 9 |
| 3 | harnessL-qwen-3.8flashxhigh | 8.5 |

<a id="kimiweb-k3-swarmmax-four"></a>

### 4：前四名纯科学终评

入选：综合榜前三 + 第 4 名同分并列两家（共 5 份）。口径：只比较最终数学、物理与数值结果，不计界面、工程材料或中间文件完整度。指标与权重：原标准第 1–8 项等权各 10 分（合计 /80），**与样例五维权重不同，分数不可直接平均比较**。统一实验电池（B1–B7）五家同初值同步长梯实测 + Python 独立复算交叉验证。

| 排名 | 参赛组合 | 科学得分 /80 |
|---:|---|---:|
| 1 | zcode-glm-5.3maxlinux | **75.5** |
| 2 | harnessL-ds-4.1flashmax | **75** |
| 3 | codex-6astra-xhigh | **74** |
| 3 | gptweb-gpt-6pro | **74** |
| 4 | zcode-glm-5.3max | **71** |

**该专家推荐 zcode-glm-5.3maxlinux**（GL4 辛积分 T=100→1000 漂移精确不变、规定网格收敛阶唯一通过之一、边界五子项唯一全科干净）；翻盘条件：JPL 内嵌对照为硬门槛则改选 codex-6astra-xhigh，极端工况自适应精度优先则选 harnessL-ds-4.1flashmax。[逐项分数、实测横表与理由](reviews/2026-09-09/kimiweb-k3-swarmmax/README.md#four)
<!-- END REVIEW kimiweb-k3-swarmmax -->
