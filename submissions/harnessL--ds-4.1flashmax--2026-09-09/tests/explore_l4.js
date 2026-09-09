
const C = require(process.argv[2]);
const mu = C.MU_EARTH_MOON;
const T = 40*Math.PI;
for (const d of [0.002,0.005,0.01]) {
  const ic = {x:0.5-mu+d, y:Math.sqrt(3)/2, z:0, vx:0, vy:0, vz:0};
  const r = C.integrate(ic, {method:"dopri5", T, mu, rtol:1e-11, atol:1e-13, guard:true, escapeR:50, collectTraj:true});
  let minr1=1e9,minr2=1e9,maxr=0,maxd=0;
  for (const q of r.traj){const d1=C.dist1(q,mu),d2=C.dist2(q,mu);if(d1<minr1)minr1=d1;if(d2<minr2)minr2=d2;const rr=Math.hypot(q.x,q.y,q.z);if(rr>maxr)maxr=rr;const dd=Math.hypot(q.x-(0.5-mu),q.y-Math.sqrt(3)/2);if(dd>maxd)maxd=dd;}
  console.log("delta="+d, "status="+r.status, "minr1="+minr1.toFixed(4), "minr2="+minr2.toFixed(4), "maxr="+maxr.toFixed(3), "maxDistL4="+maxd.toFixed(4), "drift="+r.driftMax.toExponential(2), "evals="+r.evals);
}
