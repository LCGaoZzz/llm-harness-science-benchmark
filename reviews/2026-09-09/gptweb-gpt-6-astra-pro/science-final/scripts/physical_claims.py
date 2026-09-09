import json,math,pathlib,hashlib
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar
from scipy.signal import find_peaks
from playwright.sync_api import sync_playwright
B=pathlib.Path(__file__).resolve().parents[1] / 'audit'; O=B.parent; E=json.loads((B/'entries.json').read_text());AD=(B/'scripts/adapters.js').read_text();keys=['gptweb_gpt-6pro','codex_6astra-xhigh','harnessL_ds-4.1flashmax','zcode_glm-5.3max']
def f(mu,s):
 x,y,vx,vy=s;r1=np.hypot(x+mu,y);r2=np.hypot(x-1+mu,y)
 return np.array([vx,vy,2*vy+x-(1-mu)*(x+mu)/r1**3-mu*(x-1+mu)/r2**3,-2*vx+y-(1-mu)*y/r1**3-mu*y/r2**3])
def C(mu,s):
 x,y,vx,vy=s;return x*x+y*y+2*(1-mu)/np.hypot(x+mu,y)+2*mu/np.hypot(x-1+mu,y)-vx*vx-vy*vy
out={}
with sync_playwright() as p:
 br=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for key in keys:
  pg=br.new_page();pg.route('**/*',lambda r:r.abort());pg.set_content((B/E[key]['html']).read_text());pg.wait_for_timeout(250);info=pg.evaluate(AD,key);mu=info['mu']
  presets=pg.evaluate('''key=>{const a=s=>Array.isArray(s)?s:[s.x,s.y,s.vx,s.vy];if(key.startsWith('zcode'))return Object.fromEntries(['l4','l1','earth','flyby'].map(k=>[k,presetIC(k,app.model)]));if(key.startsWith('harnessL'))return Object.fromEntries(CR3BP.presets(CR3BP.MU_EARTH_MOON).map(p=>[p.id,a(p.state)]));return Object.fromEntries(Object.entries(typeof CR3BP.presets==='function'?CR3BP.presets():CR3BP.presets).map(([k,p])=>[k,p.state]));}''',key)
  # gpt API presets may contain a different state property; assert at input.
  assert all(len(v)==4 for v in presets.values()),presets
  w2=(1-np.sqrt(1-27*mu*(1-mu)))/2; periods=[2*np.pi/np.sqrt(w2),2*np.pi/np.sqrt(1-w2)]
  data={'mu':mu,'linear_L4_periods_TU':periods,'presets':presets};out[key]=data
  s0=presets.get('flyby',presets.get('moon',presets.get('3')));print('PRESETS',key,presets,flush=True);RM=1737.4/384400;RE=6371/384400
  def em(t,s):return np.hypot(s[0]-1+mu,s[1])-RM
  def ee(t,s):return np.hypot(s[0]+mu,s[1])-RE
  em.terminal=ee.terminal=True;em.direction=ee.direction=-1
  def radial(t,s):return (s[0]-1+mu)*s[2]+s[1]*s[3]
  radial.direction=1
  def cross(t,s):return np.hypot(s[0]-1+mu,s[1])-.1
  sol=solve_ivp(lambda t,s:f(mu,s),(0,10),s0,method='DOP853',rtol=2.3e-14,atol=1e-15,max_step=.002,events=[em,ee,radial,cross],dense_output=True)
  times=[0,float(sol.t[-1])]+sol.t_events[2].tolist(); vals=[np.hypot(sol.sol(t)[0]-1+mu,sol.sol(t)[1])for t in times];ix=int(np.argmin(vals))
  fly={'T':float(sol.t[-1]),'terminated':sol.status==1,'min_moon_distance_DU':float(vals[ix]),'min_moon_time_TU':times[ix],'C0':C(mu,s0),'periselene_times':sol.t_events[2].tolist(),'cross_rmoon_point1':sol.t_events[3].tolist()}
  def quantities(s):
   x,y,vx,vy=s;v=np.array([vx-y,vy+x]);vg=np.array([vx-y,vy+x+mu]);r1=np.hypot(x+mu,y);r2=np.hypot(x-1+mu,y)
   return {'state':s.tolist(),'moon_distance':float(r2),'barycentric_inertial_speed':float(np.linalg.norm(v)),'barycentric_inertial_energy':float(.5*v@v-(1-mu)/r1-mu/r2),'geocentric_two_body_energy':float(.5*vg@vg-(1-mu)/r1)}
  ts=sol.t_events[3]
  if len(ts)>=2:
   qi=quantities(sol.sol(ts[0]));qo=quantities(sol.sol(ts[1]));fly['same_radius_pair']={'in':qi,'out':qo,'delta_barycentric_inertial_speed':qo['barycentric_inertial_speed']-qi['barycentric_inertial_speed'],'delta_geocentric_two_body_energy':qo['geocentric_two_body_energy']-qi['geocentric_two_body_energy']}
  else:fly['same_radius_pair']=None
  fly['first_and_last']={'in':quantities(np.array(s0)),'out':quantities(sol.y[:,-1])}
  data['flyby']=fly
  # Final preset L4 (not inferred linearisation) slow-angle motion measured from a trajectory.
  s0=presets['l4'];lp=np.array([.5-mu,math.sqrt(3)/2,0,0]);J=np.array([[0,0,1,0],[0,0,0,1],[.75,3*math.sqrt(3)/4*(1-2*mu),0,2],[3*math.sqrt(3)/4*(1-2*mu),2.25,-2,0]])
  ew,ev=np.linalg.eig(J);i=np.argmin(np.abs(ew-1j*math.sqrt(w2)));inv=np.linalg.inv(ev);s=solve_ivp(lambda t,s:f(mu,s),(0,300),s0,method='DOP853',rtol=2.3e-14,atol=1e-15,max_step=.03,dense_output=True);t=np.arange(0,300,.02);y=s.sol(t);mode=(inv@(y-lp[:,None]))[i];phase=np.unwrap(np.angle(mode));fit=np.polyfit(t,phase,1)
  # Low-frequency y maxima with >=15 TU peak separation; diagnostic only for finite-amplitude orbit.
  peaks,_=find_peaks(y[1],distance=750)
  data['L4_actual']={'max_deviation_DU':float(np.max(np.linalg.norm(y[:2]-lp[:2,None],axis=0))),'slow_mode_phase_period_TU':float(2*np.pi/abs(fit[0])),'y_peak_periods_TU':np.diff(t[peaks]).tolist(),'max_abs_dC':float(max(abs(C(mu,y[:,k])-C(mu,s0))for k in range(0,len(t),10)))}
  print(key, 'periods',periods,'nonlinear',data['L4_actual'],'fly',fly,flush=True)
  (O/'physical_claims.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));pg.close()
 br.close()
