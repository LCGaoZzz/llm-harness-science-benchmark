"""Independent, read-only comparison of the original seven HTML numerical kernels.
Kimi alone requires a diagnostic copy exposing references from its private closure;
no numerical function is replaced. Browser smoke evidence uses unaltered originals.
"""
import json, pathlib, time, math, hashlib
import numpy as np
from scipy.integrate import solve_ivp
from playwright.sync_api import sync_playwright
import argparse, tempfile, zipfile, shutil, sys
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[2])
parser.add_argument('--out',type=pathlib.Path,default=pathlib.Path('independent-rerun'))
parser.add_argument('--browser',default=shutil.which('chromium') or shutil.which('chromium-browser'))
args=parser.parse_args();B=args.out.resolve();(B/'evidence').mkdir(parents=True,exist_ok=True);(B/'inputs').mkdir(exist_ok=True)
manifest={'codex_6astra-xhigh': {'submission': 'codex--6astra-xhigh--2026-09-09', 'sha256': '03f3b6c7011d7f2c757cd2265bf664256f86c8135cb5d1ae33862630cd67af92', 'filename': 'index.html'}, 'gptweb_gpt-6pro': {'submission': 'gptweb--gpt-6pro--2026-09-09', 'sha256': 'e47703cc377ef47a5c1b3f356bcdbac2b555946e0e95c598b9197fe4a5ed8a75', 'filename': 'earth_moon_lab.html'}, 'harnessL_ds-4.1flashmax': {'submission': 'harnessL--ds-4.1flashmax--2026-09-09', 'sha256': '2092ed57f0bf0b21f9aff27e72de0f01e1098ecf49885f667cc844b90f692bb6', 'filename': 'lab.html'}, 'harnessL_qwen-3.8flashxhigh': {'submission': 'harnessL--qwen-3.8flashxhigh--2026-09-09', 'sha256': 'c496e3bde81beb685d321e3e2aefbaa6949a0846c0d4634e3603f389fd4663eb', 'filename': 'cr3bp_lab.html'}, 'kimiweb_k3swarm-max': {'submission': 'kimiweb--k3swarm-max--2026-09-09', 'sha256': '4ef48f6019bb7bd8e6bfde44b8189155d1e859cb8ef951645de4491161d001ba', 'filename': 'index.html'}, 'zcode_glm-5.3max': {'submission': 'zcode--glm-5.3max--2026-09-09', 'sha256': '760b0f6e0cdee3028313adf5af875e4b1b69a83342757ea3622db87a5163d906', 'filename': 'index.html'}, 'zcode_glm-5.3maxlinux': {'submission': 'zcode--glm-5.3maxlinux--2026-09-09', 'sha256': 'fe76f3a5dec68e4a6c921793af74750b6bacaddab3401220f0dc2ab981d0e65a', 'filename': 'index.html'}}
entries={}
for key,e in manifest.items():
 directory=args.repo/'submissions'/e['submission']
 if key.startswith('kimiweb'):
  with zipfile.ZipFile(directory/'Kimi_Agent_地月三体实验室.zip') as z:
   choices=[n for n in z.namelist() if n.endswith('/index.html')]
   matches=[z.read(n) for n in choices if hashlib.sha256(z.read(n)).hexdigest()==e['sha256']]
   if not matches:raise ValueError('Kimi ZIP original HTML hash mismatch')
   content=matches[0]
 else:content=(directory/e['filename']).read_bytes()
 if hashlib.sha256(content).hexdigest()!=e['sha256']:raise ValueError(key+': source changed; review fixed snapshot, do not silently rescore new code')
 target=B/'inputs'/(key+'.html');target.write_bytes(content);entries[key]={**e,'html':str(target)}
