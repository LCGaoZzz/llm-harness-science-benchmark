# 当前得分榜

> 评阅日期：2026-09-09  
> 依据：仓库根目录 `README.md` 的 10 项 × 10 分评分标准与总分封顶规则。  
> 原则：以实际代码、可执行自检和归档运行证据为主，不采用参赛者自报分数作为评分依据。

## 总排名

| Rank | Harness | Model | 物理 | 方程 | 单位/坐标 | L点 | 积分器 | 收敛 | 守恒 | 边界 | 验证/工程 | 可视化 | Total |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Codex | 6astra-xhigh | 10 | 10 | 9 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | **99** |
| 2 | GPT Web | gpt-6pro | 10 | 10 | 9 | 10 | 10 | 10 | 10 | 10 | 9 | 10 | **98** |
| 3 | HarnessL | ds-4.1flashmax | 10 | 10 | 8 | 10 | 10 | 10 | 10 | 10 | 10 | 9 | **97** |
| 4 | ZCode | glm-5.3max (Windows) | 10 | 10 | 8 | 10 | 10 | 10 | 10 | 9 | 10 | 9 | **96** |
| 5 | ZCode | glm-5.3maxlinux | 10 | 10 | 8 | 10 | 9 | 9 | 9 | 9 | 10 | 9 | **93** |
| 6 | HarnessL | qwen-3.8flashxhigh | 10 | 10 | 7 | 10 | 9 | 9 | 9 | 7 | 7 | 8 | **86** |
| 7* | Kimi Web | k3swarm-max | 5 | 5 | 5 | 5 | 5 | 4 | 4 | 4 | 4 | 5 | **46*** |

`*` Kimi 当前目录只归档了 ZIP，未提供仓库根级可直接审查的 `index.html`，且没有独立运行/自检结果可供本轮代码级复核。46 分是**证据下限暂定分**，不是对 ZIP 内方程正确性的负面判定，也没有套用“页面无法独立运行”或“无可执行验证”的封顶规则。将 ZIP 内原始 `index.html` 原样展开到提交目录后应重新评阅。

本轮其余 6 份提交均未触发总分封顶规则。

## 各评分项独立排名

采用竞赛排名（同分同名次）。

### 1. 物理模型
1= Codex / 6astra-xhigh — **10**  
1= GPT Web / gpt-6pro — **10**  
1= HarnessL / ds-4.1flashmax — **10**  
1= ZCode / glm-5.3max (Windows) — **10**  
1= ZCode / glm-5.3maxlinux — **10**  
1= HarnessL / qwen-3.8flashxhigh — **10**  
7. Kimi Web / k3swarm-max — **5***

### 2. 数学方程
1= Codex / 6astra-xhigh — **10**  
1= GPT Web / gpt-6pro — **10**  
1= HarnessL / ds-4.1flashmax — **10**  
1= ZCode / glm-5.3max (Windows) — **10**  
1= ZCode / glm-5.3maxlinux — **10**  
1= HarnessL / qwen-3.8flashxhigh — **10**  
7. Kimi Web / k3swarm-max — **5***

### 3. 单位与坐标
1= Codex / 6astra-xhigh — **9**  
1= GPT Web / gpt-6pro — **9**  
3= HarnessL / ds-4.1flashmax — **8**  
3= ZCode / glm-5.3max (Windows) — **8**  
3= ZCode / glm-5.3maxlinux — **8**  
6. HarnessL / qwen-3.8flashxhigh — **7**  
7. Kimi Web / k3swarm-max — **5***

### 4. 拉格朗日点
1= Codex / 6astra-xhigh — **10**  
1= GPT Web / gpt-6pro — **10**  
1= HarnessL / ds-4.1flashmax — **10**  
1= ZCode / glm-5.3max (Windows) — **10**  
1= ZCode / glm-5.3maxlinux — **10**  
1= HarnessL / qwen-3.8flashxhigh — **10**  
7. Kimi Web / k3swarm-max — **5***

### 5. 数值积分器
1= Codex / 6astra-xhigh — **10**  
1= GPT Web / gpt-6pro — **10**  
1= HarnessL / ds-4.1flashmax — **10**  
1= ZCode / glm-5.3max (Windows) — **10**  
5= ZCode / glm-5.3maxlinux — **9**  
5= HarnessL / qwen-3.8flashxhigh — **9**  
7. Kimi Web / k3swarm-max — **5***

