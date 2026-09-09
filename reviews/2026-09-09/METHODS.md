# 2026-09-09 评阅方法与复现

本轮评阅仓库快照 [`ac5a306be9b29978ad6787903821b4a6a181ff01`](https://github.com/LCGaoZzz/llm-harness-science-benchmark/tree/ac5a306be9b29978ad6787903821b4a6a181ff01) 中的全部 7 份提交，采用该快照 README 的原有 10 项评分和封顶规则。评阅者为本次 Codex 会话，单一评阅、未盲审；其中一个参赛组合也是 Codex，因此公开脚本、实测数据和逐项判断以便第三方复核。

## 评分口径

每项 0–10 分，十项等权求和，再应用封顶。沿用 README 的 9–10、7–8、5–6、3–4、1–2、0 六档解释；不新增速度、费用、工具数量或文件数量指标。10 分要求该项实现和验证完整；正确的部分实现、缺验证、错误标签和实测失败按其影响降分。

本轮事实依据依次包括原始源码、重新执行的页面与数值结果、随提交保存的原始验证材料。原始自述不能代替复核；反之，不把已经不对应最终 HTML 的旧失败日志直接当作最终失败。统一外部测试用于证实或否定科学性质，不会替提交补齐它没有实现的坐标转换或自检功能。

分数是依据量表的评阅判断，不是自动误差到分数的线性换算。真辛二阶方法不因阶数低于四阶而直接判错；正确处理含科氏项方程的第二方法可以得高分。但“误差在某条轨道上有界”不能证明保辛。不同有效质量参数分别使用相同参数的独立参考，不将参数来源差异误判为实现错误。

单项和总分均使用竞赛排名：排名为 `1 + 严格高于该分数的人数`。同分并列、后续跳号；同分行按标签排序仅方便显示，未另设破同分指标。

## 原始文件与运行环境

- 从固定 Git commit 读取 blob 原始字节，避免 Windows checkout 的 CRLF 转换影响哈希；7 份提交的 SHA256SUMS 合计 **182 个文件全部匹配**。
- 每份实际 HTML 的 SHA-256、字节数和 ZIP 入口均记录在 [integrity.json](evidence/integrity.json)。Kimi ZIP 的两个 HTML 字节相同，只对解包出的 `cr3bp-lab/index.html` 评分；解包不视为无法独立运行。
- 未修改任何 `submissions/` 文件。浏览器操作只影响临时内存状态；数值审查读取原 HTML 中未改写的函数定义。
- Windows、Node.js **24.13.0**、Playwright **1.62.1**、Microsoft Edge **152.0.4191.66**，视口 **1440×1000**，设备像素比 1，headless。7 个页面均使用新的断网浏览器上下文，以 `file://` 直接加载，无需服务器、CDN或构建。
- 独立参考为 Python **3.11.3**、NumPy **2.3.5**、SciPy **1.17.0** 的 DOP853。工具时间是复核成本，不作为参赛生成耗时或性能排名。

## 统一数值检查

所有状态均按 `[x,y,vx,vy]` 表示。DS 的三维内核在本轮统一测试中设 `z=vz=0`。

| 检查 | 输入与指标 | 证据 |
|---|---|---|
| 方程和 C | 四个非奇异状态，对照评阅方独立 RHS/C；势的中心差分步长 1e-5 | [numerical.json](evidence/numerical.json) 的 `math` |
| L1–L5 | 用独立 RHS 复算每个提交自身求得的平衡点残差 | 同上 `lagrange` |
| 收敛 | 初值 `[0.6,0.2,-0.1,0.35]`，T=0.4，h=0.02/0.01/0.005/0.0025，完整四维状态范数 | 同上 `methods.*.convergence` |
| 外部终态参考 | DOP853，rtol=2.3e-14、atol=2e-15；max_step 从 0.01 缩到 0.005，记录参考自身加密差 | [reference.json](evidence/reference.json) |
| 惯性系交叉核验 | 移动的地球/月球，纯牛顿引力，不复用旋转 RHS 的离心/科氏项；独立变换回旋转坐标对照 | 同上 `inertialFormulationCrosscheck` |
| L4 长时漂移 | 初值 `[0.51-μ,√3/2,0,0]`，h=0.01，T=100；逐步最大绝对 `∣C-C0∣`，分别记录前/后半程 | `methods.*.l4` |
| 绕地漂移 | r=0.3，初速 `vy=√((1-μ)/r)-r`，h=0.001，T=20；相同绝对漂移指标 | `methods.*.earth` |
| 辛性 | 转为 `px=vx-y, py=vy+x`，有限差分计算 `max∣DΦᵀ J DΦ-J∣`；h=0.02，差分步长 1e-5 和 1e-6 | `methods.*.symplecticDefect` |
| 自适应 | Qwen DOPRI5 的光滑/周期/俯冲样例；DS GBS 的光滑/L4/绕地样例，显式保存参数和完成状态 | `adaptiveProbes` |
| 隐式迭代 | 扫描 GL4 近地状态，记录迭代到上限仍被接受的残差 | `unconvergedAccepted` |

独立参考加密差小于 1e-15，但这不是长期轨迹的严格误差界。六阶方法在细步长下进入浮点误差地板，不把阶数回落等同于实现错误。原始数值文件保留全部步长误差，不只给最好的一项。

## 浏览器检查

[browser.json](evidence/browser.json) 保存重新执行的自检返回值、控制台、页面文本和尺寸；[interactions.json](evidence/interactions.json) 保存控件操作前后状态以及失败案例。`*-interaction.png` 是本次实际运行后的截图，未使用参赛者旧截图替代。

实际操作包括暂停/运行、单步、重置、算法切换、修改四个初始分量、全部预设按钮、滚轮缩放、拖拽平移、自检按钮。每个预设按钮被点击并推进；这只是入口冒烟测试。后续 [presets-reference.json](evidence/presets-reference.json) 对这些预设初值另做独立动力学传播，避免把按钮可点等同于科学效果成立。

有自动启动行为的 DS/zcode Windows 提交，独立预设传播读取保存的原始初值（`sim.ic` / `sim.s0`），不用暂停时已经演化的状态冒充初值。Kimi 闭包不暴露仿真对象，控件结果取页面显示读数；其 `t` 仅显示 4 位小数，因此显示值和精确 h 的微小差别不作为错误扣分。

标准穿体探针为 `s=[-μ-0.03,0,100,0]`、RK4、h=0.001；初值和步末均在地球外，而路径横跨地球。Codex/GPTWeb 拒绝未分辨的近场步；DS/Qwen/zcode 两份均接受。Kimi 经真实 UI 使用其滑杆默认 h≈0.001046，接受同类跨表面步，漂移约 201，只显示警告。本探针评价漏检有限高速跨步碰撞的实现，不声称此速度是典型航天任务条件。

没有在整份提交中植入新守卫或修复算法。数值脚本只是提取定义并做接口适配；交互脚本调用原页面控件或暴露的仿真接口以设定测试状态。自动截图和测试不会改变已归档的原始文件。

## 可定位的重要问题

| 提交 | 原始代码位置 | 实测或逻辑证据 | 评分主要落点 |
|---|---|---|---|
| Qwen | [单步/重置](../../submissions/harnessL--qwen-3.8flashxhigh--2026-09-09/cr3bp_lab.html#L348) | 单步循环 `S.sub=40` 次；reset 调用 `setIC(S.state.slice())`；浏览器证实 | 10 |
| Qwen | [奇点自检恢复](../../submissions/harnessL--qwen-3.8flashxhigh--2026-09-09/cr3bp_lab.html#L388) | 恢复 state 未恢复 `S.bad`；自检后 UI 显示运行但 t 不变 | 9、10 |
| Qwen | [advance](../../submissions/harnessL--qwen-3.8flashxhigh--2026-09-09/cr3bp_lab.html#L252) | 忽略 DOPRI `ok`，缩小碰撞半径，只查步末 | 5、8 |
| DS | [缩放事件](../../submissions/harnessL--ds-4.1flashmax--2026-09-09/src/ui.js#L567)、[渲染循环](../../submissions/harnessL--ds-4.1flashmax--2026-09-09/src/ui.js#L640) | 暂停时视图更新未置 dirty；滚轮前后 canvas 哈希相同，拖动后才改变 | 10 |
| DS | [允许域指标](../../submissions/harnessL--ds-4.1flashmax--2026-09-09/src/core.js#L599) | `C=jacobi(s)` 后计算 `2Ω-C`，恒等于当前 v²；不能检验初始 C0 禁区 | 9 |
| zcode Linux | [GL4 停止条件](../../submissions/zcode--glm-5.3maxlinux--2026-09-09/index.html#L408) | 目标 delta<1e-13，失败却仅在 delta≥1e-2；例如近地 r=0.03、h=0.005，delta≈1.23e-7 仍 accepted | 5、6、8 |
| zcode Windows | [飞越初值与说明](../../submissions/zcode--glm-5.3max--2026-09-09/index.html#L578) | 说明称 t≈1.3、r月≈0.028；原始初值的本次独立 T≤10 参考最小月距≈0.05459 @6.296 | 10 |
| Kimi | ZIP 的 `cr3bp-lab/index.html`：`stepVerlet` | 旋转速度、漂移和势 kick 的分裂有二阶收敛，但在正确正则坐标下的辛性缺陷≈2.67e-6；换差分尺度结论不变 | 5、6 |
| Kimi | 同一 HTML：`checkState`、`simStep` | 碰撞半径只设 1e-6；先提交状态和 t 后守卫；本次穿体被接受 | 8、9 |

跨项扣分只针对缺陷确实影响的不同能力：例如迭代收敛判据同时关系方法是否被正确求解、精度声明和运行停止条件；不会额外施加 README 未规定的总分处罚。

## 封顶规则逐项核验

| 原有封顶条件 | 上限 | 本轮结论 |
|---|---:|---|
| 预制轨迹冒充实时模拟 | 20 | 7 份均为根据初值实时推进，未触发 |
| 核心运动方程错误 | 40 | 7 份独立 RHS/C 对照均正确，未触发；Kimi 的错误在第二方法“保辛”性质声明，不是核心运动方程 |
| 页面无法独立运行 | 50 | 7 份均以断网 `file://` 直开；Kimi 先按原 ZIP 解包，未触发 |
| 没有任何可执行验证 | 70 | 7 份均有实际执行的自检，未触发；存在薄弱或失败检查不等同于完全没有验证 |

## 公平性与适用范围

本次重跑条件一致，但参赛时的提示词、工具、环境、人工干预信息和迭代预算并未被统一控制。Codex 明确附有“战役模式、10–12 轮”，zcode Linux 保存固定提示词会话；其他组合存在未提供的过程信息。依据各提交 README 保留这些差异，不猜测缺失信息，也不把耗时长短作为本量表得分。

所有评分仅针对这七份单次产物，不是基础模型排行榜或 Harness 因果比较。L4/绕地的有限样例、一次浏览器版本和桌面视口不能证明任意初值、混沌长期相位、所有浏览器或移动端的可靠性。表面探针定位漏检，没有完成连续事件误差的全域证明。独立预设的首末惯性速率差也不是隔离月球引力贡献的证明；严谨飞越增益应像 GPTWeb 的自检一样比较相同月距等明确条件。

## 与先前榜单的差异

本次评阅进行期间，远端新增了 [`53010a4` 榜单](https://github.com/LCGaoZzz/llm-harness-science-benchmark/blob/53010a454316d39a1c2cb8c76747a685d80c8674/README.md#结果索引)。该提交只改 README，没有改变七份参赛产物或评分标准，因此本次测试仍对应同一批原始文件。下面保留其总分作为版本对照；旧版全部单项分数、文字及排名可通过上述固定链接查阅。

本次不是对旧版总分机械加减，而是分别按十项标准重新判断。差异主要来自可重复的失败案例、对最终 HTML 与旧日志的区分，以及对最高分所要求的完整坐标转换和验证的检查。测试条数、方法数量和材料篇幅不直接折算为分数。

| 组合 | 先前总分 | 本次总分 | 影响判断的主要证据 |
|---|---:|---:|---|
| gptweb-gpt-6pro | 98.0 | 98 | 总分相同，单项分配不同；坐标闭合、外部参考和长时测试支持数值项高分，边界与有限网格曲线保留局限 |
| codex-6astra-xhigh | 97.5 | 95 | 惯性速率/正则动量不等于完整惯性坐标变换；画面没有速度矢量 |
| zcode-glm-5.3max | 95.5 | 88 | 穿体跨步漏检、缺完整坐标转换，飞越说明与实际初值传播不符 |
| harnessL-ds-4.1flashmax | 98.0 | 85 | 高精度算法成立；但穿体漏检、暂停缩放未重绘、允许域自检为恒等式，且缺完整惯性坐标变换 |
| zcode-glm-5.3maxlinux | 96.0 | 83 | GL4 目标求解容差与失败阈值不一致，实测接受未达到容差的迭代；另有穿体漏检和固定曲线范围 |
| harnessL-qwen-3.8flashxhigh | 79.5 | 74 | 最终 HTML 自检 7/7，旧失败日志不代表当前版本；正确的隐式中点确为辛方法，不因 DOPRI 非辛而判整个第二方法失败。扣分来自自检后冻结、单步/重置语义及边界问题 |
| kimiweb-k3swarm-max | 87.5 | 72 | 第二方法虽有二阶收敛和单轨道有界误差，有限差分正则辛性检验不通过；碰撞阈值和推进顺序也有实测缺陷 |

这些差异是本轮公开证据支持的评阅意见；不将未公开的旧版测试过程猜测为未执行或伪造。读者可按本目录脚本复算事实，并对每项评分尺度提出复核。

## 复现

准备 Node、Playwright 1.62.1 与 Edge，以及 Python 3.11、NumPy 2.3.5、SciPy 1.17.0。`playwright` 必须可由 Node 解析；也可以使用 `NODE_PATH` 指向已安装的工具目录。`REVIEW_BROWSER_CHANNEL` 默认 `msedge`，换浏览器需记录版本差异。

在仓库根目录运行（下面的 `python` 在本轮 Windows 使用 `py -3.11`）：

```text
python reviews/2026-09-09/scripts/prepare.py . ../benchmark-review-work-20260909 reviews/2026-09-09/evidence
node reviews/2026-09-09/scripts/numerical.cjs ../benchmark-review-work-20260909/submissions reviews/2026-09-09/evidence/numerical.json
python reviews/2026-09-09/scripts/reference.py reviews/2026-09-09/evidence/numerical.json reviews/2026-09-09/evidence/reference.json
node reviews/2026-09-09/scripts/browser.cjs ../benchmark-review-work-20260909/submissions reviews/2026-09-09/evidence
node reviews/2026-09-09/scripts/interactions.cjs ../benchmark-review-work-20260909/submissions reviews/2026-09-09/evidence
python reviews/2026-09-09/scripts/presets.py reviews/2026-09-09/evidence
python reviews/2026-09-09/scripts/render.py --check
```

首次复现会覆盖 `evidence/` 下的重跑输出和截图；建议另建工作副本。预设运行/暂停的墙钟时刻、截图及耗时不保证逐字节一致，固定数值核心测试可复算。`render.py` 从 [scores.json](scores.json) 生成根 README 的 11 个榜单和评阅明细；`--check` 验证生成文本、70 项覆盖、取值范围、排名、证据 ID 及七份页面加载状态。它校验评分材料一致性，不宣称评阅判断本身能被单元测试自动证明。
