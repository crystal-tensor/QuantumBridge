import {chromium} from '/Users/avalok/.codex/skills/teardown/node_modules/playwright-core/index.mjs';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const ROOT=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const S=JSON.parse(fs.readFileSync(path.join(ROOT,'timing.json'))),fps=24;
const DIR=path.join(ROOT,'production','renders');fs.mkdirSync(DIR,{recursive:true});
const url='http://127.0.0.1:8765/media/biohydrogen/film/film.html?render';
let next=0;
async function worker(n){
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--disable-background-timer-throttling','--disable-renderer-backgrounding']});
 const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
 let error;page.on('pageerror',e=>{error=e});
 await page.goto(url);await page.waitForFunction(()=>window.filmReady);await page.evaluate(()=>document.fonts.ready);
 const cdp=await page.context().newCDPSession(page);
 while(next<S.scenes.length){
  const i=next++,s=S.scenes[i],out=path.join(DIR,`${String(i).padStart(2,'0')}.mp4`);
  if(fs.existsSync(out)&&fs.statSync(out).size>10000){console.log(`resume ${i} ${s.id}`);continue;}
  const ff=spawn('ffmpeg',['-hide_banner','-loglevel','error','-y','-filter_threads','1','-threads','1','-f','image2pipe','-vcodec','mjpeg','-framerate',String(fps),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-threads','2',out],{stdio:['pipe','ignore','pipe']});
  let stderr='',pipeError;ff.stderr.on('data',b=>{stderr+=b;fs.appendFileSync(path.join(DIR,`${i}-ffmpeg.log`),b)});ff.stdin.on('error',e=>{pipeError=e});const done=once(ff,'close');
  const first=Math.round(s.start*fps),end=Math.round(s.end*fps);
  console.log(`worker ${n}: ${i} ${s.id}, ${end-first} frames`);
  for(let f=first;f<end;f++){
   await page.evaluate(t=>window.seekFilmReady(t),Math.max(s.start+.001,f/fps));
   if(error)throw error;
   const {data}=await cdp.send('Page.captureScreenshot',{format:'jpeg',quality:92,fromSurface:true,captureBeyondViewport:true,optimizeForSpeed:true,clip:{x:0,y:0,width:1920,height:1080,scale:1}});
   if(pipeError)throw Error(stderr||pipeError.message);
   if(!ff.stdin.write(Buffer.from(data,'base64')))await once(ff.stdin,'drain').catch(()=>{throw Error(stderr||'pipe closed')});
  }
  ff.stdin.end();const [code]=await done;if(code!==0)throw Error(stderr);
  console.log(`finished ${i} ${s.id}`);
 }
 await Promise.race([browser.close(),new Promise(resolve=>setTimeout(resolve,3000))]);
}
await Promise.all([worker(1),worker(2),worker(3)]);
const list=S.scenes.map((s,i)=>`file '${path.join(DIR,`${String(i).padStart(2,'0')}.mp4`)}'`).join('\n');
fs.writeFileSync(path.join(DIR,'concat.txt'),list);
const concat=spawn('ffmpeg',['-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',path.join(DIR,'concat.txt'),'-c','copy',path.join(DIR,'picture.mp4')],{stdio:'inherit'});
const [code]=await once(concat,'close');if(code!==0)throw Error('concat failed');
console.log('Picture render complete');
process.exit(0);
