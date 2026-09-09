"""Render the supplied expert's 10+4 record without modifying source packages.

--check verifies archive integrity, scores, rankings, selection, and generated text.
This does not rerun the scientific experiments in the imported packages.
"""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import sys

review = Path(__file__).resolve().parent
repo = review.parents[2]
meta = json.loads((review / 'review.json').read_text(encoding='utf-8'))
assert meta['reviewer_id'] == 'gptweb-gpt-6-astra-pro'
assert meta['review_format'] == '10+4' and meta['status'] == 'complete'
assert meta['ten_category_review']['independent_new_point_estimates'] is False
ten = json.loads((review / meta['ten_category_review']['scores']).read_text(encoding='utf-8'))
science = json.loads((review / meta['top_four_science_review']['scores']).read_text(encoding='utf-8'))
entries = json.loads((review / 'ten-category/entries.json').read_text(encoding='utf-8'))
assert ten['reviewed_source_commit'] == science['reviewed_source_commit'] == meta['reviewed_source_commit']
assert len(ten['criteria']) == 10 and len(ten['rows']) == len(entries) == 7
assert len(science['rows']) == 4
assert [c['max'] for c in science['criteria']] == meta['top_four_science_review']['weights'] == [30, 35, 25, 10]

def rank(score, values):
    return 1 + sum(value > score for value in values)

for row in ten['rows']:
    assert len(row['scores']) == 10 and all(type(v) is int and 0 <= v <= 10 for v in row['scores'])
    assert sum(row['scores']) == row['total'] and row['caps'] == []
    assert row['rank'] == rank(row['total'], [r['total'] for r in ten['rows']])
    assert row['criterion_ranks'] == [rank(v, [r['scores'][i] for r in ten['rows']]) for i, v in enumerate(row['scores'])]
for row in science['rows']:
    assert len(row['scores']) == len(row['reasons']) == len(science['criteria'])
    assert all(type(v) is int and 0 <= v <= c['max'] for v, c in zip(row['scores'], science['criteria']))
    assert sum(row['scores']) == row['total']
    assert row['rank'] == rank(row['total'], [r['total'] for r in science['rows']])
lookup = {key.replace('_', '-'): key for key in entries}
assert {lookup[r['label']] for r in ten['rows'] if r['rank'] <= 4} == {r['id'] for r in science['rows']}

for archive in meta['original_archives']:
    path = review / archive['path']
    assert path.stat().st_size == archive['bytes']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == archive['sha256']
    with ZipFile(path) as z:
        names = z.namelist()
        assert len(names) == len(set(names)) == archive['validation']['archive_members_preserved']
        manifest = {line.split(None, 1)[1].strip(): line.split(None, 1)[0] for line in z.read('SHA256SUMS').decode().splitlines() if line.strip()}
        assert set(manifest) == set(names) - {'SHA256SUMS'}
        assert len(manifest) == archive['validation']['manifest_files_verified']
        for name in names:
            assert (review / archive['extracted_to'] / name).read_bytes() == z.read(name), name
            if name in manifest:
                assert hashlib.sha256(z.read(name)).hexdigest() == manifest[name], name

def body(prefix):
    source = meta['ten_category_review']['score_source_commit']
    base = 'https://github.com/LCGaoZzz/llm-harness-science-benchmark/blob/'
    result = '<a id="gptweb-gpt-6-astra-pro-ten"></a>\n\n### 10：十项单项排名与综合总榜\n\n'
    result += f'**评分来源：独立执行复核后，保留既有统一榜 [`{source[:7]}`]({base}{source}/README.md)。** '
    result += '原包明确说明这不是另一套独立分值估计；本记录保留这一来源关系，不把相同分数当作两次独立评分。'
    result += f'[原包说明]({prefix}ten-category/README.md) · [独立复核报告]({prefix}{meta["ten_category_review"]["report"]}) · '
    result += f'[原始十项分数]({prefix}{meta["ten_category_review"]["scores"]}) · [原有 70 项理由]({base}{source}/reviews/2026-09-09/README.md)。\n\n'
    result += '十项各 10 分，等权求和；本包七份均无封顶。同分采用竞赛排名，表内同分行的先后不表示优劣。\n\n'
    result += '#### 综合总排名\n\n| 排名 | 参赛组合 | 原始合计 /100 | 封顶 | 最终得分 /100 |\n|---:|---|---:|---|---:|\n'
    for row in sorted(ten['rows'], key=lambda r: r['rank']):
        result += f'| {row["rank"]} | {row["label"]} | {row["total"]} | 无 | **{row["total"]}** |\n'
    for i, name in enumerate(ten['criteria']):
        result += f'\n#### {i + 1}. {name}\n\n| 排名 | 参赛组合 | 得分 /10 |\n|---:|---|---:|\n'
        for row in sorted(ten['rows'], key=lambda r: (-r['scores'][i], r['label'])):
            result += f'| {row["criterion_ranks"][i]} | {row["label"]} | {row["scores"][i]} |\n'
    result += '\n<a id="gptweb-gpt-6-astra-pro-four"></a>\n\n### 4：前四名纯科学终评\n\n'
    result += '本部分是该专家的新科学评分，入选四份与上述综合榜前四名一致，入选边界无同分。'
    result += '权重为数学正确性 **30**、数值结果质量 **35**、物理结果与科学解释 **25**、无效科学结果控制 **10**；'
    result += '与 `codex-gpt-6-astra-xhigh` 样例的五维权重不同，分数不直接平均。\n\n'
    result += '| 排名 | 参赛组合 | 数学 /30 | 数值 /35 | 物理结果与科学解释 /25 | 无效结果控制 /10 | 科学总分 /100 |\n'
    result += '|---:|---|---:|---:|---:|---:|---:|\n'
    for row in science['rows']:
        result += f'| {row["rank"]} | {row["label"]} | ' + ' | '.join(map(str, row['scores'])) + f' | **{row["total"]}** |\n'
    result += '\n**该专家推荐 harnessL × ds-4.1flashmax；GPT Web 与 Codex 并列第二。** '
    result += '原报告认为 DS 的高阶固定步方法与自适应 GBS 在所测场景中提供了较强数值结果；'
    result += '也明确指出四份产物在足够小的步长下均可达到高精度，1 分差不代表统计显著性或专家投票概率。'
    result += '报告未因界面、工程组织或中间文件缺失扣科学分。\n\n'
    result += f'[原始科学结论与限制]({prefix}{meta["top_four_science_review"]["report"]}) · '
    result += f'[科学评分及逐项理由]({prefix}{meta["top_four_science_review"]["scores"]})。\n'
    return result

