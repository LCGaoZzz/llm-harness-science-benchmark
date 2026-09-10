"""Render the updated Codex 10+5 record; preserve the seven prior score vectors."""
import hashlib,json,sys
from pathlib import Path

F=Path(__file__).resolve().parent
ROOT=F.parents[2]
OLD=ROOT/'reviews/2026-09-09'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
ten=read(F/'scores.json');science=read(F/'science-scores.json')
baseline=read(OLD/'scores.json');previous_science=read(OLD/'science-final/scores.json')
numeric=read(F/'numerical.json');reference=read(F/'reference.json');browser=read(F/'browser.json')
assert ten['reviewer_id']==science['reviewer_id']=='codex-gpt-6-astra-xhigh'
assert ten['review_format']==science['review_format']=='10+5'
rows=ten['submissions'];sr=science['submissions']
assert len(rows)==len({r['id'] for r in rows})==8 and len(sr)==5
for r in baseline['submissions']:
    current=next(s for s in rows if s['id']==r['id'])
    assert current['scores']==r['scores'] and current['reasons']==r['reasons']
for r in sr:
    if r['inherited']:assert r['scores']==next(s['scores'] for s in previous_science['submissions'] if s['id']==r['id'])
for r in rows:
    assert len(r['scores'])==len(r['reasons'])==10 and not r['caps']
    assert all(isinstance(n,int) and 0<=n<=10 for n in r['scores'])
for r in sr:
    assert len(r['scores'])==len(r['reasons'])==5
    assert all(isinstance(n,int) and 0<=n<=c['max'] for n,c in zip(r['scores'],science['criteria']))
total=lambda r:sum(r['scores'])
ordered=sorted(rows,key=lambda r:(-total(r),r['label']))
rank=lambda r,allrows:1+sum(total(o)>total(r) for o in allrows)
assert {r['id'] for r in ordered[:5]}=={r['id'] for r in sr}
assert browser['selfTests']['passed']==browser['selfTests']['total']==12
assert not browser['pageErrors'] and not browser['consoleErrors'] and not browser['requests']
assert len(numeric['cases'])==len(reference['cases'])==8
assert all(g['ok'] and g['reachedT'] for c in reference['cases'] for g in c['gbs'])
assert hashlib.sha256((ROOT/numeric['source']).read_text(encoding='utf-8').encode()).hexdigest()==numeric['sha256']=='1489db7bd4cba9e8c036b4828ba0855277fea5de81b6a5939612e3a3f2e5138d'
header='**评审平台：Codex · 评审模型：GPT-6 Astra（xhigh） · 评审者：`codex-gpt-6-astra-xhigh`**\n\n'
doc='# Codex：2026-09-10 增补评审（10＋5）\n\n'+header
doc+='本轮新增 `harnessL-glm5.3-max`，**十项综合 86/100，第 4；科学终评 92/100，第 4**。按用户最新要求，科学榜改为综合前五入围的“科学五强”，当前完整展示为 **10＋5**。\n\n'
doc+=f'新作品固定于提交快照 [`{ten["reviewed_commit"][:7]}`](https://github.com/LCGaoZzz/llm-harness-science-benchmark/tree/{ten["reviewed_commit"]})，HTML SHA-256 为 `{numeric["sha256"]}`。原七份十项分数及原四份科学分数沿用 [2026-09-09 评审](../../2026-09-09/codex-gpt-6-astra-xhigh/README.md)；本轮没有把旧记录冒充新的独立重跑。\n\n'
doc+='按[基准十项标准](../../../BENCHMARK.md)等权相加，八份均无封顶；同分采用竞赛排名（1、2、2、4）。[机器可读十项分数](scores.json) · [科学终评与推荐](science-final.md) · [原七份逐项理由](../../2026-09-09/README.md)。\n\n'
doc+='## 十项综合总榜\n\n| 排名 | 组合 | 得分 /100 | 评分依据 |\n|---:|---|---:|---|\n'
for r in ordered:
    link='#hglm' if r['id']=='hglm' else f'../../2026-09-09/README.md#{r["id"]}'
    doc+=f'| {rank(r,rows)} | [{r["label"]}](../../../submissions/{r["directory"]}/) | **{total(r)}** | [逐项理由]({link}) |\n'
