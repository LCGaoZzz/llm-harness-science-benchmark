#!/usr/bin/env python3
"""CR3BP lab.html 浏览器实测 harness — 全部数字来自页面内真实计算, 无预置结果."""
import json, sys, math, time, pathlib
from playwright.sync_api import sync_playwright

FILE = sys.argv[1]
OUT = sys.argv[2]
SHOTDIR = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else None
MU = 0.0121505856096241

def earth_E(s):
    vix, viy = s[2]-s[1], s[3]+s[0]
    r1 = math.hypot(s[0]+MU, s[1])
    return 0.5*(vix*vix+viy*viy) - (1-MU)/r1

res = {"console": [], "pageerror": [], "file": FILE}
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1680, "height": 1000})
    pg.on("console", lambda m: res["console"].append(f"[{m.type}] {m.text}") if m.type == "error" else None)
    pg.on("pageerror", lambda e: res["pageerror"].append(str(e)))
    pg.goto(pathlib.Path(FILE).absolute().as_uri())
    pg.wait_for_function("window.__labReady === true", timeout=20000)

    # ---- 1) 页内自检 (10) ----
    st = pg.evaluate("window.__lab.selfTests()")
    res["selftest"] = st

    # ---- 2) bench ----
    tadpole = pg.evaluate("window.__lab.getIC()")
    L4 = pg.evaluate("window.__lab.LPTS[3]")
    benches = {}
    benches["A_gbs"] = pg.evaluate("c=>window.__lab.bench(c)", {"ic": tadpole, "T": 1000, "integrator": "gbs", "tol": 1e-12, "maxEvals": 650000})
    benches["A_rk4"] = pg.evaluate("c=>window.__lab.bench(c)", {"ic": tadpole, "T": 1000, "integrator": "rk4", "dt": 1e-3, "maxEvals": 5e6})
    benches["A_imp"] = pg.evaluate("c=>window.__lab.bench(c)", {"ic": tadpole, "T": 500, "integrator": "imp", "dt": 2e-3, "maxEvals": 5e6})
    earth_ic = {"x": -MU+0.08, "y": 0.0, "vx": 0.0, "vy": math.sqrt((1-MU)/0.08)-(-MU+0.08)}
    benches["B_earth_gbs"] = pg.evaluate("c=>window.__lab.bench(c)", {"ic": earth_ic, "T": 200, "integrator": "gbs", "tol": 1e-12, "maxEvals": 3e6})
    assist_ic = {"x": 0.1078494143903759, "y": 0.0, "vx": 0.0, "vy": 3.713183179935637}
    benches["C_assist_gbs"] = pg.evaluate("c=>window.__lab.bench(c)", {"ic": assist_ic, "T": 60, "integrator": "gbs", "tol": 1e-12, "maxEvals": 3e6})
    benches["D_throughput"] = pg.evaluate("c=>window.__lab.bench(c)", {"ic": tadpole, "T": 20, "integrator": "rk4", "dt": 1e-3, "maxEvals": 5e6})
    res["bench"] = benches

    # ---- 3) 预设动力学 (live sim) ----
    presets = {}
    pg.evaluate("window.__lab.loadPreset('tadpole')")
    presets["tadpole"] = pg.evaluate("window.__lab.runFor(200, 3e6)")
    pg.evaluate("window.__lab.loadPreset('l1')")
    presets["l1"] = pg.evaluate("window.__lab.runFor(30, 3e6)")
    pg.evaluate("window.__lab.loadPreset('earth')")
    presets["earth"] = pg.evaluate("window.__lab.runFor(50, 3e6)")
    pg.evaluate("window.__lab.loadPreset('assist')")
    presets["assist14"] = pg.evaluate("window.__lab.runFor(14, 3e6)")
    pg.evaluate("window.__lab.loadPreset('assist')")
    presets["assist60"] = pg.evaluate("window.__lab.runFor(60, 3e6)")
    res["presets"] = presets

    # ---- 4) 交互 ----
    inter = {}
    pg.evaluate("window.__lab.loadPreset('tadpole')")
    pg.evaluate("window.__lab.setSpeed(0.3); window.__lab.run(true)")
    time.sleep(0.35)
    pg.evaluate("window.__lab.run(false)")
    t1 = pg.evaluate("window.__lab.state().t")
    time.sleep(0.4)
    t2 = pg.evaluate("window.__lab.state().t")
    inter["pause_freezes_t"] = (t1 == t2)
    inter["pause_t_value"] = t1
    pg.evaluate("window.__lab.setIntegrator('rk4'); window.__lab.setDt(0.01)")
    t0 = pg.evaluate("window.__lab.state().t")
    t1 = pg.evaluate("window.__lab.stepOnce()")
    inter["single_step_dt"] = abs((t1-t0) - 0.01) < 1e-9
    r = pg.evaluate("window.__lab.runFor(1.0, 1e6)")
    pg.evaluate("window.__lab.reset()")
    s0 = pg.evaluate("window.__lab.state()")
    inter["reset_ok"] = (s0["t"] == 0 and abs(s0["s"][0]-(-0.0)) >= 0 and s0["trailN"] == 0
                         and abs(s0["C"] - s0["C0"]) < 1e-12 and not s0["halted"])
    ppu0 = pg.evaluate("window.__lab.getView().ppu")
    pg.mouse.move(840, 500)
    for _ in range(3):
        pg.mouse.wheel(0, -240)
        time.sleep(0.06)
    ppu1 = pg.evaluate("window.__lab.getView().ppu")
    inter["wheel_zoom"] = ppu1 > ppu0*1.3
    cx0 = pg.evaluate("window.__lab.getView().cx")
    pg.mouse.move(840, 500); pg.mouse.down(); pg.mouse.move(900, 500, steps=5); pg.mouse.up()
    cx1 = pg.evaluate("window.__lab.getView().cx")
    inter["drag_pan"] = abs(cx1-cx0) > 0.01 and math.isfinite(cx1)
    pg.evaluate("window.__lab.loadPreset('tadpole'); window.__lab.setIntegrator('gbs')")
    pg.evaluate("window.__lab.runFor(1.0, 1e6)")
    pg.evaluate("window.__lab.setIntegrator('rk4')")
    r = pg.evaluate("window.__lab.runFor(1.0, 1e6)")
    inter["switch_continuity"] = r["driftRel"] < 1e-6
    inter["_switch_drift"] = r["driftRel"]
    res["interact"] = inter

    # ---- 4b) 扩展断言数据: fps / IMP 有界性 / 效率护栏 ----
    pg.evaluate("window.__lab.loadPreset('tadpole'); window.__lab.setIntegrator('rk4'); window.__lab.setDt(0.002); window.__lab.setSpeed(0.3); window.__lab.run(true)")
    time.sleep(1.8)
    res["perf"] = pg.evaluate("window.__lab.perf()")
    pg.evaluate("window.__lab.run(false); window.__lab.loadPreset('tadpole')")
    e_ic = earth_ic
    res["impB"] = {
        "T1000": pg.evaluate("c=>window.__lab.bench(c)", {"ic": e_ic, "T": 1000, "integrator": "imp", "dt": 1e-3, "maxEvals": 2e7}),
        "T2000": pg.evaluate("c=>window.__lab.bench(c)", {"ic": e_ic, "T": 2000, "integrator": "imp", "dt": 1e-3, "maxEvals": 2e7}),
    }

    # ---- 5) 截图 ----
    if SHOTDIR:
        SHOTDIR.mkdir(parents=True, exist_ok=True)
        pg.evaluate("window.__lab.setView({cx:0.15, cy:0.1, ppu:330})")
        pg.evaluate("window.__lab.loadPreset('tadpole'); window.__lab.setSpeed(0.6); window.__lab.run(true)")
        time.sleep(2.8)
        pg.screenshot(path=str(SHOTDIR/"shot_tadpole.png"))
        pg.evaluate("window.__lab.run(false)")
        pg.evaluate("window.__lab.loadPreset('assist'); window.__lab.setSpeed(0.8); window.__lab.run(true)")
        time.sleep(2.0)
        pg.screenshot(path=str(SHOTDIR/"shot_assist.png"))
        pg.evaluate("window.__lab.run(false); window.__lab.loadPreset('tadpole'); window.__lab.reset()")
    b.close()

