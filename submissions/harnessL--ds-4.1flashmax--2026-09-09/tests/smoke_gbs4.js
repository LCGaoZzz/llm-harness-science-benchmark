
const C = require(process.argv[2]);
const mu = C.MU_EARTH_MOON;
const ic = C.presets(mu)[0].state;
let s = ic, H = 1e-2;
for (let i=0;i<12;i++) {
  const r = C.stepGBS(s, H, mu, 1e-10, 1e-14, 4);
  console.log(i, "H="+H.toExponential(3), "err="+r.errNorm.toExponential(3), "acc="+r.accepted, "next="+r.dtNext.toExponential(3));
  if (r.accepted) s = r.state;
  H = r.dtNext;
}
for (const [k,rt] of [[3,1e-10],[4,1e-10],[5,1e-12],[6,1e-12]]) {
  C.resetStats();
  const r = C.integrate(ic, {method:"gbs", dt:1e-2, T:40*Math.PI, mu, rtol:rt, atol:1e-14, gbsK:k, guard:true, escapeR:50});
  console.log("gbs k="+k+" rtol="+rt+" -> status", r.status, "drift", r.driftMax.toExponential(2), "evals", r.evals, "steps", r.steps, "rejects", r.rejects);
}
