const http=require('node:http'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
http.createServer((req,res)=>{if(req.url==='/'||req.url==='/index.html'){res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store'});res.end(fs.readFileSync(path.join(root,'index.html')));}else{res.writeHead(404);res.end('Not found');}}).listen(8741,'127.0.0.1',()=>console.log('Earth-Moon laboratory: http://127.0.0.1:8741'));
