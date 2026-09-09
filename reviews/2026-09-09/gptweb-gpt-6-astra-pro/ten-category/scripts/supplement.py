import json,pathlib,math
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import root,brentq
from playwright.sync_api import sync_playwright
B=pathlib.Path(__file__).resolve().parents[1];E=json.loads((B/'entries.json').read_text());out={}
def f(mu,s):
 x,y,vx,vy=s;r1=np.hypot(x+mu,y);r2=np.hypot(x-1+mu,y)
 return np.array([vx,vy,2*vy+x-(1-mu)*(x+mu)/r1**3-mu*(x-1+mu)/r2**3,-2*vx+y-(1-mu)*y/r1**3-mu*y/r2**3])
for key in E:
 d=json.loads((B/'evidence'/f'{key}-numerical.json').read_text());mu=d['api']['mu'];L=d['api']['L'];L=L.get('points',L)if isinstance(L,dict)else L;L=[L[n]for n in ['L1','L2','L3','L4','L5']]if isinstance(L,dict)else L
 points=[([z['x'],z['y']]if isinstance(z,dict)else z)for z in L]
 expected=[[brentq(lambda x:f(mu,[x,0,0,0])[2],a,b,xtol=6e-16),0]for a,b in [(-mu+1e-7,1-mu-1e-7),(1-mu+1e-7,3),(-3,-mu-1e-7)]]+[[.5-mu,math.sqrt(3)/2],[.5-mu,-math.sqrt(3)/2]]
 out[key]={'root_max_acceleration_residual':max(float(np.linalg.norm(f(mu,[*z,0,0])[2:]))for z in points),'root_max_difference_from_independent_brent':max(float(np.linalg.norm(np.array(z)-r))for z,r in zip(points,expected))}
 if key.endswith('linux'):
  e=json.loads((B/'evidence'/f'{key}-edges.json').read_text());c=e['gl4_unconverged_scan'][0];s=np.array(c['s']);h=c['h'];a=np.array([[.25,.25-math.sqrt(3)/6],[.25+math.sqrt(3)/6,.25]])
  def residual(k):
   k=k.reshape(2,4);return (k-np.array([f(mu,s+h*sum(a[i,j]*k[j]for j in range(2)))for i in range(2)])).ravel()
  rr=root(residual,np.tile(f(mu,s),2),tol=1e-11);resnorm=float(np.max(np.abs(residual(rr.x))));step=s+h/2*(rr.x[:4]+rr.x[4:]);out[key]['independently_solved_GL4_same_step']={'root_success':bool(rr.success),'stage_residual_max':resnorm,'state':step.tolist(),'submitted_vs_converged_GL4_error':float(np.linalg.norm(step-c['state'])),'note':'DOP853 difference also includes large fixed-step truncation error; do not attribute its whole error to the nonlinear stopping condition.'}
with sync_playwright() as p:
 br=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);pg=br.new_page();pg.route('**/*',lambda r:r.abort())
 key='harnessL_ds-4.1flashmax';pg.set_content((B/E[key]['html']).read_text());pg.wait_for_timeout(800)
 r=pg.evaluate('''()=>{const mu=CR3BP.MU_EARTH_MOON,s={x:.6,y:.2,z:0,vx:-.1,vy:.35,vz:0},out=[];for(const method of Object.keys(CR3BP.METHODS)){const a=CR3BP.integrate(s,{method,dt:.01,T:.4,rtol:1e-12,atol:1e-14,gbsK:5,gbsSeq:'bulirsch',guard:true});out.push({method,state:a.state,t:a.t,steps:a.steps,evals:a.evals,rejects:a.rejects,driftMax:a.driftMax,status:a.status,finished:a.finished});}return out}''')
 ref=json.loads((B/'evidence'/f'{key}-numerical.json').read_text())['reference']['state']
 for row in r:row['independent_error_l2']=float(np.linalg.norm([row['state'][x]-ref[i]for i,x in enumerate(['x','y','vx','vy'])]))
 out[key]['all_nine_methods']=r
 key='harnessL_qwen-3.8flashxhigh';pg.set_content((B/E[key]['html']).read_text());pg.wait_for_timeout(600)
 c={'s':[.018-.0121505856004,0,-100000,.1],'h':.001}
 out[key]['dopri_outside_Earth_failure']=pg.evaluate('''c=>{S.running=false;const r=dopri(c.s,c.h,Math.min(c.h*.5,.02),1e-10);setIC(c.s);S.itg='dopri';S.rtol=1e-10;const bad=advance(c.h);return{input:c,dopri:r,ui:{state:S.state,t:S.t,bad},R_EARTH}}''',c)
 # Real button method switching, remaining two entries.
 for key,sel in [('harnessL_qwen-3.8flashxhigh','button'),('kimiweb_k3swarm-max','#intRK4,#intVerlet')]:
  pg.close();pg=br.new_page();pg.route('**/*',lambda r:r.abort())
  txt=(B/E[key]['html']).read_text()
  if key.startswith('kimiweb'):txt=txt.replace('setTimeout(runSelfTests,50);','window.__AUDIT_KIMI__={sim};setTimeout(runSelfTests,50);')
  pg.set_content(txt);pg.wait_for_timeout(700)
  out[key]['method_switching']=pg.evaluate('''key=>{const out=[];if(key.startsWith('kimi')){for(const id of ['intRK4','intVerlet']){document.getElementById(id).click();__AUDIT_KIMI__.sim.running=false;const t=__AUDIT_KIMI__.sim.t;document.getElementById('btnStep').click();out.push({id,method:__AUDIT_KIMI__.sim.integ,advances:__AUDIT_KIMI__.sim.t>t});}}else{S.running=false;for(const label of ['RK4','辛(隐式中点)','DOPRI5']){const b=[...document.querySelectorAll('button')].find(x=>x.textContent===label);b.click();const t=S.t;document.getElementById('step').click();out.push({label,method:S.itg,advances:S.t>t});}}return out}''',key)
 br.close()
(B/'evidence/supplement.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False,indent=2))
