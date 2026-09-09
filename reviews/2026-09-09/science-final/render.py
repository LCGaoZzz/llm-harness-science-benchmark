"""Render and check scientific-only scores and compact quantitative evidence."""
import json,sys
from pathlib import Path
import numpy as np
p=Path(__file__).resolve().parent
data=json.loads((p/'scores.json').read_text(encoding='utf-8'))
assert data['reviewer_id']=='codex-gpt-6-astra-xhigh' and data['review_format']=='10+4'
raw=json.loads((p/'results.json').read_text());refs=json.loads((p/'reference.json').read_text())
byid={s['id']:s for s in raw['submissions']};refid={s['id']:s for s in refs['submissions']}
assert set(byid)==set(refid)=={s['id'] for s in data['submissions']}=={'ds','gptweb','codex','zwin'}
assert sum(c['max'] for c in data['criteria'])==100
for s in data['submissions']:
    assert len(s['scores'])==len(s['reasons'])==5
    assert all(type(n) is int and 0<=n<=c['max'] for n,c in zip(s['scores'],data['criteria']))
    assert len(byid[s['id']]['cases'])==8
    assert all(len(c['methods']['rk4'])==3 for c in byid[s['id']]['cases'])
assert all(c['gbs']['status']=='ok' and abs(c['gbs']['t']-c['T'])<1e-9 for c in byid['ds']['cases'])
def total(s):return sum(s['scores'])
rows=sorted(data['submissions'],key=lambda s:(-total(s),s['label']))
def rank(s):return 1+sum(total(t)>total(s) for t in rows)
text='# 前四名纯科学终评\n\n'
text+=f'**评审者：`{data["reviewer_id"]}`。** 本文对应“10+4”中的四强科学终评；[配套十项评阅](../README.md)。这是该专家的独立评审样例，不是多专家共识。\n\n'
text+='**本次选择：harnessL-ds-4.1flashmax，97/100；GPT Web 与 Codex 同为 96/100，并列第二。** zcode Windows 为 91/100。'
text+='这是在“最终数学、物理与数值结果”口径下的选择，不是沿用或重算原综合榜的工程/视觉分。\n\n'
text+='## 最终评分\n\n'
text+='| 排名 | 组合 | 方程与坐标 /20 | 平衡与动力学 /15 | 轨迹精度 /25 | 长期与几何 /25 | 结论与有效域 /15 | 总分 |\n|---:|---|---:|---:|---:|---:|---:|---:|\n'
for s in rows:text+=f'| {rank(s)} | {s["label"]} | '+' | '.join(map(str,s['scores']))+f' | **{total(s)}** |\n'
text+='\n缺少中间工程文件、没有录屏、报告较短、自检数量少，都不扣分。未提供在页面上的坐标转换界面，也不再当成数学错误：直接用外部惯性系传播验证最终结果。方法数量本身不加分；只有实际交付方法产生的可核验结果计分。\n\n'
text+='## 相同问题下的数值结果\n\n'
text+='先确定[测试口径与权重](PROTOCOL.md)，再从原始 HTML 提取未改写的核心，重跑八类轨道。每类对四份产物使用相同无量纲初值/时间/步长；质量比微小差异分别用各自参考解处理。每种固定方法跑 h、h/2、h/4，不能只凭守恒量近似不变就认定轨迹正确。\n\n'
text+='下表是八工况最细步长的**最坏四维终态误差**，即无量纲 `[x,y,vx,vy]` 差的欧氏范数。不同工况的步长见原始数据；同一工况在四份产物中相同。\n\n'
text+='| 组合 | 共同 RK4 | 预先选定的固定辛方法 | 该辛方法误差 | 自适应 GBS |\n|---|---:|---|---:|---:|\n'
for s in rows:
    r=byid[s['id']];q=refid[s['id']];m=r['selectedMethod']
    rk=max(c['methods']['rk4']['stateErrors'][-1] for c in q['cases'])
    sy=max(c['methods'][m]['stateErrors'][-1] for c in q['cases'])
    gbs=f"{max(c['gbsStateError'] for c in q['cases']):.3e}" if s['id']=='ds' else '—'
    text+=f'| {s["label"]} | {rk:.3e} | {m} | {sy:.3e} | {gbs} |\n'
text+='\nDS 固定六阶方法的最坏误差约为四份共同 RK4 的 1/35；其同一组 GBS 参数在八工况均正常完成，最坏误差约为共同 RK4 的 1/967。后者是有限时间精度结论，不是保辛结论。四份 RK4 基本相同；没有只挑其他组合误差较大的辛方法来夸大差距。\n\n'
text+='DS 在可分辨截断误差的光滑和 L4 工况呈现约六阶，另三份的固定辛方法约四阶。若已接近参考/浮点误差区，步长继续减小会出现非单调结果，L1 不稳定性也会放大舍入误差；全部原值保留，不把这些点伪装成整齐的理论阶数。DS 在每个工况、每个步长上并非都最好。\n\n'
text+='## 长期守恒及数学结构\n\n'
text+='| 组合 | 固定辛方法 | L4：T=1000、h=0.01 的最大 ∣ΔC∣ | 绕地：T=100、h=0.001 的最大 ∣ΔC∣ |\n|---|---|---:|---:|\n'
for s in rows:
    r=byid[s['id']];m=r['selectedMethod']
    v=[r['longTerm'][n]['methods'][m]['maxAbsJacobiDrift'] for n in ['L4_1000','earth_100']]
    text+=f'| {s["label"]} | {m} | {v[0]:.3e} | {v[1]:.3e} |\n'
