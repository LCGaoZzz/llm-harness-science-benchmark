import json,pathlib,hashlib,time,math,sys
import numpy as np
from scipy.integrate import solve_ivp
from playwright.sync_api import sync_playwright
B=pathlib.Path(__file__).resolve().parents[1] / 'audit'; O=B.parent
E=json.loads((B/'entries.json').read_text()); AD=(B/'scripts/adapters.js').read_text()
KEYS=['gptweb_gpt-6pro','codex_6astra-xhigh','zcode_glm-5.3max','harnessL_ds-4.1flashmax']

def f(mu,s):
 x,y,vx,vy=s;r1=np.hypot(x+mu,y);r2=np.hypot(x-1+mu,y)
 return [vx,vy,2*vy+x-(1-mu)*(x+mu)/r1**3-mu*(x-1+mu)/r2**3,-2*vx+y-(1-mu)*y/r1**3-mu*y/r2**3]
def fi(mu,t,s):
 c=math.cos(t);z=math.sin(t);dx=s[0]+mu*c;dy=s[1]+mu*z;ex=s[0]-(1-mu)*c;ey=s[1]-(1-mu)*z;r1=math.hypot(dx,dy);r2=math.hypot(ex,ey)
 return [s[2],s[3],-(1-mu)*dx/r1**3-mu*ex/r2**3,-(1-mu)*dy/r1**3-mu*ey/r2**3]
def to_rot(s,t):
 c=math.cos(t);z=math.sin(t);x=c*s[0]+z*s[1];y=-z*s[0]+c*s[1];return np.array([x,y,c*s[2]+z*s[3]+y,-z*s[2]+c*s[3]-x])
JS=r'''spec=>{const a=window.__AUDIT__,out=[];
function stats(s){return [Math.atan2(s[1],s[0]+a.mu),Math.hypot(s[0]+a.mu,s[1]),Math.hypot(s[0]-1+a.mu,s[1])];}
for(const [method,fn] of Object.entries(a.methods))for(const h of [spec.h,spec.h/2]){
 let s=spec.s.slice(),c0=a.C(s),maxDC=0,minM=Infinity,steps=0,err=null;const N=Math.round(spec.T/h);let prev=stats(s)[0],angle=prev;
 try{for(let i=0;i<N;i++){s=fn(s,h);steps++;if(!s.every(Number.isFinite))throw Error('nonfinite');let q=stats(s),d=q[0]-prev;if(d>Math.PI)d-=2*Math.PI;if(d< -Math.PI)d+=2*Math.PI;angle+=d;prev=q[0];minM=Math.min(minM,q[2]);maxDC=Math.max(maxDC,Math.abs(a.C(s)-c0));}}catch(e){err=String(e)}
 out.push({method,h,state:s,T_reached:steps*h,steps,max_abs_dC:maxDC,minMoonDistance:minM,angle,error:err});
}
if(spec.key==='harnessL_ds-4.1flashmax')for(const rtol of [1e-13,1e-14]){
 const c=CR3BP,s=spec.s,ss={x:s[0],y:s[1],z:0,vx:s[2],vy:s[3],vz:0},atol=rtol*.001;const r=c.integrate(ss,{method:'gbs',dt:.001,T:spec.T,rtol,atol,gbsK:5,gbsSeq:'bulirsch',guard:true,collectTraj:true});let prev=stats(s)[0],angle=prev;
 for(const v of r.traj){const q=stats([v.x,v.y,v.vx,v.vy])[0];let d=q-prev;if(d>Math.PI)d-=2*Math.PI;if(d< -Math.PI)d+=2*Math.PI;angle+=d;prev=q;}
 out.push({method:'gbs',rtol,atol,gbsK:5,gbsSeq:'bulirsch',state:[r.state.x,r.state.y,r.state.vx,r.state.vy],T_reached:r.t,steps:r.steps,forceEvals:r.evals,rejections:r.rejects,max_abs_dC:r.driftMax*Math.abs(r.C0),angle,error:r.finished?null:r.status});
}
return out;}'''
all_results={}
with sync_playwright() as p:
 br=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for key in KEYS:
  e=E[key];text=(B/e['html']).read_bytes();assert hashlib.sha256(text).hexdigest()==e['sha256'];ctx=br.new_context();ctx.route('**/*',lambda r:r.abort());pg=ctx.new_page();pg.set_content(text.decode());pg.wait_for_timeout(500);info=pg.evaluate(AD,key);mu=info['mu'];data={'key':key,'sha256':e['sha256'],'mu':mu,'tests':{}}
  specs=[{'name':'L4','s':[.51-mu,math.sqrt(3)/2,0,0],'T':500,'h':.01}, {'name':'Earth','s':[.18-mu,0,0,math.sqrt((1-mu)/.18)-.18],'T':50,'h':.001},{'name':'Lunar','s':[.983023190751,.339530631148,.364091086118,-.756469092483],'T':.8,'h':.0001}]
  for spec in specs:
   s0=spec['s'];T=spec['T'];print('run',key,spec['name'],flush=True)
   outputs=pg.evaluate(JS,{**spec,'key':key}); refs=[];ref_sols=[]
   # Two rotational reference runs, then independent inertial formulation.
   for maxstep in ([.10,.05] if spec['name']=='L4' else [.003,.0015] if spec['name']=='Earth' else [.0005,.00025]):
    sol=solve_ivp(lambda t,s:f(mu,s),(0,T),s0,method='DOP853',rtol=2.3e-14,atol=1e-15,max_step=maxstep);assert sol.success;refs.append(sol.y[:,-1]);ref_sols.append(sol)
   ii=[s0[0],s0[1],s0[2]-s0[1],s0[3]+s0[0]]
   ins=solve_ivp(lambda t,s:fi(mu,t,s),(0,T),ii,method='DOP853',rtol=2.3e-14,atol=1e-15,max_step=(.10 if spec['name']=='L4' else .003 if spec['name']=='Earth' else .0005));assert ins.success;ir=to_rot(ins.y[:,-1],T)
   ref=refs[-1];rsol=ref_sols[-1];ref_angle=float(np.unwrap(np.arctan2(rsol.y[1],rsol.y[0]+mu))[-1]);diff=float(np.linalg.norm(refs[0]-ref));idiff=float(np.linalg.norm(ir-ref));reference={'state':ref.tolist(),'rtol':2.3e-14,'atol':1e-15,'refinement_difference':diff,'inertial_crosscheck_difference':idiff,'reference_angle':ref_angle,'inertial_state_rotated_back':ir.tolist()}
   for row in outputs:
    dif=np.array(row['state'])-ref;row['final_state_error_l2']=float(np.linalg.norm(dif));row['position_error_DU']=float(np.linalg.norm(dif[:2]));row['velocity_error_VU']=float(np.linalg.norm(dif[2:]));row['phase_error_rad']=float(row['angle']-ref_angle)
   data['tests'][spec['name']]={'spec':spec,'reference':reference,'outputs':outputs}
   (O/(key+'-extra.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2));print('reference deltas',diff,idiff,flush=True)
   for r in outputs: print(r['method'],r.get('h',r.get('rtol')),'err',r['final_state_error_l2'],'dC',r['max_abs_dC'],'phase',r['phase_error_rad'],r['error'],flush=True)
  all_results[key]=data;ctx.close()
 br.close()
(O/'new_measurements.json').write_text(json.dumps(all_results,ensure_ascii=False,indent=2))