AD=(pathlib.Path(__file__).parent/'adapters.js').read_text()
COMMON=r'''({s0,hs,T,longs,points})=>{
 const a=window.__AUDIT__, out={physics:points.map(s=>({s,rhs:a.rhs(s),C:a.C(s)})),methods:{}};
 const canon=s=>[s[0],s[1],s[2]-s[1],s[3]+s[0]],phys=z=>[z[0],z[1],z[2]+z[1],z[3]-z[0]];
 const J=[[0,0,1,0],[0,0,0,1],[-1,0,0,0],[0,-1,0,0]];
 for(const [name,fn]of Object.entries(a.methods)){
  const res={convergence:[],long_runs:[],symplectic:[]};out.methods[name]=res;
  for(const h of hs){let s=s0.slice(),err=null;try{for(let i=0;i<Math.round(T/h);i++)s=fn(s,h);}catch(e){err=String(e)}res.convergence.push({h,T,state:s,error:err});}
  for(const spec of longs){let s=spec.s.slice(),c0=a.C(s),first=0,second=0,err=null,minr=Infinity,steps=0;const N=Math.round(spec.T/spec.h);try{for(let i=0;i<N;i++){s=fn(s,spec.h);if(!s.every(Number.isFinite))throw Error('nonfinite');steps++;const d=Math.abs(a.C(s)-c0);if(i<N/2)first=Math.max(first,d);else second=Math.max(second,d);minr=Math.min(minr,Math.hypot(s[0]+a.mu,s[1]),Math.hypot(s[0]-1+a.mu,s[1]));}}catch(e){err=String(e)}res.long_runs.push({...spec,state:s,steps,first_half_max_abs_dC:first,second_half_max_abs_dC:second,max_abs_dC:Math.max(first,second),final_dC:a.C(s)-c0,min_primary_distance:minr,error:err});}
  for(const h of [.02,.01])for(const eps of [1e-5,2e-6]){
   try{const z=canon(s0),D=Array.from({length:4},()=>Array(4).fill(0));
   for(let k=0;k<4;k++){const zs=[-2,-1,1,2].map(j=>{let v=z.slice();v[k]+=j*eps;return canon(fn(phys(v),h));});for(let i=0;i<4;i++)D[i][k]=(zs[0][i]-8*zs[1][i]+8*zs[2][i]-zs[3][i])/(12*eps);}
   let defect=0;for(let i=0;i<4;i++)for(let j=0;j<4;j++){let v=-J[i][j];for(let k=0;k<4;k++)for(let l=0;l<4;l++)v+=D[k][i]*J[k][l]*D[l][j];defect=Math.max(defect,Math.abs(v));}
   const rev=fn(fn(s0,h),-h);res.symplectic.push({h,eps,canonical_defect_maxnorm:defect,reversal_error:Math.hypot(...rev.map((v,i)=>v-s0[i]))});
   }catch(e){res.symplectic.push({h,eps,error:String(e)})}
  }
 }
 return out;
}'''
def ref_rhs(mu,s):
 x,y,vx,vy=s;r1=np.hypot(x+mu,y);r2=np.hypot(x-1+mu,y)
 return np.array([vx,vy,2*vy+x-(1-mu)*(x+mu)/r1**3-mu*(x-1+mu)/r2**3,-2*vx+y-(1-mu)*y/r1**3-mu*y/r2**3])
