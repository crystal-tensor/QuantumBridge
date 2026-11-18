import {chromium} from '/Users/avalok/.codex/skills/teardown/node_modules/playwright-core/index.mjs';
import fs from 'node:fs';
const root=new URL('../',import.meta.url),story=JSON.parse(fs.readFileSync(new URL('timing.json',root)));
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
page.on('pageerror',e=>{console.error(e);process.exitCode=1});
await page.goto('http://127.0.0.1:8765/media/biohydrogen/film/film.html?render');
await page.waitForFunction(()=>window.filmReady);
fs.mkdirSync(new URL('shots/',root),{recursive:true});
for(let i=0;i<story.scenes.length;i++){
 const s=story.scenes[i];await page.evaluate(t=>window.seekFilmReady(t),s.start+Math.min(9,s.duration*.4));
 await page.screenshot({path:new URL(`shots/${s.id}.jpg`,root).pathname,type:'jpeg',quality:90});
}
await page.evaluate(()=>window.setTheme('light'));await page.evaluate(t=>window.seekFilm(t),story.scenes[6].start+8);
await page.screenshot({path:new URL('shots/enzyme-light.jpg',root).pathname,type:'jpeg',quality:90});
await browser.close();
