
const C = require(process.argv[2]);
const mu = C.MU_EARTH_MOON;
const ic = C.presets(mu)[0].state;
// one-step order test for GBS (k=4 -> order 8)
for (const k of [3,4,5]) {
  const errs=[], Hs=[];
  for (const H of [0.5,0.25,0.125,0.0625]) {
    const st = C.makeStepper({method:"gbs", dt:H, rtol:1e-14, atol:1e-16, gbsK:k});
    const r = st.step(ic, mu);
    const ref = C.integrate(ic, {method:"dopri5", T:H, mu, rtol:1e-14, atol:1e-16, guard:false});
    errs.push(C.errState(r.state, ref.state)); Hs.push(H);
  }
  console.log("gbs k="+k+" (nominal order "+(2*k)+") errs", errs.map(e=>e.toExponential(2)).join(" "), "observed order=", C.observedOrder(errs,Hs).toFixed(2));
}
// a real orbit run
C.resetStats();
const r = C.integrate(ic, {method:"gbs", dt:1e-2, T:40*Math.PI, mu, rtol:1e-10, atol:1e-14, gbsK:4, guard:true, escapeR:50});
console.log("gbs run: status", r.status, "t", r.t.toFixed(2), "drift", r.driftMax.toExponential(2), "evals", r.evals, "steps", r.steps, "rejects", r.rejects);