text+='\n四者所选固定方法在多状态正则辛性测试中的有限差分缺陷都小于 3e-10，单步正反向误差小于 1.1e-15。它们都有正确的数学结构；DS 的区别是本次实际误差更低。辛性由正则映射检验及方法构造支持，不能用 C 漂移小来代替。普通变步长控制的长期几何性质需要另论，参见 [Hairer：变步长与辛方法](https://www.unige.ch/~hairer/preprints/varsymp.html)。\n\n'
text+='本例 RK4 在 L4 上的漂移也极小，甚至低于两份四阶辛方法；全部 RK4 长期结果保存在原始文件中。不能因此把“某一条轨道能量很好”当成 RK4 保辛的证据，也不能宣称辛方法在所有误差指标上都更优。\n\n'
text+='## 物理结果复核\n\n'
text+='四份的 CR3BP 方程、质量参数、Jacobi 和五个平衡点均成立。量纲与参考系分别按提交自身的约定核验，不强行把不同 DU/TU 当成错误；[NASA/JPL 的归一化及坐标说明](https://ssd-api.jpl.nasa.gov/doc/periodic_orbits.html)提供约定对照。\n\n'
text+='月球飞越用独立 DOP853 加密并定位事件，比较同月距 r=0.18 DU 的质心惯性速率。这是有限半径的模型结果，包含地球共同作用，不是推进 Δv，也不是孤立月球贡献。\n\n'
text+='| 组合 | 最近月距 /DU | 最近时刻 /TU | 同月距出入惯性速率差 /DU·TU⁻¹ |\n|---|---:|---:|---|\n'
for s in rows:
    f=refid[s['id']]['flyby'];pair=f['firstForwardMatchedPair']
    delta=f"{pair['deltaInertialSpeed']:+.6f}" if pair else '初值已在 0.18 DU 内，无完整前向出入对'
    text+=f'| {s["label"]} | {f["minMoonDU"]:.8f} | {f["minMoonTime"]:.6f} | {delta} |\n'
text+='\nDS 的近月预设确实有近遇，不能因没有初始测量半径之外的入射段便判错或补造增益，故不据此扣分。减速也可以是引力辅助，zcode 的负速率变化本身不扣分。其实际问题是最终页面声称约 1.3 TU、0.028 DU，与上述结果不符；L4 线性长周期声称 29.9 TU，而独立公式 `ω²=(1±√(1−27μ(1−μ)))/2` 给出约 21.0698 TU。科学数值主张错误属于本次评阅范围，页面美观与否不属于。\n\n'
text+='原有表面穿越测试中 DS/zcode 接受了跨地球步，GPT/Codex 拒绝未分辨的近场步。这里扣的是结果已越出有限天体模型保护域，不是软件工程组织。八种常规共同轨道均未进入地月表面，不能把极端探针失败抹成它们常规积分都不正确。\n\n'
text+='## 逐项判断\n\n'
for s in rows:
    text+=f'### {s["label"]}：{total(s)} 分\n\n'
    for c,n,reason in zip(data['criteria'],s['scores'],s['reasons']):text+=f'- **{c["name"]} {n}/{c["max"]}：** {reason}\n'
    text+='\n'
text+='## 对传统专家团队认可度的判断\n\n'
text+='如果将“oldschool”理解为要求方程正确、坐标有定义、轨迹可独立复算、收敛和 Hamiltonian 结构经得起检查，我会优先把 **DS** 交给团队评审：它的优势是最终产物产生了更好的可核验数值结果，而不是方法菜单更长或过程材料更多。\n\n'
text+='但 97 对 96 是小幅领先，不是统计显著胜出，更不是实际专家组投票。GPT Web 与 Codex 在纯科学结果上应并列；上一版由界面、坐标展示和工程材料造成的差距在这里取消。zcode Windows 的算法质量仍高，较低名次主要来自具体物理数值说明错误和有效域问题。\n\n'
sensitivity={s['id']:sum(s['scores'][:4])*80/85+s['scores'][4]*20/15 for s in rows}
assert sensitivity['ds']<sensitivity['gptweb']==sensitivity['codex']
text+=f'权重敏感性：若把“物理结论及有效域”从 15% 提到 20%，其余四项按比例缩放，DS 为 {sensitivity["ds"]:.2f}，GPT Web/Codex 为 {sensitivity["gptweb"]:.2f}，第一名会互换。因此推荐严格依赖用户本次更重视最终数值结果的口径，不能称为所有天体物理专家共同偏好。\n\n'
text+='## 证据与复现\n\n'
text+='[原始数值运行](results.json) · [独立参考与物理事件](reference.json) · [机器可读评分](scores.json) · [旧版边界/控件证据](../evidence/interactions.json)。参考解的最大旋转/惯性或加密差约 8.8e-12；低于参考可分辨尺度的结果只解释为接近数值噪声，不能宣称更多有效数字。没有比较耗时或等力评估成本，没有证明任意轨道、任意时长或混沌长期相位。\n\n'
text+='依赖及原始 HTML 提取参见[原评阅方法](../METHODS.md)。在仓库根目录运行：\n\n```text\nnode reviews/2026-09-09/science-final/run.cjs ../benchmark-review-work-20260909/submissions reviews/2026-09-09/science-final/results.json\npython reviews/2026-09-09/science-final/reference.py\npython reviews/2026-09-09/science-final/render.py --check\n```\n\n'
text+='本评阅是单一 Codex 评阅者对固定四份最终产物的判断，未盲审，也没有改动参赛代码或原综合榜分数。\n'
dest=p/'README.md'
if '--check' in sys.argv:assert dest.read_text(encoding='utf-8')==text
else:dest.write_text(text,encoding='utf-8',newline='\n')
print([(rank(s),s['label'],total(s)) for s in rows])
