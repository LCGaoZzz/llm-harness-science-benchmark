"""Independent rotating/inertial references and physical diagnostics.

No submitted solver, self-test, or intermediate engineering file is imported.
"""
import json,sys,platform
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar

folder=Path(__file__).resolve().parent
raw=json.loads((folder/'results.json').read_text(encoding='utf-8'))
presets=json.loads((folder/'../evidence/presets-reference.json').read_text(encoding='utf-8'))
output={'python':platform.python_version(),'scipy':scipy.__version__,'rtol':2.3e-14,'atol':2e-15,'submissions':[]}
for sub in raw['submissions']:
    mu=sub['mu']
    def rhs(t,s):
        x,y,u,v=s;r=np.hypot(x+mu,y);q=np.hypot(x-1+mu,y)
        return [u,v,x+2*v-(1-mu)*(x+mu)/r**3-mu*(x-1+mu)/q**3,y-2*u-(1-mu)*y/r**3-mu*y/q**3]
    def irhs(t,s):
        c,si=np.cos(t),np.sin(t);x,y,u,v=s
        ex=x+mu*c;ey=y+mu*si;mx=x-(1-mu)*c;my=y-(1-mu)*si
        r=np.hypot(ex,ey);q=np.hypot(mx,my)
        return [u,v,-(1-mu)*ex/r**3-mu*mx/q**3,-(1-mu)*ey/r**3-mu*my/q**3]
    def cvt(s,t):
        c,si=np.cos(t),np.sin(t);R=np.array([[c,si],[-si,c]])
        q=R@s[:2];p=R@s[2:]
        return np.array([q[0],q[1],p[0]+q[1],p[1]-q[0]])
    def ref(s,T,max_step,fun=rhs):
        sol=solve_ivp(fun,[0,T],s,method='DOP853',rtol=2.3e-14,atol=2e-15,max_step=max_step)
        assert sol.success and sol.t[-1]==T
        return sol.y[:,-1]
    record={'id':sub['id'],'mu':mu,'cases':[]}
    for case in sub['cases']:
        s=case['s'];T=case['T'];mh=min(.05,case['h']*8)
        r0=ref(s,T,mh);r1=ref(s,T,mh/2)
        initial=[s[0],s[1],s[2]-s[1],s[3]+s[0]]
        inertial=cvt(ref(initial,T,mh/2,irhs),T)
        r={'name':case['name'],'state':r1.tolist(),'refinementDifference':float(np.linalg.norm(r1-r0)),
           'inertialCrossDifference':float(np.linalg.norm(r1-inertial)),'methods':{}}
        for method,runs in case['methods'].items():
            if isinstance(runs,dict):r['methods'][method]=runs;continue
            errors=[float(np.linalg.norm(np.array(run['state'])-r1)) for run in runs]
            r['methods'][method]={'h':[run['h'] for run in runs],'stateErrors':errors,
                'positionErrors':[float(np.linalg.norm(np.array(run['state'][:2])-r1[:2])) for run in runs],
                'velocityErrors':[float(np.linalg.norm(np.array(run['state'][2:])-r1[2:])) for run in runs],
                'observedOrders':[float(np.log2(a/b)) if a*b>0 else None for a,b in zip(errors,errors[1:])]}
        if 'gbs' in case:r['gbsStateError']=float(np.linalg.norm(np.array(case['gbs']['state'])-r1))
        record['cases'].append(r)
    # Linearised L4 frequencies follow directly from the independent Hessian.
    disc=np.sqrt(1-27*mu*(1-mu));freqs=np.sqrt(np.array([1-disc,1+disc])/2)
    record['L4LinearFrequencies']=freqs.tolist();record['L4LinearPeriods']=(2*np.pi/freqs).tolist()
    # Re-evaluate every supplied flyby IC using dense output and exact radius events.
    preset=next(p for p in next(p for p in presets if p['id']==sub['id'])['presets'] if '引力辅助' in p['name'])
    s=preset['initial']
    def radius(t,y):return np.hypot(y[0]-1+mu,y[1])-.18
    def earth(t,y):return np.hypot(y[0]+mu,y[1])-6371/384400
    def moon(t,y):return np.hypot(y[0]-1+mu,y[1])-1737.4/384400
    earth.terminal=moon.terminal=True
    def vI(s):return float(np.hypot(s[2]-s[1],s[3]+s[0]))
    sol=solve_ivp(rhs,[0,10],s,method='DOP853',rtol=2.3e-14,atol=2e-15,max_step=.002,events=[radius,earth,moon],dense_output=True)
    times=np.linspace(0,sol.t[-1],20001);states=sol.sol(times);radii=np.hypot(states[0]-1+mu,states[1]);j=int(np.argmin(radii))
    opt=minimize_scalar(lambda t:np.hypot(sol.sol(t)[0]-1+mu,sol.sol(t)[1]),bounds=(times[max(0,j-1)],times[min(len(times)-1,j+1)]),method='bounded',options={'xatol':1e-13})
    events=[]
    for t,y in zip(sol.t_events[0],sol.y_events[0]):
        rr=np.array([y[0]-1+mu,y[1]]);direction='outbound' if np.dot(rr,y[2:])>0 else 'inbound'
        events.append({'t':float(t),'direction':direction,'inertialSpeed':vI(y)})
    firstpair=None
    for i,e in enumerate(events[:-1]):
        if e['direction']=='inbound' and events[i+1]['direction']=='outbound':firstpair={'entry':e,'exit':events[i+1],'deltaInertialSpeed':events[i+1]['inertialSpeed']-e['inertialSpeed']};break
    record['flyby']={'initial':s,'TReached':float(sol.t[-1]),'surfaceEncounter':bool(len(sol.t_events[1])+len(sol.t_events[2])),
        'minMoonDU':float(opt.fun),'minMoonTime':float(opt.x),'sameRadiusDU':.18,'events':events,'firstForwardMatchedPair':firstpair,
        'startsInsideMeasurementRadius':bool(np.hypot(s[0]-1+mu,s[1])<.18)}
    output['submissions'].append(record)
    (folder/'reference.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(sub['id'],flush=True)
