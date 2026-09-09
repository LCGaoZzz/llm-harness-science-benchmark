"""Materialize Git blob bytes, verify submitted SHA256SUMS, unwrap Kimi's HTML.

Usage: python prepare.py REPOSITORY SCRATCH_DIRECTORY EVIDENCE_DIRECTORY
Never changes original submissions. Binary git-show output avoids checkout CRLF.
"""
from pathlib import Path
import subprocess,hashlib,json,zipfile,sys
repo,scratch,evidence=map(lambda x:Path(x).resolve(),sys.argv[1:4])
commit='ac5a306be9b29978ad6787903821b4a6a181ff01'
paths=subprocess.check_output(['git','ls-tree','-r','--name-only','-z',commit,'submissions'],cwd=repo).decode('utf-8').split('\0')
for p in filter(None,paths):
    data=subprocess.check_output(['git','show',commit+':'+p],cwd=repo)
    dest=scratch/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
records=[]
entries={'codex':'index.html','gptweb':'earth_moon_lab.html','harnessL--ds':'lab.html','harnessL--qwen':'cr3bp_lab.html','zcode':'index.html','kimiweb':'index.html'}
for d in sorted((scratch/'submissions').iterdir()):
    if not d.is_dir():continue
    checked=[]
    for row in (d/'SHA256SUMS').read_text(encoding='utf-8').splitlines():
        if not row.strip():continue
        expected,p=row.split(maxsplit=1);p=p.lstrip('*')
        actual=hashlib.sha256((d/p).read_bytes()).hexdigest()
        assert actual==expected,(d.name,p,expected,actual)
        checked.append(p)
    if d.name.startswith('kimiweb'):
        with zipfile.ZipFile(next(d.glob('*.zip'))) as z:
            raw=z.read('cr3bp-lab/index.html')
            assert raw==z.read('app/index.html')
            (d/'index.html').write_bytes(raw)
    name=next(v for k,v in entries.items() if d.name.startswith(k))
    data=(d/name).read_bytes()
    records.append({'submission':d.name,'verifiedManifestFiles':len(checked),'allManifestHashesMatch':True,'entry':name,'entryBytes':len(data),'entrySHA256':hashlib.sha256(data).hexdigest(),'zipMember':'cr3bp-lab/index.html' if d.name.startswith('kimiweb') else None})
assert len(records)==7
evidence.mkdir(parents=True,exist_ok=True)
(evidence/'integrity.json').write_text(json.dumps({'commit':commit,'submissions':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Verified',sum(r['verifiedManifestFiles'] for r in records),'original files across',len(records),'submissions')
