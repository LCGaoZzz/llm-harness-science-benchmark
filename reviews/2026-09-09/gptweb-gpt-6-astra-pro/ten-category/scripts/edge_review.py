import json,pathlib,math
import numpy as np
from scipy.integrate import solve_ivp
from playwright.sync_api import sync_playwright
B=pathlib.Path(__file__).resolve().parents[1];entries=json.loads((B/'entries.json').read_text())
probe=r'''key=>{
 const clean=o=>JSON.parse(JSON.stringify(o,(k,v)=>typeof v==='number'&&!Number.isFinite(v)?String(v):v));
 const mu=__AUDIT__.mu, cases=[{name:'NaN_input',s:[NaN,.2,0,0],h:.001},{name:'inside_physical_Earth',s:[-mu+.01,0,0,0],h:.000001},{name:'Earth_center',s:[-mu,0,0,0],h:.001},{name:'cross_Earth_fast',s:[-mu+.02,0,-100,0],h:.001},{name:'escape_R31',s:[31,0,0,0],h:.001}];
 const outputs=[];
 for(const test of cases){let result;const s=test.s.slice(),h=test.h;
  try{
   if(key.startsWith('codex')){const x=CR3BP.checkedStep(s,h,'rk4');result={state:x,committed:true};}
   else if(key.startsWith('gptweb')){const x=CR3BP.guardedStep(s,h,'rk4');result={state:x,committed:true};}
   else if(key.startsWith('harnessL_ds')){const st={x:s[0],y:s[1],z:0,vx:s[2],vy:s[3],vz:0};const z=CR3BP.integrate(st,{method:'rk4',dt:h,T:h,guard:true});result={state:z.state,t:z.t,status:z.status,message:z.message,steps:z.steps};}
   else if(key.startsWith('harnessL_qwen')){S.running=false;setIC(s);S.itg='rk4';const bad=advance(h);result={state:S.state,t:S.t,bad};}
   else if(key.startsWith('kimiweb')){const k=__AUDIT_KIMI__;k.sim.running=false;k.sim.s=s;k.sim.dt=h;k.sim.integ='rk4';k.sim.t=0;const msg=k.simStep();result={state:k.sim.s,t:k.sim.t,msg};}
   else if(key==='zcode_glm-5.3max'){const z=makeSim(app.model,s,20);const done=simStep(z,h,1,'rk4');result={state:Array.from(z.s),t:z.t,status:z.status,crashed:z.crashed,done};}
   else{sim.running=false;sim.s=s;sim.t=0;sim.status='idle';sim.nSteps=0;curDt=h;document.querySelector('#selInteg').value='rk4';const ok=stepOnce();result={state:sim.s,t:sim.t,status:sim.status,ok};}
  }catch(e){result={rejected:true,error:String(e),input_after:s};}
  outputs.push({test,...result});
 }
 return clean(outputs);
}'''
with sync_playwright() as p:
 br=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for key,e in entries.items():
  ctx=br.new_context();ctx.route('**/*',lambda r:r.abort());pg=ctx.new_page();text=(B/e['html']).read_text()
  if key.startswith('kimiweb'):text=text.replace('setTimeout(runSelfTests,50);','window.__AUDIT_KIMI__={MU,deriv,jacobi,LPTS,stepRK4,stepVerlet,runSelfTests,sim,simStep,checkState,setIC};setTimeout(runSelfTests,50);')
  pg.set_content(text);pg.wait_for_timeout(900);pg.evaluate((B/'scripts/adapters.js').read_text(),key)
  out={'key':key,'guards':pg.evaluate(probe,key)}
  if key.endswith('linux'):
   out['gl4_unconverged_scan']=pg.evaluate('''()=>{const out=[];for(const r of [.018,.02,.025,.03,.04,.05,.06,.08,.1,.15])for(const h of [.001,.002,.003,.005,.008,.01,.015,.02,.03,.05])for(const v of [0,.5,1]){const s=[-MU+r,0,0,v*Math.sqrt((1-MU)/r)-r],z=INT.gl4.step(s,h);if(!INT.gl4.failed&&INT.gl4.lastDelta>1e-8&&guard(z)===null)out.push({s,h,state:z,delta:INT.gl4.lastDelta,iters:INT.gl4.lastIters});}return out.sort((a,b)=>b.delta-a.delta).slice(0,8)}''')
   c=out['gl4_unconverged_scan'][0];out['gl4_production_acceptance']=pg.evaluate('''c=>{sim.s=c.s;sim.t=0;sim.status='idle';sim.running=false;sim.nSteps=0;curDt=c.h;$('selInteg').value='gl4';const accepted=stepOnce();return{accepted,state:sim.s,t:sim.t,status:sim.status,delta:INT.gl4.lastDelta,failed:INT.gl4.failed}}''',c)
   mu=pg.evaluate('MU');s0=c['s'];h=c['h']
   def f(t,s):
    x,y,vx,vy=s;r1=np.hypot(x+mu,y);r2=np.hypot(x-1+mu,y)
    return [vx,vy,2*vy+x-(1-mu)*(x+mu)/r1**3-mu*(x-1+mu)/r2**3,-2*vx+y-(1-mu)*y/r1**3-mu*y/r2**3]
   sol=solve_ivp(f,(0,h),s0,method='DOP853',rtol=2e-13,atol=2e-15);out['gl4_reference']={'state':sol.y[:,-1].tolist(),'success':sol.success,'error_l2':float(np.linalg.norm(np.array(c['state'])-sol.y[:,-1]))}
  if key.startswith('harnessL_qwen'):
   # Find incomplete integrations whose returned finite state passes the UI guard.
   out['dopri_incomplete_scan']=pg.evaluate('''()=>{const out=[];for(const r of [.008,.018,.03,.1,.5])for(const vx of [-1e7,-1e5,-100,0,100,1e5,1e7])for(const h of [.001,.01,.1]){const s=[-MU+r,0,vx,.1];const z=dopri(s,h,Math.min(h*.5,.02),1e-10);if(!z.ok&&z.s.every(Number.isFinite)&&Math.hypot(z.s[0]+MU,z.s[1])>=R_EARTH*.4&&Math.hypot(z.s[0]-1+MU,z.s[1])>=R_MOON*.6)out.push({s,h,result:z});}return out.slice(0,8)}''')
   if out['dopri_incomplete_scan']:
    c=out['dopri_incomplete_scan'][0];out['dopri_production_acceptance']=pg.evaluate('''c=>{setIC(c.s);S.running=false;S.itg='dopri';S.rtol=1e-10;const bad=advance(c.h);return{state:S.state,t:S.t,bad}}''',c)
  (B/'evidence'/f'{key}-edges.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(key,json.dumps(out,ensure_ascii=False)[:1600],flush=True);ctx.close()
 br.close()
