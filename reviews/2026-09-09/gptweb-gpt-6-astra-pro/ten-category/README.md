# 七作品复核审计包

repo/LEADERBOARD.md 是主仓库 faef8de 统一榜单的离线副本（98、95、88、85、83、74、72），不是另一套竞争评分。根仓库 README 为线上唯一榜单入口；70项逐条理由在 reviews/2026-09-09/README.md。

本次补充复核报告：repo/evaluations/2026-09-09-independent/REVIEW.md。inputs/保留7份原始HTML；evidence/保存实际数值、交互、控制台和截图；scripts/为实际执行脚本。原文件哈希见entries.json。未包含与任务无关的完整会话及工作区元数据。

安装NumPy、SciPy、Playwright、Chromium后，可运行scripts/numerical_review.py、edge_review.py、supplement.py、ui_review.py、post_concurrency_recheck.py等；默认浏览器路径/usr/bin/chromium。便携共同数值入口为repo/evaluations/2026-09-09-independent/reproduce.py，需--repo指向完整基准仓库。原始惯性参考脚本和HTML保存在original-gpt-validation/，直接运行independent_validation.py会执行4预设×2方法×2步长并写validation/r11.json。

本环境file://被管理员策略阻止，采用完整HTML的set_content执行；该限制没有作为作品失败。分数是量表判断，不是测试通过率。最终分数保留已有统一口径；本会话的未发布草案不在交付包中。
