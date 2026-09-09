#!/usr/bin/env python3
"""Headless browser verification of lab.html.

Launches the real page in Chromium, captures every console message and page error,
exercises the controls, runs the IN-PAGE self-test suite and reports exactly what
the page produced. Nothing here is simulated: every number comes from the page.
"""
import json
import pathlib
import sys
import time

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
LAB = ROOT / "lab.html"
SHOT = ROOT / "tests" / "lab_screenshot.png"


def main() -> int:
    if not LAB.exists():
        print(f"FATAL: {LAB} not found; run build.py first")
        return 2
    url = LAB.as_uri()
    console = []
    errors = []
    report = {"url": url, "console": console, "page_errors": errors}

    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--no-sandbox", "--allow-file-access-from-files"])
        page = browser.new_page(viewport={"width": 1600, "height": 950}, device_scale_factor=1)
        page.on("console", lambda m: console.append({"type": m.type, "text": m.text}))
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(url, wait_until="load")
        page.wait_for_function("() => window.__CR3BP_LAB__ && window.__CR3BP_LAB__.ready", timeout=20000)

        # --- structural checks -------------------------------------------------
        report["title"] = page.title()
        report["lp_table_rows"] = page.eval_on_selector_all("#lpTable tr", "els => els.length")
        report["method_options"] = page.eval_on_selector_all("#method option", "els => els.map(e => e.value)")
        report["preset_buttons"] = page.eval_on_selector_all("#presets button", "els => els.map(e => e.textContent)")
        report["canvas_size"] = page.evaluate("() => { const c = document.getElementById('view'); return [c.width, c.height]; }")

        # --- exercise every preset --------------------------------------------
        preset_results = []
        n_presets = page.eval_on_selector_all("#presets button", "els => els.length")
        for i in range(n_presets):
            page.eval_on_selector_all("#presets button", f"els => els[{i}].click()")
            page.wait_for_timeout(350)
            st = page.evaluate("""() => {
                const L = window.__CR3BP_LAB__;
                const s = L.sim.state;
                return {t: L.sim.t, x: s.x, y: s.y, vx: s.vx, vy: s.vy,
                        C: L.sim.C, C0: L.sim.C0, halted: L.sim.halted,
                        finite: [s.x,s.y,s.z,s.vx,s.vy,s.vz].every(Number.isFinite)};
            }""")
            st["preset_index"] = i
            preset_results.append(st)
        report["presets"] = preset_results

        # --- pause / step / reset ---------------------------------------------
        page.click("#play")                      # pause
        page.wait_for_timeout(120)
        t_before = page.evaluate("() => window.__CR3BP_LAB__.sim.t")
        page.click("#stepBtn")
        page.wait_for_timeout(120)
        t_after = page.evaluate("() => window.__CR3BP_LAB__.sim.t")
        report["single_step"] = {"t_before": t_before, "t_after": t_after, "advanced": t_after > t_before}
        page.click("#reset")
        page.wait_for_timeout(150)
        report["after_reset"] = page.evaluate(
            "() => ({t: window.__CR3BP_LAB__.sim.t, steps: window.__CR3BP_LAB__.sim.steps,"
            " halted: window.__CR3BP_LAB__.sim.halted})")

        # --- method switching + IC apply --------------------------------------
        method_probe = []
        for m in ["rk4", "yoshida4", "dopri5", "gbs", "verlet"]:
            page.select_option("#method", m)
            page.wait_for_timeout(80)
            page.click("#stepBtn")
            page.wait_for_timeout(80)
            method_probe.append(page.evaluate("""() => {
                const L = window.__CR3BP_LAB__;
                return {method: L.opts.method, t: L.sim.t, finite: Number.isFinite(L.sim.state.x),
                        C: L.sim.C};
            }"""))
        report["method_probe"] = method_probe

        page.fill("#ic-x", "0.6"); page.fill("#ic-y", "0.1")
        page.fill("#ic-vx", "0"); page.fill("#ic-vy", "-0.4")
        page.click("#applyIC"); page.wait_for_timeout(150)
        report["custom_ic"] = page.evaluate(
            "() => ({x: window.__CR3BP_LAB__.sim.state.x, y: window.__CR3BP_LAB__.sim.state.y,"
            " C0: window.__CR3BP_LAB__.sim.C0})")

        # --- run for a while, measure throughput (stable L4 preset) -----------
        page.select_option("#method", "gbs")
        page.eval_on_selector_all("#presets button", "els => els[0].click()")
        page.wait_for_timeout(150)
        page.evaluate("() => { window.__CR3BP_LAB__.sim.running = true; }")
        page.evaluate("() => { document.getElementById('speed').value = 1.5; document.getElementById('speed').dispatchEvent(new Event('input')); }")
        t0 = time.time()
        page.wait_for_timeout(3000)
        perf = page.evaluate("""() => {
            const L = window.__CR3BP_LAB__;
            return {t: L.sim.t, steps: L.sim.steps, evals: L.sim.evals, halted: L.sim.halted,
                    driftMax: L.sim.driftMax, lag: L.sim.lag,
                    readoutText: document.getElementById('readout').textContent.slice(0, 400)};
        }""")
        perf["wall_s"] = round(time.time() - t0, 2)
        perf["fps"] = page.evaluate("() => new Promise(res => { let n=0; const t0=performance.now(); "
            "function f(){ n++; if (performance.now()-t0 < 1000) requestAnimationFrame(f); else res(n); } "
            "requestAnimationFrame(f); })")
        report["throughput"] = perf
        page.click("#play")   # pause again

        # --- view controls ----------------------------------------------------
        page.click("#zoomIn"); page.click("#zoomOut"); page.click("#fit"); page.wait_for_timeout(100)
        page.mouse.move(800, 470)
        page.mouse.down(); page.mouse.move(900, 520, steps=6); page.mouse.up()
        page.mouse.wheel(0, -400); page.wait_for_timeout(120)
        page.uncheck("#showZVC"); page.wait_for_timeout(60)
        page.check("#showZVC"); page.wait_for_timeout(200)
        report["view_ok"] = page.evaluate("() => ({scale: window.__CR3BP_LAB__.sim ? true : false})")

        # --- in-page self tests -----------------------------------------------
        page.click("#runTests")
        page.wait_for_function(
            "() => { const e = document.getElementById('testSummary'); return e && /\\d+\\/\\d+/.test(e.textContent); }",
            timeout=120000)
        report["self_tests"] = page.evaluate("""() => {
            const rows = [...document.querySelectorAll('#testOut tr')].map(tr => ({
                status: tr.querySelector('.st') ? tr.querySelector('.st').textContent : null,
                name: tr.querySelector('.nm') ? (tr.querySelector('.nm').childNodes[0] ? tr.querySelector('.nm').childNodes[0].textContent : tr.querySelector('.nm').textContent) : null,
                value: tr.querySelector('.vl') ? tr.querySelector('.vl').textContent : null,
                detail: tr.querySelector('.detail') ? tr.querySelector('.detail').textContent : null
            }));
            return {summary: document.getElementById('testSummary').textContent, rows: rows};
        }""")

        page.screenshot(path=str(SHOT), full_page=False)
        report["screenshot"] = str(SHOT)
        browser.close()

    report["console_error_count"] = sum(1 for m in console if m["type"] == "error")
    report["console_warning_count"] = sum(1 for m in console if m["type"] == "warning")
    out = ROOT / "tests" / "browser_report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps({k: v for k, v in report.items() if k not in ("console",)},
                     indent=2, ensure_ascii=False)[:6000])
    print(f"\nconsole messages: {len(console)}  (errors {report['console_error_count']})")
    for m in console[:40]:
        print(f"  [{m['type']}] {m['text'][:300]}")
    print(f"page errors: {len(errors)}")
    for e in errors[:20]:
        print("  " + e[:500])
    print(f"full report -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