doc+='\n**入围变化：** 新作品 86 分进入综合第 4，DS 原综合 85 分转为第 5。科学榜现取综合前五，因此同时包含新作品和 DS；DS 科学 **97 分保持不变，仍居科学榜第一**。科学五强榜不等于全部八份作品的纯科学总榜。\n\n'
doc+='## 八份得分矩阵\n\n| 组合 | '+' | '.join(str(i) for i in range(1,11))+' | 总分 |\n|---|'+'---:|'*11+'\n'
for r in ordered:doc+=f'| {r["label"]} | '+' | '.join(map(str,r['scores']))+f' | **{total(r)}** |\n'
doc+='\n'+'；'.join(f'{i+1}={c}' for i,c in enumerate(ten['criteria']))+'。\n\n<a id="ten"></a>\n\n## 10 个单项排名\n\n'
for i,c in enumerate(ten['criteria']):
    doc+=f'### {i+1}. {c}\n\n| 排名 | 组合 | 得分 /10 |\n|---:|---|---:|\n'
    for r in sorted(rows,key=lambda r:(-r['scores'][i],r['label'])):
        n=1+sum(s['scores'][i]>r['scores'][i] for s in rows)
        doc+=f'| {n} | {r["label"]} | {r["scores"][i]} |\n'
    doc+='\n'
