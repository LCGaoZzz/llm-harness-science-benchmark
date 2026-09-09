"""Independent Python equations + SciPy DOP853, no JavaScript RHS reused."""
import json
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import solve_ivp

root = Path(__file__).resolve().parent
mu = 0.01215058560962404

def rhs(t, s):
    x, y, vx, vy = s
    r1 = np.hypot(x + mu, y)
    r2 = np.hypot(x - 1 + mu, y)
    ax = x + 2 * vy - (1-mu)*(x+mu)/r1**3 - mu*(x-1+mu)/r2**3
    ay = y - 2 * vx - (1-mu)*y/r1**3 - mu*y/r2**3
    return [vx, vy, ax, ay]

results = []
for case in json.loads((root / 'reference-input.json').read_text()):
    ref = solve_ivp(rhs, (0, case['T']), case['initial'], method='DOP853',
                    rtol=3e-14, atol=3e-15, t_eval=case['times'])
    cross = solve_ivp(rhs, (0, case['T']), case['initial'], method='DOP853',
                      rtol=3e-13, atol=3e-14, t_eval=case['times'])
    errors = np.linalg.norm(np.array(case['states']) - ref.y.T, axis=1)
    ref_check = np.max(np.linalg.norm(ref.y.T - cross.y.T, axis=1))
    results.append(dict(key=case['key'], method=case['method'], h=case['h'], T=case['T'],
                        max_state_error=float(np.max(errors)), final_state_error=float(errors[-1]),
                        reference_tolerance_difference=float(ref_check), threshold=case['tolerance'],
                        pass_check=bool(ref.success and cross.success and np.max(errors)<case['tolerance'] and ref_check<1e-8)))
out = dict(scipy=scipy.__version__, solver='DOP853', samples_per_case=101, rtol=3e-14, atol=3e-15,
           pass_check=all(r['pass_check'] for r in results), results=results)
(root / 'independent-reference.json').write_text(json.dumps(out, indent=2))
print(json.dumps(out))
