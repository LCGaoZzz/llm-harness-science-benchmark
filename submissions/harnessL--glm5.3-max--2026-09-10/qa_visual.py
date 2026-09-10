# -*- coding: utf-8 -*-
"""Visual QA: reshoot lab.html scenarios and do PIL/numpy pixel statistics."""
import json, sys, os
import numpy as np
from PIL import Image

BASE = "/data/users/lianchong/workspace1/outputs/turn_20260910015519_a3291877feee4ddd8268f7f43b72c533"
URL = "file://" + os.path.join(BASE, "lab.html")

SCENARIOS = [
    dict(name="qa_tadpole", preset="tadpole", view=dict(cx=0.15, cy=0.1, ppu=330),
         speed=0.6, wait_ms=2500),
    dict(name="qa_assist",  preset="assist",  view=dict(cx=0.3, cy=0.0, ppu=900),
         speed=1.5, wait_ms=2000),
]

# ---------- 1. screenshots ----------
from playwright.sync_api import sync_playwright

shots = {}
with sync_playwright() as p:
    browser = p.chromium.launch(args=["--no-sandbox"])
    page = browser.new_page(viewport={"width": 1680, "height": 1000})
    page.goto(URL)
    page.wait_for_function("window.__labReady === true", timeout=20000)
    for sc in SCENARIOS:
        page.evaluate("n => window.__lab.loadPreset(n)", sc["preset"])
        page.evaluate("v => window.__lab.setView(v)", sc["view"])
        page.evaluate("s => window.__lab.setSpeed(s)", sc["speed"])
        page.evaluate("() => window.__lab.run(true)")
        page.wait_for_timeout(sc["wait_ms"])
        out = os.path.join(BASE, sc["name"] + ".png")
        page.screenshot(path=out)
        shots[sc["name"]] = out
        print(f"[shot] {sc['name']} -> {out}")
    browser.close()

# ---------- 2. pixel statistics ----------
BGR, BGG, BGB = 13, 17, 23   # #0d1117
TOL = 12

def analyze(path):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    h, w, _ = a.shape
    R, G, B = a[..., 0], a[..., 1], a[..., 2]

    bg = ((np.abs(R - BGR) <= TOL) & (np.abs(G - BGG) <= TOL) & (np.abs(B - BGB) <= TOL))
    nonbg = ~bg

    amber = (R >= 200) & (R <= 255) & (G >= 150) & (G <= 200) & (B < 120)          # ZVC #e3b341
    green = (G >= 100) & ((G - R) >= 40) & ((G - B) >= 40)                          # L crosses #3fb950/#58d06a
    blue  = (B >= 100) & ((B - R) >= 40)                                            # trail/earth #4da3ff/#58a6ff
    mx = a.max(axis=2); mn = a.min(axis=2)
    white = (mn >= 230) & ((mx - mn) <= 25)                                         # spacecraft #ffffff

    side = nonbg[:, :348]
    canvas = nonbg[:, 348:]
    return dict(
        size=f"{w}x{h}", total_px=int(w * h),
        nonbg_pct=round(float(nonbg.mean()) * 100, 2),
        amber_px=int(amber.sum()),
        green_px=int(green.sum()),
        blue_px=int(blue.sum()),
        white_px=int(white.sum()),
        sidebar_x348_nonbg_pct=round(float(side.mean()) * 100, 2),
        canvas_nonbg_pct=round(float(canvas.mean()) * 100, 2),
    )

results = {name: analyze(p) for name, p in shots.items()}

# ---------- 3. verdicts ----------
def verdicts(r):
    return [
        ("non-background > 5%",        r["nonbg_pct"] > 5,              f'{r["nonbg_pct"]}%'),
        ("amber ZVC px > 200",         r["amber_px"] > 200,             f'{r["amber_px"]}'),
        ("green L-point px > 10",      r["green_px"] > 10,              f'{r["green_px"]}'),
        ("blue px > 100",              r["blue_px"] > 100,              f'{r["blue_px"]}'),
        ("white spacecraft px > 10",   r["white_px"] > 10,              f'{r["white_px"]}'),
        ("sidebar(x<348) non-bg > 30%",r["sidebar_x348_nonbg_pct"] > 30,f'{r["sidebar_x348_nonbg_pct"]}%'),
    ]

out = {"shots": shots, "stats": results,
       "verdicts": {n: [(c, "PASS" if ok else "FAIL", v) for c, ok, v in verdicts(r)]
                    for n, r in results.items()}}
with open(os.path.join(BASE, "qa_result.json"), "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

for n, r in results.items():
    print(f"\n== {n} ({shots[n]}) ==")
    print(json.dumps(r, ensure_ascii=False))
    for c, ok, v in verdicts(r):
        print(f"  [{'PASS' if ok else 'FAIL'}] {c}  -> {v}")