### 6. 收敛与精度
1= Codex / 6astra-xhigh — **10**  
1= GPT Web / gpt-6pro — **10**  
1= HarnessL / ds-4.1flashmax — **10**  
1= ZCode / glm-5.3max (Windows) — **10**  
5= ZCode / glm-5.3maxlinux — **9**  
5= HarnessL / qwen-3.8flashxhigh — **9**  
7. Kimi Web / k3swarm-max — **4***

### 7. 守恒量表现
1= Codex / 6astra-xhigh — **10**  
1= GPT Web / gpt-6pro — **10**  
1= HarnessL / ds-4.1flashmax — **10**  
1= ZCode / glm-5.3max (Windows) — **10**  
5= ZCode / glm-5.3maxlinux — **9**  
5= HarnessL / qwen-3.8flashxhigh — **9**  
7. Kimi Web / k3swarm-max — **4***

### 8. 稳定性与边界
1= Codex / 6astra-xhigh — **10**  
1= GPT Web / gpt-6pro — **10**  
1= HarnessL / ds-4.1flashmax — **10**  
4= ZCode / glm-5.3max (Windows) — **9**  
4= ZCode / glm-5.3maxlinux — **9**  
6. HarnessL / qwen-3.8flashxhigh — **7**  
7. Kimi Web / k3swarm-max — **4***

### 9. 验证与工程质量
1= Codex / 6astra-xhigh — **10**  
1= HarnessL / ds-4.1flashmax — **10**  
1= ZCode / glm-5.3max (Windows) — **10**  
1= ZCode / glm-5.3maxlinux — **10**  
5. GPT Web / gpt-6pro — **9**  
6. HarnessL / qwen-3.8flashxhigh — **7**  
7. Kimi Web / k3swarm-max — **4***

### 10. 交互与科学可视化
1= Codex / 6astra-xhigh — **10**  
1= GPT Web / gpt-6pro — **10**  
3= HarnessL / ds-4.1flashmax — **9**  
3= ZCode / glm-5.3max (Windows) — **9**  
3= ZCode / glm-5.3maxlinux — **9**  
6. HarnessL / qwen-3.8flashxhigh — **8**  
7. Kimi Web / k3swarm-max — **5***

## 评阅摘要与主要扣分点

### 1. Codex / 6astra-xhigh — 99
提交：[codex--6astra-xhigh--2026-09-09](submissions/codex--6astra-xhigh--2026-09-09/)

- CR3BP 方程、Jacobi 常数、L1–L5 求解均正确；L 点残差约 `3.1e-15`。
- RK4 + 正则变量下的 Yoshida 四阶辛分裂正确处理科氏项，不是把普通 Verlet 生搬到速度依赖力上。
- 页面内 23 项真实自检；另外用 SciPy DOP853 做 8 组独立高精度轨迹对照，并做到了 `T=10000 TU` 的长期积分比较。
- NaN、非法步长、奇点、表面穿越、近遇步长等防护完整，月球飞掠和 L1/L4 物理行为都有定量测试。
- 唯一保守扣分在“单位与坐标”：虽然尺度和惯性速率核验是正确的，但页面没有把完整的随时间旋转系↔惯性系坐标变换做成同等显式、可交互的验证对象。

### 2. GPT Web / gpt-6pro — 98
提交：[gptweb--gpt-6pro--2026-09-09](submissions/gptweb--gpt-6pro--2026-09-09/)

- 从 `GM_E/GM_M` 推导 `μ/TU/VU`，并有单位闭合自检；CR3BP、L 点、Jacobi 均正确。
- RK4 与正则坐标 Yoshida-4 辛分裂实现扎实，并显式验证 `C=-2H`、时间可逆性和辛映射缺陷。
- 有真实的收敛阶、长期守恒、L4 有界、L1 不稳定、月球飞掠、NaN/表面/大步长防护测试。
- UI/遥测/漂移图/零速度曲线的完成度很高。
- 扣分：完整旋转↔惯性坐标变换没有作为一等功能展示；当前归档 README 对“实际浏览器启动、控制台检查、修复后的独立重跑证据”记录弱于 Codex/DS/ZCode 两份，因此工程证据给 9 而非 10。

### 3. HarnessL / ds-4.1flashmax — 97
提交：[harnessL--ds-4.1flashmax--2026-09-09](submissions/harnessL--ds-4.1flashmax--2026-09-09/)

