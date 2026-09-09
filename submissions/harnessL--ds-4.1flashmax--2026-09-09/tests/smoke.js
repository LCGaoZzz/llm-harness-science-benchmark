
const C = require(process.argv[2]);
const mu = C.MU_EARTH_MOON;
const ic = C.presets(mu)[0].state;
console.log("IC", JSON.stringify(ic), "C0=", C.jacobi(ic,mu).toFixed(9));
const ref = C.integrate(ic, {method:"dopri5", T:1.0, mu, rtol:1e-13, atol:1e-14, guard:false});
console.log("ref: t=",ref.t, "steps", ref.steps, "rejects", ref.rejects, "evals", ref.evals, "status", ref.status, "drift", ref.driftMax.toExponential(2));
// very fine RK4 as an independent reference
const fine = C.integrate(ic, {method:"rk4", dt:1e-5, T:1.0, mu, guard:false});
console.log("fine RK4 dt=1e-5 evals", fine.evals, "DOPRI5-vs-fineRK4 =", C.errState(ref.state, fine.state).toExponential(3), "t:", ref.t, fine.t);
for (const m of ["rk4","verlet","yoshida4","yoshida6"]) {
  const r = C.integrate(ic, {method:m, dt:1e-3, T:1.0, mu, guard:false});
  console.log(m.padEnd(9), "err vs ref =", C.errState(r.state, ref.state).toExponential(3), "drift=", r.driftMax.toExponential(2), "evals=", r.evals, "t=", r.t);
}
for (const [m,dts] of [["rk4",[2e-2,1e-2,5e-3,2.5e-3]],["verlet",[1e-2,5e-3,2.5e-3,1.25e-3]],["yoshida4",[2e-2,1e-2,5e-3,2.5e-3]],["yoshida6",[1.5e-1,7.5e-2,3.75e-2,1.875e-2]]]) {
  const errs=dts.map(dt=>C.errState(C.integrate(ic,{method:m,dt,T:1.0,mu,guard:false}).state, ref.state));
  console.log(m.padEnd(9), "errs", errs.map(e=>e.toExponential(2)).join(" "), "order=", C.observedOrder(errs,dts).toFixed(3));
}
// long-run conservation at equal dt
for (const m of ["rk4","yoshida4"]) {
  const r = C.integrate(ic, {method:m, dt:2.5e-3, T:4*Math.PI, mu, guard:false});
  console.log("long", m.padEnd(9), "drift=", r.driftMax.toExponential(3), "half1=", r.driftHalf1.toExponential(3), "half2=", r.driftHalf2.toExponential(3), "evals", r.evals, "status", r.status);
}
