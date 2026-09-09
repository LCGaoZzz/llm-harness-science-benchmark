import pathlib,json,time
from playwright.sync_api import sync_playwright
B=pathlib.Path(__file__).resolve().parents[1];E=json.loads((B/'entries.json').read_text());key='zcode_glm-5.3max';out={}
with sync_playwright()as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);pg=b.new_page(viewport={'width':1280,'height':720});pg.set_default_timeout(3000);pg.route('**/*',lambda r:r.abort());errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
 pg.set_content((B/E[key]['html']).read_text());pg.wait_for_timeout(900);print('loaded',flush=True)
 out['presets']=[]
 for n in ['l4','l1','earth','flyby']:
  print(n,flush=True);r=pg.evaluate('''n=>{document.querySelector('[data-preset="'+n+'"]').click();CR3BP.setRunning(false);const a=CR3BP.getState();document.getElementById('btnStep').click();return{before:a,after:CR3BP.getState()}}''',n);out['presets'].append({'name':n,**r});print('applied',flush=True);pg.wait_for_timeout(80)
 out['methods']=[]
 pg.evaluate("()=>{CR3BP.applyPreset('l4',false)}")
 for n in ['rk4','mid','sym4']:
  pg.select_option('#selInt',n);pg.click('#btnStep');out['methods'].append(pg.evaluate('()=>CR3BP.getState()'))
 print('methods done',flush=True)
 out['desktop']={'viewport':[1280,720]};pg.screenshot(path=str(B/'evidence'/f'{key}-desktop-retry.png'),full_page=True,timeout=4000)
 pg.set_viewport_size({'width':390,'height':844});pg.wait_for_timeout(200);out['mobile']=pg.evaluate('()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,height:innerHeight,scrollHeight:document.documentElement.scrollHeight})');pg.screenshot(path=str(B/'evidence'/f'{key}-mobile.png'),full_page=True,timeout=4000)
 out['errors']=errs;(B/'evidence'/f'{key}-ui-retry.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));b.close();print('done',flush=True)
