# 得分榜（2026-09-09 首轮评阅）

> **评审者：`kimiweb-k3-swarmmax`**（2026-09-09）。本文件为该评审者的首评归档；正式 10+4 署名记录（含逐项排名、四强纯科学终评与机器可读评分）见 [reviews/2026-09-09/kimiweb-k3-swarmmax/](reviews/2026-09-09/kimiweb-k3-swarmmax/README.md)。

> 评阅方式：独立无头执行底座（Node vm + DOM stub）实际加载每个提交并运行其内嵌自检；评阅员再从源码提取物理/数值公式用 Python 独立复算（L1–L5 残差、收敛阶、Jacobi 漂移、NaN 防护实测），与独立参考真值（μ=0.0121505856：L1=0.8369151258, L2=1.1556821654, L3=−1.0050626458, L4/L5=(0.4878494144, ±0.8660254038)）比对；最后经一轮横向一致性校准。全部 7 个提交：轨迹均为实时积分（无预制轨迹）、核心方程正确、单文件可独立运行、自检真实可执行——四条封顶规则均无触发。

## 总排名

| 总排名 | Harness | Model | 总分 | 提交 |
|---:|---|---|---:|---|
| 1 | gptweb | gpt-6pro | **99** | [gptweb--gpt-6pro--2026-09-09](submissions/gptweb--gpt-6pro--2026-09-09/) |
| 2 | codex | 6astra-xhigh | **98.5** | [codex--6astra-xhigh--2026-09-09](submissions/codex--6astra-xhigh--2026-09-09/) |
| 3 | zcode | glm-5.3maxlinux | **97.5** | [zcode--glm-5.3maxlinux--2026-09-09](submissions/zcode--glm-5.3maxlinux--2026-09-09/) |
| 4 | harnessL | ds-4.1flashmax | **96.5** | [harnessL--ds-4.1flashmax--2026-09-09](submissions/harnessL--ds-4.1flashmax--2026-09-09/) |
| 4 | zcode | glm-5.3max | **96.5** | [zcode--glm-5.3max--2026-09-09](submissions/zcode--glm-5.3max--2026-09-09/) |
| 5 | kimiweb | k3swarm-max | **95** | [kimiweb--k3swarm-max--2026-09-09](submissions/kimiweb--k3swarm-max--2026-09-09/) |
| 6 | harnessL | qwen-3.8flashxhigh | **91** | [harnessL--qwen-3.8flashxhigh--2026-09-09](submissions/harnessL--qwen-3.8flashxhigh--2026-09-09/) |

## 逐项得分矩阵（校准后）

| 提交 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 总分 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gptweb--gpt-6pro |10|10|9.5|10|10|10|10|10|10|9.5| **99** |
| codex--6astra-xhigh |10|10|9|10|10|10|10|10|10|9.5| **98.5** |
| zcode--glm-5.3maxlinux |10|10|9|10|10|10|10|9|10|9.5| **97.5** |
| harnessL--ds-4.1flashmax |10|10|7|10|10|10|10|10|10|9.5| **96.5** |
| zcode--glm-5.3max |10|10|8|10|10|10|10|9|10|9.5| **96.5** |
| kimiweb--k3swarm-max |10|10|7|10|10|10|10|9|10|9| **95** |
| harnessL--qwen-3.8flashxhigh |10|10|7|10|9.5|10|9.5|8.5|8|8.5| **91** |

评分项图例：1 物理模型 · 2 数学方程 · 3 单位与坐标 · 4 拉格朗日点 · 5 数值积分器 · 6 收敛与精度 · 7 守恒量表现 · 8 稳定性与边界 · 9 验证与工程质量 · 10 交互与科学可视化

## 单项排名

### 1. 物理模型

| 排名 | 提交 | 得分 |
|---:|---|---:|
| 1 | codex--6astra-xhigh | 10 |
| 1 | gptweb--gpt-6pro | 10 |
| 1 | harnessL--ds-4.1flashmax | 10 |
| 1 | harnessL--qwen-3.8flashxhigh | 10 |
| 1 | kimiweb--k3swarm-max | 10 |
| 1 | zcode--glm-5.3max | 10 |
| 1 | zcode--glm-5.3maxlinux | 10 |

