"""Independent DOP853 references; no submitted functions are imported."""
import json, platform
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar

folder=Path(__file__).resolve().parent
raw=json.loads((folder/'numerical.json').read_text(encoding='utf-8'))
mu=raw['mu']
def rhs(t,s):
    x,y,u,v=s;r=np.hypot(x+mu,y);q=np.hypot(x-1+mu,y)
    return [u,v,x+2*v-(1-mu)*(x+mu)/r**3-mu*(x-1+mu)/q**3,y-2*u-(1-mu)*y/r**3-mu*y/q**3]
def irhs(t,s):
    c,si=np.cos(t),np.sin(t);x,y,u,v=s
    ex=x+mu*c;ey=y+mu*si;mx=x-(1-mu)*c;my=y-(1-mu)*si
    r=np.hypot(ex,ey);q=np.hypot(mx,my)
    return [u,v,-(1-mu)*ex/r**3-mu*mx/q**3,-(1-mu)*ey/r**3-mu*my/q**3]
def back(s,t):
    c,si=np.cos(t),np.sin(t);R=np.array([[c,si],[-si,c]])
    q=R@s[:2];p=R@s[2:]
    return np.array([q[0],q[1],p[0]+q[1],p[1]-q[0]])
def ref(s,T,h,fun=rhs):
    r=solve_ivp(fun,[0,T],s,method='DOP853',rtol=2.3e-14,atol=2e-15,max_step=h)
    assert r.success and r.t[-1]==T
    return r.y[:,-1]
out={'python':platform.python_version(),'scipy':scipy.__version__,'rtol':2.3e-14,'atol':2e-15,'cases':[]}
for c in raw['cases']:
    s=c['s'];T=c['T'];h=min(.05,c['h']*8)
    a=ref(s,T,h);b=ref(s,T,h/2)
    inertial=back(ref([s[0],s[1],s[2]-s[1],s[3]+s[0]],T,h/2,irhs),T)
    row={'name':c['name'],'state':b.tolist(),'refinementDifference':float(np.linalg.norm(a-b)),
         'inertialCrossDifference':float(np.linalg.norm(inertial-b)),'methods':{},'gbs':[]}
    for m,runs in c['methods'].items():
        e=[float(np.linalg.norm(np.array(r['state'])-b)) for r in runs]
        row['methods'][m]={'h':[r['h'] for r in runs],'stateErrors':e,'orders':np.log2(np.array(e[:-1])/e[1:]).tolist()}
    for r in c['gbs']:
        row['gbs'].append({'tol':r['tol'],'ok':r['ok'],'reachedT':abs(r['t']-T)<1e-9,'stateError':float(np.linalg.norm(np.array(r['s'])-b))})
    out['cases'].append(row)
    print(c['name'],{m:r['stateErrors'][-1] for m,r in row['methods'].items()},row['gbs'],flush=True)
s=list(raw['presets']['assist']['ic'].values())
# Explicit component order; JSON object order is not part of the physical model.
s=[raw['presets']['assist']['ic'][k] for k in ['x','y','vx','vy']]
def radius(t,y):return np.hypot(y[0]-1+mu,y[1])-.18
def earth(t,y):return np.hypot(y[0]+mu,y[1])-6371/384400
def moon(t,y):return np.hypot(y[0]-1+mu,y[1])-1737.4/384400
earth.terminal=moon.terminal=True
def speed(y):return float(np.hypot(y[2]-y[1],y[3]+y[0]))
def energy(y):return float(.5*((y[2]-y[1])**2+(y[3]+y[0]+mu)**2)-(1-mu)/np.hypot(y[0]+mu,y[1]))
sol=solve_ivp(rhs,[0,14],s,method='DOP853',rtol=2.3e-14,atol=2e-15,max_step=.002,events=[radius,earth,moon],dense_output=True)
times=np.linspace(0,sol.t[-1],28001);states=sol.sol(times);radii=np.hypot(states[0]-1+mu,states[1]);j=int(np.argmin(radii))
opt=minimize_scalar(lambda t:np.hypot(sol.sol(t)[0]-1+mu,sol.sol(t)[1]),bounds=(times[max(0,j-1)],times[min(len(times)-1,j+1)]),method='bounded',options={'xatol':1e-13})
events=[]
for t,y in zip(sol.t_events[0],sol.y_events[0]):
    events.append({'t':float(t),'direction':'outbound' if np.dot([y[0]-1+mu,y[1]],y[2:])>0 else 'inbound','barycentricInertialSpeed':speed(y),'geocentricSpecificEnergy':energy(y)})
out['flyby']={'initial':s,'minMoonDU':float(opt.fun),'minMoonTime':float(opt.x),'stoppedOnSurface':sol.status==1,'eventsAtMoonRadius018':events,
 'initialGeocentricEnergy':energy(s),'geocentricEnergyAtT14':energy(sol.sol(14)),'relativeEnergyChangeAtT14':(energy(sol.sol(14))-energy(s))/abs(energy(s))}
if len(events)>=2:
    out['flyby']['matchedSpeedChange']=events[1]['barycentricInertialSpeed']-events[0]['barycentricInertialSpeed']
    out['flyby']['matchedEnergyChange']=events[1]['geocentricSpecificEnergy']-events[0]['geocentricSpecificEnergy']
freqs=np.sqrt(np.array([1-np.sqrt(1-27*mu*(1-mu)),1+np.sqrt(1-27*mu*(1-mu))])/2)
out['L4LinearPeriods']=(2*np.pi/freqs).tolist()
print('Flyby',out['flyby'])
(folder/'reference.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
