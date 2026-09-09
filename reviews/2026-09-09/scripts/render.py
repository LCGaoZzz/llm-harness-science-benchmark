"""Generate all 11 rankings and every per-criterion justification from scores.json.

--check verifies generated documents, arithmetic, coverage and evidence bindings.
"""
from pathlib import Path
import json,sys

review=Path(__file__).resolve().parents[1];repo=review.parents[1]
data=json.loads((review/'scores.json').read_text(encoding='utf-8'))
science=json.loads((review/'science-final/scores.json').read_text(encoding='utf-8'))
assert data['reviewer_id']==science['reviewer_id']=='codex-gpt-6-astra-xhigh'
assert data['review_format']==science['review_format']=='10+4'
rows=data['submissions'];criteria=data['criteria']
assert len(rows)==7 and len(criteria)==10
assert len({r['id'] for r in rows})==7
assert len({r['directory'] for r in rows})==7
assert all(len(r['scores'])==len(r['reasons'])==10 for r in rows)
assert all(type(s) is int and 0<=s<=10 for r in rows for s in r['scores'])
assert all(all(t.strip() for t in r['reasons']) for r in rows)
assert all(not r['caps'] for r in rows), 'This review found no caps; revise generator for future cap-bearing reviews.'
for r in rows:r['raw_total']=sum(r['scores']);r['final_total']=min([r['raw_total']]+r['caps'])
for filename in ['integrity.json','browser.json','interactions.json','numerical.json','reference.json']:
    e=json.loads((review/'evidence'/filename).read_text(encoding='utf-8'))
    assert len(e['submissions'])==7,filename
    if filename=='integrity.json':
        assert e['commit']==data['reviewed_commit']
        assert all(s['allManifestHashesMatch'] for s in e['submissions'])
        assert {s['submission'] for s in e['submissions']}=={r['directory'] for r in rows}
    else:assert {s['id'] for s in e['submissions']}=={r['id'] for r in rows},filename
    if filename=='browser.json':assert all(s.get('loadedOffline') and not s.get('error') and not s['pageErrors'] and not s['consoleErrors'] for s in e['submissions'])
    if filename=='interactions.json':assert all(not s.get('error') for s in e['submissions'])
    if filename=='numerical.json':assert all(s['math']['maxRhsError']<1e-12 and s['math']['maxJacobiError']<1e-12 for s in e['submissions'])