def ref_c(mu,s):
 x,y,vx,vy=s
 return x*x+y*y+2*(1-mu)/np.hypot(x+mu,y)+2*mu/np.hypot(x-1+mu,y)-vx*vx-vy*vy
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=args.browser,headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for key,e in entries.items():
  out={'key':key,'html_sha256':e['sha256']};ctx=browser.new_context(viewport={'width':1440,'height':1000});ctx.route('**/*',lambda r:r.abort());pg=ctx.new_page();logs=[];errs=[];pg.on('console',lambda m:logs.append({'type':m.type,'text':m.text}));pg.on('pageerror',lambda ex:errs.append(str(ex)))
  try:
   text=pathlib.Path(e['html']).read_text();assert hashlib.sha256(pathlib.Path(e['html']).read_bytes()).hexdigest()==e['sha256']
   if key.startswith('kimiweb'):
    old='setTimeout(runSelfTests,50);';new='window.__AUDIT_KIMI__={MU,deriv,jacobi,LPTS,stepRK4,stepVerlet,runSelfTests,sim,simStep,checkState,setIC};'+old;assert old in text;text=text.replace(old,new,1);out['diagnostic_instrumentation']='Added one reference-only export statement before original setTimeout(runSelfTests,50); numerical source unchanged.'
   pg.set_content(text,wait_until='load');pg.wait_for_timeout(1200)
   info=pg.evaluate(AD,key);out['api']=info;mu=info['mu'];assert 0.01<mu<0.02,(key,mu)
   s0=[.6,.2,-.1,.35];T=.4
   refs=[]
   for rt,at in [(2e-13,2e-15),(2.3e-14,1e-15)]:
    sol=solve_ivp(lambda t,s:ref_rhs(mu,s),(0,T),s0,method='DOP853',rtol=rt,atol=at);assert sol.success;refs.append(sol.y[:,-1])
   out['reference']={'solver':'scipy.integrate.solve_ivp DOP853','rtol':2.3e-14,'atol':1e-15,'state':refs[1].tolist(),'reference_refinement_difference':float(np.linalg.norm(refs[0]-refs[1]))}
   points=[[.6,.2,-.1,.35],[.2,-.4,.7,-.9],[1.1,.3,-.2,.1],[-.7,.4,.11,-.22],[.5-mu,math.sqrt(3)/2,0,0]]
   longs=[{'name':'L4_shared','s':[.5-mu+.01,math.sqrt(3)/2,0,0],'T':500,'h':.01},{'name':'Earth_shared','s':[-mu+.18,0,0,math.sqrt((1-mu)/.18)-.18],'T':50,'h':.001}]
   out.update(pg.evaluate(COMMON,{'s0':s0,'T':T,'hs':[.02,.01,.005,.0025],'longs':longs,'points':points}))
   for row in out['physics']:
    row['rhs_max_error']=float(np.max(np.abs(np.array(row['rhs'])-ref_rhs(mu,row['s']))));row['C_error']=float(abs(row['C']-ref_c(mu,row['s'])))
   for name,r in out['methods'].items():
    last=None
    for cr in r['convergence']:
     err=float(np.linalg.norm(np.array(cr['state'])-refs[1]));cr['independent_error_l2']=err;cr['observed_order']=math.log2(last/err) if last and err else None;last=err
   # Genuine submitted tests, not inferred from documentation.
   st=time.monotonic();out['selftest_result']=pg.evaluate('async()=>await window.__AUDIT__.self()');out['selftest_seconds']=time.monotonic()-st;out['selftest_body_after']=pg.locator('body').inner_text()
   out['production_guard_probe']=pg.evaluate("key=>{\n const clean=o=>JSON.parse(JSON.stringify(o,(k,v)=>typeof v==='number'&&!Number.isFinite(v)?String(v):v));\n const mu=__AUDIT__.mu, cases=[{name:'NaN_input',s:[NaN,.2,0,0],h:.001},{name:'inside_physical_Earth',s:[-mu+.01,0,0,0],h:.000001},{name:'Earth_center',s:[-mu,0,0,0],h:.001},{name:'cross_Earth_fast',s:[-mu+.02,0,-100,0],h:.001},{name:'escape_R31',s:[31,0,0,0],h:.001}];\n const outputs=[];\n for(const test of cases){let result;const s=test.s.slice(),h=test.h;\n  try{\n   if(key.startsWith('codex')){const x=CR3BP.checkedStep(s,h,'rk4');result={state:x,committed:true};}\n   else if(key.startsWith('gptweb')){const x=CR3BP.guardedStep(s,h,'rk4');result={state:x,committed:true};}\n   else if(key.startsWith('harnessL_ds')){const st={x:s[0],y:s[1],z:0,vx:s[2],vy:s[3],vz:0};const z=CR3BP.integrate(st,{method:'rk4',dt:h,T:h,guard:true});result={state:z.state,t:z.t,status:z.status,message:z.message,steps:z.steps};}\n   else if(key.startsWith('harnessL_qwen')){S.running=false;setIC(s);S.itg='rk4';const bad=advance(h);result={state:S.state,t:S.t,bad};}\n   else if(key.startsWith('kimiweb')){const k=__AUDIT_KIMI__;k.sim.running=false;k.sim.s=s;k.sim.dt=h;k.sim.integ='rk4';k.sim.t=0;const msg=k.simStep();result={state:k.sim.s,t:k.sim.t,msg};}\n   else if(key==='zcode_glm-5.3max'){const z=makeSim(app.model,s,20);const done=simStep(z,h,1,'rk4');result={state:Array.from(z.s),t:z.t,status:z.status,crashed:z.crashed,done};}\n   else{sim.running=false;sim.s=s;sim.t=0;sim.status='idle';sim.nSteps=0;curDt=h;document.querySelector('#selInteg').value='rk4';const ok=stepOnce();result={state:sim.s,t:sim.t,status:sim.status,ok};}\n  }catch(e){result={rejected:true,error:String(e),input_after:s};}\n  outputs.push({test,...result});\n }\n return clean(outputs);\n}",key)
   out['console']=logs;out['page_errors']=errs;out['complete']=True
  except Exception as ex:out['complete']=False;out['error']=str(ex)
  (B/'evidence'/f'{key}-numerical.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False))
  print(key,'complete',out['complete'],out.get('error',''),flush=True)
  if out.get('methods'):
   for n,m in out['methods'].items():print(' ',n,'p',m['convergence'][-1].get('observed_order'),'L4max',m['long_runs'][0]['max_abs_dC'],'symp',m['symplectic'][0].get('canonical_defect_maxnorm'),flush=True)
  ctx.close()
 browser.close()

if any(not json.loads(f.read_text()).get("complete") for f in (B/"evidence").glob("*-numerical.json")):sys.exit(1)
