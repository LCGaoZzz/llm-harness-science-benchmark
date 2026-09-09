# codex-gpt-6-astra-xhigh：10+4 评审样例

## 结果索引

**评审者：`codex-gpt-6-astra-xhigh` · 展示格式：10+4 · 单专家样例。**

已完成 **7 份提交**的独立评阅（2026-09-09）。评分以提交快照 [`ac5a306`](https://github.com/LCGaoZzz/llm-harness-science-benchmark/tree/ac5a306be9b29978ad6787903821b4a6a181ff01) 为准。每项 0–10 分、等权求和，再应用原有封顶规则；本轮 7 份均未触发封顶。

**同分并列，使用竞赛排名（如 1、2、2、4）；表内同分条目的显示顺序不代表先后。** 这些是本次产物的评分，不能据此推断模型总体能力。生成环境、迭代轮数及提示词完整性不完全一致；详见各原始提交说明。

本次更新接续[先前榜单 `53010a4`](https://github.com/LCGaoZzz/llm-harness-science-benchmark/blob/53010a454316d39a1c2cb8c76747a685d80c8674/README.md#结果索引)，及[并行评阅 `bd4a59a`](https://github.com/LCGaoZzz/llm-harness-science-benchmark/blob/bd4a59a83558414797c9a6dad021e9e733e954ab/LEADERBOARD.md)。参赛文件未变；[分数差异与依据](../METHODS.md#与先前榜单的差异)单独列出，旧版分数仍可追溯。本文件保存该专家的完整 10+4 样例；其他专家见[仓库评审索引](../../../README.md)。

[评阅方法与限制](../METHODS.md) · [逐项评分证据](../README.md) · [机器可读评分](../scores.json) · [实测记录与截图](../evidence/)

**后续专项：[前四名纯科学终评](../science-final/README.md)**。只比较最终数学、物理及数值结果，不计界面、工程材料或中间文件完整度；其权重和结论单列，原综合榜分数保持原评分口径。

### 总排名

| 排名 | 参赛组合 | 原始合计 /100 | 封顶 | 最终得分 /100 | 评阅 |
|---:|---|---:|---|---:|---|
| 1 | [gptweb-gpt-6pro](../../../submissions/gptweb--gpt-6pro--2026-09-09/) | 98 | 无 | **98** | [逐项证据](../README.md#gptweb) |
| 2 | [codex-6astra-xhigh](../../../submissions/codex--6astra-xhigh--2026-09-09/) | 95 | 无 | **95** | [逐项证据](../README.md#codex) |
| 3 | [zcode-glm-5.3max](../../../submissions/zcode--glm-5.3max--2026-09-09/) | 88 | 无 | **88** | [逐项证据](../README.md#zwin) |
| 4 | [harnessL-ds-4.1flashmax](../../../submissions/harnessL--ds-4.1flashmax--2026-09-09/) | 85 | 无 | **85** | [逐项证据](../README.md#ds) |
| 5 | [zcode-glm-5.3maxlinux](../../../submissions/zcode--glm-5.3maxlinux--2026-09-09/) | 83 | 无 | **83** | [逐项证据](../README.md#zlinux) |
| 6 | [harnessL-qwen-3.8flashxhigh](../../../submissions/harnessL--qwen-3.8flashxhigh--2026-09-09/) | 74 | 无 | **74** | [逐项证据](../README.md#qwen) |
| 7 | [kimiweb-k3swarm-max](../../../submissions/kimiweb--k3swarm-max--2026-09-09/) | 72 | 无 | **72** | [逐项证据](../README.md#kimi) |

### 10 个单项排名

#### 1. 物理模型

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | [codex-6astra-xhigh](../README.md#codex) | 10 |
| 1 | [gptweb-gpt-6pro](../README.md#gptweb) | 10 |
| 1 | [harnessL-ds-4.1flashmax](../README.md#ds) | 10 |
| 1 | [harnessL-qwen-3.8flashxhigh](../README.md#qwen) | 10 |
| 1 | [zcode-glm-5.3max](../README.md#zwin) | 10 |
| 1 | [zcode-glm-5.3maxlinux](../README.md#zlinux) | 10 |
| 7 | [kimiweb-k3swarm-max](../README.md#kimi) | 9 |

#### 2. 数学方程

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | [codex-6astra-xhigh](../README.md#codex) | 10 |
| 1 | [gptweb-gpt-6pro](../README.md#gptweb) | 10 |
| 1 | [harnessL-ds-4.1flashmax](../README.md#ds) | 10 |
| 1 | [zcode-glm-5.3max](../README.md#zwin) | 10 |
| 5 | [harnessL-qwen-3.8flashxhigh](../README.md#qwen) | 9 |
| 5 | [kimiweb-k3swarm-max](../README.md#kimi) | 9 |
| 5 | [zcode-glm-5.3maxlinux](../README.md#zlinux) | 9 |

#### 3. 单位与坐标

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | [gptweb-gpt-6pro](../README.md#gptweb) | 10 |
| 2 | [codex-6astra-xhigh](../README.md#codex) | 8 |
| 3 | [zcode-glm-5.3maxlinux](../README.md#zlinux) | 7 |
| 4 | [harnessL-ds-4.1flashmax](../README.md#ds) | 6 |
| 4 | [harnessL-qwen-3.8flashxhigh](../README.md#qwen) | 6 |
| 4 | [zcode-glm-5.3max](../README.md#zwin) | 6 |
| 7 | [kimiweb-k3swarm-max](../README.md#kimi) | 5 |

#### 4. 拉格朗日点

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | [codex-6astra-xhigh](../README.md#codex) | 10 |
| 1 | [gptweb-gpt-6pro](../README.md#gptweb) | 10 |
| 1 | [harnessL-ds-4.1flashmax](../README.md#ds) | 10 |
| 1 | [harnessL-qwen-3.8flashxhigh](../README.md#qwen) | 10 |
| 1 | [kimiweb-k3swarm-max](../README.md#kimi) | 10 |
| 1 | [zcode-glm-5.3max](../README.md#zwin) | 10 |
| 1 | [zcode-glm-5.3maxlinux](../README.md#zlinux) | 10 |

#### 5. 数值积分器

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | [codex-6astra-xhigh](../README.md#codex) | 10 |
| 1 | [gptweb-gpt-6pro](../README.md#gptweb) | 10 |
| 1 | [zcode-glm-5.3max](../README.md#zwin) | 10 |
| 4 | [harnessL-ds-4.1flashmax](../README.md#ds) | 9 |
| 4 | [harnessL-qwen-3.8flashxhigh](../README.md#qwen) | 9 |
| 6 | [zcode-glm-5.3maxlinux](../README.md#zlinux) | 8 |
| 7 | [kimiweb-k3swarm-max](../README.md#kimi) | 6 |

#### 6. 收敛与精度

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | [codex-6astra-xhigh](../README.md#codex) | 10 |
| 1 | [gptweb-gpt-6pro](../README.md#gptweb) | 10 |
| 3 | [harnessL-ds-4.1flashmax](../README.md#ds) | 9 |
| 3 | [zcode-glm-5.3max](../README.md#zwin) | 9 |
| 5 | [zcode-glm-5.3maxlinux](../README.md#zlinux) | 8 |
| 6 | [harnessL-qwen-3.8flashxhigh](../README.md#qwen) | 7 |
| 6 | [kimiweb-k3swarm-max](../README.md#kimi) | 7 |

#### 7. 守恒量表现

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | [codex-6astra-xhigh](../README.md#codex) | 10 |
| 1 | [gptweb-gpt-6pro](../README.md#gptweb) | 10 |
| 1 | [harnessL-ds-4.1flashmax](../README.md#ds) | 10 |
| 1 | [zcode-glm-5.3max](../README.md#zwin) | 10 |
| 5 | [zcode-glm-5.3maxlinux](../README.md#zlinux) | 9 |
| 6 | [harnessL-qwen-3.8flashxhigh](../README.md#qwen) | 8 |
| 6 | [kimiweb-k3swarm-max](../README.md#kimi) | 8 |

#### 8. 稳定性与边界

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | [codex-6astra-xhigh](../README.md#codex) | 9 |
| 1 | [gptweb-gpt-6pro](../README.md#gptweb) | 9 |
| 3 | [harnessL-ds-4.1flashmax](../README.md#ds) | 6 |
| 3 | [zcode-glm-5.3max](../README.md#zwin) | 6 |
| 3 | [zcode-glm-5.3maxlinux](../README.md#zlinux) | 6 |
| 6 | [harnessL-qwen-3.8flashxhigh](../README.md#qwen) | 4 |
| 6 | [kimiweb-k3swarm-max](../README.md#kimi) | 4 |

#### 9. 验证与工程质量

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | [codex-6astra-xhigh](../README.md#codex) | 10 |
| 1 | [gptweb-gpt-6pro](../README.md#gptweb) | 10 |
| 3 | [zcode-glm-5.3max](../README.md#zwin) | 9 |
| 4 | [harnessL-ds-4.1flashmax](../README.md#ds) | 8 |
| 4 | [zcode-glm-5.3maxlinux](../README.md#zlinux) | 8 |
| 6 | [kimiweb-k3swarm-max](../README.md#kimi) | 7 |
| 7 | [harnessL-qwen-3.8flashxhigh](../README.md#qwen) | 6 |

#### 10. 交互与科学可视化

| 排名 | 参赛组合 | 得分 /10 |
|---:|---|---:|
| 1 | [gptweb-gpt-6pro](../README.md#gptweb) | 9 |
| 2 | [codex-6astra-xhigh](../README.md#codex) | 8 |
| 2 | [zcode-glm-5.3max](../README.md#zwin) | 8 |
| 2 | [zcode-glm-5.3maxlinux](../README.md#zlinux) | 8 |
| 5 | [harnessL-ds-4.1flashmax](../README.md#ds) | 7 |
| 5 | [kimiweb-k3swarm-max](../README.md#kimi) | 7 |
| 7 | [harnessL-qwen-3.8flashxhigh](../README.md#qwen) | 5 |

### 前四名纯科学终评（4）

评审者：`codex-gpt-6-astra-xhigh`。这是上述综合榜前四名的独立科学评分；[权重、逐项理由与实测证据](../science-final/README.md)单列。

| 排名 | 参赛组合 | 科学得分 /100 |
|---:|---|---:|
| 1 | harnessL-ds-4.1flashmax | **97** |
| 2 | codex-6astra-xhigh | **96** |
| 2 | gptweb-gpt-6pro | **96** |
| 4 | zcode-glm-5.3max（Windows） | **91** |

该专家推荐 harnessL-ds-4.1flashmax；97 与 96 的差距较小，科学终评已说明权重敏感性。
