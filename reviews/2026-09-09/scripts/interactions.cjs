const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{pathToFileURL}=require('node:url');
const {chromium}=require('playwright');
const root=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);
const configs={
 codex:{dir:'codex--6astra-xhigh--2026-09-09',file:'index.html',play:'#play',step:'#step',reset:'#reset',method:['#integrator','rk4'],ic:['x0','y0','vx0','vy0'],apply:'#apply',presets:'[data-preset]',canvas:'#plot',test:'#runTests'},
 gptweb:{dir:'gptweb--gpt-6pro--2026-09-09',file:'earth_moon_lab.html',play:'#play',step:'#step',reset:'#reset',method:['#method','rk4'],ic:['x0','y0','vx0','vy0'],apply:'#apply',presets:'[data-preset]',test:'#runTests'},
 ds:{dir:'harnessL--ds-4.1flashmax--2026-09-09',file:'lab.html',play:'#play',step:'#stepBtn',reset:'#reset',method:['#method','rk4'],ic:['ic-x','ic-y','ic-vx','ic-vy'],apply:'#applyIC',presets:'.preset',test:'#runTests'},
 qwen:{dir:'harnessL--qwen-3.8flashxhigh--2026-09-09',file:'cr3bp_lab.html',play:'#play',step:'#step',reset:'#reset',methodButton:'#itgbtns button[data-m="sympl"]',ic:['sx','sy','svx','svy'],presets:'#presets button',test:'#runtests'},
 kimi:{dir:'kimiweb--k3swarm-max--2026-09-09',file:'index.html',play:'#btnRun',step:'#btnStep',reset:'#btnReset',methodButton:'#intVerlet',ic:['icX','icY','icVX','icVY'],apply:'#btnApplyIC',presets:'#pL4,#pL1,#pEarth,#pMoon',test:'#btnRerun'},
 zwin:{dir:'zcode--glm-5.3max--2026-09-09',file:'index.html',play:'#btnRun',step:'#btnStep',reset:'#btnReset',method:['#selInt','sym4'],ic:['icx','icy','icvx','icvy'],presets:'[data-preset]',test:'#btnTest'},
 zlinux:{dir:'zcode--glm-5.3maxlinux--2026-09-09',file:'index.html',play:'#btnRun',step:'#btnStep',reset:'#btnReset',method:['#selInteg','rk4'],ic:['inX0','inY0','inVx0','inVy0'],apply:'#btnApplyIC',presets:'[data-preset]',test:'#btnSelfTest'}
};
const expressions={
 codex:'({...labSnapshot(),s:labSnapshot().state,t:labSnapshot().time})',
 gptweb:'({...Lab.getSnapshot(),s:Lab.getSnapshot().state,t:Lab.getSnapshot().time,running:!Lab.getSnapshot().paused})',
 ds:'(()=>{const a=__CR3BP_LAB__,q=a.sim;return {s:[q.state.x,q.state.y,q.state.vx,q.state.vy],originalInitial:[q.ic.x,q.ic.y,q.ic.vx,q.ic.vy],t:q.t,running:q.running,h:a.opts.dt,steps:q.steps,halted:q.halted,haltMsg:q.haltMsg,C0:q.C0,C:q.C,method:a.opts.method}})()',
 qwen:'(()=>{const q=__CR3BP__.S;return {s:q.state.slice(),t:q.t,running:q.running,h:q.h,sub:q.sub,bad:q.bad,C0:q.C0,method:q.itg,view:q.view}})()',
 zwin:'({...CR3BP.getState(),originalInitial:Array.from(CR3BP.app.sim.s0),running:CR3BP.app.running,view:CR3BP.app.cam})',
 zlinux:'({s:sim.s.slice(),t:sim.t,running:sim.running,h:curDt,steps:sim.nSteps,status:sim.status,C0:sim.C0,view:cam})',
 kimi:`(()=>{const t=document.getElementById('status').textContent,lines=t.split(String.fromCharCode(10)),get=k=>Number(lines.find(x=>x.split('=')[0].trim()===k)?.split('=')[1]);return {s:['x','y','vx','vy'].map(get),t:get('t'),h:Number(t.split('dt = ')[1]?.split(String.fromCharCode(10))[0]),running:document.getElementById('btnRun').textContent.includes('暂停'),text:t}})()`
};
const distance=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));
(async()=>{const browser=await chromium.launch({channel:process.env.REVIEW_BROWSER_CHANNEL||'msedge',headless:true});let report=process.env.REVIEW_ONLY?JSON.parse(fs.readFileSync(path.join(out,'interactions.json'),'utf8')):{browser:browser.version(),viewport:{width:1440,height:1000},generatedAt:new Date().toISOString(),submissions:[]};
for(const [id,c]of Object.entries(configs)){
 if(process.env.REVIEW_ONLY&&!process.env.REVIEW_ONLY.split(',').includes(id))continue;
 const context=await browser.newContext({viewport:report.viewport,offline:true});const page=await context.newPage();const r={id,pageErrors:[],checks:{}};
 page.on('pageerror',e=>r.pageErrors.push(e.message));
 const snap=()=>page.evaluate(expressions[id]);
 const pause=async()=>{if((await snap()).running)await page.locator(c.play).click();await page.waitForTimeout(80);};
 try{
  await page.goto(pathToFileURL(path.join(root,c.dir,c.file)).href);await page.waitForTimeout(900);await pause();await page.locator(c.reset).click();await pause();
  const initial=await snap();await page.locator(c.step).click();await page.waitForTimeout(80);const stepped=await snap();r.checks.singleStep={before:initial,after:stepped,deltaT:stepped.t-initial.t,expectedH:initial.h};
  await page.locator(c.play).click();await page.waitForTimeout(300);await pause();const played=await snap();await page.waitForTimeout(150);const paused=await snap();r.checks.playPause={timeAdvanced:played.t>stepped.t,pauseStable:paused.t===played.t,played,paused};
  await page.locator(c.reset).click();await pause();const reset=await snap();r.checks.reset={reset,initialStateError:distance(reset.s,initial.s),returnedToZero:reset.t===0};
  // Switch methods while paused and confirm continuity.
  await page.locator(c.step).click();const preSwitch=await snap();
  if(c.method)await page.locator(c.method[0]).selectOption(c.method[1]);else await page.locator(c.methodButton).click();
  const postSwitch=await snap();r.checks.methodSwitch={before:preSwitch,after:postSwitch,stateError:distance(preSwitch.s,postSwitch.s),timeError:postSwitch.t-preSwitch.t};
  for(let i=0;i<4;i++){await page.locator('#'+c.ic[i]).fill(String([.6,.2,-.1,.35][i]));await page.locator('#'+c.ic[i]).blur();}
  if(c.apply)await page.locator(c.apply).click();await pause();const custom=await snap();r.checks.customInitial={snapshot:custom,stateError:distance(custom.s,[.6,.2,-.1,.35])};
  // Every supplied preset is clicked and stepped. This is a smoke test, not a full orbit validation.
  const buttons=page.locator(c.presets);r.checks.presets=[];
  for(let i=0;i<await buttons.count();i++){const name=await buttons.nth(i).innerText();await buttons.nth(i).click();await pause();const a=await snap();await page.locator(c.step).click();await page.waitForTimeout(50);const b=await snap();r.checks.presets.push({name,before:a,after:b,advanced:b.t>a.t,finite:b.s.every(Number.isFinite)});}
  // Fresh L1 view and a real trajectory for visual review.
  if(await buttons.count()>1)await buttons.nth(1).click();await pause();
  await page.locator(c.play).click();await page.waitForTimeout(400);await pause();
  const canvas=page.locator('canvas').first();const hash=async()=>crypto.createHash('sha256').update(await canvas.screenshot()).digest('hex');
  const beforeZoom=await hash();await canvas.hover();await page.mouse.wheel(0,-240);await page.waitForTimeout(120);const afterZoom=await hash();
  const box=await canvas.boundingBox();await page.mouse.move(box.x+box.width*.6,box.y+box.height*.5);await page.mouse.down();await page.mouse.move(box.x+box.width*.6+40,box.y+box.height*.5+30,{steps:5});await page.mouse.up();await page.waitForTimeout(120);const afterPan=await hash();
  r.checks.view={zoomChanged:beforeZoom!==afterZoom,panChanged:afterZoom!==afterPan};
  await page.screenshot({path:path.join(out,id+'-interaction.png'),fullPage:true});
  if(id==='gptweb')await page.locator('#testOpen').click();
  await page.locator(c.test).click();await page.waitForTimeout(1600);await page.waitForFunction(sel=>!document.querySelector(sel).disabled,c.test,{timeout:30000});
  r.checks.selfTestPanel=(await page.locator('body').innerText());
  if(id==='qwen'){
   const a=await snap();await page.locator(c.play).click();await page.waitForTimeout(250);const b=await snap();
   r.checks.resumeAfterSelfTests={before:a,after:b,timeAdvanced:b.t>a.t};await pause();
  }
  // Boundary probe: finite high speed, endpoints outside Earth but segment crosses its surface.
  // Use the exposed simulation interface; original code and guards remain unchanged.
  if(id==='codex'||id==='gptweb')r.checks.crossing=await page.evaluate(id=>{const p=id==='codex'?CR3BP:Lab.physics,s=[-p.MU-.03,0,100,0];try{const z=id==='codex'?p.checkedStep(s,.001,'rk4'):p.guardedStep(s,.001,'rk4');return {accepted:true,before:s,after:z};}catch(e){return {accepted:false,error:e.message,before:s};}},id);
  if(id==='ds')r.checks.crossing=await page.evaluate(()=>{const a=__CR3BP_LAB__,mu=a.C.MU_EARTH_MOON,s={x:-mu-.03,y:0,z:0,vx:100,vy:0,vz:0};a.setIC(s);document.getElementById('method').value='rk4';document.getElementById('method').dispatchEvent(new Event('change'));const used=a.oneStep(.001);return {accepted:used>0,before:s,after:a.sim.state,halted:a.sim.halted,t:a.sim.t};});
  if(id==='qwen')r.checks.crossing=await page.evaluate(()=>{const a=__CR3BP__,s=[-a.MU-.03,0,100,0];a.setIC(s);a.S.itg='rk4';const bad=a.advance(.001);return {accepted:!bad,before:s,after:a.S.state,t:a.S.t};});
  if(id==='zwin')r.checks.crossing=await page.evaluate(()=>{const a=CR3BP,m=a.app.model,s=[-m.mu-.03,0,100,0],q=a.makeSim(m,s);a.simStep(q,.001,1,'rk4');return {accepted:!q.crashed,before:s,after:Array.from(q.s),t:q.t,status:q.status};});
  if(id==='zlinux')r.checks.crossing=await page.evaluate(()=>{const s=[-MU-.03,0,100,0];sim.s=s.slice();sim.t=0;sim.status='paused';curDt=.001;document.getElementById('selInteg').value='rk4';const ok=stepOnce();return {accepted:ok,before:s,after:sim.s,t:sim.t,status:sim.status};});
  if(id==='kimi'){
   for(let i=0;i<4;i++){await page.locator('#'+c.ic[i]).fill(String([-.012150585609624-.03,0,100,0][i]));}await page.locator(c.apply).click();await page.locator('#intRK4').click();await page.locator(c.step).click();await page.waitForTimeout(60);r.checks.crossing={after:await snap()};
  }
 }catch(e){r.error=String(e);}
 report.submissions=report.submissions.filter(x=>x.id!==id);report.submissions.push(r);fs.writeFileSync(path.join(out,'interactions.json'),JSON.stringify(report,null,2)+'\n');console.log(id,JSON.stringify({error:r.error,pageErrors:r.pageErrors,step:r.checks.singleStep?.deltaT,expected:r.checks.singleStep?.expectedH,resetError:r.checks.reset?.initialStateError,custom:r.checks.customInitial?.stateError,presets:r.checks.presets?.map(x=>[x.name,x.advanced]),view:r.checks.view,crossing:r.checks.crossing}));await context.close();
}
await browser.close();})().catch(e=>{console.error(e);process.exitCode=1;});
