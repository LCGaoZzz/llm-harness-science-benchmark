
const C = require(process.argv[2]);
const mu = C.MU_EARTH_MOON;
const ics = {
  newIC: {x:0.5-mu+0.01, y:Math.sqrt(3)/2, z:0, vx:0, vy:0, vz:0},
  oldIC: {x:0.5-mu+0.02, y:Math.sqrt(3)/2+0.01, z:0, vx:0, vy:0, vz:0}
};
for (const [name, ic] of Object.entries(ics)) {
  console.log("=== "+name+" ===");
  for (const H of [0.4,0.2,0.1]) {
    const ref = C.integrate(ic, {method:"dopri5", T:H, mu, rtol:1e-14, atol:1e-16, guard:false});
    const ref2 = C.integrate(ic, {method:"dopri5", T:H, mu, rtol:1e-13, atol:1e-15, guard:false});
    const yg = C.stepGBSFix(ic, H, mu, 4);
    const yg5 = C.stepGBSFix(ic, H, mu, 5);
    const yk = C.integrate(ic, {method:"rk4", dt:H/2000, T:H, mu, guard:false});
    console.log("H="+H, "refcheck="+C.errState(ref.state, ref2.state).toExponential(2),
      "gbs_k4_err="+C.errState(yg, ref.state).toExponential(2),
      "gbs_k5_err="+C.errState(yg5, ref.state).toExponential(2),
      "rk4fine_err="+C.errState(yk.state, ref.state).toExponential(2));
  }
}
