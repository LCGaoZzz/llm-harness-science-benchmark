
const C = require(process.argv[2]);
const mu = C.MU_EARTH_MOON;
const ic = C.presets(mu)[0].state;
console.log("--- conservation growth (dt=1e-2) ---");
for (const m of ["rk4","yoshida4"]) {
  const out=[];
  for (const T of [4*Math.PI, 8*Math.PI, 16*Math.PI]) {
    const r = C.integrate(ic, {method:m, dt:1e-2, T, mu, guard:false});
    out.push(r.driftMax);
  }
  console.log(m.padEnd(9), out.map(e=>e.toExponential(2)).join(" "), "growth 16pi/4pi =", (out[2]/out[0]).toFixed(2));
}
console.log("--- moon preset: find a close approach soon ---");
const moonIC = C.presets(mu)[3].state;
const rr = C.integrate(moonIC, {method:"dopri5", T:40*Math.PI, mu, rtol:1e-11, atol:1e-13, guard:true, collectTraj:true});
let best=1e9, bestI=0;
for (let i=0;i<rr.traj.length;i++){ const d2=C.dist2(rr.traj[i],mu); if(d2<best){best=d2;bestI=i;} }
const dtOut = 40*Math.PI/rr.traj.length;
const tClose = bestI*dtOut;
console.log("closest approach minr2="+best.toFixed(5)+" at t="+tClose.toFixed(3)+" TU (traj dt="+dtOut.toFixed(4)+")");
// take the state 0.25 TU before the closest approach as the new preset IC
const iNew = Math.max(0, Math.round((tClose-0.25)/dtOut));
const sNew = rr.traj[iNew];
console.log("candidate preset IC:", JSON.stringify({x:sNew.x,y:sNew.y,z:sNew.z,vx:sNew.vx,vy:sNew.vy,vz:sNew.vz}));
for (const T of [2*Math.PI, 4*Math.PI]) {
  const r2 = C.integrate(sNew, {method:"yoshida4", dt:1e-3, T, mu, guard:true, collectTraj:true});
  let mn=1e9; for (const q of r2.traj){const d=C.dist2(q,mu); if(d<mn)mn=d;}
  console.log("  new preset over T="+T.toFixed(1)+": status="+r2.status+" minr2="+mn.toFixed(5));
}
