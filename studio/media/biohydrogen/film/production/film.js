(() => {
const S=window.STORY,art=document.querySelector('#art'),stage=document.querySelector('#stage');
let sceneIndex=-1,paused=true,clock=0,last=0,visible=true,renderMode=new URLSearchParams(location.search).has('render');
document.querySelector('#standalone-home').hidden=renderMode;
let flows=[],bubbles=[];const reduced=matchMedia('(prefers-reduced-motion:reduce)');
let conditions=null;
const mechanismOf=c=>!c.light?'无光：光驱动电子流停止':!c.enzyme?'氢酶关闭：产氢反应停止':c.oxygen?'氧气积累：敏感氢酶受抑制':'光照与低氧条件：产氢通路可用';
const smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x)};
const video=document.querySelector('#model-video');
function resize(){stage.style.transform=`scale(${Math.min(innerWidth/1920,innerHeight/1080)})`;}
addEventListener('resize',resize);resize();
function set(t){
 clock=Math.max(0,Math.min(S.duration-.001,t));
 let i=S.scenes.findIndex(s=>clock>=s.start&&clock<s.end);if(i<0)i=S.scenes.length-1;
 const s=S.scenes[i],local=clock-s.start,p=local/s.duration;
 if(sceneIndex!==i){
  sceneIndex=i;art.innerHTML=window.ART[s.id];
  flows=[...art.querySelectorAll('.flow')].map(el=>{const path=art.querySelector('#'+el.dataset.route);return {el,path,length:path.getTotalLength(),offset:+el.dataset.offset,type:el.classList.contains('photon')?'photon':'other'}});
  bubbles=[...art.querySelectorAll('.bubble')];
  document.querySelector('#title').textContent=s.title;
  document.querySelector('#eyebrow').textContent=s.eyebrow;
  document.querySelector('#figure-id').textContent=`Fig ${String(i+1).padStart(2,'0')} / ${S.scenes.length}`;
  if(!renderMode&&s.id==='opening'&&!paused)video.play().catch(()=>{});else video.pause();
 }
 const entering=smooth(local/.9),exiting=smooth((s.duration-local)/.7),opacity=entering*exiting;
 art.style.opacity=opacity;
 const world=art.querySelector('.world');
 // The camera is schematic; this small continuous push has no quantitative meaning.
 const zoom=1+Math.min(.025,p*.025);world.setAttribute('transform',`translate(${960*(1-zoom)} ${530*(1-zoom)}) scale(${zoom})`);
 for(const f of flows){const fraction=((local/(f.type==='photon'?4.3:7.5)+f.offset)%1+1)%1;const point=f.path.getPointAtLength(fraction*f.length);f.el.setAttribute('transform',`translate(${point.x} ${point.y})`);f.el.style.opacity=String(smooth(fraction*10)*smooth((1-fraction)*10));}
 for(const [j,b] of bubbles.entries()){const q=(local/9+Number(b.dataset.offset))%1;b.setAttribute('transform',`translate(${Math.sin(local*.3+j)*10} ${-q*300})`);b.style.opacity=String(Math.sin(q*Math.PI)*.9);}
 if(s.id==='hydrogen'){const q=.82+.18*smooth(local/8);art.querySelector('#h2-forming').setAttribute('transform',`translate(${1160*(1-q)} ${510*(1-q)}) scale(${q})`);art.querySelector('#h2-ring').style.opacity=String(.35+.25*Math.sin(local*.7));}
 if(s.id==='oxygen'){const d=.6+.4*smooth(local/8);art.querySelector('#oxygen-inhibited').style.opacity=String(d);}
 const showVideo=s.id==='opening';video.style.opacity=showVideo?'0.58':'0';document.querySelector('#video-wash').style.opacity=showVideo?'1':'0';
 if(renderMode&&showVideo&&video.readyState>=2){const target=local/s.duration*Math.max(1,video.duration-.05);if(Math.abs(video.currentTime-target)>.012)video.currentTime=target;}
 const cap=S.captions.find(c=>clock>=c.start&&clock<c.end);document.querySelector('#subtitle').textContent=cap?.text||'';
 document.querySelector('#readout').textContent=s.id==='circuit'||s.id==='vqe'?'技术方案计算模型 · 非实物产氢':'生物机制示意 · 非实验测量';
 if(conditions){
  const active=conditions.light&&conditions.enzyme&&!conditions.oxygen;
  for(const f of flows){if(!conditions.light)f.el.style.opacity='0';}
  art.querySelectorAll('.hydrogen-molecule').forEach(el=>el.style.opacity=active?'1':'.12');
  art.querySelectorAll('.active-site').forEach(el=>el.style.opacity=conditions.enzyme&&!conditions.oxygen?'1':'.2');
  document.querySelector('#readout').textContent=mechanismOf(conditions);
 }
 document.querySelector('#progress').style.width=`${clock/S.duration*100}%`;
 stage.dataset.scene=s.id;stage.dataset.time=clock.toFixed(3);return {scene:s.id,time:clock};
}
window.seekFilm=set;window.filmDuration=S.duration;window.setTheme=theme=>document.body.dataset.theme=theme;
window.setConditions=c=>{conditions=c;set(clock);return mechanismOf(c);};
async function seekReady(t){set(t);if(video.seeking)await new Promise(resolve=>{video.addEventListener('seeked',resolve,{once:true});setTimeout(resolve,1500)});}
window.seekFilmReady=seekReady;
function tick(now){const dt=last?Math.min((now-last)/1000,1/30):0;last=now;if(!paused&&visible&&!reduced.matches){set((clock+dt)%S.duration);requestAnimationFrame(tick);}}
function play(){paused=false;last=0;if(sceneIndex===0)video.play().catch(()=>{});requestAnimationFrame(tick);}
function pause(){paused=true;video.pause();}
window.playFilm=play;window.pauseFilm=pause;
addEventListener('keydown',e=>{if(e.code==='Space'){e.preventDefault();paused?play():pause();}else if(e.key==='ArrowRight'){pause();set(S.scenes[Math.min(S.scenes.length-1,sceneIndex+1)].start+2);}else if(e.key==='ArrowLeft'){pause();set(S.scenes[Math.max(0,sceneIndex-1)].start+2);}});
new IntersectionObserver(entries=>{visible=entries.at(-1).isIntersecting;if(visible&&!paused){last=0;requestAnimationFrame(tick);}else video.pause();}).observe(stage);
document.addEventListener('visibilitychange',()=>{if(document.hidden)video.pause();});
set(2);if(!renderMode&&!reduced.matches)play();window.filmReady=true;
})();
