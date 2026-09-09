"""Independent SciPy DOP853 check, without importing any submitted code."""
import json, sys, platform
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import solve_ivp

source=Path(sys.argv[1]);data=json.loads(source.read_text(encoding='utf-8'))
result={'method':'DOP853','scipy':scipy.__version__,'python':platform.python_version(),
        'rtol':2.3e-14,'atol':2e-15,'submissions':[]}
for sub in data['submissions']:
    mu=sub['mu']
    def rhs(t,s):
        x,y,vx,vy=s
        a=np.array([x+mu,y]); b=np.array([x-1+mu,y])
        g=-(1-mu)*a/np.linalg.norm(a)**3-mu*b/np.linalg.norm(b)**3
        return [vx,vy,x+2*vy+g[0],y-2*vx+g[1]]
    initial=[.6,.2,-.1,.35]
    refs=[solve_ivp(rhs,[0,.4],initial,method='DOP853',rtol=2.3e-14,atol=2e-15,max_step=h) for h in [.01,.005]]
    assert all(r.success and r.t[-1]==.4 for r in refs)
    ref=refs[-1].y[:,-1]
    r={'id':sub['id'],'mu':mu,'state':ref.tolist(),'referenceRefinementDifference':float(np.linalg.norm(ref-refs[0].y[:,-1])),'methods':{}}
    # A second formulation: moving primaries in inertial Cartesian coordinates.
    # It contains neither centrifugal nor Coriolis acceleration.
    def inertial_rhs(t,s):
        c,si=np.cos(t),np.sin(t)
        re=np.array(s[:2])+mu*np.array([c,si])
        rm=np.array(s[:2])-(1-mu)*np.array([c,si])
        g=-(1-mu)*re/np.linalg.norm(re)**3-mu*rm/np.linalg.norm(rm)**3
        return [s[2],s[3],g[0],g[1]]
    x,y,u,v=initial
    inertial=solve_ivp(inertial_rhs,[0,.4],[x,y,u-y,v+x],method='DOP853',rtol=2.3e-14,atol=2e-15,max_step=.005)
    assert inertial.success
    c,si=np.cos(.4),np.sin(.4);R=np.array([[c,si],[-si,c]])
    q=R@inertial.y[:2,-1];p=R@inertial.y[2:,-1]
    converted=np.array([q[0],q[1],p[0]+q[1],p[1]-q[0]])
    r['inertialFormulationCrosscheck']={'rotatingEndpoint':converted.tolist(),'stateDifference':float(np.linalg.norm(converted-ref))}
    for name,m in sub['methods'].items():
        if 'error' in m:continue
        errors=[float(np.linalg.norm(np.array(run['state'])-ref)) for run in m['convergence']['runs']]
        r['methods'][name]={'stepSizes':[x['h'] for x in m['convergence']['runs']], 'stateErrors':errors,'orders':[float(np.log2(a/b)) for a,b in zip(errors,errors[1:])]}
    if sub['id']=='ds':r['gbsEndpointError']=float(np.linalg.norm(np.array([sub['adaptiveProbes'][0]['result']['state'][x] for x in ['x','y','vx','vy']])-ref))
    if sub['id']=='qwen':r['dopriEndpointError']=float(np.linalg.norm(np.array(sub['adaptiveProbes'][0]['result']['s'])-ref))
    result['submissions'].append(r)
Path(sys.argv[2]).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(result,ensure_ascii=False))
