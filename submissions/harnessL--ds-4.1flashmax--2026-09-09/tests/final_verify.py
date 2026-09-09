#!/usr/bin/env python3
"""Final verification of the shipped lab.html: long real-time run, halt path,
divergence preset, screenshots. Everything is read back from the live page."""
import json
import pathlib
import time

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
LAB = ROOT / "lab.html"


def main() -> int:
    console, errors = [], []
    rep = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=["--no-sandbox"])
        page = b.new_page(viewport={"width": 1600, "height": 950})
        page.on("console", lambda m: console.append({"type": m.type, "text": m.text}))
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(LAB.as_uri(), wait_until="load")
        page.wait_for_function("() => window.__CR3BP_LAB__ && window.__CR3BP_LAB__.ready", timeout=20000)

        # ---- 1. long real-time run on the shipped default -------------------
        page.evaluate("() => { document.getElementById('speed').value = 2.0;"
                      "document.getElementById('speed').dispatchEvent(new Event('input'));"
                      "window.__CR3BP_LAB__.sim.running = true; }")
        samples = []
        t0 = time.time()
        for i in range(10):
            page.wait_for_timeout(2000)
            samples.append(page.evaluate("""() => {
                const L = window.__CR3BP_LAB__;
                return {t: L.sim.t, steps: L.sim.steps, evals: L.sim.evals,
                        drift: L.sim.driftMax, halted: L.sim.halted, lag: L.sim.lag,
                        C: L.sim.C, C0: L.sim.C0};
            }"""))
        rep["long_run_wall_s"] = round(time.time() - t0, 2)
        rep["long_run_samples"] = samples
        page.screenshot(path=str(ROOT / "tests" / "final_longrun.png"))

        # ---- 2. halt path: put the craft at the Earth's centre --------------
        page.evaluate("() => { const L = window.__CR3BP_LAB__;"
                      "document.getElementById('ic-x').value = String(-L.C.MU_EARTH_MOON);"
                      "document.getElementById('ic-y').value = '0';"
                      "document.getElementById('ic-vx').value = '0';"
                      "document.getElementById('ic-vy').value = '0';"
                      "document.getElementById('applyIC').click(); }")
        page.wait_for_timeout(200)
        page.evaluate("() => { window.__CR3BP_LAB__.sim.running = true; }")
        page.wait_for_timeout(700)
        rep["halt"] = page.evaluate("""() => {
            const L = window.__CR3BP_LAB__;
            return {halted: L.sim.halted, msg: L.sim.haltMsg,
                    banner: document.getElementById('halt').textContent,
                    visible: document.getElementById('halt').classList.contains('show')};
        }""")
        page.screenshot(path=str(ROOT / "tests" / "final_halt.png"))

        # ---- 3. L1 unstable preset should leave L1 --------------------------
        page.evaluate("() => { document.querySelectorAll('#presets button')[1].click(); }")
        page.wait_for_timeout(300)
        page.evaluate("() => { const L=window.__CR3BP_LAB__; L.sim.running = true;"
                      "document.getElementById('speed').value = 3;"
                      "document.getElementById('speed').dispatchEvent(new Event('input')); }")
        page.wait_for_timeout(4000)
        rep["l1_preset"] = page.evaluate("""() => {
            const L = window.__CR3BP_LAB__, C = L.C, s = L.sim.state;
            const lp = L.lagrange.points.L1;
            return {t: L.sim.t, halted: L.sim.halted, finite: C.isFiniteState(s),
                    distFromL1: Math.hypot(s.x - lp.x, s.y - lp.y), drift: L.sim.driftMax};
        }""")

        # ---- 4. every method still finite after one step on a hard IC -------
        page.evaluate("() => { const L=window.__CR3BP_LAB__; L.setIC({x:0.6,y:0.1,z:0,vx:0,vy:-0.4,vz:0}); }")
        probe = []
        for m in ["gbs", "gbsfix", "dopri5", "ark4", "symadapt", "yoshida4", "yoshida6", "verlet", "rk4"]:
            page.select_option("#method", m)
            page.wait_for_timeout(60)
            page.click("#stepBtn")
            page.wait_for_timeout(60)
            probe.append(page.evaluate("""() => {
                const L = window.__CR3BP_LAB__;
                return {method: L.opts.method, finite: L.C.isFiniteState(L.sim.state),
                        halted: L.sim.halted, C: L.sim.C};
            }"""))
        rep["method_probe"] = probe
        b.close()

    rep["console_errors"] = [m for m in console if m["type"] == "error"]
    rep["page_errors"] = errors
    (ROOT / "tests" / "final_report.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False))
    print(json.dumps(rep, indent=2, ensure_ascii=False)[:5000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