header = f'**评审者：`{meta["reviewer_id"]}` · {meta["date"]} · 状态：10+4 已完整收录。**\n\n'
header += '评审者身份由仓库所有者在导入请求中指定，与参赛组合 `gptweb-gpt-6pro` 分开记录。'
header += f'两部分均评阅源快照 [`{meta["reviewed_source_commit"][:7]}`](https://github.com/LCGaoZzz/llm-harness-science-benchmark/tree/{meta["reviewed_source_commit"]})。\n\n'
local = '# gptweb-gpt-6-astra-pro：10+4 评审记录\n\n' + header + body('')
local += '\n## 原始材料与导入核对\n\n'
for archive in sorted(meta['original_archives'], key=lambda a: -int(a['part'])):
    local += f'- **{archive["part"]} 部分**：[原始 ZIP]({archive["path"]}) · [原样展开文件]({archive["extracted_to"]}/) · [原校验清单]({archive["extracted_to"]}/SHA256SUMS)。'
    local += f' {archive["validation"]["archive_members_preserved"]} 个文件逐字节保留，{archive["validation"]["manifest_files_verified"]} 个清单哈希通过。\n'
local += '- [导入元数据](review.json)：署名、评分来源关系、原包 SHA-256、源 HTML 对应关系及核对范围。\n'
local += '- 四强证据：[主要数值记录](science-final/new_measurements.json)、[物理声明核对](science-final/physical_claims.json)、[步长敏感性检查](science-final/refinement_check.json)。\n\n'
local += '导入时，十项包的七份 HTML 与四强包的四份 HTML 均与指定 Git 快照一致；Kimi 的原始 HTML 从该快照的原提交 ZIP 中核对。'
local += '已核对全部分数合计、单项及总榜并列排名、四强入选名单。此次导入未重新运行科学实验，原报告中的实验结论归属于相应评审记录。原包保留提交时的说明与路径；当前多专家展示以本记录和仓库索引为准。\n\n'
local += '本记录按两份原包生成，未重新评分。运行 `python reviews/2026-09-09/gptweb-gpt-6-astra-pro/render.py --check` 可核对原包完整性和榜单一致性。\n\n'
local += '[返回仓库专家索引](../../../README.md)\n'

root = (repo / 'README.md').read_text(encoding='utf-8')
start = '<!-- BEGIN REVIEW gptweb-gpt-6-astra-pro -->'
end = '<!-- END REVIEW gptweb-gpt-6-astra-pro -->'
assert root.count(start) == root.count(end) == 1
prefix, remainder = root.split(start, 1)
old, suffix = remainder.split(end, 1)
block = '## gptweb-gpt-6-astra-pro：10+4 评审记录\n\n' + header
block += '[完整署名记录与原始材料](reviews/2026-09-09/gptweb-gpt-6-astra-pro/README.md)。\n\n'
block += body('reviews/2026-09-09/gptweb-gpt-6-astra-pro/')
outputs = {review / 'README.md': local, repo / 'README.md': prefix + start + '\n' + block.rstrip() + '\n' + end + suffix}
for path, content in outputs.items():
    if '--check' in sys.argv:
        assert path.read_text(encoding='utf-8') == content, 'Generated document is stale: ' + str(path)
    else:
        path.write_text(content, encoding='utf-8', newline='\n')
print('Validated both immutable archives, 86 scores, all rankings, top-four selection, score lineage metadata, and complete 10+4 displays.')
