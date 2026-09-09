/* =====================================================================
   harness.js — headless evaluation instrument for the CR3BP lab.
   Loads the SAME src/core.js that is inlined into lab.html, so every
   number reported here is produced by the shipped code.

   Modes
     self   : run the in-page self-test suite, print JSON
     bench  : run the equal-force-evaluation-budget campaign benchmark
     orbits : verify the benchmark orbit ensemble is bounded/collision-free

   Protocol (fixed before round 1, never changed mid-campaign):
     * T          = 20 lunar periods = 40*pi time units
     * budget B   = 200000 force evaluations for every candidate
     * fixed-step methods use dt = T * evalsPerStep / B  (budget exactly spent)
     * adaptive methods run until the budget is exhausted
     * metric     = max over the orbit ensemble of max_t |C(t)-C(0)|/|C(0)|,
                    capped at 1.0; impact / singularity / non-finite / escape
                    => 1.0 (the invariant is completely lost)
   ===================================================================== */
'use strict';
const fs = require('fs');
const path = require('path');

function loadCore(corePath) {
  delete require.cache[require.resolve(corePath)];
  return require(corePath);
}

/* ------------------------------------------------------------------ */
/* benchmark orbit ensemble                                            */
/* Chosen 2026-09-09 by scanning ICs with DOPRI5 rtol=1e-11 over        */
/* T=40*pi and keeping bounded, collision-free orbits that span the     */
/* stiffness range (min r2 = 0.218 / 0.0104 / 0.0056, min r1 = 0.0199). */
/* ------------------------------------------------------------------ */
const MU = 0.012150585609624;
const ORBITS = [
  { id: 'l4_small',  note: 'smooth small L4 tadpole, min r1 = 0.979, min r2 = 0.930',
    ic: { x: 0.5 - MU + 0.005, y: Math.sqrt(3) / 2, z: 0, vx: 0, vy: 0, vz: 0 } },
  { id: 'halo_l2',   note: 'smooth far excursion, min r2 = 0.218',
    ic: { x: 1.2, y: 0.05, z: 0, vx: 0, vy: 0.1, vz: 0 } },
  { id: 'tadpole',   note: 'L4 tadpole with close Moon approach, min r2 = 0.0104',
    ic: { x: 0.5 - MU + 0.02, y: Math.sqrt(3) / 2 + 0.01, z: 0, vx: 0, vy: 0, vz: 0 } },
  { id: 'dro_0p5',   note: 'distant retrograde orbit, close Earth approach, min r1 = 0.0199',
    ic: { x: 0.5, y: 0, z: 0, vx: 0, vy: -0.9, vz: 0 } },
  { id: 'moonflyby', note: 'extreme Moon flyby, min r2 = 0.0056',
    ic: { x: 1.05, y: -0.18, z: 0, vx: -0.2, vy: -0.35, vz: 0 } }
];

/* Held-out control ensemble: sampled with a seed (777001) never used anywhere else,
   integrated with DOPRI5 rtol=1e-10 for T=40pi, kept only if bounded and
   collision-free, then ordered by stiffness. Used to check whether the campaign's
   winner is the best or merely the luckiest of N tries. */
const ORBITS_HELDOUT = [
  { id: 'h_stiffmoon', note: 'held-out: min r2 = 0.0046, max |r| = 22.3',
    ic: { x: 0.11567793808644636, y: 0.7877147966995836, z: 0, vx: -0.2220882179215551, vy: -0.09601872805505995, vz: 0 } },
  { id: 'h_mid',       note: 'held-out: min r2 = 0.131',
    ic: { x: 0.24831795025384054, y: 0.5942219107644632, z: 0, vx: -0.8573635943233966, vy: 0.011461984366178513, vz: 0 } },
  { id: 'h_smooth',    note: 'held-out: min r1 = 0.240, min r2 = 0.677',
    ic: { x: 0.4661270658019929, y: 0.8305141856428236, z: 0, vx: 0.2926635324954987, vy: -0.047748498246073634, vz: 0 } },
  { id: 'h_stiffearth',note: 'held-out: min r1 = 0.035',
    ic: { x: 0.1535804542596452, y: -0.249261555285193, z: 0, vx: 0.378068002872169, vy: 0.39593705423176284, vz: 0 } }
];