r=next(r for r in rows if r['id']=='hglm')
doc+='<a id="hglm"></a>\n\n## 新作品逐项理由：86/100\n\n'
doc+='[原始 HTML](../../../submissions/harnessL--glm5.3-max--2026-09-10/lab.html) · [浏览器实测](browser.json) · [八工况数值结果](numerical.json) · [独立参考](reference.json)。\n\n| # | 评分项 | 得分 /10 | 证据与判断 |\n|---:|---|---:|---|\n'
for i,(c,n,reason) in enumerate(zip(ten['criteria'],r['scores'],r['reasons'])):doc+=f'| {i+1} | {c} | {n} | {reason.replace("|","∣")} |\n'
doc+='\n页面内自检的 12/12、提交附带 harness 的断言数均不是本表的自动评分公式。自述通过项只在本轮复核后用作证据，旧开发失败记录也不直接当作最终页面失败。\n\n'
doc+='## 科学终评入口\n\n| 排名 | 组合 | 科学得分 /100 |\n|---:|---|---:|\n'
for r in sorted(sr,key=lambda r:(-total(r),r['label'])):doc+=f'| {rank(r,sr)} | {r["label"]} | **{total(r)}** |\n'
doc+='\n[五项权重、数值比较与推荐理由](science-final.md)。本轮 DS **97 分第一**，GPT Web 与 Codex **96 分并列第二**。\n\n## 复现\n\n'
doc+='浏览器使用 Windows 上的 Microsoft Edge，版本记录在 `browser.json`；Python／SciPy 版本记录在 `reference.json`。浏览器脚本需要 Node.js、Playwright 和 Edge，参考脚本需要 NumPy、SciPy。浏览器请求被拦截，直接打开原始 HTML；数值脚本只提取原 HTML 的未改写函数。以提交的 LF 原始文件核对 SHA-256。\n\n```text\nnode reviews/2026-09-10/codex-gpt-6-astra-xhigh/browser.cjs\nnode reviews/2026-09-10/codex-gpt-6-astra-xhigh/run.cjs\npython reviews/2026-09-10/codex-gpt-6-astra-xhigh/reference.py\npython reviews/2026-09-10/codex-gpt-6-astra-xhigh/render.py\npython scripts/render_cards.py\n```\n\n'
doc+='浮点末位和浏览器版本可能影响微小误差；复算数据应复查后发布。`render.py --check` 检查已发布分数、前五入围集合、原七份分数不变及生成文件一致性。截图记录自检后的残留错误横幅：[浏览器截图](browser-selftests.png)。\n'
text='# Codex：2026-09-10 五强纯科学终评\n\n'+header
text+='**科学五强：DS 97 分第一；GPT Web 与 Codex 96 分并列第二；harnessL GLM 92 分第四；ZCode Windows 91 分第五。** [配套八份十项榜](README.md)。\n\n'
text+='仅评价最终数学、物理与数值结果，权重沿用 **20／15／25／25／15**。不计界面、工程组织、自检数量和中间文件。错误的科学读数属于最终结果，仍计入判断。旧四份分数与证据沿用，新作品单独完成同口径复算。\n\n'
text+='**入围规则更新：** 按用户要求，从原“综合前四”改为“综合前五”。DS 综合分 85，现列第五，继续保留在科学五强中；其[历史科学 97 分](../../2026-09-09/science-final/README.md)不变。本榜采用 **10＋5** 展示，历史评审保留原版本。\n\n'
text+='## 最终评分\n\n| 排名 | 组合 | 方程与坐标 /20 | 平衡与动力学 /15 | 轨迹精度 /25 | 长期与几何 /25 | 结论与有效域 /15 | 总分 |\n|---:|---|---:|---:|---:|---:|---:|---:|\n'
for r in sorted(sr,key=lambda r:(-total(r),r['label'])):text+=f'| {rank(r,sr)} | {r["label"]} | '+' | '.join(map(str,r['scores']))+f' | **{total(r)}** |\n'
text+='\n## 共同工况与参考解\n\n'
text+='沿用[原八工况协议](../../2026-09-09/science-final/PROTOCOL.md)：一般光滑、宽绕地、近地、近月、L1 扰动、L4 扰动、偏心绕地、共同飞越。对新作品 RK4 和其最高阶固定辛方法（隐式中点）运行 h、h/2、h/4；GBS 另测默认 tol=1e-12 与加严 1e-13，固定绝对容差下限 1e-14。两组 GBS 均跑完八工况，不按单个工况挑最优容差。\n\n'
text+='DOP853 完全独立于参赛代码，rtol=2.3e-14、atol=2e-15，并用更小 max_step 与惯性系移动双主星传播交叉核对。本轮参考自身加密／参考系交叉差最大约 **6.11e-12**；低于此量级的误差不解释为更多有效数字。\n\n'
text+='下表为八工况最细步长下的最坏四维终态误差；旧四份为原存档结果，新作品为本次新增复算，按各自 μ 求参考。\n\n| 组合 | RK4 | 固定辛方法 | 该方法误差 | GBS 默认 / 加严 |\n|---|---:|---|---:|---:|\n'
oldraw=read(OLD/'science-final/results.json');oldrefs=read(OLD/'science-final/reference.json')
for r in sorted(sr,key=lambda r:(-total(r),r['label'])):
    if r['id']=='hglm':
        q=reference;m='imp';name='隐式中点（二阶）'
        g=' / '.join(f'{max(c["gbs"][i]["stateError"] for c in reference["cases"]):.3e}' for i in (0,1))
    else:
        a=next(a for a in oldraw['submissions'] if a['id']==r['id']);q=next(q for q in oldrefs['submissions'] if q['id']==r['id']);m=a['selectedMethod'];name=m;g='—'
        if r['id']=='ds':g=f'{max(c["gbsStateError"] for c in q["cases"]):.3e}（原配置）'
    rk=max(c['methods']['rk4']['stateErrors'][-1] for c in q['cases']);err=max(c['methods'][m]['stateErrors'][-1] for c in q['cases'])
    text+=f'| {r["label"]} | {rk:.3e} | {name} | {err:.3e} | {g} |\n'
text+='\n新作品光滑和 L4 工况的 RK4 接近四阶，隐式中点在八工况均接近二阶；部分 RK4 工况的误差抵消或舍入会改变观测阶数，不强制每点恰好四阶。GBS 很准确，加严容差在偏心绕地工况却略变差；这是局部控制、舍入及全局误差共同作用，不能宣称“容差越小，每项结果必然更好”。\n\n'
text+='## 长期误差与几何结构\n\n| 方法 | L4：T=1000、h=0.01，最大 ∣ΔC∣ | 绕地：T=100、h=0.001，最大 ∣ΔC∣ |\n|---|---:|---:|\n'
for m in ['rk4','imp']:
    v=[numeric['longTerm'][n]['methods'][m]['maxAbsJacobiDrift'] for n in ['L4_1000','earth_100']]
    text+=f'| 新作品 {m} | {v[0]:.3e} | {v[1]:.3e} |\n'