# ---- 断言汇总 ----
A = {}
n_in = res["selftest"]["passed"]; t_in = res["selftest"]["total"]
for i, r in enumerate(res["selftest"]["results"]):
    A[f"IN{i+1:02d}_{r['name'][:10]}"] = bool(r["pass"])
A["CONSOLE_clean"] = len(res["console"]) == 0 and len(res["pageerror"]) == 0
A["BEN1_gbs_drift"] = res["bench"]["A_gbs"]["ok"] and res["bench"]["A_gbs"]["driftRel"] < 1e-9
A["BEN2_gbs_budget"] = res["bench"]["A_gbs"]["evals"] <= 650000
A["BEN3_assist_flyby"] = 0.015 < res["bench"]["C_assist_gbs"]["minR2"] < 0.10
tp = res["bench"]["D_throughput"]["evals"] / max(1e-9, res["bench"]["D_throughput"]["wallMs"]/1000)
A["THR_evals_per_s"] = tp >= 1e6
tad = res["presets"]["tadpole"]
A["PRE1_tadpole"] = (not tad["halted"] or "奇点" in (tad["msg"] or "")) and tad["driftRel"] < 1e-9 and tad["minR2"] > 0.45 and tad["maxR2"] < 1.55
l1r = res["presets"]["l1"]
A["PRE2_l1_escape"] = (("奇点" in (l1r["msg"] or "")) or l1r["minR1"] < 0.15 or l1r["minR2"] < 0.15)
ear = res["presets"]["earth"]
A["PRE3_earth_bound"] = (not ear["halted"]) and ear["minR1"] > 0.05 and ear["maxR1"] < 0.16 and ear["driftRel"] < 1e-6
a14 = res["presets"]["assist14"]; a60 = res["presets"]["assist60"]
E0 = earth_E([0.1078494143903759, 0, 0, 3.713183179935637])
E1 = earth_E(a14["s"])
A["PRE4_assist"] = (0.015 < a60["minR2"] < 0.12) and (E1 - E0) > 0.1*abs(E0)
it = res["interact"]
A["INT1_pause"] = bool(it["pause_freezes_t"])
A["INT2_step"] = bool(it["single_step_dt"])
A["INT3_reset"] = bool(it["reset_ok"])
A["INT4_zoom"] = bool(it["wheel_zoom"])
A["INT5_pan"] = bool(it["drag_pan"])
A["INT6_switch"] = bool(it["switch_continuity"])
A["FPS_render"] = res.get("perf", {}).get("fps", 0) >= 40
if "impB" in res:
    d1 = res["impB"]["T1000"]["driftRel"]; d2 = res["impB"]["T2000"]["driftRel"]
    A["REG1_imp_bounded"] = d1 > 0 and (d2/d1) < 2.0 and (d2/d1) > 0.5
