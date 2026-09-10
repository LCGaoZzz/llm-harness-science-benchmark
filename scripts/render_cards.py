"""Build the README overview and eight SVG cards from published expert scores."""
from pathlib import Path
from html import escape
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'reviews/2026-09-09'

def read(path):
    return json.loads((BASE / path).read_text(encoding='utf-8'))

def competition(rows):
    for row in rows:
        row['rank'] = 1 + sum(other['score'] > row['score'] for other in rows)
    return sorted(rows, key=lambda r: (r['rank'], r['label']))

codex = read('scores.json')
codex_science = read('science-final/scores.json')
web = read('gptweb-gpt-6-astra-pro/ten-category/repo/evaluations/2026-09-09-independent/scores.json')
web_science = read('gptweb-gpt-6-astra-pro/science-final/scores.json')
kimi = read('kimiweb-k3-swarmmax/scores.json')
glm = read('zcode-glm-5.3max-win/scores.json')
experts = [
    dict(id='codex-gpt-6-astra-xhigh', platform='Codex', model='GPT-6 Astra（xhigh）', color='#2563EB', tint='#EFF6FF',
         ten=competition([dict(label=r['label'],score=sum(r['scores'])) for r in codex['submissions']]),
         four=competition([dict(label=r['label'],score=sum(r['scores'])) for r in codex_science['submissions']]),
         max_four=100, ten_note='十项等权 · 原评审分数', four_note='权重 20 / 15 / 25 / 25 / 15',
         ten_link='reviews/2026-09-09/codex-gpt-6-astra-xhigh/README.md#10-个单项排名',
         four_link='reviews/2026-09-09/science-final/README.md'),
    dict(id='gptweb-gpt-6-astra-pro', platform='ChatGPT 网页版', model='GPT-6 Astra Pro', color='#0F8B73', tint='#ECFDF5',
         ten=[dict(label=r['label'],score=r['total'],rank=r['rank']) for r in web['rows']],
         four=[dict(label=r['label'],score=r['total'],rank=r['rank']) for r in web_science['rows']],
         max_four=100, ten_note='复核后沿用既有十项评分', four_note='权重 30 / 35 / 25 / 10',
         ten_link='reviews/2026-09-09/gptweb-gpt-6-astra-pro/README.md#gptweb-gpt-6-astra-pro-ten',
         four_link='reviews/2026-09-09/gptweb-gpt-6-astra-pro/README.md#gptweb-gpt-6-astra-pro-four'),
    dict(id='kimiweb-k3-swarmmax', platform='Kimi 网页版', model='K3（Swarm Max）', color='#7C3AED', tint='#F5F3FF',
         ten=[dict(label=r['submission'],score=r['final_total'],rank=r['rank']) for r in kimi['ten']['overall']],
         four=[dict(label=r['submission'],score=r['science_total'],rank=r['rank']) for r in kimi['four']['overall']],
         max_four=80, ten_note='分数与名次按原评审展示', four_note='科学八项 /80 · 末位并列扩展至 5 份',
         ten_link='reviews/2026-09-09/kimiweb-k3-swarmmax/README.md#ten',
         four_link='reviews/2026-09-09/kimiweb-k3-swarmmax/README.md#four'),
    dict(id='zcode-glm-5.3max-win', platform='ZCode（Windows）', model='GLM-5.3（Max）', color='#C16A15', tint='#FFF7ED',
         ten=sorted([dict(label=r['label'],score=r['final'],rank=r['rank']) for r in glm['submissions']], key=lambda r:(r['rank'],r['label'])),
         four=[dict(label=next(r['label'] for r in glm['submissions'] if r['id']==key),score=v['total'],rank=v['rank']) for key,v in glm['science_final']['scores'].items()],
         max_four=100, ten_note='十项等权 · 原评审分数 · 09.10 增补第 8 份', four_note='科学十项等权 · 原评审分数 · 09.10 扩至五强', date='2026.09.09 · 09.10 增补',
         four_title='五强科学榜', four_badge='5', four_alt='五强科学评分与排名',
         ten_link='reviews/2026-09-09/zcode-glm-5.3max-win/README.md',
         four_link='reviews/2026-09-09/zcode-glm-5.3max-win/science-final/README.md'),
]

