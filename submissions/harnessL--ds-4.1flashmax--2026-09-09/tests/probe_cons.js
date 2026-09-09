
const C = require(process.argv[2]);
const mu = C.MU_EARTH_MOON;
const smooth = {x:0.5-mu+0.005, y:Math.sqrt(3)/2, z:0, vx:0, vy:0, vz:0};
console.log("--- smooth L4 tadpole, conservation growth ---");
for (const dt of [1e-2, 5e-3]) {
  for (const m of ["rk4","yoshida4"]) {
    const out=[];
    for (const T of [4*Math.PI, 8*Math.PI, 16*Math.PI, 32*Math.PI]) {
      const r = C.integrate(smooth, {method:m, dt, T, mu, guard:false});
      out.push(r.driftMax);
    }
    console.log(("dt="+dt+" "+m).padEnd(20), out.map(e=>e.toExponential(2)).join(" "), "| growth 32pi/4pi =", (out[3]/out[0]).toFixed(2));
  }
}
console.log("--- backward integration support check (current code rejects dt<0) ---");
const fwd = C.integrate(smooth, {method:"yoshida4", dt:2.5e-3, T:1.0, mu, guard:false});
const back = C.integrate(fwd.state, {method:"yoshida4", dt:-2.5e-3, T:1.0, mu, guard:false});
console.log("fwd t=", fwd.t, "back t=", back.t, "revErr=", C.errState(back.state, smooth).toExponential(3));
