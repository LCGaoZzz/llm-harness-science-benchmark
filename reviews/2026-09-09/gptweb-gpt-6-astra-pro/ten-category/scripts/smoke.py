import json, pathlib, platform, sys, time
from playwright.sync_api import sync_playwright
BASE=pathlib.Path(__file__).resolve().parents[1]; entries=json.loads((BASE/'entries.json').read_text())
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 env={'python':sys.version,'platform':platform.platform(),'browser':browser.version,'viewport':{'width':1440,'height':1000},'source_commit':'ac5a306be9b29978ad6787903821b4a6a181ff01','network_policy':'original HTML loaded via Playwright set_content into about:blank; all http/https network blocked','file_url_limitation':'Chromium policy returns ERR_BLOCKED_BY_ADMINISTRATOR for file:// and local HTTP navigation; not counted as submission failure'}
 (BASE/'evidence/environment.json').write_text(json.dumps(env,indent=2))
 for key, e in entries.items():
  ctx=browser.new_context(viewport=env['viewport'],locale='zh-CN'); requests=[]; errors=[]; logs=[]
  ctx.route('http://**/*',lambda route:(requests.append(route.request.url),route.abort())[-1]);ctx.route('https://**/*',lambda route:(requests.append(route.request.url),route.abort())[-1])
  page=ctx.new_page();page.on('pageerror',lambda err:errors.append(str(err)));page.on('console',lambda msg:logs.append({'type':msg.type,'text':msg.text}))
  result={'entry':e,'page_errors':errors,'console':logs,'external_requests':requests}
  try:
   ctx.route('http://127.0.0.1:8765/index.html',lambda route:route.fulfill(status=200,content_type='text/html; charset=utf-8',body=(BASE/e['html']).read_bytes()))
   page.set_content((BASE/e['html']).read_text(),wait_until='load',timeout=20000);page.wait_for_timeout(2000)
   result['title']=page.title();result['body']=page.locator('body').inner_text()
   result['controls']=page.locator('button,input,select').evaluate_all('(es)=>es.map(e=>({tag:e.tagName,id:e.id,type:e.type,text:e.innerText,value:e.value,disabled:e.disabled}))')
   result['globals']=page.evaluate('()=>Object.keys(window).filter(k=>/CR3BP|lab|Lab/.test(k)).map(k=>({key:k,keys:Object.keys(window[k]||{})}))')
   result['viewport']=page.evaluate('()=>({innerWidth,innerHeight,scrollWidth:document.documentElement.scrollWidth,scrollHeight:document.documentElement.scrollHeight,canvases:[...document.querySelectorAll("canvas")].map(e=>({id:e.id,width:e.width,height:e.height,rect:e.getBoundingClientRect().toJSON()}))})')
   page.screenshot(path=str(BASE/'evidence'/f'{key}-desktop.png'),full_page=True,timeout=15000)
   result['loaded']=True
  except Exception as ex: result['loaded']=False;result['error']=str(ex)
  (BASE/'evidence'/f'{key}-smoke.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)); print(key,result.get('loaded'),len(errors),len(requests),result.get('globals'),flush=True)
  ctx.close()
 browser.close()
