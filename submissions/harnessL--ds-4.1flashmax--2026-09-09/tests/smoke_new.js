
const C = require(process.argv[2]);
const mu = C.MU_EARTH_MOON;
const ic = C.presets(mu)[0].state;
// fixed-step GBS order test
{
  const errs=[], Hs=[];
  for (const H of [0.4,0.2,0.1,0.05]) {
    const r = C.integrate(ic, {method:"gbsfix", dt:H, T:H, mu, gbsK:4, guard:false});
    const ref = C.integrate(ic, {method:"dopri5", T:H, mu, rtol:1e-14, atol:1e-16, guard:false});
    errs.push(C.errState(r.state, ref.state)); Hs.push(H);
  }
  console.log("gbsfix k=4 nominal 8 errs", errs.map(e=>e.toExponential(2)).join(" "), "observed=", C.observedOrder(errs,Hs).toFixed(2));
}
// adaptive methods: tolerance sweep on one orbit
for (const m of ["ark4","symadapt","gbsfix"]) {
  for (const rt of [1e-8,1e-10,1e-12]) {
    C.resetStats();
    const r = C.integrate(ic, {method:m, dt:1e-3, T:10, mu, rtol:rt, atol:rt*1e-2, gbsK:4, guard:true});
    console.log(m.padEnd(9), "rtol="+rt.toExponential(0), "drift="+r.driftMax.toExponential(2), "evals="+r.evals, "steps="+r.steps, "status="+r.status);
  }
}
