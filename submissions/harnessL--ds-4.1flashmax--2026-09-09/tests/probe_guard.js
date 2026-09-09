
const C = require(process.argv[2]);
const mu = C.MU_EARTH_MOON;
const badMoon = {x: 1-mu, y:0, z:0, vx:0, vy:0, vz:0};
console.log("dist2 =", C.dist2(badMoon, mu), "guard:", JSON.stringify(C.guardState(badMoon, mu)));
const g = C.gradOmega(badMoon.x, badMoon.y, badMoon.z, mu);
console.log("gradOmega at Moon centre:", g);
const d = C.deriv6(badMoon, mu);
console.log("deriv6:", d);
const one = C.stepRK4(badMoon, 1e-3, mu);
console.log("stepRK4:", one);
const r = C.integrate(badMoon, {method:"rk4", dt:1e-3, T:1, mu, guard:true});
console.log("integrate status:", r.status, "t:", r.t, "state:", r.state);
// moon preset closest approach over different spans
const moonIC = C.presets(mu)[3].state;
for (const T of [2*Math.PI, 4*Math.PI, 8*Math.PI]) {
  const rr = C.integrate(moonIC, {method:"dopri5", T, mu, rtol:1e-10, atol:1e-13, guard:true, collectTraj:true});
  let minr2=1e9; for (const q of rr.traj) { const d2=C.dist2(q,mu); if(d2<minr2)minr2=d2; }
  console.log("moon preset T="+T.toFixed(1)+" status="+rr.status+" minr2="+minr2.toFixed(4));
}
// L4 preset candidates
for (const d4 of [0.005,0.01,0.02]) {
  const ic = {x:0.5-mu+d4, y:Math.sqrt(3)/2, z:0, vx:0, vy:0, vz:0};
  const rr = C.integrate(ic, {method:"yoshida4", dt:1e-3, T:2*Math.PI, mu, guard:true, collectTraj:true});
  let dmax=0; for (const q of rr.traj) { const dd=Math.hypot(q.x-(0.5-mu), q.y-Math.sqrt(3)/2); if(dd>dmax)dmax=dd; }
  console.log("L4 delta="+d4+" maxDistL4 over 2pi =", dmax.toFixed(4), "status", rr.status);
}