### 2. 数学方程

| 排名 | 提交 | 得分 |
|---:|---|---:|
| 1 | codex--6astra-xhigh | 10 |
| 1 | gptweb--gpt-6pro | 10 |
| 1 | harnessL--ds-4.1flashmax | 10 |
| 1 | harnessL--qwen-3.8flashxhigh | 10 |
| 1 | kimiweb--k3swarm-max | 10 |
| 1 | zcode--glm-5.3max | 10 |
| 1 | zcode--glm-5.3maxlinux | 10 |

### 3. 单位与坐标

| 排名 | 提交 | 得分 |
|---:|---|---:|
| 1 | gptweb--gpt-6pro | 9.5 |
| 2 | codex--6astra-xhigh | 9 |
| 2 | zcode--glm-5.3maxlinux | 9 |
| 3 | zcode--glm-5.3max | 8 |
| 4 | harnessL--ds-4.1flashmax | 7 |
| 4 | harnessL--qwen-3.8flashxhigh | 7 |
| 4 | kimiweb--k3swarm-max | 7 |

### 4. 拉格朗日点

| 排名 | 提交 | 得分 |
|---:|---|---:|
| 1 | codex--6astra-xhigh | 10 |
| 1 | gptweb--gpt-6pro | 10 |
| 1 | harnessL--ds-4.1flashmax | 10 |
| 1 | harnessL--qwen-3.8flashxhigh | 10 |
| 1 | kimiweb--k3swarm-max | 10 |
| 1 | zcode--glm-5.3max | 10 |
| 1 | zcode--glm-5.3maxlinux | 10 |

### 5. 数值积分器

| 排名 | 提交 | 得分 |
|---:|---|---:|
| 1 | codex--6astra-xhigh | 10 |
| 1 | gptweb--gpt-6pro | 10 |
| 1 | harnessL--ds-4.1flashmax | 10 |
| 1 | kimiweb--k3swarm-max | 10 |
| 1 | zcode--glm-5.3max | 10 |
| 1 | zcode--glm-5.3maxlinux | 10 |
| 2 | harnessL--qwen-3.8flashxhigh | 9.5 |

### 6. 收敛与精度

| 排名 | 提交 | 得分 |
|---:|---|---:|
| 1 | codex--6astra-xhigh | 10 |
| 1 | gptweb--gpt-6pro | 10 |
| 1 | harnessL--ds-4.1flashmax | 10 |
| 1 | harnessL--qwen-3.8flashxhigh | 10 |
| 1 | kimiweb--k3swarm-max | 10 |
| 1 | zcode--glm-5.3max | 10 |
| 1 | zcode--glm-5.3maxlinux | 10 |

### 7. 守恒量表现

| 排名 | 提交 | 得分 |
|---:|---|---:|
| 1 | codex--6astra-xhigh | 10 |
| 1 | gptweb--gpt-6pro | 10 |
| 1 | harnessL--ds-4.1flashmax | 10 |
| 1 | kimiweb--k3swarm-max | 10 |
| 1 | zcode--glm-5.3max | 10 |
| 1 | zcode--glm-5.3maxlinux | 10 |
| 2 | harnessL--qwen-3.8flashxhigh | 9.5 |

### 8. 稳定性与边界

| 排名 | 提交 | 得分 |
|---:|---|---:|
| 1 | codex--6astra-xhigh | 10 |
| 1 | gptweb--gpt-6pro | 10 |
| 1 | harnessL--ds-4.1flashmax | 10 |
| 2 | kimiweb--k3swarm-max | 9 |
| 2 | zcode--glm-5.3max | 9 |
| 2 | zcode--glm-5.3maxlinux | 9 |
| 3 | harnessL--qwen-3.8flashxhigh | 8.5 |

### 9. 验证与工程质量

