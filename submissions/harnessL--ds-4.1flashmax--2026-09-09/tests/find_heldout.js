
const C = require(process.argv[2]);
const mu = C.MU_EARTH_MOON;
const T = 40*Math.PI;
const rnd = C.mulberry32(777001);          // a seed never used for the campaign ensemble
const found = [];
for (let i = 0; i < 400 && found.length < 60; i++) {
  const s0 = {x:-0.15+1.45*rnd(), y:-0.85+1.7*rnd(), z:0, vx:-1.2+2.4*rnd(), vy:-1.2+2.4*rnd(), vz:0};
  const r = C.integrate(s0, {method:"dopri5", T, mu, rtol:1e-10, atol:1e-13, guard:true, escapeR:30, collectTraj:true});
  if (r.status !== "ok") continue;
  let minr1=1e9,minr2=1e9,maxr=0;
  for (const q of r.traj){const d1=C.dist1(q,mu),d2=C.dist2(q,mu),rr=Math.hypot(q.x,q.y,q.z);
    if(d1<minr1)minr1=d1; if(d2<minr2)minr2=d2; if(rr>maxr)maxr=rr;}
  found.push({ic:s0, minr1, minr2, maxr, drift:r.driftMax, evals:r.evals});
}
console.log("bounded candidates:", found.length);
found.sort((a,b)=> Math.min(a.minr2,b.minr1) - Math.min(b.minr2,a.minr1));
// pick 5 with a stiffness spread: smoothest, then increasingly stiff
const pick = [];
const idxs = [0, Math.floor(found.length*0.25), Math.floor(found.length*0.5), Math.floor(found.length*0.75), found.length-1];
for (const i of idxs) pick.push(found[i]);
console.log(JSON.stringify(pick, null, 1));