- 数值内核最丰富之一：RK4、Verlet、Yoshida-4/6、DOPRI5、GBS、步长加倍等多种方法，并把计算核心与 UI 明确分离后内联成单文件。
- 正则动量、`gradU` 与 `gradΩ` 的区别处理正确；自述中还保留了发现并修复错误分裂势、GBS Richardson 分母、adaptive rejection 等真实修复历史。
- 有随机状态 NaN 防护、奇点/碰撞、时间可逆、预设行为以及较长时间守恒测试，验证广度很强。
- 扣分：当前可见实现没有把完整惯性系坐标变换做成明确验证路径；UI 的零速度曲线以当前数值 `C` 重建，而不是始终锁定初始 `C0`，在漂移极小时影响很小，但科学表达上不如固定能级边界严谨。

### 4. ZCode / glm-5.3max (Windows) — 96
提交：[zcode--glm-5.3max--2026-09-09](submissions/zcode--glm-5.3max--2026-09-09/)

- 不是“只有漂亮页面”：代码实际实现 RK4、隐式中点和 Yoshida 四阶，并分别测量约 4/2/4 阶收敛。
- 自检包含 L1–L5、独立 Newton 交叉验证、Routh/L4 Hessian、Jacobi 漂移、`T=1000` 长期 RK4 vs 辛4、禁止区一致性、NaN/碰撞和确定性。
- 单文件工程与交互较完整。
- 扣分：缺少完整惯性系坐标验证；边界/近遇质量控制不如前三名全面，视觉与审计证据也略少。

### 5. ZCode / glm-5.3maxlinux — 93
提交：[zcode--glm-5.3maxlinux--2026-09-09](submissions/zcode--glm-5.3maxlinux--2026-09-09/)

- CR3BP、L 点、Jacobi 与 ZVC 均正确；第二积分器是二级 Gauss–Legendre 隐式四阶辛方法，适用于含科氏项的完整一阶系统。
- 7 项页面内自检真实执行：L 点残差、RK4 收敛、RK4/GL4 互检、`T=30/300` Jacobi、NaN 和 ZVC 完整性。
- 有实际 Chromium 运行与长时间/飞掠记录。
- 扣分：GL4 采用固定点迭代，近强场时收敛鲁棒性弱于 Newton/解析分裂方案；自检只直接测了 RK4 的阶数，GL4 主要靠互检与守恒侧证；完整惯性系变换未展示。

### 6. HarnessL / qwen-3.8flashxhigh — 86
提交：[harnessL--qwen-3.8flashxhigh--2026-09-09](submissions/harnessL--qwen-3.8flashxhigh--2026-09-09/)

- 核心 CR3BP、L 点、Jacobi、RK4、隐式中点、DOPRI5 和 marching-squares ZVC 都是真实计算，不是预制轨迹。
- RK4 收敛阶约 `4.03`；L 点残差约 `1e-15`；RK4 与隐式中点长时 Jacobi 测试有定量结果。
- 主要扣分有两个明确证据：归档浏览器记录里 DOPRI5 的近俯冲安全测试有失败项；`重置`按钮把**当前状态**重新设成新初值，而不是恢复原预设/初始状态，属于真实交互/工程缺陷。
- 另外没有完整惯性系转换验证，边界处理主要是积分后检查，强近遇鲁棒性弱于前五名。

### 7. Kimi Web / k3swarm-max — 46*（暂定）
提交：[kimiweb--k3swarm-max--2026-09-09](submissions/kimiweb--k3swarm-max--2026-09-09/)

- 当前提交目录只有 `Kimi_Agent_地月三体实验室.zip`、README 与校验和；ZIP 中包含两个同内容 HTML，但没有按仓库提交格式把原始 `index.html` 直接展开。
- 本轮可以核验“确有 HTML 产物”，但无法从仓库文本直接复核 ZIP 内的方程、积分器和自检实现，也没有独立运行结果。
- 因此各科学项只给“存在实现但未验证”的证据下限，不把未知内容猜成正确，也不把未知内容判成错误；这份分数必须在原始 HTML 展开后重审。

## 结论

当前第一梯队是 **Codex 6astra-xhigh / GPT Web gpt-6pro / HarnessL ds-4.1flashmax / ZCode glm-5.3max Windows**，差距主要在验证深度与工程审计，而不是 CR3BP 基本方程。Linux ZCode 紧随其后。Qwen 的科学核心是正确的，但有可复现的工程/鲁棒性缺陷。

后续新增提交应按同一矩阵追加评分；不要因为参赛者 README 自报分数、模型品牌或页面观感改变尺度。