def rank(value,values):return 1+sum(x>value for x in values)
ordered=sorted(rows,key=lambda r:(-r['final_total'],r['label']))
for r in ordered:r['rank']=rank(r['final_total'],[x['final_total'] for x in rows])
assert {r['id'] for r in ordered[:4]}=={r['id'] for r in science['submissions']}
intro=(
    '## 结果索引\n\n'
    f'**评审者：`{data["reviewer_id"]}` · 展示格式：10+4 · 单专家样例。**\n\n'
    '已完成 **7 份提交**的独立评阅（2026-09-09）。评分以提交快照 '
    f'[`{data["reviewed_commit"][:7]}`](https://github.com/LCGaoZzz/llm-harness-science-benchmark/tree/{data["reviewed_commit"]}) 为准。'
    '每项 0–10 分、等权求和，再应用原有封顶规则；本轮 7 份均未触发封顶。\n\n'
    '**同分并列，使用竞赛排名（如 1、2、2、4）；表内同分条目的显示顺序不代表先后。** '
    '这些是本次产物的评分，不能据此推断模型总体能力。生成环境、迭代轮数及提示词完整性不完全一致；详见各原始提交说明。\n\n'
    f'本次更新接续[先前榜单 `{data["previous_leaderboard_commit"][:7]}`](https://github.com/LCGaoZzz/llm-harness-science-benchmark/blob/{data["previous_leaderboard_commit"]}/README.md#结果索引)，'
    f'及[并行评阅 `{data["parallel_leaderboard_commit"][:7]}`](https://github.com/LCGaoZzz/llm-harness-science-benchmark/blob/{data["parallel_leaderboard_commit"]}/LEADERBOARD.md)。'
    '参赛文件未变；[分数差异与依据](reviews/2026-09-09/METHODS.md#与先前榜单的差异)单独列出，旧版分数仍可追溯。'
    '该专家的当前榜单统一在本 README 展示；其他专家的结果由上方索引分别收录。\n\n'
    '[评阅方法与限制](reviews/2026-09-09/METHODS.md) · '
    '[逐项评分证据](reviews/2026-09-09/README.md) · '
    '[机器可读评分](reviews/2026-09-09/scores.json) · '
    '[实测记录与截图](reviews/2026-09-09/evidence/)\n\n'
    '**后续专项：[前四名纯科学终评](reviews/2026-09-09/science-final/README.md)**。只比较最终数学、物理及数值结果，不计界面、工程材料或中间文件完整度；其权重和结论单列，原综合榜分数保持原评分口径。\n\n'
    '### 总排名\n\n'
    '| 排名 | 参赛组合 | 原始合计 /100 | 封顶 | 最终得分 /100 | 评阅 |\n'
    '|---:|---|---:|---|---:|---|\n'
)
for r in ordered:intro+=f'| {r["rank"]} | [{r["label"]}](submissions/{r["directory"]}/) | {r["raw_total"]} | 无 | **{r["final_total"]}** | [逐项证据](reviews/2026-09-09/README.md#{r["id"]}) |\n'
intro+='\n### 10 个单项排名\n\n'
for i,name in enumerate(criteria):
    intro+=f'#### {i+1}. {name}\n\n| 排名 | 参赛组合 | 得分 /10 |\n|---:|---|---:|\n'
    vals=[r['scores'][i] for r in rows]
    for r in sorted(rows,key=lambda r:(-r['scores'][i],r['label'])):intro+=f'| {rank(r["scores"][i],vals)} | [{r["label"]}](reviews/2026-09-09/README.md#{r["id"]}) | {r["scores"][i]} |\n'
    intro+='\n'
