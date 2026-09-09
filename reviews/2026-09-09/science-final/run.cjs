// Reuse reviewer-owned adapters; extract only the shipped HTML numerical code.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=process.argv[2],out=process.argv[3];
if(!root||!out)throw Error('Usage: node run.cjs EXTRACTED_SUBMISSIONS OUTPUT.json');
const source=fs.readFileSync(path.join(__dirname,'../scripts/numerical.cjs'),'utf8');
const c={require,process:{argv:['node','adapter',root,'unused']},console,setTimeout,clearTimeout,performance};
vm.runInNewContext(source.slice(0,source.indexOf('const results='))+';globalThis.review={make,referenceRhs,referenceC,symplecticDefect};',c);
const {make,referenceC,symplecticDefect}=c.review;
const selected={codex:'yoshida',gptweb:'sy4',ds:'yoshida6',zwin:'sym4'};
const norm=x=>Math.hypot(...x),distance=(a,b)=>norm(a.map((x,i)=>x-b[i]));
function advance(a,method,s0,T,h){
 const n=Math.round(T/h),step=a.methods[method];let s=s0.slice(),max=0,minEarth=Infinity,minMoon=Infinity,quarters=[0,0,0,0];const C0=referenceC(s,a.mu);
 const started=performance.now();
 for(let i=0;i<n;i++){
  s=Array.from(step(s,h));if(!s.every(Number.isFinite))throw Error('nonfinite');
  const d=Math.abs(referenceC(s,a.mu)-C0);max=Math.max(max,d);const j=Math.min(3,Math.floor(4*i/n));quarters[j]=Math.max(quarters[j],d);
  minEarth=Math.min(minEarth,Math.hypot(s[0]+a.mu,s[1]));minMoon=Math.min(minMoon,Math.hypot(s[0]-1+a.mu,s[1]));
 }
 return {h,T,steps:n,state:s,maxAbsJacobiDrift:max,quarterMaxima:quarters,minEarth,minMoon,elapsedMs:performance.now()-started};
}
const result={reviewedCommit:'ac5a306be9b29978ad6787903821b4a6a181ff01',node:process.version,generatedAt:new Date().toISOString(),submissions:[]};
for(const id of Object.keys(selected)){
 const a=make(id),mu=a.mu,L1=a.points.find(p=>(p.name||p.n)==='L1')||a.points[0];
 const orbit=(r,mass,primary)=>[primary+r,0,0,Math.sqrt(mass/r)-r];
 const cases=[
  {name:'smooth',s:[.6,.2,-.1,.35],T:.4,h:.02},
  {name:'earth_wide',s:orbit(.3,1-mu,-mu),T:20,h:.01},
  {name:'earth_close',s:orbit(.04,1-mu,-mu),T:.1,h:.0001},
  {name:'moon_orbit',s:orbit(.02,mu,1-mu),T:1,h:.0005},
  {name:'L1_perturbation',s:[L1.x-.0001,0,0,0],T:2,h:.001},
  {name:'L4_perturbation',s:[.51-mu,Math.sqrt(3)/2,0,0],T:100,h:.02},
  {name:'earth_eccentric',s:[.15-mu,0,0,.8*Math.sqrt((1-mu)/.15)-.15],T:2,h:.0005},
  {name:'common_flyby',s:[1-mu-.25,-.02,.6,.15],T:1.5,h:.0005}
 ];
 const row={id,mu,selectedMethod:selected[id],cases:[],longTerm:{},geometry:[]};
 for(const x of cases){
  const r={...x,methods:{}};
  for(const method of ['rk4',selected[id]]){try{r.methods[method]=[1,2,4].map(k=>advance(a,method,x.s,x.T,x.h/k));}catch(e){r.methods[method]={error:String(e)};}}
  if(id==='ds'){
   const z=a.p.integrate(a.obj(x.s),{method:'gbs',dt:x.h,T:x.T,mu,rtol:1e-13,atol:1e-15,gbsK:5,gbsSeq:'bulirsch',budget:5e6});
   r.gbs={state:a.arr(z.state),t:z.t,status:z.status,message:z.message,evals:z.evals,steps:z.steps,rejects:z.rejects,maxAbsJacobiDrift:z.driftMax};
  }
  row.cases.push(r);console.log(id,x.name);
 }
 for(const x of [{name:'L4_1000',s:cases[5].s,T:1000,h:.01},{name:'earth_100',s:cases[1].s,T:100,h:.001}]){
  row.longTerm[x.name]={...x,methods:{}};
  for(const method of ['rk4',selected[id]])row.longTerm[x.name].methods[method]=advance(a,method,x.s,x.T,x.h);
 }
 for(const s of [[.6,.2,-.1,.35],[-.5,.4,.2,-.3],[1.1,.2,-.3,.1],[.5,.85,0,0]]){
  const h=.01,f=a.methods[selected[id]],z=Array.from(f(s,h)),back=Array.from(f(z,-h));
  row.geometry.push({s,h,symplecticDefect:[1e-5,1e-6].map(e=>({e,value:symplecticDefect(f,s,h,e)})),reversalError:distance(s,back)});
 }
 result.submissions.push(row);
 fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n');
}
