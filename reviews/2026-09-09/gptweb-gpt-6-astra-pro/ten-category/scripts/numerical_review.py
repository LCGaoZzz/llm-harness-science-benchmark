"""Independent, read-only comparison of the original seven HTML numerical kernels.
Kimi alone requires a diagnostic copy exposing references from its private closure;
no numerical function is replaced. Browser smoke evidence uses unaltered originals.
"""
import json, pathlib, time, math, hashlib
import numpy as np
from scipy.integrate import solve_ivp
from playwright.sync_api import sync_playwright
B=pathlib.Path(__file__).resolve().parents[1]; entries=json.loads((B/'entries.json').read_text())
AD=(B/'scripts/adapters.js').read_text()
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
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for key,e in entries.items():
  out={'key':key,'html_sha256':e['sha256']};ctx=browser.new_context(viewport={'width':1440,'height':1000});ctx.route('**/*',lambda r:r.abort());pg=ctx.new_page();logs=[];errs=[];pg.on('console',lambda m:logs.append({'type':m.type,'text':m.text}));pg.on('pageerror',lambda ex:errs.append(str(ex)))
  try:
   text=(B/e['html']).read_text();assert hashlib.sha256((B/e['html']).read_bytes()).hexdigest()==e['sha256']
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
   out['console']=logs;out['page_errors']=errs;out['complete']=True
  except Exception as ex:out['complete']=False;out['error']=str(ex)
  (B/'evidence'/f'{key}-numerical.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False))
  print(key,'complete',out['complete'],out.get('error',''),flush=True)
  if out.get('methods'):
   for n,m in out['methods'].items():print(' ',n,'p',m['convergence'][-1].get('observed_order'),'L4max',m['long_runs'][0]['max_abs_dC'],'symp',m['symplectic'][0].get('canonical_defect_maxnorm'),flush=True)
  ctx.close()
 browser.close()
