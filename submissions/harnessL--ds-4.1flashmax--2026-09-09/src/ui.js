/* =====================================================================
   ui.js — Earth-Moon CR3BP laboratory front end.
   Depends only on window.CR3BP (inlined above). No network, no modules.
   ===================================================================== */
(function () {
  'use strict';
  var C = window.CR3BP;
  if (!C) { document.body.innerHTML = '<pre style="color:#f66;padding:20px">CR3BP core failed to load</pre>'; return; }
  var MU = C.MU_EARTH_MOON;

  var $ = function (id) { return document.getElementById(id); };
  var cv = $('view'), ctx = cv.getContext('2d');
  var dpr = Math.min(2, window.devicePixelRatio || 1);
  var W = 800, H = 600;

  /* ---------------------------------------------------------------- */
  /* state                                                             */
  /* ---------------------------------------------------------------- */
  var LP = C.lagrangePoints(MU);
  var PRESETS = C.presets(MU);

  var sim = {
    ic: null, state: null, t: 0, C0: 0, C: 0,
    running: false, halted: false, haltMsg: '',
    trail: [], drift: [], driftMax: 0,
    steps: 0, rejects: 0, evals0: 0, evals: 0, lag: false,
    lagWarned: false
  };
  var view = { cx: 0.35, cy: 0, scale: 220, follow: false };
  var opts = {
    method: 'gbs', dt: 1e-3, rtol: 1e-13, atol: 1e-16, gbsK: 5, gbsSeq: 'bulirsch',
    speed: 0.6, showZVC: true, showTrail: true, showL: true
  };
  var stepper = null;
  var zvc = { mask: null, curve: null, C: NaN, viewKey: '', lastMs: 0 };
  var lastTs = 0, frameCount = 0, dirty = true;

  /* ---------------------------------------------------------------- */
  /* helpers                                                           */
  /* ---------------------------------------------------------------- */
  function fmt(x, d) { return (x == null || !isFinite(x)) ? '—' : x.toFixed(d == null ? 4 : d); }
  function fmtE(x, d) { return (x == null || !isFinite(x)) ? '—' : x.toExponential(d == null ? 2 : d); }
  function clone(s) { return { x: s.x, y: s.y, z: s.z, vx: s.vx, vy: s.vy, vz: s.vz }; }
  function w2s(x, y) { return [(x - view.cx) * view.scale + W / 2, -(y - view.cy) * view.scale + H / 2]; }
  function s2w(sx, sy) { return [(sx - W / 2) / view.scale + view.cx, -(sy - H / 2) / view.scale + view.cy]; }

  /* ---------------------------------------------------------------- */
  /* stepper                                                           */
  /* ---------------------------------------------------------------- */
  function rebuildStepper() {
    stepper = C.makeStepper({ method: opts.method, dt: opts.dt, rtol: opts.rtol, atol: opts.atol, gbsK: opts.gbsK, gbsSeq: opts.gbsSeq });
  }

  /* ---------------------------------------------------------------- */
  /* reset / presets                                                   */
  /* ---------------------------------------------------------------- */
  function setIC(ic) {
    sim.ic = clone(ic);
    ['x', 'y', 'z', 'vx', 'vy', 'vz'].forEach(function (k) { $('ic-' + k).value = ic[k]; });
    reset();
  }

  function reset() {
    sim.state = clone(sim.ic);
    sim.t = 0;
    sim.C0 = C.jacobi(sim.state, MU);
    sim.C = sim.C0;
    sim.trail = [];
    sim.drift = [];
    sim.driftMax = 0;
    sim.halted = false; sim.haltMsg = '';
    sim.steps = 0; sim.rejects = 0; sim.lag = false; sim.lagWarned = false;
    C.resetStats();
    sim.evals = 0;
    rebuildStepper();
    zvc.C = NaN;
    $('halt').classList.remove('show');
    $('halt').textContent = '';
    updateReadout();
    render();
  }

  function halt(msg) {
    sim.halted = true;
    sim.running = false;
    sim.haltMsg = msg;
    $('halt').textContent = '积分已停止：' + msg + '（t = ' + fmt(sim.t, 3) + ' TU）';
    $('halt').classList.add('show');
    syncRunButton();
  }

  /* ---------------------------------------------------------------- */
  /* stepping                                                          */
  /* ---------------------------------------------------------------- */
  function oneStep(maxDt) {
    if (sim.halted) return 0;
    var pre = C.guardState(sim.state, MU);
    if (!pre.ok) { halt(pre.message); return 0; }
    var h = stepper.adaptive ? stepper.adaptiveDt : stepper.dt;
    if (!isFinite(h) || h <= 0) { halt('无效步长'); return 0; }
    var clamped = false;
    if (maxDt != null && h > maxDt) { h = maxDt; clamped = true; }
    var out;
    try { out = stepper.step(sim.state, MU, clamped ? h : undefined); }
    catch (e) { halt('积分器异常：' + (e && e.message ? e.message : e)); return 0; }
    if (!out.accepted) { sim.rejects++; return 0; }

    sim.state = out.state;
    sim.t += h;
    sim.steps++;
    sim.evals = C.snapshotStats().evals;

    if (!C.isFiniteState(sim.state)) { halt('状态出现 NaN / Inf'); return 0; }
    var g = C.guardState(sim.state, MU);
    if (!g.ok) { halt(g.message); return 0; }

    sim.C = C.jacobi(sim.state, MU);
    var d = Math.abs(sim.C - sim.C0) / Math.max(Math.abs(sim.C0), 1e-12);
    if (d > sim.driftMax) sim.driftMax = d;
    sim.drift.push({ t: sim.t, d: d });
    if (sim.drift.length > 4000) sim.drift.splice(0, sim.drift.length - 4000);
    sim.trail.push(sim.state.x, sim.state.y);
    if (sim.trail.length > 12000) sim.trail.splice(0, sim.trail.length - 12000);
    return h;
  }

  function advance(simDt) {
    var budget = simDt, n = 0, maxSteps = 6000;
    while (budget > 1e-12 && n < maxSteps) {
      var h = oneStep(budget);
      if (sim.halted) break;
      if (h === 0) { if (sim.rejects > 100000) { halt('自适应步长反复被拒绝'); break; } n++; continue; }
      budget -= h; n++;
    }
    sim.lag = n >= maxSteps;
    if (sim.lag && !sim.lagWarned) { sim.lagWarned = true; }
  }

  /* ---------------------------------------------------------------- */
  /* zero-velocity curve                                               */
  /* ---------------------------------------------------------------- */
  function computeZVC() {
    var nx = 200, ny = Math.max(40, Math.round(200 * H / W));
    var x0 = view.cx - (W / 2) / view.scale, x1 = view.cx + (W / 2) / view.scale;
    var y0 = view.cy - (H / 2) / view.scale, y1 = view.cy + (H / 2) / view.scale;
    var g = new Float64Array((nx + 1) * (ny + 1));
    var i, j, wx, wy, k = 0;
    for (j = 0; j <= ny; j++) {
      wy = y0 + (y1 - y0) * j / ny;
      for (i = 0; i <= nx; i++) {
        wx = x0 + (x1 - x0) * i / nx;
        g[k++] = 2 * C.omega(wx, wy, 0, MU) - sim.C;
      }
    }
    /* forbidden mask (2 Omega < C) as a low-res image */
    var img = ctx.createImageData(nx, ny);
    var px = img.data, p = 0;
    for (j = 0; j < ny; j++) {
      for (i = 0; i < nx; i++) {
        var a = g[j * (nx + 1) + i], b = g[j * (nx + 1) + i + 1];
        var c = g[(j + 1) * (nx + 1) + i], d = g[(j + 1) * (nx + 1) + i + 1];
        var inside = (a < 0 && b < 0 && c < 0 && d < 0);
        px[p++] = 90; px[p++] = 40; px[p++] = 60; px[p++] = inside ? 110 : 0;
      }
    }
    /* marching squares on g = 0 */
    var segs = [];
    var interp = function (ga, gb, ta, tb) { var t = ga / (ga - gb); return ta + (tb - ta) * t; };
    for (j = 0; j < ny; j++) {
      for (i = 0; i < nx; i++) {
        var g00 = g[j * (nx + 1) + i], g10 = g[j * (nx + 1) + i + 1];
        var g01 = g[(j + 1) * (nx + 1) + i], g11 = g[(j + 1) * (nx + 1) + i + 1];
        var X0 = x0 + (x1 - x0) * i / nx, X1 = x0 + (x1 - x0) * (i + 1) / nx;
        var Y0 = y0 + (y1 - y0) * j / ny, Y1 = y0 + (y1 - y0) * (j + 1) / ny;
        var idx = (g00 > 0 ? 1 : 0) | (g10 > 0 ? 2 : 0) | (g11 > 0 ? 4 : 0) | (g01 > 0 ? 8 : 0);
        if (idx === 0 || idx === 15) continue;
        var eB = null, eR = null, eT = null, eL = null;
        if (((idx >> 0) & 1) !== ((idx >> 1) & 1)) eB = [interp(g00, g10, X0, X1), Y0];
        if (((idx >> 1) & 1) !== ((idx >> 2) & 1)) eR = [X1, interp(g10, g11, Y0, Y1)];
        if (((idx >> 3) & 1) !== ((idx >> 2) & 1)) eT = [interp(g01, g11, X0, X1), Y1];
        if (((idx >> 0) & 1) !== ((idx >> 3) & 1)) eL = [X0, interp(g00, g01, Y0, Y1)];
        var pts = [eB, eR, eT, eL].filter(function (q) { return q; });
        if (pts.length === 2) segs.push(pts[0], pts[1]);
        else if (pts.length === 4) { segs.push(pts[0], pts[1], pts[2], pts[3]); }
      }
    }
    zvc.mask = img; zvc.curve = segs; zvc.C = sim.C; zvc.dirtyMask = true;
    zvc.viewKey = view.cx + '|' + view.cy + '|' + view.scale + '|' + W + 'x' + H;
    zvc.lastMs = performance.now();
  }

  /* ---------------------------------------------------------------- */
  /* rendering                                                         */
  /* ---------------------------------------------------------------- */
  function drawGrid() {
    var step = 0.5;
    while (step * view.scale < 60) step *= 2;
    while (step * view.scale > 240) step /= 2;
    var x0 = view.cx - (W / 2) / view.scale, x1 = view.cx + (W / 2) / view.scale;
    var y0 = view.cy - (H / 2) / view.scale, y1 = view.cy + (H / 2) / view.scale;
    ctx.lineWidth = 1;
    ctx.strokeStyle = '#141c2b';
    ctx.beginPath();
    for (var x = Math.ceil(x0 / step) * step; x <= x1; x += step) {
      var sx = Math.round(w2s(x, 0)[0]) + 0.5;
      ctx.moveTo(sx, 0); ctx.lineTo(sx, H);
    }
    for (var y = Math.ceil(y0 / step) * step; y <= y1; y += step) {
      var sy = Math.round(w2s(0, y)[1]) + 0.5;
      ctx.moveTo(0, sy); ctx.lineTo(W, sy);
    }
    ctx.stroke();
    /* axes through the barycentre */
    ctx.strokeStyle = '#1d2a40';
    ctx.beginPath();
    var o = w2s(0, 0);
    ctx.moveTo(0, o[1] + 0.5); ctx.lineTo(W, o[1] + 0.5);
    ctx.moveTo(o[0] + 0.5, 0); ctx.lineTo(o[0] + 0.5, H);
    ctx.stroke();
  }

  function drawZVC() {
    if (!isFinite(sim.C)) return;
    var viewKey = view.cx + '|' + view.cy + '|' + view.scale + '|' + W + 'x' + H;
    var stale = !isFinite(zvc.C) || Math.abs(zvc.C - sim.C) > 1e-11 ||
                zvc.viewKey !== viewKey || !zvc.mask ||
                (performance.now() - zvc.lastMs > 500 && Math.abs(zvc.C - sim.C) > 1e-13);
    if (stale) computeZVC();

    /* forbidden region: reuse one offscreen canvas, rebuilt only when the ZVC is */
    if (!zvc.off) { zvc.off = document.createElement('canvas'); }
    if (zvc.off.width !== zvc.mask.width || zvc.off.height !== zvc.mask.height) {
      zvc.off.width = zvc.mask.width; zvc.off.height = zvc.mask.height;
      zvc.offCtx = zvc.off.getContext('2d');
    }
    if (zvc.dirtyMask) { zvc.offCtx.putImageData(zvc.mask, 0, 0); zvc.dirtyMask = false; }
    ctx.save();
    ctx.globalAlpha = 0.85;
    ctx.imageSmoothingEnabled = true;
    ctx.drawImage(zvc.off, 0, 0, W, H);
    ctx.restore();

    /* the curve itself */
    var s = zvc.curve;
    ctx.save();
    ctx.strokeStyle = 'rgba(255,180,84,0.85)';
    ctx.lineWidth = 1.4;
    ctx.beginPath();
    for (var i = 0; i < s.length; i += 2) {
      var a = w2s(s[i][0], s[i][1]), b = w2s(s[i + 1][0], s[i + 1][1]);
      ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]);
    }
    ctx.stroke();
    ctx.restore();
  }

  function drawBodies() {
    var bodies = [
      { x: -MU, y: 0, r: C.R_EARTH, c: '#4ea1ff', name: '地球' },
      { x: 1 - MU, y: 0, r: C.R_MOON, c: '#c9d3e4', name: '月球' }
    ];
    bodies.forEach(function (b) {
      var p = w2s(b.x, b.y);
      var r = Math.max(4.5, b.r * view.scale);
      var grd = ctx.createRadialGradient(p[0], p[1], r * 0.2, p[0], p[1], r * 3.2);
      grd.addColorStop(0, b.c);
      grd.addColorStop(0.18, b.c);
      grd.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = grd;
      ctx.beginPath(); ctx.arc(p[0], p[1], r * 3.2, 0, 6.2832); ctx.fill();
      ctx.fillStyle = b.c;
      ctx.beginPath(); ctx.arc(p[0], p[1], r, 0, 6.2832); ctx.fill();
      ctx.fillStyle = 'rgba(219,228,242,0.75)';
      ctx.font = '11px ui-monospace,monospace';
      ctx.fillText(b.name, p[0] + r + 5, p[1] - r - 3);
    });
  }

  function drawLagrange() {
    var names = ['L1', 'L2', 'L3', 'L4', 'L5'];
    ctx.font = '11px ui-monospace,monospace';
    for (var i = 0; i < names.length; i++) {
      var p = LP.points[names[i]], s = w2s(p.x, p.y);
      if (s[0] < -40 || s[0] > W + 40 || s[1] < -40 || s[1] > H + 40) continue;
      ctx.strokeStyle = 'rgba(126,224,192,0.9)';
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.moveTo(s[0] - 5, s[1]); ctx.lineTo(s[0] + 5, s[1]);
      ctx.moveTo(s[0], s[1] - 5); ctx.lineTo(s[0], s[1] + 5);
      ctx.stroke();
      ctx.fillStyle = 'rgba(126,224,192,0.95)';
      ctx.fillText(names[i], s[0] + 7, s[1] - 6);
    }
  }

  function drawTrail() {
    var n = sim.trail.length / 2;
    if (n < 2) return;
    ctx.save();
    ctx.lineJoin = 'round'; ctx.lineCap = 'round';
    var pts = [];
    for (var i = 0; i < n; i++) pts.push(w2s(sim.trail[2 * i], sim.trail[2 * i + 1]));
    ctx.strokeStyle = 'rgba(126,224,192,0.14)';
    ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]);
    for (var j = 1; j < n; j++) ctx.lineTo(pts[j][0], pts[j][1]);
    ctx.stroke();
    ctx.strokeStyle = 'rgba(126,224,192,0.75)';
    ctx.lineWidth = 1.2;
    ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]);
    for (var k = 1; k < n; k++) ctx.lineTo(pts[k][0], pts[k][1]);
    ctx.stroke();
    ctx.restore();
  }

  function drawCraft() {
    var s = sim.state, p = w2s(s.x, s.y);
    ctx.save();
    ctx.shadowColor = '#7ee0c0'; ctx.shadowBlur = 10;
    ctx.fillStyle = '#eafff6';
    ctx.beginPath(); ctx.arc(p[0], p[1], 3.2, 0, 6.2832); ctx.fill();
    ctx.restore();
    /* velocity direction, scaled */
    var vn = Math.hypot(s.vx, s.vy);
    if (vn > 1e-9) {
      var L = Math.min(46, 10 + 12 * Math.log(1 + vn));
      var q = w2s(s.x + s.vx / vn * (L / view.scale), s.y + s.vy / vn * (L / view.scale));
      ctx.strokeStyle = 'rgba(126,224,192,0.55)';
      ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(p[0], p[1]); ctx.lineTo(q[0], q[1]); ctx.stroke();
    }
  }

  function render() {
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = '#05070c';
    ctx.fillRect(0, 0, W, H);
    drawGrid();
    if (opts.showZVC) drawZVC();
    if (opts.showL) drawLagrange();
    drawBodies();
    if (opts.showTrail) drawTrail();
    if (sim.state) drawCraft();
  }

  /* ---------------------------------------------------------------- */
  /* readouts                                                          */
  /* ---------------------------------------------------------------- */
  function updateReadout() {
    var s = sim.state || sim.ic;
    var r1 = C.dist1(s, MU), r2 = C.dist2(s, MU);
    var v = Math.hypot(s.vx, s.vy, s.vz);
    var dC = Math.abs(sim.C - sim.C0) / Math.max(Math.abs(sim.C0), 1e-12);
    var rows = [
      ['时间 t', fmt(sim.t, 3) + ' TU  ·  ' + fmt(sim.t * C.TU_DAYS, 2) + ' d'],
      ['位置 (x,y,z)', fmt(s.x, 5) + ', ' + fmt(s.y, 5) + ', ' + fmt(s.z, 5)],
      ['位置 (km)', fmt(s.x * C.DU_KM, 0) + ', ' + fmt(s.y * C.DU_KM, 0) + ', ' + fmt(s.z * C.DU_KM, 0)],
      ['速度 (vx,vy,vz)', fmt(s.vx, 5) + ', ' + fmt(s.vy, 5) + ', ' + fmt(s.vz, 5)],
      ['速率 |v|', fmt(v, 5) + ' VU  ·  ' + fmt(v * C.VU_KMS, 3) + ' km/s'],
      ['r₁ (地心距)', fmt(r1, 5) + ' DU  ·  ' + fmt(r1 * C.DU_KM, 0) + ' km'],
      ['r₂ (月心距)', fmt(r2, 5) + ' DU  ·  ' + fmt(r2 * C.DU_KM, 0) + ' km'],
      ['Jacobi C', fmt(sim.C, 9)],
      ['C₀', fmt(sim.C0, 9)],
      ['ΔC / |C₀|', fmtE(dC, 3)],
      ['步数 / 力评估', sim.steps + ' / ' + sim.evals],
      ['平均步长', fmt(sim.t / Math.max(sim.steps, 1), 5) + ' TU'],
      ['最小步长', fmt(stepper && stepper.adaptive ? stepper.dt : opts.dt, 5) + ' (当前)']
    ];
    var html = '';
    for (var i = 0; i < rows.length; i++) {
      html += '<span class="k">' + rows[i][0] + '</span><span class="v">' + rows[i][1] + '</span>';
    }
    $('readout').innerHTML = html;
    $('driftNow').textContent = fmtE(dC, 3);
    $('driftMax').textContent = fmtE(sim.driftMax, 3);
  }

  function drawSpark() {
    var c = $('driftCanvas');
    var w = c.clientWidth || 280, h = 64;
    if (c.width !== Math.round(w * dpr)) { c.width = Math.round(w * dpr); c.height = Math.round(h * dpr); }
    var g = c.getContext('2d');
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    g.clearRect(0, 0, w, h);
    g.fillStyle = '#0b101a'; g.fillRect(0, 0, w, h);
    var lo = -16, hi = 1;   /* log10 range */
    g.strokeStyle = '#1b2434'; g.lineWidth = 1;
    for (var e = lo; e <= hi; e += 4) {
      var yy = h - (e - lo) / (hi - lo) * h;
      g.beginPath(); g.moveTo(0, yy + 0.5); g.lineTo(w, yy + 0.5); g.stroke();
      g.fillStyle = '#3c4a63'; g.font = '9px ui-monospace,monospace';
      g.fillText('1e' + e, 2, yy - 2);
    }
    var d = sim.drift;
    if (d.length < 2) return;
    var t0 = d[0].t, t1 = d[d.length - 1].t;
    if (t1 - t0 < 1e-12) return;
    g.strokeStyle = '#7ee0c0'; g.lineWidth = 1.3;
    g.beginPath();
    var started = false;
    for (var i = 0; i < d.length; i++) {
      var x = (d[i].t - t0) / (t1 - t0) * w;
      var lg = Math.log(Math.max(d[i].d, 1e-17)) / Math.LN10;
      var y = h - (lg - lo) / (hi - lo) * h;
      if (y < 0) y = 0; if (y > h) y = h;
      if (!started) { g.moveTo(x, y); started = true; } else g.lineTo(x, y);
    }
    g.stroke();
  }

  /* ---------------------------------------------------------------- */
  /* lagrange table + tests                                            */
  /* ---------------------------------------------------------------- */
  function buildLPTable() {
    var names = ['L1', 'L2', 'L3', 'L4', 'L5'];
    var html = '<tr><th>点</th><th>x</th><th>y</th><th>C</th><th>|∇Ω|</th></tr>';
    names.forEach(function (n) {
      var p = LP.points[n];
      html += '<tr><td>' + n + '</td><td>' + fmt(p.x, 6) + '</td><td>' + fmt(p.y, 6) +
              '</td><td>' + fmt(p.C, 6) + '</td><td>' + fmtE(p.residual, 1) + '</td></tr>';
    });
    $('lpTable').innerHTML = html;
    $('lpNote').textContent = '由 Ω 的梯度零点用二分 + 牛顿求得（L4/L5 为闭式解）。最大残差 ' +
      fmtE(LP.maxResidual, 2) + '，C(L4)=3−μ+μ²=' + fmt(3 - MU + MU * MU, 6) + '。';
  }

  function runTests() {
    var btn = $('runTests');
    btn.disabled = true;
    $('testSummary').textContent = '正在运行（真实计算，约 1–3 秒）…';
    $('testOut').innerHTML = '';
    setTimeout(function () {
      var t0 = performance.now();
      var res;
      try { res = C.runSelfTests({}); }
      catch (e) { res = { error: String(e && e.stack || e) }; }
      var ms = Math.round(performance.now() - t0);
      if (res.error) {
        $('testSummary').innerHTML = '<span class="badge bad">异常</span> ' + res.error;
        btn.disabled = false; return;
      }
      var html = '<table class="tests">';
      res.tests.forEach(function (t) {
        html += '<tr><td class="st ' + (t.pass ? 'pass' : 'fail') + '">' + (t.pass ? 'PASS' : 'FAIL') + '</td>' +
                '<td class="nm">' + t.name + '<span class="detail">' + t.detail + '</span></td>' +
                '<td class="vl">' + (typeof t.value === 'number' ? fmtE(t.value, 2) : t.value) + '</td></tr>';
      });
      html += '</table>';
      $('testOut').innerHTML = html;
      var s = res.summary;
      $('testSummary').innerHTML = (s.failed === 0
        ? '<span class="badge good">全部通过</span> '
        : '<span class="badge bad">' + s.failed + ' 项未通过</span> ') +
        s.passed + '/' + s.total + ' · ' + ms + ' ms';
      btn.disabled = false;
    }, 30);
  }

  /* ---------------------------------------------------------------- */
  /* controls                                                          */
  /* ---------------------------------------------------------------- */
  function syncRunButton() {
    var b = $('play');
    b.textContent = sim.running ? '⏸ 暂停' : '▶ 运行';
    b.classList.toggle('primary', !sim.running);
    var dot = $('statusDot'), txt = $('statusText');
    dot.className = 'dot ' + (sim.halted ? 'halt' : (sim.running ? 'run' : 'pause'));
    txt.textContent = sim.halted ? '已停止' : (sim.running ? '运行中' : '暂停');
  }

  function buildMethodSelect() {
    var sel = $('method');
    var order = ['gbs', 'dopri5', 'gbsfix', 'ark4', 'symadapt', 'yoshida4', 'yoshida6', 'verlet', 'rk4'];
    sel.innerHTML = '';
    order.forEach(function (m) {
      var info = C.METHODS[m];
      var o = document.createElement('option');
      o.value = m; o.textContent = info.name;
      sel.appendChild(o);
    });
    sel.value = opts.method;
  }

  function syncMethodUI() {
    var info = C.METHODS[opts.method];
    $('methodBlurb').textContent = info.blurb + ' · 阶数 ' + info.order +
      ' · ' + (info.adaptive ? '自适应' : '固定步长') +
      (info.symplectic ? ' · 辛' : '');
    $('tolRow').style.display = info.adaptive ? '' : 'none';
    $('gbsKRow').style.display = (opts.method === 'gbs' || opts.method === 'gbsfix') ? '' : 'none';
    $('gbsSeqRow').style.display = (opts.method === 'gbs' || opts.method === 'gbsfix') ? '' : 'none';
    $('methodBadge').textContent = info.name.split(' ')[0];
    $('dtNum').value = opts.dt;
    $('dt').value = Math.log10(opts.dt);
    $('rtol').value = opts.rtol;
    $('gbsK').value = opts.gbsK;
    $('gbsSeq').value = opts.gbsSeq;
    $('stepHint').textContent = info.adaptive
      ? '自适应方法：dt 只是初始步长，控制器会按 rtol 调整。'
      : '固定步长：dt = ' + fmt(opts.dt, 6) + ' TU，每步 ' + info.evalsPerStep + ' 次力评估。';
  }

  function wire() {
    /* presets */
    var pw = $('presets');
    PRESETS.forEach(function (p) {
      var b = document.createElement('button');
      b.className = 'preset'; b.textContent = p.name; b.title = p.expect;
      b.onclick = function () { setIC(p.state); sim.running = true; syncRunButton(); };
      pw.appendChild(b);
    });

    buildMethodSelect();
    $('method').onchange = function () {
      opts.method = this.value; rebuildStepper(); syncMethodUI(); reset();
    };
    $('dt').oninput = function () {
      opts.dt = Math.pow(10, parseFloat(this.value));
      $('dtNum').value = opts.dt.toPrecision(3);
      rebuildStepper(); syncMethodUI();
    };
    $('dtNum').onchange = function () {
      var v = parseFloat(this.value);
      if (isFinite(v) && v > 0) { opts.dt = v; rebuildStepper(); syncMethodUI(); }
    };
    $('rtol').onchange = function () {
      var v = parseFloat(this.value);
      if (isFinite(v) && v > 0) { opts.rtol = v; opts.atol = v * 1e-2; rebuildStepper(); }
    };
    $('gbsK').onchange = function () {
      var v = parseInt(this.value, 10);
      if (isFinite(v) && v >= 2 && v <= 8) { opts.gbsK = v; rebuildStepper(); }
    };
    $('gbsSeq').onchange = function () {
      opts.gbsSeq = this.value; rebuildStepper(); reset();
    };

    $('applyIC').onclick = function () {
      var ic = {};
      ['x', 'y', 'z', 'vx', 'vy', 'vz'].forEach(function (k) {
        var v = parseFloat($('ic-' + k).value);
        ic[k] = isFinite(v) ? v : 0;
      });
      setIC(ic);
    };

    $('play').onclick = function () {
      if (sim.halted) { reset(); }
      sim.running = !sim.running;
      syncRunButton();
    };
    $('stepBtn').onclick = function () {
      sim.running = false; syncRunButton();
      oneStep();
      updateReadout(); drawSpark(); render();
    };
    $('reset').onclick = function () { reset(); syncRunButton(); };

    $('speed').value = opts.speed;
    $('speed').oninput = function () {
      opts.speed = parseFloat(this.value);
      $('speedHint').textContent = '仿真速度 ≈ ' + fmt(opts.speed, 2) + ' TU/s（1 个月球周期 = 2π TU ≈ ' +
        fmt(2 * Math.PI / Math.max(opts.speed, 1e-6), 1) + ' s 真实时间）';
    };
    $('speed').oninput();

    $('zoom').value = Math.log10(view.scale / 220);
    $('zoom').oninput = function () {
      view.scale = 220 * Math.pow(10, parseFloat(this.value));
      zvc.viewKey = '';
    };
    $('zoomIn').onclick = function () { view.scale *= 1.4; $('zoom').value = Math.log10(view.scale / 220); zvc.viewKey = ''; };
    $('zoomOut').onclick = function () { view.scale /= 1.4; $('zoom').value = Math.log10(view.scale / 220); zvc.viewKey = ''; };
    $('fit').onclick = function () {
      view.cx = 0.35; view.cy = 0; view.scale = Math.min(W / 3.4, H / 2.4);
      $('zoom').value = Math.log10(view.scale / 220); zvc.viewKey = '';
    };
    $('follow').onclick = function () {
      view.follow = !view.follow;
      this.classList.toggle('on', view.follow);
    };
    $('showZVC').onchange = function () { opts.showZVC = this.checked; dirty = true; };
    $('showTrail').onchange = function () { opts.showTrail = this.checked; dirty = true; };
    $('showL').onchange = function () { opts.showL = this.checked; dirty = true; };
    $('runTests').onclick = runTests;

    /* canvas interaction */
    var dragging = false, lastX = 0, lastY = 0;
    cv.addEventListener('pointerdown', function (e) {
      dragging = true; lastX = e.clientX; lastY = e.clientY;
      cv.classList.add('drag'); cv.setPointerCapture(e.pointerId);
    });
    cv.addEventListener('pointermove', function (e) {
      if (!dragging) return;
      view.cx -= (e.clientX - lastX) / view.scale;
      view.cy += (e.clientY - lastY) / view.scale;
      lastX = e.clientX; lastY = e.clientY;
      zvc.viewKey = '';
      render();
    });
    cv.addEventListener('pointerup', function (e) {
      dragging = false; cv.classList.remove('drag');
      try { cv.releasePointerCapture(e.pointerId); } catch (err) {}
    });
    cv.addEventListener('wheel', function (e) {
      e.preventDefault();
      var rect = cv.getBoundingClientRect();
      var mx = e.clientX - rect.left, my = e.clientY - rect.top;
      var before = s2w(mx, my);
      view.scale *= Math.exp(-e.deltaY * 0.0012);
      view.scale = Math.max(4, Math.min(20000, view.scale));
      var after = s2w(mx, my);
      view.cx += before[0] - after[0];
      view.cy += before[1] - after[1];
      $('zoom').value = Math.log10(view.scale / 220);
      zvc.viewKey = '';
    }, { passive: false });

    window.addEventListener('keydown', function (e) {
      if (e.target && /input|select|textarea/i.test(e.target.tagName)) return;
      if (e.code === 'Space') { e.preventDefault(); $('play').click(); }
      else if (e.key === 's' || e.key === 'S') $('stepBtn').click();
      else if (e.key === 'r' || e.key === 'R') $('reset').click();
    });
  }

  /* ---------------------------------------------------------------- */
  /* resize + loop                                                     */
  /* ---------------------------------------------------------------- */
  function resize() {
    var rect = cv.parentElement.getBoundingClientRect();
    W = Math.max(200, Math.round(rect.width));
    H = Math.max(200, Math.round(rect.height));
    cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
    cv.style.width = W + 'px'; cv.style.height = H + 'px';
    zvc.viewKey = '';
    render();
  }

  function loop(ts) {
    requestAnimationFrame(loop);
    if (!lastTs) lastTs = ts;
    var wall = Math.min(0.05, (ts - lastTs) / 1000);
    lastTs = ts;

    if (sim.running && !sim.halted) {
      advance(opts.speed * wall);
      if (view.follow && sim.state) { view.cx = sim.state.x; view.cy = sim.state.y; zvc.viewKey = ''; }
      dirty = true;
    }
    if (dirty) { render(); dirty = false; }
    frameCount++;
    if (frameCount % 4 === 0) { updateReadout(); drawSpark(); }
    if (frameCount % 30 === 0) syncRunButton();
  }

  /* ---------------------------------------------------------------- */
  /* boot                                                              */
  /* ---------------------------------------------------------------- */
  function boot() {
    wire();
    syncMethodUI();
    buildLPTable();
    setIC(PRESETS[0].state);
    resize();
    window.addEventListener('resize', resize);
    if (window.ResizeObserver) new ResizeObserver(resize).observe(cv.parentElement);
    syncRunButton();
    requestAnimationFrame(loop);
    window.__CR3BP_LAB__ = {   /* headless test hook */
      sim: sim, opts: opts, C: C, lagrange: LP,
      setIC: setIC, reset: reset, oneStep: oneStep, render: render,
      runSelfTests: C.runSelfTests, ready: true
    };
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
