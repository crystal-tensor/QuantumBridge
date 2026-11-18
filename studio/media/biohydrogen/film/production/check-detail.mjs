import {chromium} from '/Users/avalok/.codex/skills/teardown/node_modules/playwright-core/index.mjs';
import fs from 'node:fs';
const root=new URL('../',import.meta.url),S=JSON.parse(fs.readFileSync(new URL('timing.json',root)));
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:4});
await page.goto('http://127.0.0.1:8765/media/biohydrogen/film/film.html?render');
await page.waitForFunction(()=>window.filmReady);
for(const theme of ['dark','light'])for(const [id,clip] of [['cell',{x:1120,y:390,width:250,height:230}],['chain',{x:570,y:430,width:270,height:230}],['enzyme',{x:795,y:360,width:380,height:260}]]){
 await page.evaluate(theme=>window.setTheme(theme),theme);
 await page.evaluate(t=>window.seekFilm(t),S.scenes.find(s=>s.id===id).start+8);
 await page.screenshot({path:new URL(`shots/detail-${theme}-${id}.jpg`,root).pathname,clip,type:'jpeg',quality:95});
}
await browser.close();process.exit(0);
