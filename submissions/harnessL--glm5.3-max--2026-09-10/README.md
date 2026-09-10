# harnessL-glm5.3-max

状态：原始结果暂存，等待后续评分。用户指定本组合标签为 `harnessL-glm5.3-max`，产物目录由用户提供，要求如实上传、保持原样；并要求**不提交与科学智能体、战役过程有关的文件（闭源）**。归档过程未运行、未修复、未改动任何原始文件。

## 基本信息

- Harness：`harnessL`（用户指定标签；会话内部结构未随产物提供，版本未知）。
- Model：`glm5.3-max`（用户指定标签；产物中未含模型自述信息，无法从文件独立核实）。
- 测试日期：2026-09-10（Asia/Shanghai）。产物目录创建于 09:55，最后文件修改于 11:28，跨度约 93 分钟（含验证，非纯生成耗时）。
- 操作系统与浏览器：`harness.py` / `qa_visual.py` 为 Playwright 驱动 Chromium（1680×1000）的实测脚本；具体版本未记录。
- 总耗时：未记录，不根据文件时间戳推算端到端耗时。
- 工具和网络权限：未提供完整配置；产物中无外部网络获取痕迹。
- 人工干预：未提供。
- 是否为未经上传阶段修改的原始产物：是。25 个原始文件按原始字节复制（`cmp` 逐一校验一致）；仅新增本说明与 `SHA256SUMS`。

## 闭源范围说明（应用户要求）

用户要求不提交与科学智能体、战役过程有关的文件。归档前已核查：本产物目录中**不存在** `.campaign/`、ledger、theory、proposal、轮次台账等战役过程文件（对比其他会话的 `.campaign/conversations/*.jsonl`、`ledger-*.json`、`theories-*.json` 结构）。目录内 25 个文件均为页面交付物、页面源码提取物或对页面的验证记录，无智能体内部过程内容，故全部归档。若该会话的战役过程文件存放于本目录之外，则未包含、也不会包含。

## 提示词与过程来源

本结果由用户作为本仓库 CR3BP 测试的 harnessL 结果提供。完整提示词、对话与工具调用记录未随产物提供，因此不将其他会话的提示词推定为本次实际输入。基准固定提示词见[基准任务与评分标准](../../BENCHMARK.md#固定提示词)。

## 原始文件映射

原始来源：`/data/users/lianchong/workspace1/outputs/turn_20260910015519_a3291877feee4ddd8268f7f43b72c533/`

| 归档路径 | 说明 |
|---|---|
| [lab.html](lab.html) | 交付物，单文件，54,140 B，SHA-256 `1489db7b…`；标题"地月 CR3BP 实验室 · 旋转坐标系三体问题" |
| [harness.py](harness.py) | Playwright 浏览器实测 harness（自述"全部数字来自页面内真实计算，无预置结果"）：12 项页面自检 + 基准 + 预设 + 交互 + 性能 + 断言汇总 |
| [matrix.py](matrix.py) / [matrix_result.json](matrix_result.json) | 积分器数值矩阵（页面内 bench() 真实计算：GBS 容差 × 轨道 × 时长扫描） |
| [r1](r1_result.json)–[r4](r4_result.json)、[r7](r7_result.json)、[r7b](r7b_result.json)`_result.json` | 开发各阶段的 harness 运行记录（r1 自检 6/10 → r7 11/12 → final 12/12，修复过程如实保留） |
| [final_result.json](final_result.json) | 最终实测：自检 12/12、断言 30/30、console/page 错误 0、fps ≈ 60 |
| [qa_visual.py](qa_visual.py) / [qa_result.json](qa_result.json) | 截图像素级 QA（非背景占比、色带统计、侧栏/画布分区） |
| [shot_tadpole](shot_tadpole.png) / [shot_assist](shot_assist.png)（10:16）与 [qa_tadpole](qa_tadpole.png) / [qa_assist](qa_assist.png)（11:28）| 页面截图（含 figmeta 溯源副件） |
| [_script.js](_script.js)、[combined.js](combined.js)、[core_debug.js](core_debug.js)、[probe.js](probe.js) | 页面脚本提取物与 Node 探针（开发/调试产物） |

原始目录中的 `figures/` 为空目录（git 不跟踪，未归档）。lab.html SHA-256：`1489db7bd4cba9e8c036b4828ba0855277fea5de81b6a5939612e3a3f2e5138d`。[SHA256SUMS](SHA256SUMS) 覆盖全部 25 个原始文件。

## 产物自述内容（摘自原始文件，未复核）

以下均为原始会话自己的记录，归档方未重跑、未复核：

- **最终自检 12/12、断言 30/30 通过**（`final_result.json`）：含拉格朗日点残差 4.44e-16（Newton 法至机器精度）、势梯度/Jacobi 有限差分一致性、RK4 收敛阶 4.02、隐式中点收敛阶、GBS 容差符合性、Jacobi 守恒等；console/page 错误 0 条；实测 fps 60.0、173.8 步/秒。
- **积分器矩阵**（`matrix_result.json`）：GBS（tol 1e-12）tadpole 轨道 T=500/2000 相对漂移 4.5e-15 / 2.2e-14 等。
- **修复过程**：r1（10:17）自检 6/10（有限差分一致性、RK4 阶数等 4 项失败）→ r7（11:22）11/12 → final（11:26）12/12；中间记录全部保留。
- **交互实测**（`r7/final_result.json` 的 `interact` 字段）：暂停冻结、单步 dt、重置、滚轮缩放、拖拽平移、积分器切换均为 true。
- 页面集成 GBS / RK4 / 隐式中点等积分器（以 `final_result.json` 的 bench 键 A_gbs / A_rk4 / A_imp / B_earth_gbs / C_assist_gbs / D_throughput 为证）。

## 评分与验证状态

待后续独立评分。本次归档仅验证复制与上传的文件完整性，没有重跑数值测试或复核原始记录中的科学陈述。
