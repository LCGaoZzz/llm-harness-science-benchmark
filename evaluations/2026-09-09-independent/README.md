# 独立复核补充证据

当前统一评分以[根 README](../../README.md#结果索引)和[主榜分数文件](../../reviews/2026-09-09/scores.json)为准，本目录不另设排行榜。[REVIEW.md](REVIEW.md)记录第二次复核范围、结果和限制；scores.json仅保留交叉核查时主榜的冻结快照及原始HTML哈希，不产生另一套分数。

从仓库根目录执行：

```sh
python -m pip install numpy scipy playwright
python -m playwright install chromium
python evaluations/2026-09-09-independent/reproduce.py --repo . --out independent-rerun
```

脚本校验七份原始HTML哈希后调用原函数；网络请求关闭。可加 `--browser /usr/bin/chromium` 指定浏览器。共同数值实验结果在输出目录evidence中。特殊GL4非线性求解、DOPRI失败输入及补充控件检查的独立脚本和完整记录随交付审计ZIP提供，不声称单一命令覆盖所有额外反例。
