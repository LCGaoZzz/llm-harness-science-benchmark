// Reviewer-owned tests. Extract unchanged numerical definitions from the HTML;
// never run a submission's filesystem scripts or modify its numerical algorithms.
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const root = process.argv[2], out = process.argv[3];
if (!root || !out) throw Error('Usage: node numerical.cjs EXTRACTED_SUBMISSIONS OUTPUT.json');
const files = {
  codex:['codex--6astra-xhigh--2026-09-09','index.html'],
  gptweb:['gptweb--gpt-6pro--2026-09-09','earth_moon_lab.html'],
  ds:['harnessL--ds-4.1flashmax--2026-09-09','lab.html'],
  qwen:['harnessL--qwen-3.8flashxhigh--2026-09-09','cr3bp_lab.html'],
  kimi:['kimiweb--k3swarm-max--2026-09-09','index.html'],
  zwin:['zcode--glm-5.3max--2026-09-09','index.html'],
  zlinux:['zcode--glm-5.3maxlinux--2026-09-09','index.html']
};
function between(s,a,b) {const i=s.indexOf(a), j=s.indexOf(b,i+a.length); if(i<0||j<0)throw Error('Missing extraction boundary '+a);return s.slice(i,j);}
function make(id){
 const html=fs.readFileSync(path.join(root,...files[id]),'utf8');
 const scripts=[...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
 const c=vm.createContext({console,setTimeout,clearTimeout,performance}); let code;
 if(id==='codex')code=scripts[0]+';globalThis.api=CR3BP;';
 if(id==='gptweb'||id==='ds')code=scripts[0]+';globalThis.api=CR3BP;';
 if(id==='qwen')code=between(html,'const MU =','/* ================= 应用状态')+';globalThis.api={MU,deriv,jacobi,omega,rk4,sympl,dopri,LP,PRESETS};';
 if(id==='kimi')code=between(html,'const MU=','/* ==================================================================\n * SECTION: SIM-STATE')+';globalThis.api={MU,deriv,jacobi,gradOmega,stepRK4,stepVerlet,LPTS,checkState};';
 if(id==='zwin')code=between(html,'function buildModel(mu){','/* =====================================================================\n * 2. 零速度曲线')+';globalThis.api=buildModel(0.0121505856188314);';
 if(id==='zlinux')code=between(html,'const MU =','/* ════════════════════════════════════════════════════════════════\n * 3.')+';globalThis.api={MU,f,jacobi,omega,LPTS,INT};';
 vm.runInContext(code,c,{timeout:10000});const p=c.api;
 const obj=s=>({x:s[0],y:s[1],z:0,vx:s[2],vy:s[3],vz:0}), arr=s=>[s.x,s.y,s.vx,s.vy];
 let mu=p.MU||p.mu||p.MU_EARTH_MOON, rhs=p.rhs||p.deriv||p.f,C=p.jacobi,O=p.omega||p.Omega,methods={},points;
 if(id==='codex'){methods=p.methods;points=p.L;}
 if(id==='gptweb'){methods={rk4:p.rk4,sy4:p.sy4};points=p.lagrangePoints();}
 if(id==='qwen'){methods={rk4:p.rk4,midpoint:p.sympl};points=Object.entries(p.LP).map(([name,v])=>({name,x:v[0],y:v[1]}));}
 if(id==='kimi'){methods={rk4:p.stepRK4,verlet:p.stepVerlet};C=s=>p.jacobi(...s);O=(x,y)=>p.jacobi(x,y,0,0)/2;points=p.LPTS;}
 if(id==='zwin'){rhs=s=>{const d=[];p.deriv(s,d);return d;};for(const m of ['rk4','mid','sym4'])methods[m]=(s,h)=>{const a=s.slice();if(!p.step(a,h,m))throw Error('implicit solve failed');return a;};points=Object.entries(p.L).filter(([k])=>/^L\d$/.test(k)).map(([name,v])=>({name,...v}));}
 if(id==='zlinux'){methods={rk4:(s,h)=>p.INT.rk4.step(s,h),gl4:(s,h)=>{const a=p.INT.gl4.step(s,h);if(p.INT.gl4.failed)throw Error('GL4 failed');return a;}};points=Object.entries(p.LPTS).map(([name,v])=>({name,...v}));}
 if(id==='ds'){rhs=s=>arr(p.deriv6(obj(s),mu));C=s=>p.jacobi(obj(s),mu);O=(x,y)=>p.omega(x,y,0,mu);points=Object.entries(p.lagrangePoints(mu).points).map(([name,v])=>({name,...v}));for(const [k,f] of Object.entries({rk4:p.stepRK4,verlet:p.stepVerlet,yoshida4:p.stepYoshida4,yoshida6:p.stepYoshida6}))methods[k]=(s,h)=>arr(f(obj(s),h,mu));}
 return {id,mu,rhs,C,O,methods,points,p,obj,arr};
}
const norm=a=>Math.hypot(...a), dist=(a,b)=>norm(a.map((v,i)=>v-b[i]));
function referenceRhs(s,mu){const [x,y,u,v]=s,dx=x+mu,ex=x-1+mu,r=Math.hypot(dx,y),q=Math.hypot(ex,y),a=(1-mu)/r**3,b=mu/q**3;return [u,v,2*v+x-a*dx-b*ex,-2*u+y-(a+b)*y];}
function referenceC(s,mu){return s[0]**2+s[1]**2+2*(1-mu)/Math.hypot(s[0]+mu,s[1])+2*mu/Math.hypot(s[0]-1+mu,s[1])-s[2]**2-s[3]**2;}
function propagate(a,method,s0,h,T){let s=s0.slice(),max=0,first=0,second=0,minMoon=Infinity,maxEarth=0,n=Math.round(T/h);const C0=referenceC(s,a.mu);for(let i=0;i<n;i++){s=Array.from(a.methods[method](s,h));if(!s.every(Number.isFinite))throw Error('nonfinite at step '+i);const d=Math.abs(referenceC(s,a.mu)-C0);max=Math.max(max,d);if(i<n/2)first=Math.max(first,d);else second=Math.max(second,d);minMoon=Math.min(minMoon,Math.hypot(s[0]-1+a.mu,s[1]));maxEarth=Math.max(maxEarth,Math.hypot(s[0]+a.mu,s[1]));}return {state:s,h,T,steps:n,maxAbsJacobiDrift:max,firstHalfMax:first,secondHalfMax:second,minMoon,maxEarth};}
function symplecticDefect(step,s,h,e){const canon=s=>[s[0],s[1],s[2]-s[1],s[3]+s[0]],phys=z=>[z[0],z[1],z[2]+z[1],z[3]-z[0]],z=canon(s),M=Array.from({length:4},()=>[]),J=[[0,0,1,0],[0,0,0,1],[-1,0,0,0],[0,-1,0,0]];for(let k=0;k<4;k++){let a=z.slice(),b=z.slice();a[k]+=e;b[k]-=e;let u=canon(step(phys(a),h)),v=canon(step(phys(b),h));for(let i=0;i<4;i++)M[i][k]=(u[i]-v[i])/(2*e);}let d=0;for(let i=0;i<4;i++)for(let j=0;j<4;j++){let x=0;for(let k=0;k<4;k++)for(let l=0;l<4;l++)x+=M[k][i]*J[k][l]*M[l][j];d=Math.max(d,Math.abs(x-J[i][j]));}return d;}
const results={reviewedCommit:'ac5a306be9b29978ad6787903821b4a6a181ff01',node:process.version,generatedAt:new Date().toISOString(),submissions:[]};
for(const id of Object.keys(files)){
 const a=make(id),r={id,submission:files[id][0],mu:a.mu,math:{},lagrange:[],methods:{}};
 const samples=[[.6,.2,-.1,.35],[-.5,.4,.2,-.3],[1.1,.2,-.3,.1],[.5,.85,0,0]];
 r.math.maxRhsError=Math.max(...samples.map(s=>dist(a.rhs(s),referenceRhs(s,a.mu))));
 r.math.maxJacobiError=Math.max(...samples.map(s=>Math.abs(a.C(s)-referenceC(s,a.mu))));
 r.math.maxPotentialGradientError=Math.max(...samples.map(s=>{const d=1e-5,g=[(a.O(s[0]+d,s[1])-a.O(s[0]-d,s[1]))/(2*d),(a.O(s[0],s[1]+d)-a.O(s[0],s[1]-d))/(2*d)],f=a.rhs([s[0],s[1],0,0]);return dist(g,f.slice(2));}));
 r.lagrange=a.points.map((p,i)=>({name:p.name||p.n||'L'+(i+1),x:p.x,y:p.y,independentResidual:norm(referenceRhs([p.x,p.y,0,0],a.mu).slice(2))}));
 const s0=[.6,.2,-.1,.35],l4=[.51-a.mu,Math.sqrt(3)/2,0,0],earth=[.3-a.mu,0,0,Math.sqrt((1-a.mu)/.3)-.3];
 for(const method of Object.keys(a.methods)){
  try{const conv=[.02,.01,.005,.0025].map(h=>propagate(a,method,s0,h,.4));const differences=conv.slice(0,-1).map((v,i)=>dist(v.state,conv[i+1].state));r.methods[method]={convergence:{initial:s0,T:.4,runs:conv,differences,orders:differences.slice(0,-1).map((v,i)=>Math.log2(v/differences[i+1]))},l4:propagate(a,method,l4,.01,100),earth:propagate(a,method,earth,.001,20),symplecticDefect:[1e-5,1e-6].map(e=>({differenceStep:e,h:.02,value:symplecticDefect(a.methods[method],s0,.02,e)}))};}catch(e){r.methods[method]={error:String(e)};}
 }
 if(id==='qwen'){
  r.adaptiveProbes=[{state:s0,T:.4,h:.02},{state:a.p.PRESETS['L1 周期轨道 (Lyapunov)'],T:20,h:.05},{state:[-a.mu+.02,0,0,2.8],T:5,h:.05}].map(x=>({...x,result:a.p.dopri(x.state,x.T,x.h,1e-10)}));
 }
 if(id==='ds')r.adaptiveProbes=[s0,l4,earth].map((s,i)=>({initial:s,result:a.p.integrate(a.obj(s),{method:'gbs',dt:.01,T:[.4,100,20][i],mu:a.mu,rtol:1e-13,atol:1e-15,gbsK:5,gbsSeq:'bulirsch',budget:2e6})}));
 if(id==='zlinux'){
  r.unconvergedAccepted=[];
  for(const rad of [.02,.03,.05,.08,.1,.15])for(const h of [.001,.002,.005,.01,.02]){const s=[rad-a.mu,0,0,Math.sqrt((1-a.mu)/rad)-rad];const z=a.p.INT.gl4.step(s,h),k=a.p.INT.gl4;if(!k.failed&&k.lastDelta>1e-10)r.unconvergedAccepted.push({initial:s,h,iterations:k.lastIters,delta:k.lastDelta,failed:k.failed,jacobiChange:referenceC(z,a.mu)-referenceC(s,a.mu),state:z});}
 }
 results.submissions.push(r);console.log(id,JSON.stringify({math:r.math,methods:Object.fromEntries(Object.entries(r.methods).map(([k,v])=>[k,v.error||{p:v.convergence.orders,l4:v.l4.maxAbsJacobiDrift,earth:v.earth.maxAbsJacobiDrift,defect:v.symplecticDefect[0].value}]))}));
}
fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(results,null,2)+'\n');
