
const C = require(process.argv[2]);
const mu = C.MU_EARTH_MOON;
const ic = C.presets(mu)[0].state;
// direct one-step order test (ignore acceptance)
for (const k of [2,3,4,5]) {
  const errs=[], Hs=[];
  for (const H of [0.5,0.25,0.125,0.0625]) {
    C.resetStats();
    const r = C.stepGBS(ic, H, mu, 1e-14, 1e-16, k);
    const ref = C.integrate(ic, {method:"dopri5", T:H, mu, rtol:1e-14, atol:1e-16, guard:false});
    errs.push(C.errState(r.state, ref.state)); Hs.push(H);
  }
  console.log("gbs k="+k+" nominal order "+(2*k)+" errs", errs.map(e=>e.toExponential(2)).join(" "), "observed=", C.observedOrder(errs,Hs).toFixed(2));
}
// controller trace
let s = ic, H = 1e-2;
for (let i=0;i<25;i++) {
  const r = C.stepGBS(s, H, mu, 1e-10, 1e-14, 4);
  console.log(i, "H="+H.toExponential(3), "err="+r.errNorm.toExponential(3), "acc="+r.accepted, "next="+r.dtNext.toExponential(3));
  if (r.accepted) s = r.state;
  H = r.dtNext;
}