| 排名 | 提交 | 得分 |
|---:|---|---:|
| 1 | codex--6astra-xhigh | 10 |
| 1 | gptweb--gpt-6pro | 10 |
| 1 | harnessL--ds-4.1flashmax | 10 |
| 1 | kimiweb--k3swarm-max | 10 |
| 1 | zcode--glm-5.3max | 10 |
| 1 | zcode--glm-5.3maxlinux | 10 |
| 2 | harnessL--qwen-3.8flashxhigh | 8 |

### 10. 交互与科学可视化

| 排名 | 提交 | 得分 |
|---:|---|---:|
| 1 | codex--6astra-xhigh | 9.5 |
| 1 | gptweb--gpt-6pro | 9.5 |
| 1 | harnessL--ds-4.1flashmax | 9.5 |
| 1 | zcode--glm-5.3max | 9.5 |
| 1 | zcode--glm-5.3maxlinux | 9.5 |
| 2 | kimiweb--k3swarm-max | 9 |
| 3 | harnessL--qwen-3.8flashxhigh | 8.5 |

## 各提交评阅要点

### 1. gptweb--gpt-6pro — 99
- 页面自检 25/25 真实执行（probe 触发 `#runTests`，实测耗时 1.27s，无硬编码 PASS）；Node 直跑 verify_core.js 亦 24/24。
- Python 独立复算逐位复现：RK4 收敛阶 4.150、SY4（正则分裂 Yoshida 四阶辛）3.991、T=100 漂移 4.24e-8 / 1.35e-10；L1–L5 残差 ≤2e-15。
- 惯性系 DOP853 独立参考积分交叉验证端到端正确（L1 预设 T=4 位置误差 3.4e-10）；probe 重放 1,085 步与页面状态逐位一致（实时积分确证）。
- 扣分：项 3 −0.5（无惯性系可视化视图，仅有数值读数）；项 10 −0.5（无头环境无法目检像素渲染）。

### 2. codex--6astra-xhigh — 98.5
- 23/23 自检经直调 `selfTests()` 与按钮两路径实测通过；L1–L5 残差 3.11e-15、JPL 锚点差 8.95e-16。
- Yoshida 四阶辛分裂（A 子流含科氏/离心旋转）经解析验证并独立复现（2,000 步差 4.7e-14）；RK4 收敛比 15.89 独立复算一致。
- DOP853(rtol=3e-14) 对照：T=20 轨迹偏差 rk4 6.3e-11 / yoshida 5.2e-8；飞掠预设独立确认（minMoon=0.0072 DU）。
- 扣分：项 3 −1（无惯性系轨迹视图，惯性速度转换读数已验证正确）。

### 3. zcode--glm-5.3maxlinux — 97.5
- 自检 7/7 数值全部逐位独立复现（L 点残差 2.887e-15、收敛阶 3.978、RK4↔GL4 互检 1.10e-12、GL4 t=30/300 漂移均 1.65e-7）。
- probe 实测：GL4 积分 L4 蝌蚪轨道至 t=46 TU，|ΔC|=8.9e-15；撞击/逃逸(|r|>30)/非法初值防护均真实触发。
- README 定量声明全部复现（flyby 能量变化、近月距离、L1 λ=2.93/TU 等）；与姊妹提交 zcode--glm-5.3max 为同模型独立会话实现（diff 2,189 行），非复制。
- 扣分：项 3 −1（无惯性系视图，转换读数已验证）；项 8 −1（无步内连续碰撞检测，极端速度下理论可隧穿）；项 10 −0.5（帧率无法无头实测）。

### 4. harnessL--ds-4.1flashmax — 96.5（并列）
- 自检 14/14 三重复现（页面 / Node / 独立复算，原评审记录）；src/core.js 与 lab.html 内联块逐字节一致。
- 9 种积分器（GBS 外推自适应、DOPRI5、Yoshida-4/6、Verlet、RK4 等）；收敛阶独立测得 rk4 3.99 / verlet 2.00 / yosh4 4.00 / yosh6 5.99 / GBS 8.95，与页面一致。
- T=16π 漂移对照 rk4 3.6e-15 vs yosh4 7.0e-11，复现「辛有界/RK4 增长」；奇点停机横幅实测触发。
- 扣分：项 3 −3（全页面无任何旋转系→惯性系转换）；项 10 −0.5（无惯性系视角、帧率自述无法复核）。

