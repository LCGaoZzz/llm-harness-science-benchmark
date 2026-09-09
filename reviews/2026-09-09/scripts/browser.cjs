const fs=require('node:fs'),path=require('node:path'),{pathToFileURL}=require('node:url');
const {chromium}=require('playwright');
const root=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);
const entries=[
 ['codex','codex--6astra-xhigh--2026-09-09','index.html','#runTests'],
 ['gptweb','gptweb--gpt-6pro--2026-09-09','earth_moon_lab.html',null],
 ['ds','harnessL--ds-4.1flashmax--2026-09-09','lab.html',null],
 ['qwen','harnessL--qwen-3.8flashxhigh--2026-09-09','cr3bp_lab.html',null],
 ['kimi','kimiweb--k3swarm-max--2026-09-09','index.html','#btnRerun'],
 ['zwin','zcode--glm-5.3max--2026-09-09','index.html',null],
 ['zlinux','zcode--glm-5.3maxlinux--2026-09-09','index.html',null]
];
(async()=>{
 fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({channel:process.env.REVIEW_BROWSER_CHANNEL||'msedge',headless:true});
 const report={browser:browser.version(),node:process.version,platform:process.platform,viewport:{width:1440,height:1000},generatedAt:new Date().toISOString(),submissions:[]};
 for(const [id,dir,file,testButton]of entries){
  const context=await browser.newContext({viewport:report.viewport,deviceScaleFactor:1,offline:true});
  const page=await context.newPage();const r={id,dir,entry:file,pageErrors:[],consoleErrors:[],console:[],requests:[]};
  page.on('pageerror',e=>r.pageErrors.push(e.message));page.on('console',m=>{if(m.type()==='error')r.consoleErrors.push(m.text());r.console.push({type:m.type(),text:m.text()});});
  page.on('request',q=>{if(!q.url().startsWith('file:'))r.requests.push(q.url());});
  try{
   await page.goto(pathToFileURL(path.join(root,dir,file)).href,{waitUntil:'load',timeout:30000});await page.waitForTimeout(1200);
   r.loadedOffline=true;
   // Explicitly re-run submitted self-tests, using their existing UI/API only.
   if(testButton)await page.locator(testButton).click();
   if(id==='gptweb')r.selfTestReturn=await page.evaluate(async()=>{await window.Lab.runSelfTests();return window.Lab.getTestReport();});
   if(id==='ds')r.selfTestReturn=await page.evaluate(()=>window.CR3BP.runSelfTests());
   if(id==='qwen')r.selfTestReturn=await page.evaluate(()=>window.__CR3BP__.runTests());
   if(id==='zwin')r.selfTestReturn=await page.evaluate(()=>window.CR3BP.runSelfTests());
   if(id==='zlinux')r.selfTestReturn=await page.evaluate(()=>runSelfTests(true));
   await page.waitForTimeout(1200);
   if(id==='codex'){await page.waitForFunction(()=>window.lastSelfTest, {timeout:30000});r.selfTestReturn=await page.evaluate(()=>window.lastSelfTest);}
   r.text=await page.locator('body').innerText();
   r.controls=await page.locator('button,input,select').evaluateAll(es=>es.map(e=>({tag:e.tagName,id:e.id,type:e.type,text:e.textContent.trim().slice(0,180),value:e.value,options:e.tagName==='SELECT'?[...e.options].map(x=>({value:x.value,text:x.textContent})):undefined})));
   r.layout=await page.evaluate(()=>({width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth,scrollHeight:document.documentElement.scrollHeight,canvases:[...document.querySelectorAll('canvas')].map(c=>({id:c.id,width:c.width,height:c.height,rect:c.getBoundingClientRect().toJSON()}))}));
   await page.screenshot({path:path.join(out,id+'.png'),fullPage:true});
  }catch(e){r.error=String(e);}
  report.submissions.push(r);fs.writeFileSync(path.join(out,'browser.json'),JSON.stringify(report,null,2)+'\n');
  console.log(id,JSON.stringify({loaded:r.loadedOffline,error:r.error,pageErrors:r.pageErrors,consoleErrors:r.consoleErrors,self:r.selfTestReturn?.summary||r.selfTestReturn?.passed||r.selfTestReturn?.pass,controls:r.controls?.filter(c=>c.tag!=='INPUT').map(c=>({id:c.id,text:c.text.slice(0,35)}))}));
  await context.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1;});
