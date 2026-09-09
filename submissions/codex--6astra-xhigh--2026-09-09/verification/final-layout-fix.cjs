const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),file=path.join(root,'index.html');let s=fs.readFileSync(file,'utf8'),old=s;
function replace(a,b){if(!s.includes(a))throw Error('Missing edit target '+a);s=s.replace(a,b);}
replace('let center=[.15,0],span=2.9,W=800,H=600,dpr=1,','let autoFit=true,center=[.15,0],span=2.9,W=800,H=600,dpr=1,');
replace('function loadPreset(key){preset=key;','function fittedSpan(p){const vertical=preset===\'l4\'?2.0:preset===\'l1\'?1.0:.85;return Math.max(p.span,vertical*W/Math.max(1,H-96));}\n function loadPreset(key){preset=key;autoFit=true;');
replace('center=p.center.slice();span=p.span;','center=p.center.slice();span=fittedSpan(p);');
replace('H=Math.max(1,rect.height);dpr=','H=Math.max(1,rect.height);if(autoFit){span=fittedSpan(P.presets[preset]);syncSettings();updateData();}dpr=');
replace('function zoomAt(factor,px=W/2,py=H/2){const before=','function zoomAt(factor,px=W/2,py=H/2){autoFit=false;const before=');
replace("$('home').onclick=()=>{center=P.presets[preset].center.slice();span=P.presets[preset].span;","$('home').onclick=()=>{autoFit=true;center=P.presets[preset].center.slice();span=fittedSpan(P.presets[preset]);");
replace("if(e.button!==0)return;drag=","if(e.button!==0)return;autoFit=false;drag=");
replace('if(moves[e.key]){e.preventDefault();center','if(moves[e.key]){e.preventDefault();autoFit=false;center');
const physics=x=>x.match(/<script id="physics">([\s\S]*?)<\/script>/)[1];
if(physics(old)!==physics(s))throw Error('Unexpected numerical core change');
fs.writeFileSync(path.join(__dirname,'round-12-before-layout.html'),old);
fs.writeFileSync(file,s);
fs.writeFileSync(path.join(__dirname,'final-layout-audit.json'),JSON.stringify({stage:'Round 12 final delivery QA; no new numerical method or configuration',reason:'At actual 1265px viewport the L4 initial position was outside the plot. Fit both world dimensions after resize/preset/home, preserve manual zoom and pan.',before_sha256:crypto.createHash('sha256').update(old).digest('hex'),after_sha256:crypto.createHash('sha256').update(s).digest('hex'),physics_unchanged:physics(old)===physics(s)},null,2));
