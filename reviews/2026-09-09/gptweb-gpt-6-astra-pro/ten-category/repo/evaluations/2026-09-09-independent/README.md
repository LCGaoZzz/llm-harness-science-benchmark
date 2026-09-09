# 独立复核补充证据

当前统一评分以根 README 和 reviews/2026-09-09/scores.json 为准，本目录不另设排行榜。阅读 REVIEW.md 查看复核范围、执行结果和限制。

从仓库根目录执行：

```sh
python -m pip install numpy scipy playwright
python -m playwright install chromium
python evaluations/2026-09-09-independent/reproduce.py --repo . --out independent-rerun
```

脚本校验七份原始HTML哈希后调用原函数；网络请求关闭。可加 --browser /usr/bin/chromium 指定浏览器。共同数值实验结果在输出目录evidence中。
