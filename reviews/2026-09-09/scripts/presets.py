"""Independent physical check of the initial states selected by actual UI buttons.

This tests intended preset dynamics; it is not a measurement of the submitted
integrator and does not replace the separate numerical and browser evidence.
"""
import json,sys
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
folder=Path(sys.argv[1]);nums=json.loads((folder/'numerical.json').read_text())
mus={s['id']:s['mu'] for s in nums['submissions']}
uis=json.loads((folder/'interactions.json').read_text(encoding='utf-8'))
output=[]
for sub in uis['submissions']:
    mu=mus[sub['id']]
    def rhs(t,s):
        x,y,vx,vy=s;r1=np.hypot(x+mu,y);r2=np.hypot(x-1+mu,y)
        return [vx,vy,x+2*vy-(1-mu)*(x+mu)/r1**3-mu*(x-1+mu)/r2**3,y-2*vx-(1-mu)*y/r1**3-mu*y/r2**3]
    def earth(t,s):return np.hypot(s[0]+mu,s[1])-6371/384400
    def moon(t,s):return np.hypot(s[0]-1+mu,s[1])-1737.4/384400
    earth.terminal=moon.terminal=True
    r={'id':sub['id'],'presets':[]}
    for preset in sub['checks']['presets']:
        name=preset['name'];s0=preset['before'].get('originalInitial',preset['before']['s']);T=10 if '引力辅助' in name else 2
        sol=solve_ivp(rhs,[0,T],s0,method='DOP853',rtol=1e-11,atol=1e-13,max_step=.005,events=[earth,moon],dense_output=True)
        t=np.linspace(0,sol.t[-1],max(2,int(sol.t[-1]/.0005)+1));s=sol.sol(t)
        rm=np.hypot(s[0]-1+mu,s[1]);re=np.hypot(s[0]+mu,s[1]);vi=np.hypot(s[2]-s[1],s[3]+s[0]);j=int(np.argmin(rm))
        r['presets'].append({'name':name,'initial':s0,'T_requested':T,'T_reached':float(sol.t[-1]),'success':bool(sol.success),'earthImpact':bool(len(sol.t_events[0])),'moonImpact':bool(len(sol.t_events[1])),'minMoonDU':float(rm[j]),'minMoonTime':float(t[j]),'earthDistanceRangeDU':[float(min(re)),float(max(re))],'initialInertialSpeedDU':float(vi[0]),'finalInertialSpeedDU':float(vi[-1])})
    output.append(r)
(folder/'presets-reference.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
for r in output:print(r['id'],json.dumps([p for p in r['presets'] if '引力辅助' in p['name']],ensure_ascii=True))