### 4. zcode--glm-5.3max — 96.5（并列）
- 20/20 自检真实执行（单项 7.9s 实测耗时，排除伪造）；L 点残差 ~1e-15，与真值差完全由 μ 取值差解释。
- Python 重写 RK4 端点与页面**逐位相同**；收敛阶独立复算与页面报告逐位一致；隐式中点精确 Jacobian 含科氏项。
- 守恒定量对比：T=1000 RK4 漂移 9.5e-3（线性）vs 辛4 5.6e-8（有界），经独立复核吻合。
- 扣分：项 3 −2（无惯性系视图/转换；页脚静态单位文本 TU/VU 有小误差，代码内常量正确）；项 8 −1（无显式逃逸检测）；项 10 −0.5。

### 5. kimiweb--k3swarm-max — 95
- 自检全部数值经 Python 逐行重写公式后精确复现（L1=0.8369151258 残差 6.7e-16、收敛比 16.17、RK4 50TU ΔC=1.78e-15、辛 Verlet 500TU 6.5e-8 有界）。
- 辛积分器为「科氏精确旋转 Strang 分裂 Verlet」，符号复核正确；probe 泵 7,500+ 帧全程零脚本错误。
- NaN/奇点/碰撞防护真实接线主循环并实测触发（非法输入、地心碰撞、近地冲激均正确处理）。
- 扣分：项 3 −3（无任何惯性系转换）；项 8 −1（固定步长无自适应）；项 10 −1（无 C(t) 定量曲线）。

### 6. harnessL--qwen-3.8flashxhigh — 91
- 自检 7/7 真实执行（probe 实测）；RK4 收敛阶 4.03（复现 4.029）、DOPRI5 容差扫描、T=40 漂移 1.69e-10 均独立复现；3D 晕轨道 C_J=3.17008031 与 JPL 公布值差 7.1e-11。
- 积分器：RK4 + 自适应 DOPRI5 + 隐式中点（辛，2 阶）三种。
- 扣分：项 3 −3（无任何惯性系转换）；项 5 −0.5（DOPRI5 FSAL 复用瑕疵）；项 7 −0.5（辛漂移 8.67e-7 较其他提交高一个量级）；项 8 −1.5（碰撞阈值 0.4/0.6 半径带随意性）；项 9 −2（自检后 S.bad 残留导致模拟冻结的实测 bug；browser_check.json 为旧版陈旧记录）；项 10 −1.5（缺惯性视图与误差曲线）。

## 校准说明

原始 7 份独立评阅经一轮横向一致性校准（标尺统一，非重评）：
- 项 3 统一标尺：单位正确但完全无惯性系转换 = 7；有经核验的转换读数但无视图 = 9（gptweb 另有页面内单位自检 = 9.5；glm 另有静态文本小误差 = 8）。据此 qwen 项 3 由 5.5 调为 7。
- 项 8 统一标尺：无碰撞正则化不扣分（超出 10 分标准要求）；防护体系完备且实测触发 = 10。据此 codex 项 8 由 9.5 调为 10。
- codex 项 10 由 9 调为 9.5（原扣分纯因无头环境无法目检，属评测环境限制而非提交缺陷，与 gptweb/ds 对齐）。
- qwen 项 6 由 9.5 调为 10（原扣分无理由，证据与其他 10 分提交同级）。
- 校准只动分数档内不一致处；原始分数保留于各提交目录的评阅记录中。

## 方法与公平性备注

- 本轮评分全部由独立评阅完成：无头执行每个 HTML、真实触发其自检、并从源码重写公式独立复算关键数值；不以页面观感或 README 自述计分。
- 7 个提交的 μ、L 点、方程、Jacobi 公式全部经核验正确，差异主要在第 3 项（惯性系转换/视图）、第 8–10 项（边界处理完备度、工程验证深度、可视化丰富度）。
- 按基准说明，本榜比较的是「Harness + LLM + 提示词条件」的一次任务产物，不构成模型能力排名。
