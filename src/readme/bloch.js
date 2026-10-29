// Copyright 2026 QuantumBridge Contributors. Apache-2.0.
// Analytic illustration only: no SDK or hardware execution in the browser.
export function mountBloch(container, english) {
  const text=(zh,en)=>english?en:zh;
  container.innerHTML=`<div class="lab-stage"><canvas class="lab-canvas" role="img" aria-label="${text('RY 旋转的三维 Bloch 球；概率由下方文本提供','3D Bloch sphere of RY rotation; probabilities are provided as text below')}"></canvas><div class="lab-readout"><h3>RY(θ) |0⟩</h3><div class="lab-formula" data-state></div><div><div class="prob-row"><span>P(0)</span><output data-prob="0"></output></div><div class="prob-track"><div class="prob-fill" data-bar="0"></div></div></div><div><div class="prob-row"><span>P(1)</span><output data-prob="1"></output></div><div class="prob-track"><div class="prob-fill" data-bar="1"></div></div></div></div></div><div class="lab-controls"><button type="button" data-play aria-pressed="false">▷ ${text('播放','Play')}</button><label><span>${text('旋转角度','Angle')}</span><input type="range" min="0" max="360" step="1" value="90" aria-label="${text('RY 旋转角度（度）','RY rotation angle (degrees)')}"></label><output class="lab-angle">90°</output></div><label class="lab-view">${text('观察视角','View angle')}<input type="range" min="-60" max="60" value="25" aria-label="${text('Bloch 球观察视角','Bloch sphere view angle')}"></label><div class="lab-caption">${text('解析示意 · 单比特纯态 · Z 基测量 · 不调用真实设备','Analytic illustration · one pure qubit · Z measurement · no device calls')}</div>`;
  const canvas=container.querySelector('canvas'),ctx=canvas.getContext('2d');
  const angle=container.querySelector('.lab-controls input'),view=container.querySelector('.lab-view input'),play=container.querySelector('[data-play]');
  let theta=90,rotation=25,playing=false,raf=0,last=0;
  function draw(){
    const box=canvas.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,2);
    canvas.width=Math.max(1,Math.round(box.width*dpr));canvas.height=Math.max(1,Math.round(box.height*dpr));ctx.setTransform(dpr,0,0,dpr,0,0);
    const width=box.width,height=box.height,r=Math.min(width*.33,height*.38),cx=width/2,cy=height/2;
    const az=rotation*Math.PI/180,tilt=.26;
    const project=([x,y,z])=>{const a=x*Math.cos(az)+y*Math.sin(az),b=-x*Math.sin(az)+y*Math.cos(az);return [cx+r*a,cy-r*(z*Math.cos(tilt)-b*Math.sin(tilt))]};
    function path(points,color,lineWidth=1,dash=[]){ctx.beginPath();points.forEach((pt,i)=>{let [x,y]=project(pt);i?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.strokeStyle=color;ctx.lineWidth=lineWidth;ctx.setLineDash(dash);ctx.stroke();ctx.setLineDash([])}
    ctx.clearRect(0,0,width,height);
    ctx.beginPath();ctx.arc(cx,cy,r,0,2*Math.PI);ctx.fillStyle='#f1f7f3';ctx.fill();ctx.strokeStyle='#d8e7df';ctx.lineWidth=1;ctx.stroke();
    for(const plane of [0,1,2]){const points=[];for(let t=0;t<=128;t++){let u=t/128*Math.PI*2;points.push(plane===0?[Math.cos(u),Math.sin(u),0]:plane===1?[Math.cos(u),0,Math.sin(u)]:[0,Math.cos(u),Math.sin(u)])}path(points,'#c0d9ce',1,[3,3])}
    path([[0,0,-1.12],[0,0,1.12]],'#a4bfb2');path([[-1.1,0,0],[1.1,0,0]],'#b8cfc5');path([[0,-1.1,0],[0,1.1,0]],'#b8cfc5');
    ctx.font='11px ui-monospace,monospace';ctx.fillStyle='#79958a';for(const [label,pt] of [['|0⟩',[0,0,1.25]],['|1⟩',[0,0,-1.27]],['x',[1.22,0,0]],['y',[0,1.25,0]]]){const [x,y]=project(pt);ctx.fillText(label,x-9,y+4)}
    const t=theta*Math.PI/180,target=[Math.sin(t),0,Math.cos(t)];path([[0,0,0],target],'#237c60',3);
    const end=project(target),start=project([0,0,0]),a=Math.atan2(end[1]-start[1],end[0]-start[0]);ctx.beginPath();ctx.moveTo(...end);ctx.lineTo(end[0]-11*Math.cos(a-.4),end[1]-11*Math.sin(a-.4));ctx.lineTo(end[0]-11*Math.cos(a+.4),end[1]-11*Math.sin(a+.4));ctx.closePath();ctx.fillStyle='#237c60';ctx.fill();ctx.beginPath();ctx.arc(...start,3,0,2*Math.PI);ctx.fill();
  }
  function update(){const t=theta*Math.PI/180,p0=Math.cos(t/2)**2;angle.value=Math.round(theta);container.querySelector('.lab-angle').textContent=`${Math.round(theta)}°`;container.querySelector('[data-state]').textContent=`⟨Z⟩ = ${Math.cos(t).toFixed(3)}`;for(const [id,p] of [['0',p0],['1',1-p0]]){container.querySelector(`[data-prob="${id}"]`).textContent=`${(p*100).toFixed(1)}%`;container.querySelector(`[data-bar="${id}"]`).style.width=`${p*100}%`}draw()}
  function frame(now){if(!playing)return;if(last)theta=(theta+Math.min(now-last,80)*.025)%360;last=now;update();raf=requestAnimationFrame(frame)}
  function pause(){playing=false;last=0;cancelAnimationFrame(raf);play.textContent=`▷ ${text('播放','Play')}`;play.setAttribute('aria-pressed','false')}
  play.addEventListener('click',()=>{if(playing){pause();return}playing=true;play.textContent=`Ⅱ ${text('暂停','Pause')}`;play.setAttribute('aria-pressed','true');raf=requestAnimationFrame(frame)});
  angle.addEventListener('input',()=>{pause();theta=Number(angle.value);update()});view.addEventListener('input',()=>{rotation=Number(view.value);draw()});
  const resize=new ResizeObserver(draw);resize.observe(canvas);update();
  const visibility=()=>{if(document.hidden)pause()};document.addEventListener('visibilitychange',visibility);
  return ()=>{pause();resize.disconnect();document.removeEventListener('visibilitychange',visibility)};
}
