const fs=require('node:fs'),vm=require('node:vm'),crypto=require('node:crypto');
const path=require('node:path');const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
vm.runInThisContext(html.match(/<script id="physics">([\s\S]*?)<\/script>/)[1]);
const method=process.argv[2]||'rk4',h=Number(process.argv[3]||.02),round=process.argv[4]||'probe';
(async()=>{const start=performance.now(),r=CR3BP.integrate(CR3BP.presets.l4.state,method,h,100),test=await CR3BP.selfTests();const report={round,method,h,T:100,...r,log10_max_jacobi_drift:Math.log10(Math.max(r.maxDrift,1e-16)),elapsed_ms:performance.now()-start,tests:test,artifact:{path:path.join(root,'index.html'),sha256:crypto.createHash('sha256').update(html).digest('hex'),bytes:Buffer.byteLength(html)}};fs.writeFileSync(path.join(__dirname,`round-${round}.json`),JSON.stringify(report,null,2));console.log(JSON.stringify({...report,tests:{passed:test.passed,total:test.total,failures:test.results.filter(x=>!x.pass)}}));})();