def entrant(label):
    low=label.lower()
    if 'gptweb' in low:return 'GPT Web', 'gpt-6pro'
    if 'codex' in low:return 'Codex', '6astra-xhigh'
    if 'ds-4' in low:return 'HarnessL · DeepSeek', 'ds-4.1flashmax'
    if 'qwen' in low:return 'HarnessL · Qwen', 'qwen-3.8flashxhigh'
    if 'kimi' in low:return 'Kimi Web', 'k3swarm-max'
    if 'glm5.3' in low:return 'HarnessL · GLM', 'glm5.3-max'
    if 'linux' in low:return 'ZCode · Linux', 'glm-5.3maxlinux'
    return 'ZCode · Windows', 'glm-5.3max'

def number(value):
    return f'{value:g}'

def svg(expert, kind):
    rows=expert[kind]
    assert (kind=='ten' and len(rows) in (7,8)) or (kind=='four' and len(rows) in (4,5)), f'{expert["id"]} {kind}: {len(rows)} rows'
    extra=(len(rows)-7)*56 if kind=='ten' else 0
    height=660+extra
    maximum=100 if kind=='ten' else expert['max_four']
    assert all(0<=r['score']<=maximum and r['rank']>=1 for r in rows)
    color,tint=expert['color'],expert['tint']
    title='十项综合榜' if kind=='ten' else expert.get('four_title','四强科学榜')
    badge='10' if kind=='ten' else expert.get('four_badge','4')
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="{height}" viewBox="0 0 600 {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{expert["id"]} · {title}</title>',
        f'<desc id="desc">'+escape('；'.join(f'第 {r["rank"]} 名 {r["label"]}，{number(r["score"])} / {maximum}' for r in rows))+'</desc>',
        f'<rect x="1" y="1" width="598" height="{height-2}" rx="24" fill="#FFFFFF" stroke="#DDE3EC" stroke-width="2"/>',
        '<path d="M25 1 H575 Q599 1 599 25 V144 H1 V25 Q1 1 25 1Z" fill="#101C32"/>',
        f'<rect x="28" y="29" width="4" height="24" rx="2" fill="{color}"/>',
        f'<text x="44" y="48" fill="#DCE5F6" font-size="19" font-weight="600">{expert["id"]}</text>',
        f'<text x="44" y="70" fill="#A8B7CE" font-size="14">平台：{escape(expert["platform"])} · 模型：{escape(expert["model"])}</text>',
        f'<text x="28" y="106" fill="#FFFFFF" font-size="33" font-weight="700">{title}</text>',
        f'<rect x="480" y="70" width="89" height="50" rx="13" fill="{color}"/>',
        f'<text x="524" y="105" fill="#FFFFFF" font-size="31" font-weight="700" text-anchor="middle">{badge}</text>',
        '<text x="28" y="177" fill="#7C879A" font-size="15" letter-spacing="2">排名</text>',
        '<text x="99" y="177" fill="#7C879A" font-size="15" letter-spacing="2">参赛作品</text>',
        f'<text x="566" y="177" fill="#7C879A" font-size="15" text-anchor="end">评分 /{maximum}</text>']
    row_height=56 if kind=='ten' else 72
    for index,row in enumerate(rows):
        y=197+index*row_height
        winner=row['rank']==1
        fill=tint if winner else ('#F8FAFD' if index%2==0 else '#FFFFFF')
        parts.append(f'<rect x="18" y="{y}" width="564" height="{row_height-3}" rx="11" fill="{fill}"/>')
        cy=y+(row_height-3)/2
        parts.append(f'<rect x="29" y="{cy-16}" width="38" height="32" rx="9" fill="{color if winner else "#EAEFF6"}"/>')
        parts.append(f'<text x="48" y="{cy+6}" text-anchor="middle" fill="{"#FFFFFF" if winner else "#617087"}" font-size="20" font-weight="700">{row["rank"]}</text>')
        name,model=entrant(row['label'])
        parts.append(f'<text x="99" y="{cy-3}" fill="#14233B" font-size="22" font-weight="600">{escape(name)}</text>')
        parts.append(f'<text x="99" y="{cy+17}" fill="#7C879A" font-size="15">{escape(model)}</text>')
        parts.append(f'<text x="565" y="{cy+10}" text-anchor="end" fill="{color if winner else "#22314B"}" font-size="31" font-weight="700">{number(row["score"])}</text>')
    if kind=='four' and len(rows)==4:
        parts.append(f'<rect x="28" y="510" width="544" height="65" rx="12" fill="{tint}"/>')
        parts.append(f'<text x="47" y="536" fill="{color}" font-size="16" font-weight="600">数学 · 物理 · 数值结果</text>')
        parts.append('<text x="47" y="560" fill="#64748B" font-size="15">详细指标、依据及推荐见评分页</text>')
    parts += [f'<path d="M28 {604+extra} H572" stroke="#E8EDF4"/>',
        f'<text x="28" y="{632+extra}" fill="#64748B" font-size="15">{escape(expert[kind+"_note"])}</text>',
        f'<text x="572" y="{632+extra}" text-anchor="end" fill="#94A0B2" font-size="13">{expert.get("date","2026.09.09")}</text>', '</svg>']
    return '\n'.join(parts).replace('<svg ', '<svg font-family="Segoe UI, Microsoft YaHei, Arial, sans-serif" ',1)+'\n'

