"""Build the compact README and eight SVG cards from published expert scores."""
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
         ten=[dict(label=r['label'],score=r['final'],rank=r['rank']) for r in glm['submissions']],
         four=[dict(label=next(r['label'] for r in glm['submissions'] if r['id']==key),score=v['total'],rank=v['rank']) for key,v in glm['science_final']['scores'].items()],
         max_four=100, ten_note='十项等权 · 原评审分数', four_note='科学十项等权 · 原评审分数',
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
    if 'linux' in low:return 'ZCode · Linux', 'glm-5.3maxlinux'
    return 'ZCode · Windows', 'glm-5.3max'

def number(value):
    return f'{value:g}'

def svg(expert, kind):
    rows=expert[kind]
    assert len(rows)==(7 if kind=='ten' else (5 if expert['id'].startswith('kimi') else 4))
    maximum=100 if kind=='ten' else expert['max_four']
    assert all(0<=r['score']<=maximum and r['rank']>=1 for r in rows)
    color,tint=expert['color'],expert['tint']
    title='十项综合榜' if kind=='ten' else '四强科学榜'
    badge='10' if kind=='ten' else '4'
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="660" viewBox="0 0 600 660" role="img" aria-labelledby="title desc">',
        f'<title id="title">{expert["id"]} · {title}</title>',
        f'<desc id="desc">'+escape('；'.join(f'第 {r["rank"]} 名 {r["label"]}，{number(r["score"])} / {maximum}' for r in rows))+'</desc>',
        '<rect x="1" y="1" width="598" height="658" rx="24" fill="#FFFFFF" stroke="#DDE3EC" stroke-width="2"/>',
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
    parts += ['<path d="M28 604 H572" stroke="#E8EDF4"/>',
        f'<text x="28" y="632" fill="#64748B" font-size="15">{escape(expert[kind+"_note"])}</text>',
        '<text x="572" y="632" text-anchor="end" fill="#94A0B2" font-size="13">2026.09.09</text>', '</svg>']
    return '\n'.join(parts).replace('<svg ', '<svg font-family="Segoe UI, Microsoft YaHei, Arial, sans-serif" ',1)+'\n'

readme='# CR3BP 专家排行榜\n\n'
readme+='**10 榜**按十项标准综合评价全部作品的科学、工程与交互表现；**科学榜**只对入围作品的最终数学、物理和数值结果复评，不计界面或中间工程材料。\n\n'
outputs={}
for expert in experts:
    readme+=f'## {expert["id"]}\n\n'
    readme+=f'**评审平台：{expert["platform"]} · 评审模型：{expert["model"]}**\n\n'
    for kind in ['ten','four']:
        path=f'assets/leaderboards/{expert["id"]}-{kind}.svg'
        title='十项综合评分与排名' if kind=='ten' else '四强科学评分与排名'
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
