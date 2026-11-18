import {chromium} from '/Users/avalok/.codex/skills/teardown/node_modules/playwright-core/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const root=new URL('../',import.meta.url),S=JSON.parse(fs.readFileSync(new URL('timing.json',root)));
const base='http://127.0.0.1:8765/media/biohydrogen/film/';
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
const results=[];
for(const [device,viewport] of [['desktop',{width:1440,height:1000}],['mobile',{width:390,height:844}]]){
 const page=await browser.newPage({viewport});await page.goto(base);
 await page.waitForFunction(()=>document.querySelector('#film').readyState>=2);
 const duration=await page.locator('#film').evaluate(v=>v.duration);assert(Math.abs(duration-S.duration/1.2)<.1);
 await page.locator('#film').evaluate(async v=>{v.muted=true;await v.play()});
 await page.waitForFunction(()=>document.querySelector('#film').currentTime>.3);
 await page.locator('#film').evaluate(v=>v.pause());
 await page.locator('.chapter[data-time]').nth(12).click();
 await page.waitForFunction(t=>document.querySelector('#film').currentTime>=t,S.scenes[12].start/1.2);
 await page.locator('#film').evaluate(v=>v.pause());
 const dimensions=await page.locator('#film').evaluate(v=>[v.videoWidth,v.videoHeight]);assert.deepEqual(dimensions,[1920,1080]);
 await page.screenshot({path:new URL(`shots/final-${device}.jpg`,root).pathname,type:'jpeg',quality:90});
 results.push({device,playback:true,chapter_seek:true,dimensions,duration});await page.close();
}
for(const file of ['source.zip','captions.srt','SCRIPT.txt','production/receipt.json']){
 const response=await fetch(base+file);assert.equal(response.status,200,file);
}
const range=await fetch(base+'biohydrogen-zh.mp4',{headers:{Range:'bytes=0-1023'}});assert.equal(range.status,206);assert.equal((await range.arrayBuffer()).byteLength,1024);
fs.writeFileSync(new URL('production/media-check.json',root),JSON.stringify({profiles:results,downloads:true,range_requests:true},null,2));
await browser.close();console.log(JSON.stringify(results));process.exit(0);
