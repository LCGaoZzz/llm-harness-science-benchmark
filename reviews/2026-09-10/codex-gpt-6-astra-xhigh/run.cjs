// Reviewer-owned adapter. Run the shipped HTML numerical definitions unchanged.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..');
const file=path.join(root,'submissions/harnessL--glm5.3-max--2026-09-10/lab.html');
const bytes=fs.readFileSync(file),html=bytes.toString('utf8').replace(/\r\n/g,'\n');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const prefix=script.slice(0,script.indexOf('const sim={'));
const bench=script.slice(script.indexOf('function bench(cfg)'),script.indexOf('function maxAbsDiff'));
const ctx=vm.createContext({performance,console});
vm.runInContext(prefix+bench+';globalThis.api={MU,LPTS,PRESETS,deriv,jacobiC,makeState,stepRK4,stepIMP,stepGBS,bench};',ctx);
const p=ctx.api,mu=p.MU,norm=a=>Math.hypot(...a),obj=s=>({x:s[0],y:s[1],vx:s[2],vy:s[3]});
function C(s){return s[0]**2+s[1]**2+2*(1-mu)/Math.hypot(s[0]+mu,s[1])+2*mu/Math.hypot(s[0]-1+mu,s[1])-s[2]**2-s[3]**2;}
function rhs(s){const [x,y,u,v]=s,r=Math.hypot(x+mu,y),q=Math.hypot(x-1+mu,y);return [u,v,x+2*v-(1-mu)*(x+mu)/r**3-mu*(x-1+mu)/q**3,y-2*u-(1-mu)*y/r**3-mu*y/q**3];}
function step(s,h){const st=p.makeState(obj(s),'imp');p.stepIMP(st,h);if(st.halted)throw Error(st.haltMsg);return Array.from(st.s);}
function defect(s,h,e){
 const canon=s=>[s[0],s[1],s[2]-s[1],s[3]+s[0]],phys=z=>[z[0],z[1],z[2]+z[1],z[3]-z[0]],z=canon(s),M=Array.from({length:4},()=>[]),J=[[0,0,1,0],[0,0,0,1],[-1,0,0,0],[0,-1,0,0]];
 for(let k=0;k<4;k++){let a=z.slice(),b=z.slice();a[k]+=e;b[k]-=e;const u=canon(step(phys(a),h)),v=canon(step(phys(b),h));for(let i=0;i<4;i++)M[i][k]=(u[i]-v[i])/(2*e);}
 let d=0;for(let i=0;i<4;i++)for(let j=0;j<4;j++){let x=0;for(let k=0;k<4;k++)for(let l=0;l<4;l++)x+=M[k][i]*J[k][l]*M[l][j];d=Math.max(d,Math.abs(x-J[i][j]));}return d;
}
function advance(s0,T,h,method){
 const st=p.makeState(obj(s0),method),C0=C(s0),n=Math.round(T/h),quarters=[0,0,0,0];let max=0;
 for(let i=0;i<n;i++){(method==='rk4'?p.stepRK4:p.stepIMP)(st,h);if(st.halted)throw Error(st.haltMsg);const d=Math.abs(C(st.s)-C0);max=Math.max(max,d);const j=Math.min(3,Math.floor(4*i/n));quarters[j]=Math.max(quarters[j],d);}
 return {h,T,steps:n,state:Array.from(st.s),maxAbsJacobiDrift:max,quarterMaxima:quarters};
}
const orbit=(r,mass,primary)=>[primary+r,0,0,Math.sqrt(mass/r)-r];
const cases=[
 {name:'smooth',s:[.6,.2,-.1,.35],T:.4,h:.02},
 {name:'earth_wide',s:orbit(.3,1-mu,-mu),T:20,h:.01},
 {name:'earth_close',s:orbit(.04,1-mu,-mu),T:.1,h:.0001},
 {name:'moon_orbit',s:orbit(.02,mu,1-mu),T:1,h:.0005},
 {name:'L1_perturbation',s:[p.LPTS[0].x-.0001,0,0,0],T:2,h:.001},
 {name:'L4_perturbation',s:[.51-mu,Math.sqrt(3)/2,0,0],T:100,h:.02},
 {name:'earth_eccentric',s:[.15-mu,0,0,.8*Math.sqrt((1-mu)/.15)-.15],T:2,h:.0005},
 {name:'common_flyby',s:[1-mu-.25,-.02,.6,.15],T:1.5,h:.0005}
];
const samples=[[.6,.2,-.1,.35],[-.5,.4,.2,-.3],[1.1,.2,-.3,.1],[.5,.85,0,0]];
const out={reviewer:'codex-gpt-6-astra-xhigh',reviewedCommit:'09d165d2211c515959a1431fba79fae1599b4dbb',source:'submissions/harnessL--glm5.3-max--2026-09-10/lab.html',sha256:crypto.createHash('sha256').update(html).digest('hex'),workingTreeSha256:crypto.createHash('sha256').update(bytes).digest('hex'),hashNormalization:'CRLF to LF, matching the committed original HTML bytes',node:process.version,mu,selectedMethod:'imp',cases:[],longTerm:{},geometry:[],presets:p.PRESETS};
out.math={maxRhsError:Math.max(...samples.map(s=>{const d=[];p.deriv(s,d);return norm(d.map((x,i)=>x-rhs(s)[i]));})),maxJacobiError:Math.max(...samples.map(s=>Math.abs(p.jacobiC(s)-C(s))))};
out.lagrange=p.LPTS.map(q=>({...q,residual:norm(rhs([q.x,q.y,0,0]).slice(2))}));
for(const c of cases){const r={...c,methods:{}};for(const method of ['rk4','imp'])r.methods[method]=[1,2,4].map(k=>advance(c.s,c.T,c.h/k,method));r.gbs=[1e-12,1e-13].map(tol=>({tol,...p.bench({ic:obj(c.s),T:c.T,integrator:'gbs',tol,maxEvals:5e6})}));out.cases.push(r);console.log(c.name);}
for(const c of [{name:'L4_1000',s:cases[5].s,T:1000,h:.01},{name:'earth_100',s:cases[1].s,T:100,h:.001}]){
 out.longTerm[c.name]={...c,methods:{}};for(const m of ['rk4','imp'])out.longTerm[c.name].methods[m]=advance(c.s,c.T,c.h,m);out.longTerm[c.name].gbs=p.bench({ic:obj(c.s),T:c.T,integrator:'gbs',tol:1e-12,maxEvals:5e6});
}
for(const s of samples){const h=.01,z=step(s,h),back=step(z,-h);out.geometry.push({s,h,symplecticDefects:[1e-5,1e-6].map(e=>({e,value:defect(s,h,e)})),reversalError:norm(back.map((x,i)=>x-s[i]))});}
fs.writeFileSync(path.join(__dirname,'numerical.json'),JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify({math:out.math,geometry:out.geometry,longTerm:out.longTerm},null,2));
