
const C = require(process.argv[2]);
const mu = C.MU_EARTH_MOON;
const T20 = 20*2*Math.PI;
const cands = [
  ["tadpole", {x:0.5-mu+0.02, y:Math.sqrt(3)/2+0.01, z:0, vx:0, vy:0, vz:0}],
  ["earth_r0.1", {x:-mu+0.1, y:0, z:0, vx:0, vy:Math.sqrt(10)-0.1, vz:0}],
  ["earth_r0.15", {x:-mu+0.15, y:0, z:0, vx:0, vy:Math.sqrt(1/0.15)-0.15, vz:0}],
  ["moonflyby_A", {x:1.05, y:-0.18, z:0, vx:-0.2, vy:-0.35, vz:0}],
  ["dro_0.7", {x:0.7, y:0, z:0, vx:0, vy:-0.6, vz:0}],
  ["dro_0.5", {x:0.5, y:0, z:0, vx:0, vy:-0.9, vz:0}],
  ["dro_0.35", {x:0.35, y:0, z:0, vx:0, vy:-1.2, vz:0}],
  ["l2_halo", {x:1.2, y:0.05, z:0, vx:0, vy:0.1, vz:0}],
  ["l1_lyap", {x:0.84, y:0.06, z:0, vx:0, vy:0.0, vz:0}],
  ["moon_retro", {x:1.0-mu+0.06, y:0, z:0, vx:0, vy:1.4, vz:0}],
];
for (const [name, ic] of cands) {
  const r = C.integrate(ic, {method:"dopri5", T:T20, mu, rtol:1e-11, atol:1e-13, guard:true, collectTraj:true});
  let minr1=1e9,minr2=1e9,maxr=0;
  for (const q of r.traj) { const d1=C.dist1(q,mu), d2=C.dist2(q,mu); if(d1<minr1)minr1=d1; if(d2<minr2)minr2=d2; const rr=Math.hypot(q.x,q.y,q.z); if(rr>maxr)maxr=rr; }
  console.log(name.padEnd(12), "status="+r.status.padEnd(12), "t="+r.t.toFixed(1), "minr1="+minr1.toFixed(4), "minr2="+minr2.toFixed(4), "maxr="+maxr.toFixed(3), "drift="+r.driftMax.toExponential(2), "evals="+r.evals);
}
