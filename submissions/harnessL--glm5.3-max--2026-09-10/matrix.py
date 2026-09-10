#!/usr/bin/env python3
"""积分器数值矩阵 — 全部数字来自 lab.html 页面内 bench() 真实计算."""
import json, sys, time, pathlib
from playwright.sync_api import sync_playwright

FILE = sys.argv[1]
OUT = sys.argv[2]

ICS = {
    "tadpole": {"x": 0.5078494143903759, "y": 0.8660254037844386, "vx": 0.0, "vy": 0.0},
    "earth":   {"x": -0.0121505856096241 + 0.08, "y": 0.0, "vx": 0.0,
                 "vy": (0.9878494143903759 / 0.08) ** 0.5 - (-0.0121505856096241 + 0.08)},
    "assist":  {"x": 0.1078494143903759, "y": 0.0, "vx": 0.0, "vy": 3.713183179935637},
}

CONFIGS = [
    ("gbs_tol12_tadpole_T2000", "gbs", {"tol": 1e-12}, "tadpole", 2000),
    ("gbs_tol12_tadpole_T4000", "gbs", {"tol": 1e-12}, "tadpole", 4000),
    ("gbs_tol12_assist_T2000",  "gbs", {"tol": 1e-12}, "assist", 2000),
    ("imp_dt1e3_earth_T4000",   "imp", {"dt": 1e-3},   "earth", 4000),
    ("imp_dt2e3_tadpole_T4000", "imp", {"dt": 2e-3},   "tadpole", 4000),
    ("rk4_dt5e4_assist_T2000",  "rk4", {"dt": 5e-4},   "assist", 2000),
    ("rk4_dt1e3_earth_T2000",   "rk4", {"dt": 1e-3},   "earth", 2000),
    ("rk4_dt1e3_tadpole_T4000", "rk4", {"dt": 1e-3},   "tadpole", 4000),
]

rows = []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(pathlib.Path(FILE).absolute().as_uri())
    pg.wait_for_function("window.__labReady === true", timeout=20000)
    for label, integ, param, ic, T in CONFIGS:
        for Tn in sorted(set([500, T] + ([2000] if T > 2000 else []))):
            cfg = {"ic": ICS[ic], "T": Tn, "integrator": integ, "maxEvals": 4e7}
            cfg.update(param)
            t0 = time.time()
            r = pg.evaluate("c => window.__lab.bench(c)", cfg)
            rows.append({"label": label, "integrator": integ, "param": json.dumps(param),
                         "ic": ic, "T": Tn, **{k: r[k] for k in
                         ["driftRel", "evals", "steps", "wallMs", "minH", "capped", "ok", "t", "minR2", "maxR2"]}})
            print(f"{label} T={Tn}: drift={r['driftRel']:.3e} evals={r['evals']} steps={r['steps']} "
                  f"wall={r['wallMs']:.0f}ms capped={r['capped']} ok={r['ok']}", flush=True)
    b.close()

pathlib.Path(OUT).write_text(json.dumps(rows, indent=1))
print("PAGEERRORS:", errs[:5])
print("WROTE", OUT, len(rows), "rows")
