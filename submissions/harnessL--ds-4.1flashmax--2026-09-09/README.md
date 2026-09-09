# harnessL-ds-4.1flashmax

状态：原始结果暂存，等待后续横评评分。用户指定本组合标签为 `harnessL-ds-4.1flashmax`，产物目录由用户提供，要求如实上传、保持原样。归档过程未运行、未修复、未改动任何原始文件。

## 基本信息

- Harness：`harnessL`（用户指定标签；会话内部结构未随产物提供，版本未知）。
- Model：`ds-4.1flashmax`（用户指定标签；产物中未含模型自述信息，无法从文件独立核实）。
- 测试日期：2026-09-09（Asia/Shanghai）。产物目录创建于 14:08，最后文件修改于 15:37，跨度约 89 分钟（含检索文献与验证，非纯生成耗时）。
- 操作系统与浏览器：REPORT.md 自述实际启动验证使用 Chromium / Playwright（`file://` 加载）；具体版本未记录。
- 总耗时：未记录，不根据文件时间戳推算端到端耗时。
- 工具和网络权限：未提供完整配置。`tests/_anchor_sources/` 表明会话期间下载了 10 篇第三方公开文献（NASA/ESA 技术报告与学位论文，约 100 MB）作为外部数值锚点。
- 人工干预：未提供。
- 是否为未经上传阶段修改的原始产物：是。76 个原始文件按原始字节复制（`cmp` 逐一校验一致）；仅新增本说明、`SHA256SUMS` 与 `ANCHOR_PDF_MANIFEST.txt`。

## 提示词与过程来源

本结果由用户作为本仓库 CR3BP 测试的 harnessL 结果提供。完整提示词、对话与工具调用记录未随产物提供，因此不将其他会话的提示词推定为本次实际输入。基准固定提示词见[仓库说明](../../README.md#固定提示词)。

## 原始文件映射

| 归档路径 | 原始来源（`/data/users/lianchong/workspace3/outputs/turn_20260909060823_7f04edadd3c74c7fbb2df231e97604f9/`） | 说明 |
|---|---|---|
| [lab.html](lab.html) | 同名 | 交付物，单文件，81,352 B；REPORT 自述 SHA-256 `2092ed57…`，归档时独立复算一致 |
| [REPORT.md](REPORT.md) | 同名 | 15,106 B，会话自己撰写的交付报告（含战役记录、修复记录、局限） |
| [build.py](build.py) | 同名 | 由 `src/` 组装单文件的构建脚本（内联字节级校验） |
| [src/](src/) | `src/{core.js, ui.js, style.css, index.html}` | 源码（core 42 KB / ui 28 KB / css / html 模板） |
| [lab_screenshot.png](lab_screenshot.png)、[lab_longrun.png](lab_longrun.png) | 同名 | 页面首屏与长时运行截图（含 figmeta 溯源） |
| [tests/](tests/) | `tests/` 全部非 PDF 文件（65 个） | 评估仪器（harness.js）、5 轮 + 留出集基准 JSON、探针脚本、浏览器验证（Playwright）、最终报告与截图 |

原始目录中的 `figures/` 为空目录（git 不跟踪，未归档）；`tests/_anchor_sources/` 下 10 个第三方参考 PDF（约 100 MB）未随包搬运，其 `.figmeta.json` 溯源副件已归档，PDF 清单与 SHA-256 见 [ANCHOR_PDF_MANIFEST.txt](ANCHOR_PDF_MANIFEST.txt)——这是归档阶段的范围决定，不是原始会话的产物差异。lab.html SHA-256：`2092ed57f0bf0b21f9aff27e72de0f01e1098ecf49885f667cc844b90f692bb6`。[SHA256SUMS](SHA256SUMS) 覆盖全部 76 个原始文件。

## 产物自述内容（摘自 REPORT.md / tests/*.json，未复核）

以下均为原始会话自己的陈述，归档方未重跑、未复核：

- **积分器九种可切换**：GBS 外推（默认，自适应）、DOPRI5、GBS-fixed、自适应 RK4、自适应 symplectic-4、Yoshida-4/6（正则动量旋转分裂，自述"真辛"）、Verlet（旋转分裂蛙跳）、RK4。
- **战役**：第 1 轮前冻结协议（目标 = 4 条核心轨道 max Jacobi 相对漂移，预算 200k 力评估/轨道，T=40π），5 轮 + 第 6 轮留出集对照；最终 GBS（k=5，Bulirsch 序列，rtol=1e-13）把最差轨道漂移压到 1.76e-12，比第 1 轮最优（DOPRI5@1e-12）好 14.5 倍。
- **自检抓到并修复 8 个真实 bug**（REPORT §3 逐条列出：辛分裂势能项用错、GBS Richardson 分母写反、末步步长未传递、自适应拒绝后不收缩、守卫只查步后、守恒判据写错、负跨度被拒、每帧重建离屏 canvas 等）。
- **浏览器实测自述**：console/page 错误 0 条；4 预设可运行；实时性 1.5 TU/s 设定下 61 fps；20.1 s 长跑 t=40.27 TU、ΔC/|C₀| 稳定 4.5e-16；地心初值立即触发 singularity 停机横幅；原始 JSON 见 `tests/browser_report.json`、`tests/final_report.json`。
- **外部锚点**：L 点与 C_J 对 JPL SSD / AAS 15-615 等公布值比对（`tests/external_anchor.json`）；自述 μ 用现代质量比 0.012150585609624。
- **局限**：REPORT §5 列了 11 条（两套 C 约定差 μ(1−μ)/2、μ 选取影响第 4–5 位小数、ZVC 仅 z=0、最差轨道指标掩盖光滑轨道差异、固定步长在近交会无解、辛性=有界而非更小、变步长破坏辛性、预算约束、选择偏差、未做混沌量化、浮点地板 1e-16）。

## 评分与验证状态

待后续横评独立评分。本次归档仅验证复制与上传的文件完整性（含 lab.html 与其自述哈希的一致性），没有重跑数值测试或复核原始记录中的科学陈述。
