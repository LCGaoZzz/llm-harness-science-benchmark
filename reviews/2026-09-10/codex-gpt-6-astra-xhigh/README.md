# Codex：2026-09-10 增补评审（10＋5）

**评审平台：Codex · 评审模型：GPT-6 Astra（xhigh） · 评审者：`codex-gpt-6-astra-xhigh`**

本轮新增 `harnessL-glm5.3-max`，**十项综合 86/100，第 4；科学终评 92/100，第 4**。按用户最新要求，科学榜改为综合前五入围的“科学五强”，当前完整展示为 **10＋5**。

新作品固定于提交快照 [`09d165d`](https://github.com/LCGaoZzz/llm-harness-science-benchmark/tree/09d165d2211c515959a1431fba79fae1599b4dbb)，HTML SHA-256 为 `1489db7bd4cba9e8c036b4828ba0855277fea5de81b6a5939612e3a3f2e5138d`。原七份十项分数及原四份科学分数沿用 [2026-09-09 评审](../../2026-09-09/codex-gpt-6-astra-xhigh/README.md)；本轮没有把旧记录冒充新的独立重跑。

按[基准十项标准](../../../BENCHMARK.md)等权相加，八份均无封顶；同分采用竞赛排名（1、2、2、4）。[机器可读十项分数](scores.json) · [科学终评与推荐](science-final.md) · [原七份逐项理由](../../2026-09-09/README.md)。

## 十项综合总榜

| 排名 | 组合 | 得分 /100 | 评分依据 |
|---:|---|---:|---|
| 1 | [gptweb-gpt-6pro](../../../submissions/gptweb--gpt-6pro--2026-09-09/) | **98** | [逐项理由](../../2026-09-09/README.md#gptweb) |
| 2 | [codex-6astra-xhigh](../../../submissions/codex--6astra-xhigh--2026-09-09/) | **95** | [逐项理由](../../2026-09-09/README.md#codex) |
| 3 | [zcode-glm-5.3max](../../../submissions/zcode--glm-5.3max--2026-09-09/) | **88** | [逐项理由](../../2026-09-09/README.md#zwin) |
| 4 | [harnessL-glm5.3-max](../../../submissions/harnessL--glm5.3-max--2026-09-10/) | **86** | [逐项理由](#hglm) |
| 5 | [harnessL-ds-4.1flashmax](../../../submissions/harnessL--ds-4.1flashmax--2026-09-09/) | **85** | [逐项理由](../../2026-09-09/README.md#ds) |
| 6 | [zcode-glm-5.3maxlinux](../../../submissions/zcode--glm-5.3maxlinux--2026-09-09/) | **83** | [逐项理由](../../2026-09-09/README.md#zlinux) |
| 7 | [harnessL-qwen-3.8flashxhigh](../../../submissions/harnessL--qwen-3.8flashxhigh--2026-09-09/) | **74** | [逐项理由](../../2026-09-09/README.md#qwen) |
| 8 | [kimiweb-k3swarm-max](../../../submissions/kimiweb--k3swarm-max--2026-09-09/) | **72** | [逐项理由](../../2026-09-09/README.md#kimi) |

**入围变化：** 新作品 86 分进入综合第 4，DS 原综合 85 分转为第 5。科学榜现取综合前五，因此同时包含新作品和 DS；DS 科学 **97 分保持不变，仍居科学榜第一**。科学五强榜不等于全部八份作品的纯科学总榜。

## 八份得分矩阵

| 组合 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 总分 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gptweb-gpt-6pro | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 9 | 10 | 9 | **98** |
| codex-6astra-xhigh | 10 | 10 | 8 | 10 | 10 | 10 | 10 | 9 | 10 | 8 | **95** |
| zcode-glm-5.3max | 10 | 10 | 6 | 10 | 10 | 9 | 10 | 6 | 9 | 8 | **88** |
| harnessL-glm5.3-max | 10 | 10 | 5 | 10 | 10 | 9 | 10 | 5 | 9 | 8 | **86** |
| harnessL-ds-4.1flashmax | 10 | 10 | 6 | 10 | 9 | 9 | 10 | 6 | 8 | 7 | **85** |
| zcode-glm-5.3maxlinux | 10 | 9 | 7 | 10 | 8 | 8 | 9 | 6 | 8 | 8 | **83** |
| harnessL-qwen-3.8flashxhigh | 10 | 9 | 6 | 10 | 9 | 7 | 8 | 4 | 6 | 5 | **74** |
| kimiweb-k3swarm-max | 9 | 9 | 5 | 10 | 6 | 7 | 8 | 4 | 7 | 7 | **72** |

1=物理模型；2=数学方程；3=单位与坐标；4=拉格朗日点；5=数值积分器；6=收敛与精度；7=守恒量表现；8=稳定性与边界；9=验证与工程质量；10=交互与科学可视化。

<a id="ten"></a>

## 10 个单项排名

### 1. 物理模型

| 排名 | 组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 1 | harnessL-ds-4.1flashmax | 10 |
| 1 | harnessL-glm5.3-max | 10 |
| 1 | harnessL-qwen-3.8flashxhigh | 10 |
| 1 | zcode-glm-5.3max | 10 |
| 1 | zcode-glm-5.3maxlinux | 10 |
| 8 | kimiweb-k3swarm-max | 9 |

### 2. 数学方程

| 排名 | 组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 1 | harnessL-ds-4.1flashmax | 10 |
| 1 | harnessL-glm5.3-max | 10 |
| 1 | zcode-glm-5.3max | 10 |
| 6 | harnessL-qwen-3.8flashxhigh | 9 |
| 6 | kimiweb-k3swarm-max | 9 |
| 6 | zcode-glm-5.3maxlinux | 9 |

### 3. 单位与坐标

| 排名 | 组合 | 得分 /10 |
|---:|---|---:|
| 1 | gptweb-gpt-6pro | 10 |
| 2 | codex-6astra-xhigh | 8 |
| 3 | zcode-glm-5.3maxlinux | 7 |
| 4 | harnessL-ds-4.1flashmax | 6 |
| 4 | harnessL-qwen-3.8flashxhigh | 6 |
| 4 | zcode-glm-5.3max | 6 |
| 7 | harnessL-glm5.3-max | 5 |
| 7 | kimiweb-k3swarm-max | 5 |

### 4. 拉格朗日点

| 排名 | 组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 1 | harnessL-ds-4.1flashmax | 10 |
| 1 | harnessL-glm5.3-max | 10 |
| 1 | harnessL-qwen-3.8flashxhigh | 10 |
| 1 | kimiweb-k3swarm-max | 10 |
| 1 | zcode-glm-5.3max | 10 |
| 1 | zcode-glm-5.3maxlinux | 10 |

### 5. 数值积分器

| 排名 | 组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 1 | harnessL-glm5.3-max | 10 |
| 1 | zcode-glm-5.3max | 10 |
| 5 | harnessL-ds-4.1flashmax | 9 |
| 5 | harnessL-qwen-3.8flashxhigh | 9 |
| 7 | zcode-glm-5.3maxlinux | 8 |
| 8 | kimiweb-k3swarm-max | 6 |

### 6. 收敛与精度

| 排名 | 组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 3 | harnessL-ds-4.1flashmax | 9 |
| 3 | harnessL-glm5.3-max | 9 |
| 3 | zcode-glm-5.3max | 9 |
| 6 | zcode-glm-5.3maxlinux | 8 |
| 7 | harnessL-qwen-3.8flashxhigh | 7 |
| 7 | kimiweb-k3swarm-max | 7 |

### 7. 守恒量表现

| 排名 | 组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 1 | harnessL-ds-4.1flashmax | 10 |
| 1 | harnessL-glm5.3-max | 10 |
| 1 | zcode-glm-5.3max | 10 |
| 6 | zcode-glm-5.3maxlinux | 9 |
| 7 | harnessL-qwen-3.8flashxhigh | 8 |
| 7 | kimiweb-k3swarm-max | 8 |

### 8. 稳定性与边界

| 排名 | 组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 9 |
| 1 | gptweb-gpt-6pro | 9 |
| 3 | harnessL-ds-4.1flashmax | 6 |
| 3 | zcode-glm-5.3max | 6 |
| 3 | zcode-glm-5.3maxlinux | 6 |
| 6 | harnessL-glm5.3-max | 5 |
| 7 | harnessL-qwen-3.8flashxhigh | 4 |
| 7 | kimiweb-k3swarm-max | 4 |

### 9. 验证与工程质量

| 排名 | 组合 | 得分 /10 |
|---:|---|---:|
| 1 | codex-6astra-xhigh | 10 |
| 1 | gptweb-gpt-6pro | 10 |
| 3 | harnessL-glm5.3-max | 9 |
| 3 | zcode-glm-5.3max | 9 |
| 5 | harnessL-ds-4.1flashmax | 8 |
| 5 | zcode-glm-5.3maxlinux | 8 |
| 7 | kimiweb-k3swarm-max | 7 |
| 8 | harnessL-qwen-3.8flashxhigh | 6 |

### 10. 交互与科学可视化

| 排名 | 组合 | 得分 /10 |
|---:|---|---:|
| 1 | gptweb-gpt-6pro | 9 |
| 2 | codex-6astra-xhigh | 8 |
| 2 | harnessL-glm5.3-max | 8 |
| 2 | zcode-glm-5.3max | 8 |
| 2 | zcode-glm-5.3maxlinux | 8 |
| 6 | harnessL-ds-4.1flashmax | 7 |
| 6 | kimiweb-k3swarm-max | 7 |
| 8 | harnessL-qwen-3.8flashxhigh | 5 |

<a id="hglm"></a>

## 新作品逐项理由：86/100

[原始 HTML](../../../submissions/harnessL--glm5.3-max--2026-09-10/lab.html) · [浏览器实测](browser.json) · [八工况数值结果](numerical.json) · [独立参考](reference.json)。

| # | 评分项 | 得分 /10 | 证据与判断 |
|---:|---|---:|---|
| 1 | 物理模型 | 10 | 平面 CR3BP、质心旋转系、质量比、主天体位置与圆轨道／质点假设明确；页面说明偏心率、太阳摄动等局限，轨迹实时计算。 |
| 2 | 数学方程 | 10 | Ω、科氏项、运动方程与 Jacobi 正确；独立 RHS 最大差 9.93e-16，C 最大差 4.44e-16；势梯度与解析 Jacobian 的页内有限差分自检实跑通过。 |
| 3 | 单位与坐标 | 5 | DU/TU/速度换算有定义，但没有完整旋转／惯性位置速度变换及往返验证；状态栏相对月球速率用了 hypot(vx+y,vy-x)，应为 hypot(vx-y,vy+x-(1-μ))。这会把与月球共动的极限状态显示为约 0.988 而非 0 DU/TU，构成实际物理读数错误。 |
| 4 | 拉格朗日点 | 10 | L1–L3 Newton、L4/L5 解析构造正确；独立复算五点加速度残差小于 1e-14，页面点位与临界 C 对照真实执行。 |
| 5 | 数值积分器 | 10 | RK4、牛顿求解的隐式中点及修正中点外推 GBS 均按含科氏项的完整方程实现；中点二阶且多状态正则辛性缺陷最大约 1.34e-10，不因阶数低直接判算法错误。 |
| 6 | 收敛与精度 | 9 | 页内 RK4≈4.02 阶、中点≈2.00 阶与 GBS 容差检查通过；外部八工况再次验证。提交的 GBS 容差自检仍以同一实现的加严结果为参考，缺多工况独立全状态误差控制，保留 1 分。 |
| 7 | 守恒量表现 | 10 | C0 与实际 C 分开保存，不做能量投影；GBS、RK4 与中点的长期记录可复现。共同 L4 T=1000 中点最大绝对漂移 4.45e-9、绕地 T=100 为 1.80e-7，均呈有界表现；GBS 精度与保辛性质分别评价。 |
| 8 | 稳定性与边界 | 5 | NaN 与极近月心可停止，隐式求解失败与 GBS 重试有上限；但输入负 dt 后单步直接倒退到 -0.01，未提供相应操作语义。共同穿体探针仍被接受，单步 ∣ΔC∣≈255.68；无未分辨近场步拒绝或有限天体事件定位。 |
| 9 | 验证与工程质量 | 9 | 断网单文件运行，12 项自检真实执行，页面与控制台无错误，物理／测试／绘图分节清晰。自检结束后 halted=false、t=0，却遗留“加速度过大—已停止”红色横幅，测试未完整恢复显示状态，扣 1 分；不按文件或断言数量加分。 |
| 10 | 交互与科学可视化 | 8 | 预设、暂停、单步、重置、缩放、平移及切换积分器实测有效，提供速度箭头、L 点、零速度曲线与比例网格。轨迹仅连接自适应大步末点，精细几何容易被折线掩盖；所谓拓扑自检只核对七个点的允许域及线段有限性，不能证明整条等值线或窄通道拓扑精度。 |

页面内自检的 12/12、提交附带 harness 的断言数均不是本表的自动评分公式。自述通过项只在本轮复核后用作证据，旧开发失败记录也不直接当作最终页面失败。

## 科学终评入口

| 排名 | 组合 | 科学得分 /100 |
|---:|---|---:|
| 1 | harnessL-ds-4.1flashmax | **97** |
| 2 | codex-6astra-xhigh | **96** |
| 2 | gptweb-gpt-6pro | **96** |
| 4 | harnessL-glm5.3-max | **92** |
| 5 | zcode-glm-5.3max（Windows） | **91** |

[五项权重、数值比较与推荐理由](science-final.md)。本轮 DS **97 分第一**，GPT Web 与 Codex **96 分并列第二**。

## 复现

浏览器使用 Windows 上的 Microsoft Edge，版本记录在 `browser.json`；Python／SciPy 版本记录在 `reference.json`。浏览器脚本需要 Node.js、Playwright 和 Edge，参考脚本需要 NumPy、SciPy。浏览器请求被拦截，直接打开原始 HTML；数值脚本只提取原 HTML 的未改写函数。以提交的 LF 原始文件核对 SHA-256。

```text
node reviews/2026-09-10/codex-gpt-6-astra-xhigh/browser.cjs
node reviews/2026-09-10/codex-gpt-6-astra-xhigh/run.cjs
python reviews/2026-09-10/codex-gpt-6-astra-xhigh/reference.py
python reviews/2026-09-10/codex-gpt-6-astra-xhigh/render.py
python scripts/render_cards.py
```

浮点末位和浏览器版本可能影响微小误差；复算数据应复查后发布。`render.py --check` 检查已发布分数、前五入围集合、原七份分数不变及生成文件一致性。截图记录自检后的残留错误横幅：[浏览器截图](browser-selftests.png)。