intro+='### 前四名纯科学终评（4）\n\n'
intro+=f'评审者：`{science["reviewer_id"]}`。这是上述综合榜前四名的独立科学评分；[权重、逐项理由与实测证据](reviews/2026-09-09/science-final/README.md)单列。\n\n'
intro+='| 排名 | 参赛组合 | 科学得分 /100 |\n|---:|---|---:|\n'
science_rows=sorted(science['submissions'],key=lambda r:(-sum(r['scores']),r['label']))
science_totals=[sum(r['scores']) for r in science_rows]
for r in science_rows:intro+=f'| {rank(sum(r["scores"]),science_totals)} | {r["label"]} | **{sum(r["scores"])}** |\n'
intro+='\n该专家推荐 harnessL-ds-4.1flashmax；97 与 96 的差距较小，科学终评已说明权重敏感性。\n'
root_readme=(repo/'README.md').read_text(encoding='utf-8');prefix=root_readme.split('## 结果索引')[0]
assert '## 评分标准（100 分）' in prefix and '## 公平性原则' in prefix
doc='# 2026-09-09：七份 CR3BP 提交评阅\n\n'
doc+=f'**评审者：`{data["reviewer_id"]}`。** 本文对应“10+4”中的十项评阅；[配套四强纯科学终评](science-final/README.md)。这是该专家的独立评审样例，不是多专家共识。\n\n'
doc+='评阅对象为固定提交快照，原始 HTML、ZIP、报告与提交说明均未修改。'
doc+='[评分方法、实测条件、封顶核验与复现步骤](METHODS.md)；[主榜及十项独立排名](../../README.md#结果索引)。\n\n'
doc+='评分是单一评阅者依据 README 作出的判断，整数分值不代表统计置信区间。统一测试用于查验事实；没有按原始误差数值机械线性换分，也未把自检条数当成得分。\n\n'
doc+='## 得分矩阵\n\n| 排名 | 组合 | '+' | '.join(f'{i+1}' for i in range(10))+' | 合计 |\n|---:|---|'+'---:|'*11+'\n'
for r in ordered:doc+=f'| {r["rank"]} | [{r["label"]}](#{r["id"]}) | '+' | '.join(map(str,r['scores']))+f' | **{r["final_total"]}** |\n'
doc+='\n'+ '；'.join(f'{i+1}={n}' for i,n in enumerate(criteria))+'。\n\n'
doc+='## 本轮关键实测\n\n'
doc+='| 组合 | 页面自检 | 断网单文件 | 原始运动方程 | 主要复核发现 |\n|---|---|---|---|---|\n'
findings={
 'gptweb':'完整单位/惯性参考证据；近场和跨表面步被拒绝。',
 'codex':'双四阶方法和事务式守卫有效；缺完整惯性向量转换与画面速度矢量。',
 'zwin':'三个方法及长期守恒成立；穿体未拒绝，飞越说明与初值不符。',
 'ds':'高精度 GBS 有独立支持；穿体未拒绝，暂停缩放不重绘，允许域测试为代数恒等式。',
 'zlinux':'GL4 光滑区四阶/保辛；迭代终止标准过宽，穿体未拒绝。',
 'qwen':'最终自检已为 7/7；单步=40h、重置基于当前状态、自检后 bad 标志使播放冻结。',
 'kimi':'第二方法二阶但不保辛；弱碰撞半径及先提交后检查会接受穿体步。'
}
for r in ordered:doc+=f'| {r["label"]} | {r["self_tests"]} | 成功 | 正确 | {findings[r["id"]]} |\n'
doc+='\n所有组合的基本运行、自检、初值输入、算法切换、预设按钮、缩放/平移均实际操作过；发现的缺陷记录为缺陷，而不把控件存在本身视为通过。Kimi 的时间与状态由 UI 读数采集，存在显示舍入，不能把 0.0010 与真实步长约 0.001046 的差异当作单步错误。\n\n'
for r in ordered:
    doc+=f'<a id="{r["id"]}"></a>\n\n## {r["label"]} — {r["final_total"]}/100\n\n'
    doc+=f'[原始提交](../../submissions/{r["directory"]}/) · [原始入口](../../submissions/{r["directory"]}/{r["source"]}) · [实际交互截图](evidence/{r["id"]}-interaction.png)\n\n'
    doc+='| # | 评分项 | 得分 /10 | 证据与判断 |\n|---:|---|---:|---|\n'
    for i,(n,s,t) in enumerate(zip(criteria,r['scores'],r['reasons'])):doc+=f'| {i+1} | {n} | {s} | {t.replace("|","∣")} |\n'
    doc+=f'\n原始合计 **{r["raw_total"]}**；封顶规则：**无**；最终 **{r["final_total"]}**；总榜第 **{r["rank"]}**。\n\n'
    doc+=f'原始实测可按 `id="{r["id"]}"` 查阅 [数值结果](evidence/numerical.json)、[独立参考](evidence/reference.json)、[自检/控制台](evidence/browser.json)、[控件与边界](evidence/interactions.json)。\n\n'
outputs={repo/'README.md':prefix+intro.rstrip()+'\n',review/'README.md':doc.rstrip()+'\n'}
for p,s in outputs.items():
    if '--check' in sys.argv:assert p.read_text(encoding='utf-8')==s,'Generated document is stale: '+str(p)
    else:p.write_text(s,encoding='utf-8',newline='\n')
print('Validated reviewer identity, 10+4 linkage, 7 submissions, 70 scores, 11 comprehensive rankings, ties, totals, caps and evidence coverage.')
print([(r['rank'],r['label'],r['final_total']) for r in ordered])
