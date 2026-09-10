
const fs=require('fs');
eval(fs.readFileSync(process.argv[2],'utf8'));
const earth={x:-MU+0.08,y:0,vx:0,vy:Math.sqrt((1-MU)/0.08)-(-MU+0.08)};
const y=[earth.x,earth.y,earth.vx,earth.vy];
function mkst(y,dt){return {s:y.slice(),dt:dt,tol:1e-12,gbsH:0.05,evals:0,steps:0,hLast:0,minH:Infinity,minR1:Infinity,maxR1:0,minR2:Infinity,maxR2:0,halted:false,haltMsg:""};}
console.log("=== GBS 单步 (earth IC) ===");
for(const h of [0.05,0.01,0.005,0.001]){
  console.log("h="+h);
  const r=gbsTryStep(y,h,1e-12);
  console.log("  -> ok="+r.ok+" k="+r.k+" err="+r.err.toExponential(3));
}
console.log("=== GBS 完整 stepGBS T=1 (earth) ===");
const st=mkst(y,2e-3);
for(let i=0;i<200 && st.t<1 && !st.halted;i++) stepGBS(st);
console.log("t="+st.t.toFixed(4)+" steps="+st.steps+" evals="+st.evals+" halted="+st.halted+" "+st.haltMsg);
console.log("=== IMP 单步 (earth IC, dt=2e-3) ===");
const st2=mkst(y,2e-3);
const r2=stepIMP(st2);
console.log("-> "+JSON.stringify(r2)+" halted="+st2.halted+" "+st2.haltMsg+" s="+st2.s.map(v=>v.toFixed(6)).join(","));
console.log("=== RK4 参照 (dt=1e-5, T=0.05) ===");
const st3=mkst(y,1e-5);
for(let i=0;i<5000;i++) stepRK4(st3);
console.log("s="+st3.s.map(v=>v.toFixed(9)).join(","));
