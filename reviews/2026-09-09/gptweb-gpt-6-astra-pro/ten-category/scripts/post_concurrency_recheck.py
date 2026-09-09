"""Validate specific issues raised by a concurrent reviewer, without modifying entries."""
import json, pathlib, zipfile, hashlib, subprocess, sys
from playwright.sync_api import sync_playwright
B=pathlib.Path(__file__).resolve().parents[1];entries=json.loads((B/'entries.json').read_text());out={}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for k in ['harnessL_qwen-3.8flashxhigh','harnessL_ds-4.1flashmax']:
  ctx=browser.new_context(viewport={'width':1440,'height':1000});ctx.route('**/*',lambda r:r.abort());pg=ctx.new_page();pg.set_content((B/entries[k]['html']).read_text());pg.wait_for_timeout(300)
  if 'qwen' in k:
   r=pg.evaluate('''()=>{S.running=false;setIC([.6,.2,-.1,.35]);const ic=S.state.slice();document.querySelector('#step').click();const afterStep={s:S.state.slice(),t:S.t,h:S.h,sub:S.sub};document.querySelector('#reset').click();const afterReset={s:S.state.slice(),t:S.t};runTests();return {ic,afterStep,afterReset,afterTests:{s:S.state.slice(),t:S.t,bad:S.bad}};}''');pg.evaluate("()=>{S.running=true;}");pg.wait_for_timeout(250);r['afterPlay']=pg.evaluate('()=>({s:S.state.slice(),t:S.t,running:S.running,bad:S.bad})');out[k]=r
  else:
   pg.evaluate('()=>{__CR3BP_LAB__.sim.running=false;}');pg.wait_for_timeout(150)
   cv=pg.locator('canvas').first
   before=hashlib.sha256(cv.screenshot()).hexdigest()
   prior=pg.evaluate("()=>document.querySelector('#zoom').value")
   pg.evaluate("()=>{const z=document.querySelector('#zoom');z.value=Number(z.value)+0.1;z.dispatchEvent(new Event('input',{bubbles:true}));}")
   pg.wait_for_timeout(200);after=hashlib.sha256(cv.screenshot()).hexdigest()
   pg.evaluate('()=>__CR3BP_LAB__.render()');forced=hashlib.sha256(cv.screenshot()).hexdigest()
   out[k]={'paused_zoom_before_input':prior,'canvas_before':before,'canvas_after_zoom_input':after,'canvas_after_forced_render':forced,'input_changes_canvas':before!=after,'forced_render_changes_canvas':after!=forced}
  ctx.close()
 browser.close()
(B/'evidence/post-concurrency-recheck.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False,indent=2))
