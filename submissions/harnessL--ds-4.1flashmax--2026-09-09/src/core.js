/* =====================================================================
   CR3BP core — Earth-Moon circular restricted three-body problem
   Pure numerics. No DOM, no rendering, no hidden state beyond CR3BP.
   Loads as a Node module (require) and as a browser global (window.CR3BP).
   Units: distance = Earth-Moon separation, time = 1/omega, mass ratio mu.
   Frame: rotating, barycentre at origin, Earth at (-mu,0), Moon at (1-mu,0).
   ===================================================================== */
(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module && module.exports) module.exports = api;
  if (typeof root !== 'undefined' && root) root.CR3BP = api;
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  /* ------------------------------------------------------------------ */
  /* 1. constants                                                        */
  /* ------------------------------------------------------------------ */
  var MU_EARTH_MOON = 0.012150585609624;      // M_moon / (M_earth + M_moon)
  var DU_KM   = 384400.0;                     // distance unit (km)
  var TU_DAYS = 27.321661 / (2 * Math.PI);    // time unit (days)
  var VU_KMS  = (DU_KM / TU_DAYS) / 86400.0;  // velocity unit (km/s)
  var R_EARTH = 6371.0 / DU_KM;               // Earth radius in DU  (0.016571)
  var R_MOON  = 1737.4 / DU_KM;               // Moon radius in DU   (0.004520)
  var R_SINGULARITY = 1e-4;                   // numerical singularity guard (DU)

  /* ------------------------------------------------------------------ */
  /* 2. counters (force evaluations, steps, rejects, guards)             */
  /* ------------------------------------------------------------------ */
  var STATS = { evals: 0, steps: 0, rejects: 0, guards: 0 };
  function resetStats() { STATS.evals = 0; STATS.steps = 0; STATS.rejects = 0; STATS.guards = 0; }
  function snapshotStats() {
    return { evals: STATS.evals, steps: STATS.steps, rejects: STATS.rejects, guards: STATS.guards };
  }

  /* ------------------------------------------------------------------ */
  /* 3. potential, gradient, Hessian, Jacobi constant                    */
  /* ------------------------------------------------------------------ */
  function omega(x, y, z, mu) {
    var d1 = x + mu, d2 = x - 1 + mu;
    var r1 = Math.sqrt(d1 * d1 + y * y + z * z);
    var r2 = Math.sqrt(d2 * d2 + y * y + z * z);
    return 0.5 * (x * x + y * y) + (1 - mu) / r1 + mu / r2;
  }

  function gradOmega(x, y, z, mu) {
    var d1 = x + mu, d2 = x - 1 + mu;
    var r1s = d1 * d1 + y * y + z * z, r2s = d2 * d2 + y * y + z * z;
    var r1 = Math.sqrt(r1s), r2 = Math.sqrt(r2s);
    var r1c = r1s * r1, r2c = r2s * r2;      // r^3
    return [
      x - (1 - mu) * d1 / r1c - mu * d2 / r2c,
      y - (1 - mu) * y / r1c - mu * y / r2c,
      -(1 - mu) * z / r1c - mu * z / r2c
    ];
  }

  /* gravitational potential U = (1-mu)/r1 + mu/r2 and its gradient.
     The CR3BP Hamiltonian in canonical momenta (p_x = x'-y, p_y = y'+x) is
       H = (1/2)|p|^2 + (y p_x - x p_y) - U,
     so the rotation-split symplectic step must kick with grad U, not grad Omega
     (grad Omega = grad U + (x,y,0); the centrifugal part is carried by the
      canonical rotation term).                                       */
  function gradU(x, y, z, mu) {
    var d1 = x + mu, d2 = x - 1 + mu;
    var r1s = d1 * d1 + y * y + z * z, r2s = d2 * d2 + y * y + z * z;
    var r1c = r1s * Math.sqrt(r1s), r2c = r2s * Math.sqrt(r2s);
    return [
      -(1 - mu) * d1 / r1c - mu * d2 / r2c,
      -(1 - mu) * y / r1c - mu * y / r2c,
      -(1 - mu) * z / r1c - mu * z / r2c
    ];
  }

  function hessOmega(x, y, z, mu) {
    var d1 = x + mu, d2 = x - 1 + mu;
    var r1s = d1 * d1 + y * y + z * z, r2s = d2 * d2 + y * y + z * z;
    var r1 = Math.sqrt(r1s), r2 = Math.sqrt(r2s);
    var r1c = r1s * r1, r2c = r2s * r2;
    var r1f = r1c * r1s, r2f = r2c * r2s;    // r^5
    var inv13 = 1 / r1c, inv23 = 1 / r2c, inv15 = 1 / r1f, inv25 = 1 / r2f;
    var xx = 1 - (1 - mu) * inv13 - mu * inv23 + 3 * (1 - mu) * d1 * d1 * inv15 + 3 * mu * d2 * d2 * inv25;
    var yy = 1 - (1 - mu) * inv13 - mu * inv23 + 3 * (1 - mu) * y * y * inv15 + 3 * mu * y * y * inv25;
    var zz = -(1 - mu) * inv13 - mu * inv23 + 3 * (1 - mu) * z * z * inv15 + 3 * mu * z * z * inv25;
    var xy = 3 * (1 - mu) * d1 * y * inv15 + 3 * mu * d2 * y * inv25;
    var xz = 3 * (1 - mu) * d1 * z * inv15 + 3 * mu * d2 * z * inv25;
    var yz = 3 * (1 - mu) * y * z * inv15 + 3 * mu * y * z * inv25;
    return { xx: xx, yy: yy, zz: zz, xy: xy, xz: xz, yz: yz };
  }

  function jacobi(s, mu) {
    var v2 = s.vx * s.vx + s.vy * s.vy + s.vz * s.vz;
    return 2 * omega(s.x, s.y, s.z, mu) - v2;
  }

  function dist1(s, mu) { return Math.hypot(s.x + mu, s.y, s.z); }
  function dist2(s, mu) { return Math.hypot(s.x - 1 + mu, s.y, s.z); }

  /* rotating-frame equations of motion:
       x'' =  2 y' + Omega_x
       y'' = -2 x' + Omega_y
       z'' =         Omega_z                                          */
  function deriv6(s, mu) {
    var g = gradOmega(s.x, s.y, s.z, mu);
    return {
      x: s.vx, y: s.vy, z: s.vz,
      vx: 2 * s.vy + g[0],
      vy: -2 * s.vx + g[1],
      vz: g[2]
    };
  }

  function axpy(s, k, h) {
    return {
      x: s.x + h * k.x, y: s.y + h * k.y, z: s.z + h * k.z,
      vx: s.vx + h * k.vx, vy: s.vy + h * k.vy, vz: s.vz + h * k.vz
    };
  }

  function cloneState(s) { return { x: s.x, y: s.y, z: s.z, vx: s.vx, vy: s.vy, vz: s.vz }; }
  function isFiniteState(s) {
    return Number.isFinite(s.x) && Number.isFinite(s.y) && Number.isFinite(s.z) &&
           Number.isFinite(s.vx) && Number.isFinite(s.vy) && Number.isFinite(s.vz);
  }

  /* ------------------------------------------------------------------ */
  /* 4. Lagrange points                                                  */
  /* ------------------------------------------------------------------ */
  function collinearF(x, mu) { return gradOmega(x, 0, 0, mu)[0]; }

  /* bisection on a sign-changing bracket, then Newton polish */
  function solveCollinear(mu, lo, hi) {
    var flo = collinearF(lo, mu), fhi = collinearF(hi, mu);
    if (!Number.isFinite(flo) || !Number.isFinite(fhi) || flo * fhi > 0) return NaN;
    var a = lo, b = hi;
    for (var i = 0; i < 200 && (b - a) > 1e-16 * Math.max(1, Math.abs(a)); i++) {
      var m = 0.5 * (a + b), fm = collinearF(m, mu);
      if (fm === 0) { a = b = m; break; }
      if (flo * fm <= 0) { b = m; } else { a = m; flo = fm; }
    }
    var x = 0.5 * (a + b);
    /* Newton polish with central differences */
    for (var k = 0; k < 8; k++) {
      var h = 1e-7 * Math.max(1e-3, Math.abs(x));
      var f = collinearF(x, mu);
      var d = (collinearF(x + h, mu) - collinearF(x - h, mu)) / (2 * h);
      if (!Number.isFinite(f) || !Number.isFinite(d) || d === 0) break;
      var step = f / d;
      var xn = x - step;
      if (!Number.isFinite(xn)) break;
      x = xn;
      if (Math.abs(step) < 1e-15) break;
    }
    return x;
  }

  function lagrangePoints(mu) {
    var eps = 1e-7;
    var L1x = solveCollinear(mu, -mu + eps, 1 - mu - eps);
    var L2x = solveCollinear(mu, 1 - mu + eps, 3.0);
    var L3x = solveCollinear(mu, -3.0, -mu - eps);
    var s3 = Math.sqrt(3) / 2;
    var pts = {
      L1: { x: L1x, y: 0, z: 0, kind: 'collinear' },
      L2: { x: L2x, y: 0, z: 0, kind: 'collinear' },
      L3: { x: L3x, y: 0, z: 0, kind: 'collinear' },
      L4: { x: 0.5 - mu, y: s3, z: 0, kind: 'triangular' },
      L5: { x: 0.5 - mu, y: -s3, z: 0, kind: 'triangular' }
    };
    var names = ['L1', 'L2', 'L3', 'L4', 'L5'];
    var maxResidual = 0, resids = {};
    for (var i = 0; i < names.length; i++) {
      var p = pts[names[i]];
      var g = gradOmega(p.x, p.y, p.z, mu);
      var r = Math.sqrt(g[0] * g[0] + g[1] * g[1] + g[2] * g[2]);
      resids[names[i]] = r;
      if (!(r <= maxResidual)) maxResidual = r;
      p.residual = r;
      p.C = jacobi({ x: p.x, y: p.y, z: p.z, vx: 0, vy: 0, vz: 0 }, mu);
    }
    return { points: pts, residuals: resids, maxResidual: maxResidual };
  }

  /* linear stability of an equilibrium: eigenvalues of
       A = [[0,0,1,0],[0,0,0,1],[Oxx,Oxy,0,2],[Oxy,Oyy,-2,0]]
     characteristic polynomial in L = lambda^2:  L^2 + U L + V = 0,
       U = 4 - Oxx - Oyy,  V = Oxx*Oyy - Oxy^2.
     Collinear points: V < 0  -> one positive real root -> unstable.
     Triangular points: stable (purely imaginary lambda) iff 1 - 27 mu (1-mu) >= 0. */
  function stability(p, mu) {
    var H = hessOmega(p.x, p.y, p.z, mu);
    var U = 4 - H.xx - H.yy;
    var V = H.xx * H.yy - H.xy * H.xy;
    var disc = U * U - 4 * V;
    var L1r = (-U + Math.sqrt(disc)) / 2, L2r = (-U - Math.sqrt(disc)) / 2;
    var maxRealLambda = 0;
    var roots = [L1r, L2r];
    for (var i = 0; i < 2; i++) {
      var L = roots[i];
      if (L >= 0) { maxRealLambda = Math.max(maxRealLambda, Math.sqrt(L)); }
      else { maxRealLambda = Math.max(maxRealLambda, 0); }
    }
    return { U: U, V: V, disc: disc, Lroots: roots, maxRealLambda: maxRealLambda,
             unstable: maxRealLambda > 1e-12, hess: H };
  }

  /* ------------------------------------------------------------------ */
  /* 5. integrators                                                      */
  /* ------------------------------------------------------------------ */
  /* physical <-> canonical momenta  (p_x = x' - y, p_y = y' + x, p_z = z') */
  function toCanon(s) { return { x: s.x, y: s.y, z: s.z, px: s.vx - s.y, py: s.vy + s.x, pz: s.vz }; }
  function toPhys(c) { return { x: c.x, y: c.y, z: c.z, vx: c.px + c.y, vy: c.py - c.x, vz: c.pz }; }

  /* exact flow of H_B = y*p_x - x*p_y  (rotation, clockwise for a>0) */
  function rotCanon(c, a) {
    var ca = Math.cos(a), sa = Math.sin(a);
    return {
      x:  ca * c.x + sa * c.y,
      y: -sa * c.x + ca * c.y,
      z: c.z,
      px:  ca * c.px + sa * c.py,
      py: -sa * c.px + ca * c.py,
      pz: c.pz
    };
  }

  /* one symmetric 2nd-order symplectic step of the rotation splitting:
       Phi2(t) = rot(t/2) . kick(t/2) . drift(t) . kick(t/2) . rot(t/2)      */
  function symBase(c, dt, mu) {
    var st = rotCanon(c, dt / 2);
    var g = gradU(st.x, st.y, st.z, mu); STATS.evals++;
    st.px += (dt / 2) * g[0]; st.py += (dt / 2) * g[1]; st.pz += (dt / 2) * g[2];
    st.x += dt * st.px; st.y += dt * st.py; st.z += dt * st.pz;
    g = gradU(st.x, st.y, st.z, mu); STATS.evals++;
    st.px += (dt / 2) * g[0]; st.py += (dt / 2) * g[1]; st.pz += (dt / 2) * g[2];
    return rotCanon(st, dt / 2);
  }

  function stepRK4(s, dt, mu) {
    var k1 = deriv6(s, mu); STATS.evals++;
    var k2 = deriv6(axpy(s, k1, dt / 2), mu); STATS.evals++;
    var k3 = deriv6(axpy(s, k2, dt / 2), mu); STATS.evals++;
    var k4 = deriv6(axpy(s, k3, dt), mu); STATS.evals++;
    return {
      x:  s.x  + (dt / 6) * (k1.x  + 2 * k2.x  + 2 * k3.x  + k4.x),
      y:  s.y  + (dt / 6) * (k1.y  + 2 * k2.y  + 2 * k3.y  + k4.y),
      z:  s.z  + (dt / 6) * (k1.z  + 2 * k2.z  + 2 * k3.z  + k4.z),
      vx: s.vx + (dt / 6) * (k1.vx + 2 * k2.vx + 2 * k3.vx + k4.vx),
      vy: s.vy + (dt / 6) * (k1.vy + 2 * k2.vy + 2 * k3.vy + k4.vy),
      vz: s.vz + (dt / 6) * (k1.vz + 2 * k2.vz + 2 * k3.vz + k4.vz)
    };
  }

  /* Yoshida (1990) symmetric compositions of a symmetric 2nd-order map.
     4th order: S(w1 t) S(w0 t) S(w1 t)
     6th order: S(w1 t) S(w2 t) S(w3 t) S(w0 t) S(w3 t) S(w2 t) S(w1 t)   */
  var Y4_W1 = 1.0 / (2.0 - Math.cbrt(2.0));
  var Y4_W0 = -Math.cbrt(2.0) / (2.0 - Math.cbrt(2.0));
  var Y6 = [0.784513610477560, 0.235573213359357, -1.17767998417887, 1.315186320683906,
            -1.17767998417887, 0.235573213359357, 0.784513610477560];

  function stepVerlet(s, dt, mu) { return toPhys(symBase(toCanon(s), dt, mu)); }

  function stepYoshida4(s, dt, mu) {
    var c = toCanon(s);
    c = symBase(c, Y4_W1 * dt, mu);
    c = symBase(c, Y4_W0 * dt, mu);
    c = symBase(c, Y4_W1 * dt, mu);
    return toPhys(c);
  }

  function stepYoshida6(s, dt, mu) {
    var c = toCanon(s);
    for (var i = 0; i < Y6.length; i++) c = symBase(c, Y6[i] * dt, mu);
    return toPhys(c);
  }

  /* Dormand-Prince 5(4), adaptive. Returns one attempted step. */
  var DP_A = [
    [],
    [1 / 5],
    [3 / 40, 9 / 40],
    [44 / 45, -56 / 15, 32 / 9],
    [19372 / 6561, -25360 / 2187, 64448 / 6561, -212 / 729],
    [9017 / 3168, -355 / 33, 46732 / 5247, 49 / 176, -5103 / 18656],
    [35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84]
  ];
  var DP_C = [0, 1 / 5, 3 / 10, 4 / 5, 8 / 9, 1, 1];
  var DP_B5 = [35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84, 0];
  var DP_B4 = [5179 / 57600, 0, 7571 / 16695, 393 / 640, -92097 / 339200, 187 / 2100, 1 / 40];

  function stepDOPRI5(s, dt, mu, rtol, atol) {
    rtol = rtol == null ? 1e-10 : rtol;
    atol = atol == null ? 1e-12 : atol;
    var k = new Array(7), i, j;
    k[0] = deriv6(s, mu); STATS.evals++;
    var tmp = cloneState(s);
    for (i = 1; i < 7; i++) {
      tmp = cloneState(s);
      var a = DP_A[i];
      for (j = 0; j < i; j++) {
        tmp.x  += dt * a[j] * k[j].x;
        tmp.y  += dt * a[j] * k[j].y;
        tmp.z  += dt * a[j] * k[j].z;
        tmp.vx += dt * a[j] * k[j].vx;
        tmp.vy += dt * a[j] * k[j].vy;
        tmp.vz += dt * a[j] * k[j].vz;
      }
      k[i] = deriv6(tmp, mu); STATS.evals++;
    }
    var y5 = cloneState(s), y4 = cloneState(s), err = 0;
    var scale = { x: 0, y: 0, z: 0, vx: 0, vy: 0, vz: 0 };
    var names = ['x', 'y', 'z', 'vx', 'vy', 'vz'];
    for (i = 0; i < 7; i++) {
      y5.x  += dt * DP_B5[i] * k[i].x;  y4.x  += dt * DP_B4[i] * k[i].x;
      y5.y  += dt * DP_B5[i] * k[i].y;  y4.y  += dt * DP_B4[i] * k[i].y;
      y5.z  += dt * DP_B5[i] * k[i].z;  y4.z  += dt * DP_B4[i] * k[i].z;
      y5.vx += dt * DP_B5[i] * k[i].vx; y4.vx += dt * DP_B4[i] * k[i].vx;
      y5.vy += dt * DP_B5[i] * k[i].vy; y4.vy += dt * DP_B4[i] * k[i].vy;
      y5.vz += dt * DP_B5[i] * k[i].vz; y4.vz += dt * DP_B4[i] * k[i].vz;
    }
    for (i = 0; i < 6; i++) {
      var nm = names[i];
      var sc = atol + rtol * Math.max(Math.abs(s[nm]), Math.abs(y5[nm]));
      var e = (y5[nm] - y4[nm]) / sc;
      err += e * e;
    }
    err = Math.sqrt(err / 6);
    var fac = 0.9 * Math.pow(err === 0 ? 1e-16 : err, -0.2);
    fac = err > 1 ? Math.max(0.1, fac) : Math.min(5.0, Math.max(0.2, fac));
    var dtNext = dt * fac;
    var accepted = err <= 1.0 && Number.isFinite(err);
    if (!accepted) STATS.rejects++;
    return { state: accepted ? y5 : cloneState(s), dtUsed: dt, dtNext: dtNext,
             accepted: accepted, errNorm: err };
  }

  /* ---- Gragg-Bulirsch-Stoer: modified midpoint + Neville extrapolation ---- */
  var GBS_SEQ_HARMONIC = [2, 4, 6, 8, 10, 12, 14, 16];
  var GBS_SEQ_BULIRSCH = [2, 4, 6, 8, 12, 16, 24, 32];
  var GBS_SEQ = GBS_SEQ_HARMONIC;   /* default; stepGBS/stepGBSFix take a sequence override */
  function gbsSequence(name) {
    if (name === 'bulirsch') return GBS_SEQ_BULIRSCH;
    return GBS_SEQ_HARMONIC;
  }

  function subState(a, b) {
    return { x: a.x - b.x, y: a.y - b.y, z: a.z - b.z, vx: a.vx - b.vx, vy: a.vy - b.vy, vz: a.vz - b.vz };
  }
  function addScaledState(a, b, c) {
    return { x: a.x + c * b.x, y: a.y + c * b.y, z: a.z + c * b.z,
             vx: a.vx + c * b.vx, vy: a.vy + c * b.vy, vz: a.vz + c * b.vz };
  }
  function scaledErrNorm(a, b, ref, rtol, atol) {
    var names = ['x', 'y', 'z', 'vx', 'vy', 'vz'], e = 0, i, nm, sc, d;
    for (i = 0; i < 6; i++) {
      nm = names[i];
      sc = atol + rtol * Math.max(Math.abs(ref[nm]), Math.abs(a[nm]));
      d = (a[nm] - b[nm]) / sc;
      e += d * d;
    }
    return Math.sqrt(e / 6);
  }

  /* one pass of the modified midpoint method: n substeps of h = H/n */
  function mmidState(s, H, n, mu) {
    var h = H / n;
    var f = deriv6(s, mu); STATS.evals++;
    var zprev = cloneState(s);
    var zcur = axpy(s, f, h);
    for (var m = 1; m < n; m++) {
      f = deriv6(zcur, mu); STATS.evals++;
      var znext = {
        x: zprev.x + 2 * h * f.x, y: zprev.y + 2 * h * f.y, z: zprev.z + 2 * h * f.z,
        vx: zprev.vx + 2 * h * f.vx, vy: zprev.vy + 2 * h * f.vy, vz: zprev.vz + 2 * h * f.vz
      };
      zprev = zcur; zcur = znext;
    }
    f = deriv6(zcur, mu); STATS.evals++;
    return {
      x: 0.5 * (zcur.x + zprev.x + h * f.x), y: 0.5 * (zcur.y + zprev.y + h * f.y),
      z: 0.5 * (zcur.z + zprev.z + h * f.z), vx: 0.5 * (zcur.vx + zprev.vx + h * f.vx),
      vy: 0.5 * (zcur.vy + zprev.vy + h * f.vy), vz: 0.5 * (zcur.vz + zprev.vz + h * f.vz)
    };
  }

  /* extrapolation core shared by the adaptive and the fixed-step GBS variants */
  function gbsExtrapolate(s, H, mu, k, seqName) {
    var SEQ = gbsSequence(seqName);
    k = Math.max(2, Math.min(SEQ.length, k || 4));
    var T = [], i, m;
    for (i = 0; i < k; i++) {
      var ni = SEQ[i];
      var y = mmidState(s, H, ni, mu);
      var row = [y];
      for (m = 1; m <= i; m++) {
        var den = Math.pow(ni / SEQ[i - m], 2) - 1;   // (n_fine/n_coarse)^2 - 1
        row.push(addScaledState(row[m - 1], subState(row[m - 1], T[i - 1][m - 1]), 1 / den));
      }
      T.push(row);
    }
    return { best: T[k - 1][k - 1], prev: T[k - 1][k - 2], order: 2 * k, k: k };
  }

  /* extrapolate k rows of the harmonic sequence -> order 2k; returns accepted?/dtNext */
  function stepGBS(s, H, mu, rtol, atol, k, seqName) {
    rtol = rtol == null ? 1e-10 : rtol;
    atol = atol == null ? 1e-14 : atol;
    var ex = gbsExtrapolate(s, H, mu, k, seqName);
    var best = ex.best, prev = ex.prev, order = ex.order;
    var err = scaledErrNorm(best, prev, s, rtol, atol);
    var fac = 0.9 * Math.pow(err === 0 ? 1e-16 : err, -1 / (order + 1));
    fac = err > 1 ? Math.max(0.1, fac) : Math.min(5.0, Math.max(0.2, fac));
    var accepted = err <= 1.0 && Number.isFinite(err) && isFiniteState(best);
    if (!accepted) STATS.rejects++;
    return { state: accepted ? best : cloneState(s), dtUsed: H, dtNext: H * fac,
             accepted: accepted, errNorm: err };
  }

  /* fixed-step GBS: one extrapolation step at a prescribed H, no error control */
  function stepGBSFix(s, H, mu, k, seqName) {
    var ex = gbsExtrapolate(s, H, mu, k, seqName);
    return ex.best;
  }

  /* step-doubling error control around any base map of order p */
  function stepDoubling(baseStep, p, s, H, mu, rtol, atol) {
    rtol = rtol == null ? 1e-10 : rtol;
    atol = atol == null ? 1e-14 : atol;
    var y1 = baseStep(s, H, mu);
    var yh = baseStep(s, H / 2, mu);
    var y2 = baseStep(yh, H / 2, mu);
    var err = scaledErrNorm(y2, y1, s, rtol, atol) / (Math.pow(2, p) - 1);
    var fac = 0.9 * Math.pow(err === 0 ? 1e-16 : err, -1 / (p + 1));
    fac = err > 1 ? Math.max(0.1, fac) : Math.min(5.0, Math.max(0.2, fac));
    var accepted = err <= 1.0 && Number.isFinite(err) && isFiniteState(y2);
    if (!accepted) STATS.rejects++;
    return { state: accepted ? y2 : cloneState(s), dtUsed: H, dtNext: H * fac,
             accepted: accepted, errNorm: err };
  }

  function stepARK4(s, H, mu, rtol, atol) { return stepDoubling(stepRK4, 4, s, H, mu, rtol, atol); }
  function stepSymAdapt(s, H, mu, rtol, atol) { return stepDoubling(stepYoshida4, 4, s, H, mu, rtol, atol); }

  var METHODS = {
    rk4:      { name: 'RK4',            order: 4, evalsPerStep: 4, symplectic: false, adaptive: false,
                step: stepRK4, blurb: 'classic explicit Runge-Kutta, 4 stages' },
    verlet:   { name: 'Verlet (symplectic, 2)', order: 2, evalsPerStep: 2, symplectic: true, adaptive: false,
                step: stepVerlet, blurb: 'rotation-splitting leapfrog' },
    yoshida4: { name: 'Yoshida-4 (symplectic, 4)', order: 4, evalsPerStep: 6, symplectic: true, adaptive: false,
                step: stepYoshida4, blurb: '3 x symmetric 2nd-order composition' },
    yoshida6: { name: 'Yoshida-6 (symplectic, 6)', order: 6, evalsPerStep: 14, symplectic: true, adaptive: false,
                step: stepYoshida6, blurb: '7 x symmetric 2nd-order composition' },
    dopri5:   { name: 'DOPRI5 (adaptive, 5)', order: 5, evalsPerStep: 6, symplectic: false, adaptive: true,
                step: null, blurb: 'Dormand-Prince 5(4) with error control' },
    gbs:      { name: 'GBS (adaptive extrapolation)', order: 8, evalsPerStep: 24, symplectic: false, adaptive: true,
                step: null, blurb: 'Gragg-Bulirsch-Stoer, order 2k from the harmonic sequence' },
    gbsfix:   { name: 'GBS-fixed (order 8)', order: 8, evalsPerStep: 24, symplectic: false, adaptive: false,
                step: null, blurb: 'one Gragg-Bulirsch-Stoer extrapolation step at a prescribed H' },
    ark4:     { name: 'Adaptive RK4 (step doubling)', order: 4, evalsPerStep: 12, symplectic: false, adaptive: true,
                step: null, blurb: 'RK4 with step-doubling error control' },
    symadapt: { name: 'Adaptive symplectic-4 (step doubling)', order: 4, evalsPerStep: 18, symplectic: true, adaptive: true,
                step: null, blurb: 'Yoshida-4 with step doubling; map structure kept, exact symplecticity lost when H varies' }
  };

  /* stateful stepper used by both the app and the benchmark */
  function makeStepper(cfg) {
    var method = cfg.method || 'yoshida4';
    if (!METHODS[method]) throw new Error('unknown method ' + method);
    var dt = cfg.dt == null ? 1e-3 : cfg.dt;
    var rtol = cfg.rtol == null ? 1e-10 : cfg.rtol;
    var atol = cfg.atol == null ? 1e-12 : cfg.atol;
    var dtAdaptive = cfg.dtAdaptive == null ? dt : cfg.dtAdaptive;
    var gbsK = cfg.gbsK == null ? 4 : cfg.gbsK;
    var gbsSeq = cfg.gbsSeq || 'harmonic';
    var obj = {
      method: method,
      order: METHODS[method].order,
      evalsPerStep: METHODS[method].evalsPerStep,
      symplectic: METHODS[method].symplectic,
      adaptive: METHODS[method].adaptive,
      get dt() { return dt; },
      set dt(v) { dt = v; dtAdaptive = v; },
      get rtol() { return rtol; },
      set rtol(v) { rtol = v; },
      set atol(v) { atol = v; },
      get adaptiveDt() { return dtAdaptive; },
      step: function (s, mu, dtOverride) {
        if (METHODS[method].adaptive) {
          var h = dtOverride == null ? dtAdaptive : dtOverride;
          var r;
          if (method === 'gbs') r = stepGBS(s, h, mu, rtol, atol, gbsK, gbsSeq);
          else if (method === 'ark4') r = stepARK4(s, h, mu, rtol, atol);
          else if (method === 'symadapt') r = stepSymAdapt(s, h, mu, rtol, atol);
          else r = stepDOPRI5(s, h, mu, rtol, atol);
          if (dtOverride == null) dtAdaptive = r.dtNext;
          return r;
        }
        var hf = dtOverride == null ? dt : dtOverride;
        STATS.steps++;
        var st = (method === 'gbsfix') ? stepGBSFix(s, hf, mu, gbsK, gbsSeq) : METHODS[method].step(s, hf, mu);
        return { state: st, dtUsed: hf, accepted: true, errNorm: 0 };
      }
    };
    return obj;
  }

  /* ------------------------------------------------------------------ */
  /* 6. guards                                                           */
  /* ------------------------------------------------------------------ */
  function guardState(s, mu) {
    if (!isFiniteState(s)) return { ok: false, code: 'nonfinite', message: 'state is not finite (NaN/Inf)' };
    var r1 = dist1(s, mu), r2 = dist2(s, mu);
    if (r1 < R_SINGULARITY || r2 < R_SINGULARITY)
      return { ok: false, code: 'singularity', message: 'singularity: r < ' + R_SINGULARITY + ' DU' };
    if (r1 < R_EARTH) return { ok: false, code: 'impact-earth', message: 'impact with Earth (r1 < R_earth)' };
    if (r2 < R_MOON)  return { ok: false, code: 'impact-moon',  message: 'impact with Moon (r2 < R_moon)' };
    var rr = Math.hypot(s.x, s.y, s.z), vv = Math.hypot(s.vx, s.vy, s.vz);
    if (rr > 1e6 || vv > 1e6)
      return { ok: false, code: 'diverged', message: 'state diverged: |r|=' + rr.toExponential(2) + ' |v|=' + vv.toExponential(2) };
    return { ok: true, code: 'ok', message: '' };
  }

  function validateDt(dt) {
    if (!Number.isFinite(dt)) return 'dt is not finite';
    if (dt === 0) return 'dt is zero';
    if (dt < 0) return 'dt is negative';
    return null;
  }

  /* ------------------------------------------------------------------ */
  /* 7. integration driver                                               */
  /* ------------------------------------------------------------------ */
  /* opts: { method, dt, T, mu, rtol, atol, budget (force evals), sampleEvery,
            collectTraj, guard:true }                                        */
  function integrate(s0, opts) {
    opts = opts || {};
    var mu = opts.mu == null ? MU_EARTH_MOON : opts.mu;
    var method = opts.method || 'yoshida4';
    var T = opts.T == null ? 1.0 : opts.T;
    var forward = T >= 0;
    var budget = opts.budget == null ? Infinity : opts.budget;
    var dt = opts.dt == null ? 1e-3 : opts.dt;
    var stepper = makeStepper({ method: method, dt: dt, rtol: opts.rtol, atol: opts.atol, gbsK: opts.gbsK, gbsSeq: opts.gbsSeq });
    var C0 = jacobi(s0, mu);
    var absC0 = Math.max(Math.abs(C0), 1e-12);
    var s = cloneState(s0), t = 0, steps = 0, rejects = 0;
    var driftMax = 0, driftHalf1 = 0, driftHalf2 = 0, minAllowed = Infinity, maxR = 0;
    var dtMin = Infinity, dtSum = 0;
    var traj = opts.collectTraj ? [cloneState(s0)] : null;
    var status = 'ok', message = '', guardHit = null;
    var e0 = snapshotStats();
    var maxIter = 5e7;

    while ((forward ? t < T : t > T) && (snapshotStats().evals - e0.evals) < budget && steps < maxIter) {
      if (opts.guard !== false) {
        var gPre = guardState(s, mu);
        if (!gPre.ok) {
          status = gPre.code; message = gPre.message;
          guardHit = { t: t, code: gPre.code, message: gPre.message, state: cloneState(s) };
          STATS.guards++;
          break;
        }
      }
      var dtUse = stepper.adaptive ? stepper.adaptiveDt : stepper.dt;
      if (!Number.isFinite(dtUse) || dtUse === 0) { status = 'invalid-dt'; message = 'zero or non-finite step'; break; }
      if ((forward && dtUse < 0) || (!forward && dtUse > 0)) {
        status = 'invalid-dt'; message = 'step sign does not match the integration span'; break;
      }
      var clamped = false;
      if (forward ? (t + dtUse > T) : (t + dtUse < T)) { dtUse = T - t; clamped = true; }
      if (dtUse === 0) break;

      var out;
      try { out = stepper.step(s, mu, clamped ? dtUse : undefined); }
      catch (e) { status = 'exception'; message = String(e && e.message || e); break; }
      if (!out.accepted) { rejects++; if (rejects > 1e6) { status = 'stalled'; message = 'adaptive step rejected > 1e6 times'; break; } continue; }

      s = out.state; t += dtUse; steps++;
      if (dtUse < dtMin) dtMin = dtUse;
      dtSum += dtUse;

      if (!isFiniteState(s)) {
        status = 'nonfinite'; message = 'state became non-finite at t=' + t.toExponential(3);
        STATS.guards++;
        guardHit = { t: t, code: 'nonfinite', message: message, state: cloneState(s) };
        break;
      }
      if (opts.guard !== false) {
        var g = guardState(s, mu);
        if (!g.ok) {
          status = g.code; message = g.message; guardHit = { t: t, code: g.code, message: g.message, state: cloneState(s) };
          STATS.guards++;
          break;
        }
      }
      var C = jacobi(s, mu);
      var d = Math.abs(C - C0) / absC0;
      if (d > driftMax) driftMax = d;
      if (T !== 0 ? (t / T) <= 0.5 : true) { if (d > driftHalf1) driftHalf1 = d; }
      else { if (d > driftHalf2) driftHalf2 = d; }
      var om = omega(s.x, s.y, s.z, mu);
      var allowed = 2 * om - C;              // = v^2 >= 0 for an exact trajectory
      if (allowed < minAllowed) minAllowed = allowed;
      var rr = Math.hypot(s.x, s.y, s.z);
      if (rr > maxR) maxR = rr;
      if (opts.escapeR != null && rr > opts.escapeR) {
        status = 'escaped'; message = 'escaped to |r| > ' + opts.escapeR + ' at t=' + t.toFixed(3);
        guardHit = { t: t, code: 'escaped', message: message, state: cloneState(s) };
        STATS.guards++;
        break;
      }
      if (traj) traj.push(cloneState(s));
    }
    var e1 = snapshotStats();
    return {
      state: s, t: t, C0: C0, C: jacobi(s, mu), steps: steps, rejects: rejects,
      evals: e1.evals - e0.evals, driftMax: driftMax, driftHalf1: driftHalf1, driftHalf2: driftHalf2,
      minAllowed: minAllowed, maxR: maxR, status: status, message: message, guardHit: guardHit,
      dtMin: dtMin === Infinity ? 0 : dtMin, dtMean: steps ? dtSum / steps : 0,
      traj: traj, finished: forward ? (t >= T - 1e-15) : (t <= T + 1e-15)
    };
  }

  /* ------------------------------------------------------------------ */
  /* 8. presets                                                          */
  /* ------------------------------------------------------------------ */
  function presets(mu) {
    var lp = lagrangePoints(mu);
    var s3 = Math.sqrt(3) / 2;
    return [
      { id: 'l4', name: 'L4 稳定岛 / tadpole', expect: 'librates around L4 (stable for mu < mu_Routh)',
        state: { x: 0.5 - mu + 0.01, y: s3, z: 0, vx: 0, vy: 0, vz: 0 } },
      { id: 'l1', name: 'L1 不稳定鞍点', expect: 'departs from L1 exponentially',
        state: { x: lp.points.L1.x + 1e-3, y: 0, z: 0, vx: 0, vy: 0, vz: 0 } },
      { id: 'earth', name: '绕地轨道', expect: 'stays bound to Earth',
        state: { x: -mu + 0.1, y: 0, z: 0, vx: 0, vy: Math.sqrt(1 / 0.1) - 0.1, vz: 0 } },
      { id: 'moon', name: '月球引力辅助', expect: 'close approach to the Moon within one period',
        state: { x: 0.9936802819055943, y: 0.00031531731116218523, z: 0,
                 vx: -0.5212378117477119, vy: 1.9767638156628915, vz: 0 } }
    ];
  }

  /* ------------------------------------------------------------------ */
  /* 9. deterministic PRNG (for reproducible ensembles)                  */
  /* ------------------------------------------------------------------ */
  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /* ------------------------------------------------------------------ */
  /* 10. self-tests — every number below is computed, never hard-coded    */
  /* ------------------------------------------------------------------ */
  function errState(a, b) {
    var m = 0, names = ['x', 'y', 'z', 'vx', 'vy', 'vz'];
    for (var i = 0; i < 6; i++) m = Math.max(m, Math.abs(a[names[i]] - b[names[i]]));
    return m;
  }

  function observedOrder(errs, dts) {
    var ps = [];
    for (var i = 0; i + 1 < errs.length; i++) {
      if (errs[i] > 0 && errs[i + 1] > 0)
        ps.push(Math.log(errs[i] / errs[i + 1]) / Math.log(dts[i] / dts[i + 1]));
    }
    if (!ps.length) return NaN;
    ps.sort(function (a, b) { return a - b; });
    return ps[ps.length - 1];   // best (largest) observed order over the ladder
  }

  function runSelfTests(opts) {
    opts = opts || {};
    var mu = opts.mu == null ? MU_EARTH_MOON : opts.mu;
    var tests = [];
    function push(id, name, value, threshold, pass, detail, unit) {
      tests.push({ id: id, name: name, value: value, threshold: threshold, pass: !!pass,
                   detail: detail || '', unit: unit || '' });
    }

    /* ---- T1: Lagrange points ------------------------------------- */
    var lp = lagrangePoints(mu);
    push('lagrange-residual', '拉格朗日点梯度残差 max|∇Ω|', lp.maxResidual, 1e-10,
         lp.maxResidual < 1e-10,
         'L1..L5: ' + ['L1','L2','L3','L4','L5'].map(function (k) {
           return k + '=' + lp.residuals[k].toExponential(2);
         }).join(' '), '');
    var cs = ['L1','L2','L3','L4','L5'].map(function (k) { return k + ' C=' + lp.points[k].C.toFixed(6); }).join('  ');
    push('lagrange-C', '拉格朗日点 Jacobi 常数', lp.points.L4.C, 3.0, Math.abs(lp.points.L4.C - (3 - mu + mu * mu)) < 1e-12,
         cs + '  (C_L4 analytic 3-mu+mu^2 = ' + (3 - mu + mu * mu).toFixed(6) + ')', '');
    var st = {};
    ['L1','L2','L3','L4','L5'].forEach(function (k) { st[k] = stability(lp.points[k], mu); });
    var collinearUnstable = st.L1.unstable && st.L2.unstable && st.L3.unstable;
    var muRouth = 0.5 * (1 - Math.sqrt(23 / 27));   // 0.038521
    var triStable = !st.L4.unstable && !st.L5.unstable;
    push('lagrange-stability', 'L 点线性稳定性分类', triStable && collinearUnstable ? 1 : 0, 1,
         collinearUnstable && triStable,
         'collinear unstable (λmax>0): ' + collinearUnstable +
         '; triangular stable: ' + triStable +
         '; mu=' + mu.toFixed(6) + ' < mu_Routh=' + muRouth.toFixed(6), 'bool');

    /* ---- T2: step-size convergence --------------------------------- */
    var ic = opts.ic || presets(mu)[0].state;
    var Tconv = opts.Tconv == null ? 1.0 : opts.Tconv;
    var ref = integrate(ic, { method: 'dopri5', T: Tconv, mu: mu, rtol: 1e-13, atol: 1e-14, guard: false });
    var ladders = {
      verlet:   [1e-2, 5e-3, 2.5e-3, 1.25e-3],
      rk4:      [2e-2, 1e-2, 5e-3, 2.5e-3],
      yoshida4: [2e-2, 1e-2, 5e-3, 2.5e-3],
      yoshida6: [1.5e-1, 7.5e-2, 3.75e-2, 1.875e-2]
    };
    var orders = {};
    Object.keys(ladders).forEach(function (m) {
      var dts = ladders[m], errs = [];
      for (var i = 0; i < dts.length; i++) {
        var r = integrate(ic, { method: m, dt: dts[i], T: Tconv, mu: mu, guard: false });
        errs.push(errState(r.state, ref.state));
      }
      var p = observedOrder(errs, dts);
      orders[m] = { order: p, errs: errs, dts: dts };
      var nominal = METHODS[m].order;
      push('order-' + m, '步长收敛阶 ' + METHODS[m].name, p, nominal,
           Math.abs(p - nominal) <= (nominal >= 6 ? 1.0 : 0.6),
           'errors ' + errs.map(function (e) { return e.toExponential(1); }).join(', '), '');
    });

    /* GBS one-step order: k rows of the harmonic sequence -> order 2k */
    (function () {
      var Hs = [0.8, 0.4, 0.2, 0.1], errs = [];
      Hs.forEach(function (H) {
        var y = stepGBSFix(ic, H, mu, 4);
        var rf = integrate(ic, { method: 'dopri5', T: H, mu: mu, rtol: 1e-14, atol: 1e-16, guard: false });
        errs.push(errState(y, rf.state));
      });
      var pg = Math.log(errs[0] / errs[1]) / Math.log(Hs[0] / Hs[1]);
      push('order-gbs', 'GBS 外推单步收敛阶 (k=4 → 名义 8)', pg, 8, pg >= 6.0,
           'errors ' + errs.map(function (e) { return e.toExponential(1); }).join(', '), '');
    })();

    /* ---- T3: conservation — bounded (symplectic) vs secular (RK4) --- */
    var icSmooth = { x: 0.5 - mu + 0.005, y: Math.sqrt(3) / 2, z: 0, vx: 0, vy: 0, vz: 0 };
    var dtc = opts.dtCons == null ? 1e-2 : opts.dtCons;
    var Tshort = 4 * Math.PI, TlongC = 16 * Math.PI;
    var cons = {};
    ['rk4', 'yoshida4'].forEach(function (m) {
      cons[m] = {
        short: integrate(icSmooth, { method: m, dt: dtc, T: Tshort, mu: mu, guard: false }).driftMax,
        long: integrate(icSmooth, { method: m, dt: dtc, T: TlongC, mu: mu, guard: false }).driftMax
      };
    });
    var gSym = cons.yoshida4.short > 0 ? cons.yoshida4.long / cons.yoshida4.short : Infinity;
    var gRk = cons.rk4.short > 0 ? cons.rk4.long / cons.rk4.short : Infinity;
    push('conservation-bounded', '辛算法漂移有界：T=16π / T=4π 的最大漂移之比', gSym, 1.5, gSym < 1.5,
         'yoshida4 ' + cons.yoshida4.short.toExponential(2) + ' -> ' + cons.yoshida4.long.toExponential(2) +
         ' (dt=' + dtc + ', 4 倍时长)', 'ratio');
    push('conservation-secular', 'RK4 漂移随时长增长：T=16π / T=4π 的最大漂移之比', gRk, 1.5, gRk > 1.5,
         'rk4 ' + cons.rk4.short.toExponential(2) + ' -> ' + cons.rk4.long.toExponential(2) +
         ' (dt=' + dtc + ', 4 倍时长)', 'ratio');

    /* ---- T4: NaN / singularity guards ------------------------------ */
    var guardCases = [];
    var badMoon = { x: 1 - mu, y: 0, z: 0, vx: 0, vy: 0, vz: 0 };
    var g1 = guardState(badMoon, mu);
    guardCases.push({ name: 'state at Moon centre', ok: !g1.ok, code: g1.code });
    var badNan = { x: NaN, y: 0, z: 0, vx: 0, vy: 0, vz: 0 };
    guardCases.push({ name: 'NaN in state', ok: !guardState(badNan, mu).ok, code: guardState(badNan, mu).code });
    guardCases.push({ name: 'dt = 0 rejected', ok: validateDt(0) !== null, code: 'dt=0' });
    guardCases.push({ name: 'dt = NaN rejected', ok: validateDt(NaN) !== null, code: 'dt=NaN' });
    guardCases.push({ name: 'dt < 0 rejected', ok: validateDt(-1e-3) !== null, code: 'dt<0' });
    /* integrate a state exactly at the Moon: must stop with a guard, never emit NaN */
    var atMoon = integrate(badMoon, { method: 'rk4', dt: 1e-3, T: 1, mu: mu, guard: true });
    guardCases.push({ name: 'integration at Moon flagged', ok: atMoon.status !== 'ok' || !isFiniteState(atMoon.state),
                      code: atMoon.status });
    /* random ensemble: no silent non-finite escape */
    var rnd = mulberry32(20260909);
    var escaped = 0, flagged = 0, runs = opts.guardRuns == null ? 120 : opts.guardRuns;
    for (var i = 0; i < runs; i++) {
      var s0 = { x: -0.2 + 1.6 * rnd(), y: -0.8 + 1.6 * rnd(), z: -0.2 + 0.4 * rnd(),
                 vx: -2 + 4 * rnd(), vy: -2 + 4 * rnd(), vz: -0.5 + 1.0 * rnd() };
      var rr = integrate(s0, { method: 'rk4', dt: 5e-3, T: 2.0, mu: mu, guard: true });
      if (!isFiniteState(rr.state)) escaped++;
      if (rr.status !== 'ok') flagged++;
    }
    guardCases.push({ name: 'random ensemble: no NaN escape', ok: escaped === 0, code: 'escaped=' + escaped });
    var guardPass = guardCases.every(function (c) { return c.ok; });
    push('nan-guard', 'NaN / 奇点防护', guardPass ? 1 : 0, 1, guardPass,
         guardCases.map(function (c) { return c.name + '=' + (c.ok ? 'ok' : 'FAIL(' + c.code + ')'); }).join('; ') +
         '; flagged runs=' + flagged + '/' + runs, 'bool');

    /* ---- T5: trajectory stays inside the allowed ZVC region -------- */
    var zr = integrate(ic, { method: 'yoshida4', dt: dtc, T: TlongC, mu: mu, guard: false });
    push('zvc-allowed', '轨迹不越出零速度曲线允许区 min(2Ω−C)', zr.minAllowed, -1e-9, zr.minAllowed > -1e-9,
         'min(2Ω−C) along trajectory (should be v² >= 0)', '');

    /* ---- T6: time reversibility of the symplectic map -------------- */
    var fwd = integrate(ic, { method: 'yoshida4', dt: dtc, T: 1.0, mu: mu, guard: false });
    var back = integrate(fwd.state, { method: 'yoshida4', dt: -dtc, T: -1.0, mu: mu, guard: false });
    var revErr = errState(back.state, ic);
    push('reversibility', '辛算法时间可逆性 |forward∘backward − IC|', revErr, 1e-9, revErr < 1e-9,
         'after T=+1.0 then T=-1.0 with dt=±' + dtc + ' (backward reached t=' + back.t.toFixed(3) + ')', '');

    /* ---- T7: presets behave as advertised -------------------------- */
    var pre = presets(mu);
    var preResults = [];
    pre.forEach(function (p) {
      var r = integrate(p.state, { method: 'yoshida4', dt: 1e-3, T: 2 * Math.PI, mu: mu, guard: true, collectTraj: true });
      var ok = isFiniteState(r.state) && r.status === 'ok';
      var extra = '';
      if (p.id === 'l4') {
        var dmax = 0;
        for (var j = 0; j < r.traj.length; j++) {
          var q = r.traj[j];
          dmax = Math.max(dmax, Math.hypot(q.x - lp.points.L4.x, q.y - lp.points.L4.y));
        }
        ok = ok && dmax < 0.3; extra = 'max dist from L4 = ' + dmax.toFixed(4);
      } else if (p.id === 'l1') {
        var d1 = Math.hypot(r.state.x - lp.points.L1.x, r.state.y - lp.points.L1.y);
        ok = ok && d1 > 0.01; extra = 'final dist from L1 = ' + d1.toFixed(4);
      } else if (p.id === 'earth') {
        var r1max = 0, r1min = Infinity;
        for (var k2 = 0; k2 < r.traj.length; k2++) {
          var qq = r.traj[k2], d = Math.hypot(qq.x + mu, qq.y, qq.z);
          r1max = Math.max(r1max, d); r1min = Math.min(r1min, d);
        }
        ok = ok && r1max < 0.25; extra = 'r1 in [' + r1min.toFixed(4) + ', ' + r1max.toFixed(4) + ']';
      } else if (p.id === 'moon') {
        var r2min = Infinity;
        for (var k3 = 0; k3 < r.traj.length; k3++) {
          var q3 = r.traj[k3], dd = Math.hypot(q3.x - (1 - mu), q3.y, q3.z);
          r2min = Math.min(r2min, dd);
        }
        ok = ok && r2min < 0.15; extra = 'min dist to Moon = ' + r2min.toFixed(4);
      }
      preResults.push({ id: p.id, ok: ok, extra: extra, status: r.status });
    });
    var prePass = preResults.every(function (r) { return r.ok; });
    push('presets', '预设轨道符合动力学预期', prePass ? 1 : 0, 1, prePass,
         preResults.map(function (r) { return r.id + '=' + (r.ok ? 'ok' : 'FAIL') + (r.extra ? ' (' + r.extra + ')' : ''); }).join('; '), 'bool');

    var passed = tests.filter(function (t) { return t.pass; }).length;
    return {
      mu: mu, tests: tests, orders: orders,
      summary: { passed: passed, failed: tests.length - passed, total: tests.length },
      pass: passed === tests.length,
      generated_at: new Date().toISOString()
    };
  }

  /* ------------------------------------------------------------------ */
  /* 11. export                                                          */
  /* ------------------------------------------------------------------ */
  return {
    MU_EARTH_MOON: MU_EARTH_MOON,
    DU_KM: DU_KM, TU_DAYS: TU_DAYS, VU_KMS: VU_KMS,
    R_EARTH: R_EARTH, R_MOON: R_MOON, R_SINGULARITY: R_SINGULARITY,
    omega: omega, gradOmega: gradOmega, hessOmega: hessOmega, jacobi: jacobi,
    dist1: dist1, dist2: dist2, deriv6: deriv6,
    lagrangePoints: lagrangePoints, stability: stability,
    stepRK4: stepRK4, stepVerlet: stepVerlet, stepYoshida4: stepYoshida4,
    stepYoshida6: stepYoshida6, stepDOPRI5: stepDOPRI5, stepGBS: stepGBS, mmidState: mmidState,
    stepGBSFix: stepGBSFix, gbsExtrapolate: gbsExtrapolate,
    stepARK4: stepARK4, stepSymAdapt: stepSymAdapt,
    METHODS: METHODS, makeStepper: makeStepper, integrate: integrate,
    guardState: guardState, validateDt: validateDt, isFiniteState: isFiniteState,
    presets: presets, mulberry32: mulberry32,
    resetStats: resetStats, snapshotStats: snapshotStats,
    runSelfTests: runSelfTests, errState: errState, observedOrder: observedOrder,
    toCanon: toCanon, toPhys: toPhys
  };
}));