const T_SPAN = 40 * Math.PI;      // 20 lunar periods
const BUDGET = 200000;            // force evaluations per orbit
let CORE_IDS = ['l4_small', 'halo_l2', 'tadpole', 'moonflyby'];   // objective ensemble
let STRESS_IDS = ['dro_0p5'];                                     // reported, not optimised
let ACTIVE = ORBITS;

function setEnsemble(name) {
  if (name === 'heldout') {
    ACTIVE = ORBITS_HELDOUT;
    CORE_IDS = ORBITS_HELDOUT.map(o => o.id);
    STRESS_IDS = [];
  } else {
    ACTIVE = ORBITS;
    CORE_IDS = ['l4_small', 'halo_l2', 'tadpole', 'moonflyby'];
    STRESS_IDS = ['dro_0p5'];
  }
}

/* ------------------------------------------------------------------ */
function benchCandidate(C, cfg, opts) {
  opts = opts || {};
  const T = opts.T == null ? T_SPAN : opts.T;
  const budget = opts.budget == null ? BUDGET : opts.budget;
  const mu = opts.mu == null ? C.MU_EARTH_MOON : opts.mu;
  const method = cfg.method;
  const info = C.METHODS[method];
  if (!info) throw new Error('unknown method ' + method);
  const eps = cfg.evalsPerStep || info.evalsPerStep;

  let dt = null;
  if (!info.adaptive) {
    dt = T * eps / budget;
    if (cfg.dtScale) dt *= cfg.dtScale;
  } else {
    dt = cfg.dt0 == null ? 1e-3 : cfg.dt0;
  }

  const perOrbit = [];
  let maxDrift = 0, maxErr = 0, totalEvals = 0, maxR = 0, failures = 0;
  let dtMinAll = Infinity, dtMeanSum = 0;
  const t0 = process.hrtime.bigint();

  for (const ob of ACTIVE) {
    C.resetStats();
    const r = C.integrate(ob.ic, {
      method, dt, T, mu, guard: true, escapeR: opts.escapeR == null ? 50 : opts.escapeR,
      rtol: cfg.rtol, atol: cfg.atol, budget: info.adaptive ? budget : undefined,
      gbsK: cfg.gbsK, gbsSeq: cfg.gbsSeq
    });
    const evals = r.evals;
    totalEvals += evals;
    if (r.dtMin < dtMinAll) dtMinAll = r.dtMin;
    dtMeanSum += r.dtMean;
    let drift = r.driftMax;
    let gate = 'ok';
    const fracT = T > 0 ? Math.min(1, r.t / T) : 1;
    if (r.status !== 'ok' || !C.isFiniteState(r.state)) { gate = r.status; drift = 1.0; failures++; }
    else if (fracT < 1 - 1e-12) { gate = 'incomplete'; drift = 1.0; failures++; }
    if (!(drift <= 1)) drift = 1.0;
    if (r.maxR > maxR) maxR = r.maxR;
    perOrbit.push({ id: ob.id, drift, gate, evals, t: r.t, fracT, status: r.status,
                    steps: r.steps, rejects: r.rejects, maxR: r.maxR });
    if (CORE_IDS.indexOf(ob.id) >= 0 && drift > maxDrift) maxDrift = drift;
  }
  const wallMs = Number(process.hrtime.bigint() - t0) / 1e6;
  const metrics = { jacobi_drift_rel: maxDrift };
  for (const o of perOrbit) metrics['drift_' + o.id] = o.drift;
  metrics.dt_min = dtMinAll === Infinity ? 0 : dtMinAll;
  metrics.dt_mean = dtMeanSum / ACTIVE.length;
  return {
    label: cfg.label || method,
    method, dt, rtol: cfg.rtol == null ? null : cfg.rtol,
    evalsPerStep: eps, order: info.order, symplectic: info.symplectic,
    adaptive: info.adaptive,
    metrics,
    jacobi_drift_rel: maxDrift,
    failures, totalEvals, wallMs: Math.round(wallMs),
    perOrbit
  };
}

