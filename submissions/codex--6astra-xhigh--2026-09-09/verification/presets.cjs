const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
vm.runInThisContext(fs.readFileSync(path.join(__dirname,'../index.html'),'utf8').match(/<script id="physics">([\s\S]*?)<\/script>/)[1]);
const results=[];
for(const [key,p] of Object.entries(CR3BP.presets))for(const method of ['rk4','yoshida']){
 let s=p.state.slice(),minMoon=Infinity,minEarth=Infinity,c0=CR3BP.jacobi(s),maxDrift=0,stopped=null,t=0,v0=Math.hypot(s[2]-s[1],s[3]+s[0]),closest=null;
 const T=key==='l4'?100:key==='l1'?3:key==='earth'?3:1;
 for(let i=0;i<Math.round(T/p.h);i++){try{s=CR3BP.checkedStep(s,p.h,method);t+=p.h;}catch(e){stopped=e.message;break;}const f=CR3BP.field(s[0],s[1]);if(f.r2<minMoon){minMoon=f.r2;closest={t,state:s.slice()};}minEarth=Math.min(minEarth,f.r1);maxDrift=Math.max(maxDrift,Math.abs(CR3BP.jacobi(s)-c0));}
 results.push({key,method,t,stopped,minMoon,minEarth,maxDrift,initialInertialSpeed:v0,finalInertialSpeed:Math.hypot(s[2]-s[1],s[3]+s[0]),final:s,closest});
}
fs.writeFileSync(path.join(__dirname,'presets-results.json'),JSON.stringify(results,null,2));console.log(JSON.stringify(results));
