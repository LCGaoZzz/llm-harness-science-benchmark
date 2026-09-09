"""Independent inertial-frame DOP853 comparison against the actual HTML kernel.
Requires scipy, numpy, playwright and Chromium. Does not reuse CR3BP.rhs.
Run after build.py. Reference tolerances are local controls, NOT error bounds.
"""
from pathlib import Path
import json, math, sys, hashlib
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent
HTML=P/'earth_moon_lab.html'
# Independent constants, from JPL DE440 GM file; no JS functions imported.
GE=398600.43550702266; GM=4902.80011845755; MU=GM/(GE+GM); A=1-MU
DU=384400.; TU=math.sqrt(DU**3/(GE+GM)); VU=DU/TU

def inertial_rhs(t, z):
    c=math.cos(t); s=math.sin(t)
    de=np.array([z[0]+MU*c,z[1]+MU*s])
    dm=np.array([z[0]-A*c,z[1]-A*s])
    acc=-A*de/np.linalg.norm(de)**3-MU*dm/np.linalg.norm(dm)**3
    return [z[2],z[3],acc[0],acc[1]]

def to_inertial_initial(z):
    x,y,vx,vy=z
    return [x,y,vx-y,vy+x]

def to_rotating(z,t):
    c=math.cos(t); s=math.sin(t)
    x=c*z[0]+s*z[1]; y=-s*z[0]+c*z[1]
    px=c*z[2]+s*z[3]; py=-s*z[2]+c*z[3]
    return np.array([x,y,px+y,py-x])

def reference(z,T,tight=False):
    sol=solve_ivp(inertial_rhs,[0,T],to_inertial_initial(z),method='DOP853',
                  rtol=2.3e-14 if tight else 1e-12,
                  atol=2e-15 if tight else 1e-14,
                  max_step=.02 if tight else .05)
    if not sol.success: raise RuntimeError(sol.message)
    return to_rotating(sol.y[:,-1],T),sol.nfev,len(sol.t)-1

cases=[]; console=[]; errors=[]
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=b.new_page(viewport={'width':1560,'height':1000})
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('console',lambda m:console.append({'type':m.type,'text':m.text}))
    page.set_content(HTML.read_text())
    presets=page.evaluate('CR3BP.presets()')
    for name,T in [('l4',20.),('l1',4.),('earth',10.),('flyby',1.5)]:
        p=presets[name]; s0=p['state']; ref,nfev,nref=reference(s0,T,True); loose,lf,ln=reference(s0,T)
        ref_delta=float(np.linalg.norm(ref-loose))
        for method in ['rk4','sy4']:
            # Both nominal and half steps are propagated in real browser JS.
            runs=[]
            for h in [p['h'],p['h']/2]:
                n=round(T/h)
                out=page.evaluate('(v)=>CR3BP.integrate(v.s,v.h,v.n,v.method)',{'s':s0,'h':h,'n':n,'method':method})
                diff=np.array(out['state'])-ref
                ep=float(np.linalg.norm(diff[:2])); ev=float(np.linalg.norm(diff[2:]))
                runs.append({'h':h,'n':n,'state':out['state'],'position_error_DU':ep,'position_error_km':ep*DU,
                             'velocity_error_VU':ev,'velocity_error_km_s':ev*VU,
                             'state_error_dimensionless_norm':float(np.linalg.norm(diff)),
                             'max_jacobi_drift':out['maxDrift']})
            # Preselected modest threshold: 1e-6 DU (~384 m), 1e-5 VU.
            # It is a cross-check for these cases only, not a global guarantee.
            ok=all(r['position_error_DU']<1e-6 and r['velocity_error_VU']<1e-5 for r in runs) and ref_delta<1e-7
            case={'preset':name,'method':method,'T':T,'initial':s0,'reference_state':ref.tolist(),
                  'reference_tight_loose_state_difference':ref_delta,'reference_nfev':nfev,'reference_steps':nref,
                  'runs':runs,'pass':bool(ok)}
            cases.append(case)
            print(name,method,'pos error km',*[format(r['position_error_km'],'.4g') for r in runs],
                  'ref difference',format(ref_delta,'.3g'),'PASS' if ok else 'FAIL')
    result={'scipy_version':scipy.__version__,'browser':b.version,'formulation':'Inertial Cartesian; rotating primaries; no centrifugal or Coriolis terms in reference RHS',
            'reference_method':'DOP853','tight_rtol':2.3e-14,'tight_atol':2e-15,'tight_max_step':.02,
            'loose_rtol':1e-12,'loose_atol':1e-14,'loose_max_step':.05,
            'thresholds':{'position_error_DU':1e-6,'velocity_error_VU':1e-5,'reference_difference':1e-7},
            'html_sha256':hashlib.sha256(HTML.read_bytes()).hexdigest(),
            'cases':cases,'pageErrors':errors,'console':console,'pass':all(c['pass'] for c in cases) and not errors,
            'caveat':'Local tolerances are not rigorous global error bounds. Reference tight-loose differences include phase accumulation and are only a numerical consistency estimate.'}
    (P/'validation/r11.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    b.close()
if not result['pass']: sys.exit(1)