A["REG2_gbs_budget_earth"] = res["bench"]["B_earth_gbs"]["evals"] <= 1600000

passed = sum(1 for v in A.values() if v); total = len(A)
driftA = res["bench"]["A_gbs"]["driftRel"] if res["bench"]["A_gbs"]["ok"] else 1.0
bonus = 30*min(1.0, math.log10(1/max(driftA, 1e-16))/14) if driftA > 0 and math.isfinite(driftA) else 0.0
score = 70*passed/total + bonus
res["assertions"] = A
res["summary"] = {"passed": passed, "total": total, "passRate": passed/total,
                  "driftA_gbs": driftA, "driftBonus": bonus, "verify_score": round(score, 3)}
pathlib.Path(OUT).write_text(json.dumps(res, ensure_ascii=False, indent=1))
print(json.dumps({"summary": res["summary"],
                  "failed": [k for k, v in A.items() if not v],
                  "selftest_fails": [r["name"] for r in res["selftest"]["results"] if not r["pass"]],
                  "console_errors": res["console"][:5], "pageerrors": res["pageerror"][:5],
                  "bench_drifts": {k: v["driftRel"] for k, v in res["bench"].items()},
                  "bench_evals": {k: v["evals"] for k, v in res["bench"].items()}},
                 ensure_ascii=False, indent=1))
