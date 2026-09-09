
const C = require(process.argv[2]);
const mu = C.MU_EARTH_MOON;
const ic = C.presets(mu)[0].state;
const H = 0.1;
const ref = C.integrate(ic, {method:"dopri5", T:H, mu, rtol:1e-14, atol:1e-16, guard:false}).state;
console.log("MMID convergence (error should fall ~4x when n doubles):");
for (const n of [2,4,8,16,32,64]) {
  const y = C.mmidState(ic, H, n, mu);
  console.log("n="+n, "err="+C.errState(y, ref).toExponential(3));
}
// also RK4 single step for comparison
const y4 = C.stepRK4(ic, H/100, mu);
console.log("sanity: RK4 dt=H/100 err", C.errState(y4, ref).toExponential(3));
// GBS with forced acceptance (loose tol) -> order test
for (const k of [2,3,4,5]) {
  const errs=[], Hs=[];
  for (const h of [0.2,0.1,0.05,0.025]) {
    const r = C.stepGBS(ic, h, mu, 1.0, 1.0, k);   // always accepted
    const rf = C.integrate(ic, {method:"dopri5", T:h, mu, rtol:1e-14, atol:1e-16, guard:false}).state;
    errs.push(C.errState(r.state, rf)); Hs.push(h);
  }
  console.log("gbs k="+k+" nominal "+(2*k)+" errs", errs.map(e=>e.toExponential(2)).join(" "), "observed=", C.observedOrder(errs,Hs).toFixed(2));
}
