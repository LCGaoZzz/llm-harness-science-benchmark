(key)=>{
const arr=o=>[o.x,o.y,o.vx,o.vy], obj=a=>({x:a[0],y:a[1],z:0,vx:a[2],vy:a[3],vz:0});
let A;
if(key==='codex_6astra-xhigh'){const c=CR3BP;A={mu:c.MU,rhs:c.rhs,C:c.jacobi,L:c.L,methods:{rk4:c.rk4,yoshida4:c.yoshida},self:c.selfTests};}
if(key==='gptweb_gpt-6pro'){const c=CR3BP;A={mu:c.MU,rhs:c.rhs,C:c.jacobi,L:c.lagrangePoints(),methods:{rk4:c.rk4,yoshida4:c.sy4},self:()=>Lab.runSelfTests()};}
if(key==='harnessL_ds-4.1flashmax'){const c=CR3BP,mu=c.MU_EARTH_MOON;A={mu,rhs:s=>arr(c.deriv6(obj(s),mu)),C:s=>c.jacobi(obj(s),mu),L:c.lagrangePoints(mu),methods:{rk4:(s,h)=>arr(c.stepRK4(obj(s),h,mu)),yoshida4:(s,h)=>arr(c.stepYoshida4(obj(s),h,mu)),verlet2:(s,h)=>arr(c.stepVerlet(obj(s),h,mu)),yoshida6:(s,h)=>arr(c.stepYoshida6(obj(s),h,mu))},self:()=>c.runSelfTests()};}
if(key==='harnessL_qwen-3.8flashxhigh'){A={mu:MU,rhs:deriv,C:jacobi,L:LP,methods:{rk4,midpoint:sympl},self:runTests};}
if(key==='kimiweb_k3swarm-max'){const c=window.__AUDIT_KIMI__;A={mu:c.MU,rhs:c.deriv,C:s=>c.jacobi(...s),L:c.LPTS,methods:{rk4:c.stepRK4,claimed_symplectic_verlet:c.stepVerlet},self:c.runSelfTests};}
if(key==='zcode_glm-5.3max'){const c=CR3BP,m=app.model;A={mu:app.mu,rhs:s=>{let o=new Float64Array(4);m.deriv(s,o);return Array.from(o)},C:s=>m.jacobi(s),L:m.L,methods:Object.fromEntries(['rk4','mid','sym4'].map(n=>[n,(s,h)=>{let a=new Float64Array(s);const ok=m.step(a,h,n);if(!ok)throw Error('step failed');return Array.from(a)}])),self:runSelfTests};}
if(key==='zcode_glm-5.3maxlinux'){A={mu:MU,rhs:f,C:jacobi,L:LPTS,methods:{rk4:(s,h)=>INT.rk4.step(s,h),gauss_legendre4:(s,h)=>{const a=INT.gl4.step(s,h);if(INT.gl4.failed)throw Error('GL4 failed');return a;}},self:()=>runSelfTests(true)};}
window.__AUDIT__=A;
return {mu:A.mu,L:A.L,methods:Object.keys(A.methods)};
}