/* ------------------------------------------------------------------ */
function verifyOrbits(C, opts) {
  opts = opts || {};
  const mu = opts.mu == null ? C.MU_EARTH_MOON : opts.mu;
  const out = [];
  for (const ob of ACTIVE) {
    const r = C.integrate(ob.ic, {
      method: 'dopri5', T: T_SPAN, mu, rtol: 1e-11, atol: 1e-13,
      guard: true, escapeR: 50, collectTraj: true
    });
    let minr1 = Infinity, minr2 = Infinity, maxr = 0;
    for (const q of r.traj) {
      const d1 = C.dist1(q, mu), d2 = C.dist2(q, mu), rr = Math.hypot(q.x, q.y, q.z);
      if (d1 < minr1) minr1 = d1;
      if (d2 < minr2) minr2 = d2;
      if (rr > maxr) maxr = rr;
    }
    out.push({ id: ob.id, status: r.status, t: r.t, minr1, minr2, maxr,
               drift: r.driftMax, evals: r.evals, bounded: r.status === 'ok' });
  }
  return out;
}

/* ------------------------------------------------------------------ */
function main() {
  const args = process.argv.slice(2);
  const corePath = path.resolve(args[0] || path.join(__dirname, '..', 'src', 'core.js'));
  let mode = 'self', outPath = null, cfgPath = null, budget = BUDGET, T = T_SPAN, ensemble = 'core';
  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--mode') mode = args[++i];
    else if (args[i] === '--out') outPath = args[++i];
    else if (args[i] === '--configs') cfgPath = args[++i];
    else if (args[i] === '--budget') budget = Number(args[++i]);
    else if (args[i] === '--T') T = Number(args[++i]);
    else if (args[i] === '--orbits') ensemble = args[++i];
  }
  const C = loadCore(corePath);
  setEnsemble(ensemble);
  let result;
  if (mode === 'self') {
    result = C.runSelfTests({});
  } else if (mode === 'orbits') {
    result = verifyOrbits(C, {});
  } else if (mode === 'bench') {
    const cfgs = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
    result = {
      protocol: { T, budget, ensemble, orbits: ACTIVE.map(o => o.id), metric: 'max_t |C(t)-C0|/|C0|, cap 1.0, gate failure = 1.0' },
      results: cfgs.map(cfg => benchCandidate(C, cfg, { T, budget }))
    };
  } else {
    throw new Error('unknown mode ' + mode);
  }
  const txt = JSON.stringify(result, null, 2);
  if (outPath) fs.writeFileSync(outPath, txt);
  if (mode === 'bench') {
    const lines = [];
    lines.push('label'.padEnd(22) + 'metric'.padEnd(13) + 'fail'.padEnd(6) + 'evals'.padEnd(10) + 'wall_ms'.padEnd(9) + 'per-orbit drift');
    for (const r of result.results) {
      lines.push(
        String(r.label).padEnd(22) +
        r.jacobi_drift_rel.toExponential(3).padEnd(13) +
        String(r.failures).padEnd(6) +
        String(r.totalEvals).padEnd(10) +
        String(r.wallMs).padEnd(9) +
        r.perOrbit.map(o => o.id + '=' + o.drift.toExponential(2) + (o.gate !== 'ok' ? '[' + o.gate + ']' : '')).join(' ')
      );
    }
    process.stdout.write(lines.join('\n') + '\n');
  } else {
    process.stdout.write(txt + '\n');
  }
}

if (require.main === module) main();
module.exports = { ORBITS, ORBITS_HELDOUT, setEnsemble, T_SPAN, BUDGET, benchCandidate, verifyOrbits, loadCore };
