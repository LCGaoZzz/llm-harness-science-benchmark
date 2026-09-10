// Reviewer-owned browser checks against the unmodified shipped HTML.
const {chromium}=require('playwright'),{pathToFileURL}=require('node:url');
const fs=require('node:fs'),path=require('node:path');
(async()=>{
 const root=path.resolve(__dirname,'../../..'),browser=await chromium.launch({channel:'msedge',headless:true});
 const page=await browser.newPage({viewport:{width:1680,height:1000}});
 const out={browser:browser.version(),pageErrors:[],consoleErrors:[],requests:[]};
 page.on('pageerror',e=>out.pageErrors.push(String(e)));page.on('console',m=>{if(m.type()==='error')out.consoleErrors.push(m.text())});
 await page.route('http://**/*',r=>{out.requests.push(r.request().url());return r.abort()});
 await page.route('https://**/*',r=>{out.requests.push(r.request().url());return r.abort()});
 await page.goto(pathToFileURL(path.join(root,'submissions/harnessL--glm5.3-max--2026-09-10/lab.html')).href);
 await page.waitForFunction('window.__labReady===true');
 out.selfTests=await page.evaluate('window.__lab.selfTests()');
 out.afterSelfTests=await page.evaluate(()=>({state:__lab.state(),banner:document.getElementById('banner').textContent,visible:getComputedStyle(document.getElementById('banner')).display!=='none'}));
 await page.screenshot({path:path.join(__dirname,'browser-selftests.png')});
 out.presets={};for(const [name,T] of Object.entries({tadpole:200,l1:30,earth:50,assist:14})){
  await page.locator(`[data-preset="${name}"]`).click();out.presets[name]=await page.evaluate(t=>__lab.runFor(t,3e6),T);
 }
 await page.locator('[data-preset="tadpole"]').click();
 await page.locator('#selInteg').selectOption('rk4');await page.locator('#inpDt').fill('0.01');await page.locator('#inpDt').press('Tab');
 const before=await page.evaluate('window.__lab.state()');await page.locator('#btnStep').click();const after=await page.evaluate('window.__lab.state()');
 await page.locator('#btnReset').click();const reset=await page.evaluate('window.__lab.state()');
 out.interactions={singleStep:after.t-before.t,resetTime:reset.t,resetStateError:Math.hypot(...reset.s.map((x,i)=>x-before.s[i])),resetTrail:reset.trailN};
 await page.locator('#btnRun').click();await page.waitForTimeout(250);await page.locator('#btnRun').click();
 const frozen=await page.evaluate('window.__lab.state().t');await page.waitForTimeout(100);out.interactions.pauseFreezes=frozen===await page.evaluate('window.__lab.state().t');
 const view=await page.evaluate('window.__lab.getView()');await page.mouse.move(850,500);await page.mouse.wheel(0,-720);await page.waitForTimeout(100);
 out.interactions.wheelZoom=(await page.evaluate('window.__lab.getView().ppu'))>view.ppu;
 const x=await page.evaluate('window.__lab.getView().cx');await page.mouse.move(850,500);await page.mouse.down();await page.mouse.move(920,500,{steps:5});await page.mouse.up();out.interactions.panChangesX=x!==await page.evaluate('window.__lab.getView().cx');
 const state1=await page.evaluate('window.__lab.state()');await page.locator('#selInteg').selectOption('imp');const state2=await page.evaluate('window.__lab.state()');out.interactions.switchPreservesState=JSON.stringify(state1.s)===JSON.stringify(state2.s)&&state1.C0===state2.C0&&state1.t===state2.t;
 await page.locator('#selInteg').selectOption('rk4');
 out.boundaries={};
 for(const [name,s,h] of [['crossingEarth',[-.0121505856096241-.03,0,100,0],.001],['moonCenter',[1-.0121505856096241,0,0,0],.001],['insideEarth',[.005-.0121505856096241,0,0,1],.00001]]){
  out.boundaries[name]=await page.evaluate(({s,h})=>{__lab.setIC({x:s[0],y:s[1],vx:s[2],vy:s[3]});__lab.setDt(h);const before=__lab.state();__lab.stepOnce();return {before,after:__lab.state()};},{s,h});
 }
 await page.locator('[data-preset="tadpole"]').click();await page.locator('#inpDt').fill('-0.01');await page.locator('#inpDt').press('Tab');await page.locator('#btnStep').click();out.boundaries.negativeDt=await page.evaluate('window.__lab.state()');
 out.moonSpeed=await page.evaluate(()=>{__lab.setIC({x:1-__lab.MU,y:0,vx:0,vy:0});return {pageFormula:Math.hypot(0+0,0-(1-__lab.MU)),correctMoonRelativeSpeed:0};});
 fs.writeFileSync(path.join(__dirname,'browser.json'),JSON.stringify(out,null,2)+'\n');
 console.log(JSON.stringify({selfTests:[out.selfTests.passed,out.selfTests.total],afterSelfTests:out.afterSelfTests,interactions:out.interactions,boundaries:out.boundaries,moonSpeed:out.moonSpeed},null,2));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