readme='''# LLM × Harness 科学计算基准

同一道地月三体问题，比较不同 **Harness＋LLM** 能否交付数学正确、数值可信、可以实际操作的科学计算程序。当前收录 **8 份参赛作品、4 位 AI 评审的“10＋4”评分**（评审日期 2026-09-09；[ZCode／GLM 评审](reviews/2026-09-09/zcode-glm-5.3max-win/README.md)于 09-10 增补评阅第 8 份 `harnessL--glm5.3-max`）。

## 任务是什么

创建一个可直接在浏览器运行的单文件 HTML **“地月限制性三体问题实验室”**。采用圆型限制性三体模型（CR3BP）：地球与月球绕共同质心做圆周运动，航天器质量忽略不计。程序需要：

- 在旋转坐标系中实时积分轨迹，计算 L1–L5 拉格朗日点和零速度曲线。
- 实现 RK4 和一种适合长期模拟的积分器；支持调初值、步长、暂停、单步与视图操作，显示 Jacobi 常数及其漂移。
- 提供 L4 扰动、L1 不稳定运动、绕地轨道和月球引力辅助预设，并实际验证平衡点残差、步长收敛、守恒误差与数值异常防护。

轨迹必须实时计算，自检必须真实执行。完整提示词、评分尺度与封顶规则见 [基准任务与评分标准](BENCHMARK.md)；作品存放于 [submissions](submissions/)。

## 比的是什么

这里的 **Harness** 指承载模型完成任务的平台、工具和执行环境。比较的是模型与这些条件共同产出的最终作品，包括科学建模、数值求解、验证与交互交付；参赛名称按提交者标注保留，Windows 与 Linux 产物分别计入。当前记录没有统一所有组合的算力、时间和工具预算，结论限于本轮作品。

**10 榜**按十项标准综合评价全部参赛作品（ZCode／GLM 评审已含 8 份，其余评审仍为其评阅快照内的 7 份）；**科学榜**只对入围作品的最终数学、物理和数值结果复评，不计界面或中间工程材料。

“10”指评分维度，前八项是科学与数值计算，后两项是工程验证与交互表达；“4”指每位评审综合榜的前四名。Kimi 评审因入选边界并列扩展至五份；ZCode／GLM 评审于 09-10 增补第 8 份作品后，科学榜直接改为五强。缺少中间工程文件不构成科学榜扣分理由。

## 综合评价与推荐

**综合交付首选 `gptweb × gpt-6pro`；若优先考虑最终数值精度，首选 `harnessL × ds-4.1flashmax`。** 这是对现有评审的归纳，具体选择取决于使用目标：

| 使用目标 | 推荐 Harness＋LLM | 现有评审支持 |
|---|---|---|
| 完整、严谨且便于操作的科学实验室 | **gptweb × gpt-6pro**（ChatGPT 网页版） | 四份综合榜记录均为第一，其中一次并列；单位与坐标说明、科学验证和可视化交付较完整。 |
| 优先检验轨迹精度与自适应求解结果 | **harnessL × ds-4.1flashmax** | 四份科学榜均在前二，两份列第一；高阶固定步与自适应方法在所测工况中取得了较强的数值结果。 |
| 综合与科学表现都稳定的另一选择 | **Codex × 6astra-xhigh** | 四份综合榜均在前二，科学榜均在前三（含并列）；方程、单位定义和独立参考核验得到多份评审肯定。 |

多份评审认可领先作品的基本运动方程、Jacobi 常数和平衡点计算；主要差距出现在**轨迹误差、长期数值行为、边界处理，以及演示中的物理声明能否复算**。尤其是 GPT Web 与 Codex，两份数值复评在对齐条件后发现其共同 RK4 方法结果基本一致，不能仅凭默认演示读数不同判断谁的方程错了。比较轨迹前应对齐初值、单位、参考系与积分设置，再与独立参考解核对。[Codex 数值复评](reviews/2026-09-09/science-final/README.md) · [GPT Web 数值复评](reviews/2026-09-09/gptweb-gpt-6-astra-pro/science-final/SCIENCE_REVIEW.md)

**面向重视数学与天体力学的传统专家团队，本页建议优先送审 DS 的数值结果，同时提供 GPT Web 作为完整科学演示的对照。** 科学首选并未形成一致意见：Codex 与 GPT Web 评审选 DS；[Kimi 评审](reviews/2026-09-09/kimiweb-k3-swarmmax/README.md#four) 更重视其规定步长、长期守恒与边界测试下的表现，选 ZCode Linux × GLM-5.3max；[ZCode／GLM 评审](reviews/2026-09-09/zcode-glm-5.3max-win/science-final/README.md) 更重视单位闭合、动力学演示和科学解释，选 GPT Web。GLM Linux 只进入了 Kimi 的科学终评，其他评审未对它做同一阶段的比较。首选随测试与权重变化，少量分差不足以证明普遍优势。

> **如何读这些结论：** 四份记录分别保留原始分数。GPT Web 评审的十项评分在复核后沿用了已有统一榜，不能把相同分数当成两次独立估计，见[评分来源说明](reviews/2026-09-09/gptweb-gpt-6-astra-pro/README.md#gptweb-gpt-6-astra-pro-ten)。科学榜的指标、权重和入围集合不同（Kimi 为 /80，其余为 /100），本页不直接平均总分，也不把这些 AI 评审解释为人类专家投票概率。

## 各位专家的评分与排名

卡片上方注明的是**评审者的模型与平台**，卡片内列出的是**参赛组合**；点击卡片或下方链接可查看单项排名、扣分理由和数值依据。后续评审也按“十项综合榜＋四强科学榜”展示。

'''
outputs={}
for expert in experts:
    readme+=f'### {expert["id"]}\n\n'
    readme+=f'**评审平台：{expert["platform"]} · 评审模型：{expert["model"]}**\n\n'
    for kind in ['ten','four']:
        path=f'assets/leaderboards/{expert["id"]}-{kind}.svg'
        title='十项综合评分与排名' if kind=='ten' else expert.get('four_alt','四强科学评分与排名')
        outputs[ROOT/path]=svg(expert,kind)
        readme+=f'<a href="{expert[kind+"_link"]}"><img src="{path}" width="420" alt="{expert["id"]} · {title}"></a> '
    readme=readme.rstrip()+f'\n\n[十项具体评分与单项排名]({expert["ten_link"]}) · [四强具体评分与推荐]({expert["four_link"]})\n\n'
outputs[ROOT/'README.md']=readme.rstrip()+'\n'
for path,content in outputs.items():
    if '--check' in sys.argv:assert path.read_text(encoding='utf-8')==content, str(path)
    else:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(content,encoding='utf-8',newline='\n')
print('Validated 4 experts, 8 cards, original published scores/ranks, and explicit science denominators.')
