import json,pathlib,time
from playwright.sync_api import sync_playwright
B=pathlib.Path(__file__).resolve().parents[1];E=json.loads((B/'entries.json').read_text())
SNAP=r'''key=>{
 if(key.startsWith('codex')){const a=labSnapshot();return{t:a.time,s:a.state,running:a.running,view:[a.span,...a.center],h:a.h,method:a.method}}
 if(key.startsWith('gptweb')){const a=Lab.getSnapshot();return{t:a.time,s:a.state,running:!a.paused,view:a.view,h:a.h,method:a.method}}
 if(key.startsWith('harnessL_ds')){const a=__CR3BP_LAB__.sim;return{t:a.t,s:[a.state.x,a.state.y,a.state.vx,a.state.vy],running:a.running,halted:a.halted}}
 if(key.startsWith('harnessL_qwen'))return{t:S.t,s:S.state,running:S.running,view:S.view,method:S.itg,h:S.h};
 if(key.startsWith('kimiweb')){const a=__AUDIT_KIMI__.sim;return{t:a.t,s:a.s,running:a.running,view:__AUDIT_KIMI__.view,h:a.dt,method:a.integ}}
 if(key==='zcode_glm-5.3max'){return{t:app.sim.t,s:Array.from(app.sim.s),running:app.running,view:app.view,h:app.h,method:app.integrator}}
 return{t:sim.t,s:sim.s,running:sim.running,view:cam,h:curDt,method:$('selInteg').value};
}'''
with sync_playwright() as p:
 br=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for key,e in E.items():
  ctx=br.new_context(viewport={'width':1440,'height':1000});ctx.route('**/*',lambda r:r.abort());pg=ctx.new_page();err=[];pg.on('pageerror',lambda ex:err.append(str(ex)));txt=(B/e['html']).read_text()
  if key.startswith('kimiweb'):txt=txt.replace('setTimeout(runSelfTests,50);','window.__AUDIT_KIMI__={sim,view};setTimeout(runSelfTests,50);')
  pg.set_content(txt);pg.wait_for_timeout(1200);out={'key':key,'steps':[],'errors':err}
  play='#btnRun' if key.startswith(('kimiweb','zcode')) else '#play';step='#btnStep' if key.startswith(('kimiweb','zcode')) else ('#stepBtn' if key.startswith('harnessL_ds') else '#step');reset='#btnReset' if key.startswith(('kimiweb','zcode')) else '#reset'
  def snap():return pg.evaluate(SNAP,key)
  def pause():
   if snap().get('running'):pg.locator(play).click();pg.wait_for_timeout(30)
  try:
   pause();a=snap();pg.wait_for_timeout(150);b=snap();out['pause_holds_time']=a['t']==b['t']
   pg.locator(step).click();c=snap();out['single_step']={'before':b,'after':c,'advances':c['t']>b['t']}
   pg.locator(play).click();pg.wait_for_timeout(220);pause();d=snap();out['run_advances']=d['t']>c['t']
   pg.locator(reset).click();pause();out['reset']=snap()
   preset_sel='[data-preset]'
   if key.startswith('kimiweb'):preset_sel='#pL4,#pL1,#pEarth,#pMoon'
   if key.startswith('harnessL_qwen'):preset_sel='#presets button'
   # Qwen container is generated; fall back to buttons containing known preset text.
   if key.startswith('harnessL_qwen') and not pg.locator(preset_sel).count():preset_sel='button.preset'
   if key.startswith('harnessL_ds') and not pg.locator(preset_sel).count():preset_sel='#presets button'
   out['presets']=[]
   for i in range(pg.locator(preset_sel).count()):
    item=pg.locator(preset_sel).nth(i);label=item.inner_text();item.click();pause();before=snap();pg.locator(step).click();after=snap();out['presets'].append({'label':label,'before':before,'after':after,'advances':after['t']>before['t']})
   # Restore default preset; test every displayed integrator choice.
   if pg.locator(preset_sel).count():pg.locator(preset_sel).first.click();pause()
   meth={'codex_6astra-xhigh':'#integrator','gptweb_gpt-6pro':'#method','harnessL_ds-4.1flashmax':'#method','zcode_glm-5.3max':'#selInt','zcode_glm-5.3maxlinux':'#selInteg'}.get(key)
   out['method_controls']=[]
   if meth:
    for val in pg.locator(meth+' option').evaluate_all('(es)=>es.map(e=>e.value)'):
     pg.locator(meth).select_option(val);pause();a=snap();pg.locator(step).click();b=snap();out['method_controls'].append({'value':val,'advances':b['t']>a['t'],'after':b})
   canvas=pg.locator('canvas').first;box=canvas.bounding_box();pg.mouse.move(box['x']+box['width']*.4,box['y']+box['height']*.4);before=snap();pg.mouse.wheel(0,-150);pg.wait_for_timeout(90);after=snap();out['wheel_zoom']={'before':before.get('view'),'after':after.get('view')}
   before=snap();pg.mouse.move(box['x']+box['width']*.45,box['y']+box['height']*.45);pg.mouse.down();pg.mouse.move(box['x']+box['width']*.45+40,box['y']+box['height']*.45+25,steps=5);pg.mouse.up();after=snap();out['drag_pan']={'before':before.get('view'),'after':after.get('view')}
   pg.set_viewport_size({'width':390,'height':844});pg.wait_for_timeout(250);out['mobile']=pg.evaluate('()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,height:innerHeight,scrollHeight:document.documentElement.scrollHeight,canvases:[...document.querySelectorAll("canvas")].map(x=>({id:x.id,rect:x.getBoundingClientRect().toJSON()}))})');pg.screenshot(path=str(B/'evidence'/f'{key}-mobile.png'),full_page=True)
   out['complete']=True
  except Exception as ex:out['complete']=False;out['error']=str(ex)
  (B/'evidence'/f'{key}-ui.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(key,out['complete'],out.get('error'),len(out.get('presets',[])),len(out.get('method_controls',[])),out.get('mobile',{}).get('scrollWidth'),flush=True);ctx.close()
 br.close()