v=[abs(numeric['longTerm'][n]['gbs']['C0'])*numeric['longTerm'][n]['gbs']['driftRel'] for n in ['L4_1000','earth_100']]
text+=f'| 新作品 GBS（自适应，tol=1e-12） | {v[0]:.3e} | {v[1]:.3e} |\n'
text+='\n隐式中点正则辛性有限差分缺陷最大 **1.34e-10**，正反向误差小于 **1.2e-18**；方法构造与数值检验相符。其长期分段最大漂移有界，但同一步长误差高于旧四强的高阶固定辛方法。GBS 的优异精度独立评价，不把自适应 GBS 宣称为保辛。\n\n'
text+='## 最终物理读数与预设\n\n'
text+='状态栏“相对月球速度”使用 `hypot(vx+y, vy-x)`，正确的月心相对惯性速率应为 `hypot(vx-y, vy+x-(1-μ))`；整体旋转矩阵不改变范数。独立参考能证明轨迹的坐标自洽，却不能使这条错误的显示公式变正确，因此计入科学扣分。\n\n'
f=reference['flyby']
text+=f'独立飞越最近月距 **{f["minMoonDU"]:.8f} DU**，发生于 **{f["minMoonTime"]:.6f} TU**；相同 0.18 DU 月距出入的质心惯性速率增加 **{f["matchedSpeedChange"]:.6f} DU/TU**。用地心相对速度 `[vx-y, vy+x+μ]` 计算，比能在 T=14 相对初值增加约 **{100*f["relativeEnergyChangeAtT14"]:.2f}%**，支持页面“约 +90%”的粗略叙述。它是特定时刻与参考系的量，不能当推进 Δv 或全部归因于孤立月球。\n\n'
text+='新作品明确采用质点主星，故不把进入物理天体半径本身视为方程错误。不过同一高速近场探针在 h=0.001 时仍接受 |ΔC|≈255.68 的一步，缺少未分辨步拒绝；这是数值有效域问题，扣在结果与有效域项，且不代表常规八工况都不正确。\n\n## 新作品五项理由\n\n'
r=next(r for r in sr if r['id']=='hglm')
for c,n,reason in zip(science['criteria'],r['scores'],r['reasons']):text+=f'- **{c["name"]} {n}/{c["max"]}：** {reason}\n'
text+='\n旧四份的[逐项理由与原始证据](../../2026-09-09/science-final/README.md#逐项判断)保留不变。\n\n## 推荐与边界\n\n'
text+='面向重视数学与天体力学的传统专家团队，本轮仍优先推荐 **DS（97）**，GPT Web 与 Codex **96 分并列第二**。DS 的固定六阶与自适应结果支持小幅领先；原有权重敏感性依然成立。新作品的 GBS 结果很强，但月球相对速率读数、固定步长精度和未分辨近场处理仍有不足，未改变首选。\n\n'
text+='97 与 96、92 与 91 的一分差均为量表判断，不是统计显著性或人类专家投票。单一轨道的守恒小误差不能证明任意轨道、任意时长的轨迹精度；本轮不比较等成本效率，也未对未入围的三份作品新增纯科学评分。\n\n'
text+='[科学评分 JSON](science-scores.json) · [未改写内核运行](numerical.json) · [独立参考与飞越事件](reference.json) · [浏览器证据](browser.json) · [复现命令](README.md#复现)。\n'
for dest,value in [(F/'README.md',doc),(F/'science-final.md',text)]:
    if '--check' in sys.argv:assert dest.read_text(encoding='utf-8')==value,str(dest)
    else:dest.write_text(value,encoding='utf-8',newline='\n')
print('Validated 8 entrants, 80 scores, 10 item rankings, top-five admission, inherited scores, input hash and all new numerical evidence.')
