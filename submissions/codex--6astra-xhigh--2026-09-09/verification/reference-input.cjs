const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
vm.runInThisContext(fs.readFileSync(path.join(__dirname,'../index.html'),'utf8').match(/<script id="physics">([\s\S]*?)<\/script>/)[1]);
const cases=[];
for(const [key,T,tolerance] of [['l4',100,1e-6],['l1',2,2e-7],['earth',3,1e-7],['flyby',.6,3e-6]])for(const method of ['rk4','yoshida']){
 const p=CR3BP.presets[key],n=Math.round(T/p.h),stride=n/100;let s=p.state.slice();const states=[s.slice()],times=[0];
 for(let i=1;i<=n;i++){s=CR3BP.checkedStep(s,p.h,method);if(i%stride===0){states.push(s.slice());times.push(i*p.h);}}
 cases.push({key,T,h:p.h,method,tolerance,initial:p.state,times,states});
}
fs.writeFileSync(path.join(__dirname,'reference-input.json'),JSON.stringify(cases));
const long=[];for(const method of ['rk4','yoshida'])long.push({method,h:.02,T:10000,...CR3BP.integrate(CR3BP.presets.l4.state,method,.02,10000)});
fs.writeFileSync(path.join(__dirname,'long-run.json'),JSON.stringify(long,null,2));console.log(JSON.stringify(long));
