import pathlib,json,hashlib
import numpy as np
from playwright.sync_api import sync_playwright
B=pathlib.Path(__file__).resolve().parents[1] / 'audit';O=B.parent;E=json.loads((B/'entries.json').read_text());AD=(B/'scripts/adapters.js').read_text();D=json.loads((O/'new_measurements.json').read_text());out={}
with sync_playwright() as p:
 br=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for key,d in D.items():
  pg=br.new_page();pg.route('**/*',lambda r:r.abort());pg.set_content((B/E[key]['html']).read_text());pg.wait_for_timeout(100);pg.evaluate(AD,key)
  s=d['tests']['Earth']['spec'];ref=np.array(d['tests']['Earth']['reference']['state'])
  vals=pg.evaluate('''s=>{const a=__AUDIT__,out=[];for(const h of [.0001,.00005]){let v=s.s.slice(),maxDC=0,C0=a.C(v);const n=Math.round(s.T/h);for(let i=0;i<n;i++){v=a.methods.rk4(v,h);maxDC=Math.max(maxDC,Math.abs(a.C(v)-C0));}out.push({h,T:s.T,method:'rk4',state:v,max_abs_dC:maxDC,steps:n});}return out;}''',s)
  for r in vals:r['final_state_error_l2']=float(np.linalg.norm(np.array(r['state'])-ref))
  out[key]=vals;print(key,vals,flush=True);pg.close();(O/'refinement_check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
 br.close()
