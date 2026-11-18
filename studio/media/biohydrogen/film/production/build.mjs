import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {blobOf,blobSvg,blobPath,BIO_CSS} from './anima-kit/blob.mjs';
import {moleculeOf,moleculeSvg,helixOf,helixSvg,ribbonOf,ribbonSvg} from './anima-kit/chem.mjs';
import {ISO_CSS,iso,fitProjection} from './anima-kit/iso-kit.mjs';
import {bioAudit} from './anima-kit/bio-audit.mjs';

const HERE=path.dirname(fileURLToPath(import.meta.url)),ROOT=path.dirname(HERE);
const story=JSON.parse(fs.readFileSync(path.join(ROOT,'timing.json')));
const P={origin:[0,0],scale:1/Math.sqrt(1.6),azimuth:90,elevation:90};
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
const ring=(cx,cy,rx,ry,seed=0)=>Array.from({length:40},(_,i)=>{const a=i/40*Math.PI*2,w=1+.035*Math.sin(a*3+seed)+.025*Math.cos(a*5+seed);return [cx+rx*Math.cos(a)*w,cy+ry*Math.sin(a)*w,0]});
const circle=(x,y,r,cl='',extra='')=>`<circle class="${cl}" cx="${x}" cy="${y}" r="${r}" ${extra}/>`;
const text=(x,y,s,cl='label',anchor='middle')=>`<text class="${cl}" x="${x}" y="${y}" text-anchor="${anchor}">${esc(s)}</text>`;
const protein=(x,y,rx,ry,seed=0,tone='hi')=>blobSvg(blobOf(ring(x,y,rx,ry,seed),P,{tone}));
const label=(x,y,title,sub='')=>text(x,y,title,'label')+(sub?text(x,y+32,sub,'micro'):'' );
const line=(x1,y1,x2,y2,cl='bond')=>`<path class="${cl}" d="M${x1},${y1}L${x2},${y2}"/>`;
const particle=(type,x,y,r=15)=>`<g class="particle ${type}">${circle(x,y,r,'particle-core')}${text(x,y+5,type==='electron'?'−':type==='proton'?'+':type==='oxygen'?'O₂':'','sign')}</g>`;
const mover=(id,route,type,count=8)=>`<path id="${id}" class="flow-path" d="${route}"/>`+Array.from({length:count},(_,i)=>`<g class="flow ${type}" data-route="${id}" data-offset="${i/count}">${circle(0,0,type==='photon'?9:12,'particle-core')}${text(0,5,type==='electron'?'−':type==='proton'?'+':type==='oxygen'?'O₂':'','sign')}</g>`).join('');
const box=(x,y,w,h,title,desc)=>`<rect class="panel" x="${x}" y="${y}" width="${w}" height="${h}" rx="20"/>${text(x+28,y+42,title,'label','start')}${text(x+28,y+80,desc,'micro','start')}`;
const note=(s,source='B1')=>text(112,887,s,'note','start')+text(1800,887,source,'note','end');
const counters=[];

function cell(){
  const outer=ring(1000,530,435,245,.6),inner=ring(1000,530,420,230,.6);
  counters.push({id:'cell-envelope',boundary:outer},{id:'chloroplast-envelope',boundary:ring(1020,535,355,179,.6)});
  let out=`<g id="cell-body">${protein(1000,530,435,245,.6,'mid')}<path class="cell-rim" d="${blobPath(inner,P)}"/>`;
  out+=`<path class="chloroplast" d="${blobPath(ring(1020,535,355,179,.6),P)}"/>`;
  for(let j=0;j<6;j++){
    let cy=410+j*45;
    out+=`<g class="thylakoid">`;
    for(let k=0;k<3;k++)out+=`<ellipse cx="${1080-j*7}" cy="${cy+k*7}" rx="${220-j*6}" ry="15" class="thylakoid-disc"/>`;
    out+='</g>';
  }
  out+=protein(840,536,87,95,1.5,'mid')+protein(840,536,33,35,1,'hi');
  out+=`<path class="stigma" d="${blobPath(ring(1305,475,31,52,2),P)}"/>`;
  for(let i=0;i<24;i++){let a=i*2.399,rr=95+35*(i%4);out+=circle(1000+Math.cos(a)*rr*1.6,530+Math.sin(a)*rr*.8,2.5,'ribosome');}
  out+=`<path class="flagellum" d="M653 426 C490 320 622 290 469 216"/><path class="flagellum" d="M672 404 C622 246 716 269 668 194"/></g>`;
  return out;
}

function membrane({labels=true,full=true}={}){
  let out=`<g class="membrane"><path class="bilayer-fill" d="M170 481 Q790 458 1415 481 L1415 538 Q790 515 170 538 Z"/>`;
  for(let i=0;i<75;i++){
    const x=170+i*16.8,y=481-22*Math.sin((x-170)/1245*Math.PI);
    out+=`<g class="lipid">${circle(x,y,5,'head')}${line(x-2,y+5,x-4,y+23,'tail')}${line(x+2,y+5,x+4,y+23,'tail')}${circle(x,y+57,5,'head')}${line(x-2,y+52,x-4,y+31,'tail')}${line(x+2,y+52,x+4,y+31,'tail')}</g>`;
  }
  out+='</g>';
  const ps=[{x:360,y:485,rx:90,ry:114,name:'PSII',cn:'光系统 II'},{x:730,y:490,rx:64,ry:93,name:'Cyt b₆f',cn:'细胞色素复合体'},{x:1115,y:485,rx:84,ry:115,name:'PSI',cn:'光系统 I'}];
  for(const [i,p] of ps.entries()){
    out+=`<g id="protein-${i}" class="membrane-protein">${protein(p.x,p.y,p.rx,p.ry,i+1)}${protein(p.x-14,p.y-38,p.rx*.38,p.ry*.32,i+2,'mid')}`;
    for(let k=0;k<7;k++)out+=circle(p.x+Math.cos(k*.9)*p.rx*.6,p.y+Math.sin(k*.9)*p.ry*.55,5,'cofactor');
    out+='</g>';
    if(labels)out+=label(p.x,665,p.cn,p.name);
  }
  out+=protein(555,504,24,15,2,'mid')+protein(935,584,24,19,3,'mid');
  if(labels)out+=label(555,737,'质体醌','PQ')+label(935,737,'质体蓝素','PC');
  out+=`<g id="ferredoxin">${protein(1330,353,35,31,4,'hi')}${circle(1330,353,8,'cofactor')}</g>`;
  if(labels)out+=label(1330,290,'铁氧还蛋白','Fd');
  out+=text(176,365,'基质侧','micro','start')+text(176,624,'类囊体腔','micro','start');
  if(full){
    out+=mover('electron-route','M360 480 Q460 504 555 504 Q640 504 730 490 Q820 584 935 584 Q1020 580 1115 485 Q1200 343 1330 353','electron',9);
    out+=mover('light-route','M210 205 Q320 260 360 410','photon',3)+mover('light-route2','M960 205 Q1075 260 1115 410','photon',3);
    out+=mover('proton-route','M730 405 Q815 470 730 584','proton',3);
  }
  return out;
}

function hydrogenase(cx=1030,cy=510,scale=1){
  let out=`<g id="enzyme-body" transform="translate(${cx} ${cy}) scale(${scale})">`;
  out+=protein(-70,0,200,175,2,'mid')+protein(100,20,140,149,4,'hi');
  for(let j=0;j<6;j++){
    const points=Array.from({length:24},(_,i)=>{const a=i/23*5.8;return [-178+j*59+14*Math.sin(a*2),-95+i*7,0]});
    out+=ribbonSvg(ribbonOf(points,P,{width:4,tone:'lo'}));
  }
  out+=`<g class="relay">`;
  // CrHydA1 carries its H-cluster, without the extra relay clusters found in
  // some bacterial hydrogenases. Cubane topology is schematic, not a PDB pose.
  const cube=[[-80,-45,0],[-40,-45,0],[-40,-5,0],[-80,-5,0],[-65,-60,0],[-25,-60,0],[-25,-20,0],[-65,-20,0]];
  out+=moleculeSvg(moleculeOf(cube.map((position,i)=>({element:i%2?'S':'Fe',position})),[[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]]),P,{atomRadius:8,bondWidth:2});
  out+=`<path class="ligand" d="M-25 -20 L0 -6 L27 10"/>`;
  out+='</g>';
  out+=`<g class="active-site">${line(45,10,90,10,'metal-bond')}${circle(45,10,19,'metal')}${circle(90,10,19,'metal')}${text(45,16,'Fe','atom-label')}${text(90,16,'Fe','atom-label')}`;
  out+=`<path class="ligand" d="M45 -8 L45 -34 L68 -44 L90 -34 L90 -8 M28 20 L4 40 M105 20 L128 40"/>`;
  out+=`${circle(45,-34,7,'sulfur')}${circle(90,-34,7,'sulfur')}</g></g>`;
  return out;
}

function molecule(x,y,kind='H₂',s=1){
 let a=kind==='O₂'?'O':'H';
 return `<g class="${a==='O'?'oxygen-molecule':'hydrogen-molecule'}" transform="translate(${x} ${y}) scale(${s})">${moleculeSvg(moleculeOf([{element:a,position:[-22,0,0]},{element:a,position:[22,0,0]}],[[0,1]]),P,{atomRadius:22,bondWidth:9})}${text(-22,7,a,'atom-label')}${text(22,7,a,'atom-label')}</g>`;
}

const art={};
art.opening=`<g class="hero-title-art">${Array.from({length:14},(_,i)=>molecule(200+i*115,380+Math.sin(i*1.8)*150,'H₂',.45+(i%3)*.2)).join('')}${molecule(1150,565,'H₂',3.8)}${text(430,560,'从光能到化学键','large','start')}${text(430,625,'一场发生在微生物内部的能量接力','label','start')}</g>`;
art.cell=cell()+label(831,706,'细胞核')+label(1170,803,'类囊体膜')+label(1338,400,'眼点')+text(180,450,'莱茵衣藻','large','start')+text(180,500,'Chlamydomonas reinhardtii','micro','start')+text(180,558,'以绿藻氢酶产氢通路为例','label','start')+note('跨尺度结构示意 · 不按实际比例','B1 · B2');
art.antenna=`<g id="antenna-field">${Array.from({length:12},(_,i)=>{let a=i*Math.PI*2/12,x=780+Math.cos(a)*280,y=520+Math.sin(a)*190;return protein(x,y,56,45,i,'mid')+Array.from({length:5},(_,j)=>circle(x+Math.cos(j*1.26)*28,y+Math.sin(j*1.26)*23,6,'pigment')).join('')}).join('')}${protein(780,520,92,100,4)}${circle(780,520,29,'reaction-centre')}</g>`+Array.from({length:6},(_,i)=>{let a=i*Math.PI/3;return mover('excitation-'+i,`M${780+Math.cos(a)*280} ${520+Math.sin(a)*190} Q780 400 780 520`,'photon',2)}).join('')+label(780,795,'捕光复合体 → 反应中心')+box(1270,360,500,150,'光子的能量被吸收','色素吸收 · 激发能传递')+box(1270,545,500,150,'反应中心形成电荷分离','电子进入后续传递链')+note('光脉冲为能量传递符号 · 非光子的实际轨迹','B4');
art.water=protein(965,485,130,152,1)+label(965,704,'光系统 II','水氧化提供电子')+moleculeSvg(moleculeOf([{element:'O',position:[450,430,0],radius:43},{element:'H',position:[390,485,0],radius:26},{element:'H',position:[510,485,0],radius:26}],[[0,1],[0,2]]),P,{bondWidth:12})+text(450,575,'H₂O','large')+mover('water-electrons','M520 445 Q700 370 965 485 Q1110 380 1370 370','electron',4)+mover('water-protons','M915 570 Q930 720 1310 685','proton',4)+molecule(1450,540,'O₂',1.6)+text(1450,630,'释放氧气','label')+text(960,809,'2 H₂O → O₂ + 4 H⁺ + 4 e⁻','equation')+note('净氧化半反应计量 · 蛋白质结构及原子尺寸为示意','B4');
art.chain=membrane()+box(1480,360,340,135,'电子接力','位置与载体均为示意')+box(1480,540,340,135,'质子动力势','膜内外建立电化学差异')+note('展示线性光合电子传递的代表路径 · 未画出全部分支','B4');
art.psi=`<g transform="translate(-160 40)">${membrane({labels:false,full:false})}</g>`+mover('psi-light','M680 200 Q850 285 955 445','photon',4)+mover('psi-electrons','M955 445 Q1060 265 1170 313 Q1350 295 1475 450','electron',7)+hydrogenase(1570,500,.72)+label(955,730,'光系统 I','再次吸收光能')+label(1210,260,'还原型 Fd','传递还原力')+label(1580,730,'氢酶通路','适当低氧条件下')+note('PSI → Fd → HydA 为本片采用的绿藻通路 · 不代表全部微生物','B1');
art.enzyme=hydrogenase(960,505,1.45)+mover('enzyme-electrons','M240 430 Q500 410 850 465 Q970 500 1050 520','electron',6)+mover('enzyme-protons','M1570 330 Q1370 370 1090 520','proton',5)+label(430,330,'来自 Fd 的电子')+label(1480,720,'蛋白质内的质子传递')+label(940,815,'H-cluster：[4Fe–4S] 与双铁位点相连')+note('CrHydA1 辅因子拓扑与蛋白折叠均为示意 · 非结构坐标或反应轨迹','B1 · B5');
art.hydrogen=`<g class="reaction-stage">${hydrogenase(520,510,.85)}${mover('reaction-electrons','M260 340 Q650 300 955 500','electron',2)}${mover('reaction-protons','M700 260 Q930 260 1000 500','proton',2)}<g id="h2-forming">${molecule(1160,510,'H₂',3.2)}</g><g id="h2-ring"><circle class="reaction-ring" cx="1160" cy="510" r="170"/></g>${label(1520,510,'氢氢键形成','酶催化的净结果')}${text(985,805,'2 H⁺ + 2 e⁻ → H₂','equation')}</g>`+note('粒子汇聚表示净计量 · 不将复杂催化过程简化为直接碰撞','B1');
art.oxygen=`<g id="oxygen-safe">${hydrogenase(580,510,1.0)}${molecule(610,295,'H₂',1)}${text(580,780,'低氧 · 有利于敏感氢酶工作','label')}</g><g id="oxygen-inhibited">${hydrogenase(1400,510,1.0)}${molecule(1385,288,'O₂',1.2)}${text(1400,780,'氧气积累 · 可能抑制氢酶','label')}<path class="inhibition" d="M1320 410 L1490 610 M1490 410 L1320 610"/></g>${text(960,310,'条件，决定通路能否持续','large')}`+note('对比为机制示意 · 氧敏感性随酶种类而异','B2 · B3');
art.reactor=`<g id="reactor-body"><path class="vessel" d="M600 310 Q960 205 1320 310 L1320 710 Q960 850 600 710 Z"/><ellipse class="liquid" cx="960" cy="660" rx="358" ry="85"/><path class="liquid" d="M602 450 Q960 552 1318 450 L1318 660 Q960 760 602 660 Z"/><ellipse class="liquid-top" cx="960" cy="450" rx="358" ry="85"/>${Array.from({length:22},(_,i)=>{let x=680+(i*97)%560,y=525+(i*59)%155;return protein(x,y,17,12,i,'mid')}).join('')}<ellipse class="vessel-rim" cx="960" cy="310" rx="360" ry="106"/></g>`+Array.from({length:13},(_,i)=>`<g class="bubble" data-offset="${i/13}">${circle(720+i*39,600,14+i%4*3,'bubble-core')}</g>`).join('')+mover('reactor-light','M260 230 Q415 350 740 600','photon',5)+label(370,720,'光照培养')+label(1530,540,'H₂ 进入气相','概念性收集画面')+note('反应器为教学概念设计 · 未表示氢氧混合收集或参考技术文献实测装置','P · B2');

// Separate experimental systems; these are mechanism illustrations, not a
// composite device or a quantitative prediction of their performance.
const bacteria=(x,y,angle=0)=>`<g transform="translate(${x} ${y}) rotate(${angle})"><rect class="bacterium" x="-23" y="-9" width="46" height="18" rx="9"/>${line(-12,0,12,0,'bacterial-nucleoid')}</g>`;
art.wholecell=protein(750,515,360,190,1,'mid')+Array.from({length:5},(_,i)=>`<ellipse class="thylakoid-disc" cx="750" cy="${440+i*35}" rx="275" ry="22"/>`).join('')+protein(1300,455,115,95,2)+text(1300,463,'[NiFe]','gate-label')+molecule(1515,430,'H₂',1.2)+mover('wc-electron','M470 465 Q800 365 1035 465 Q1160 440 1300 455 Q1420 430 1515 430','electron',7)+mover('wc-branch','M1000 460 Q1125 620 1410 650','electron',3)+mover('wc-light','M300 260 Q510 340 580 435','photon',4)+label(750,760,'蓝藻整细胞','光系统与代谢共同分配还原力')+label(1510,690,'竞争性电子去路')+label(1310,590,'细胞内氢酶 · 局部放大')+label(1370,300,'目标：供电子与氧管理协同')+note('2026 年整细胞研究 · 水氧化供电子与耗氧条件须共同验证','R1');
let gel=`<g id="gel-fibre"><path class="gel-shell" d="M350 365 Q600 270 960 315 L1060 755 Q680 865 350 720 Z"/><path class="gel-core" d="M380 425 Q650 355 950 400 L1000 680 Q650 760 380 660 Z"/><ellipse class="gel-shell" cx="1050" cy="535" rx="170" ry="225"/><ellipse class="gel-core" cx="1050" cy="535" rx="108" ry="150"/>`;
for(let i=0;i<15;i++){const a=i*2.4,r=35+(i%3)*24;gel+=protein(1050+Math.cos(a)*r,535+Math.sin(a)*r*1.5,16,19,i,'hi');}
for(let i=0;i<22;i++){const a=i/22*Math.PI*2;gel+=bacteria(1050+Math.cos(a)*138,535+Math.sin(a)*190,a*180/Math.PI+90);}
for(let i=0;i<10;i++)gel+=bacteria(410+i*48,355+Math.sin(i)*25,-10);gel+='</g>';
art.hydrogel=gel+mover('gel-oxygen','M1260 270 Q1320 400 1185 535','oxygen',4)+mover('gel-light','M300 220 Q640 300 970 470','photon',5)+molecule(1430,405,'H₂',1.1)+label(1480,520,'外壳：细菌耗氧','为内核建立局部低氧微环境')+label(1480,675,'内核：微藻产氢','核壳纤维 · 空间分隔 · 传光传质')+note('2026 年同轴 3D 生物打印研究 · 粒子和纤维尺寸不表示实测值','R2');
let sheets='';for(let i=0;i<5;i++)sheets+=`<path class="nano-sheet" d="M${270+i*35} ${420+i*30} l225 -80 l90 65 l-225 80 Z"/>`;
art.biohybrid=sheets+protein(1180,535,350,124,2,'mid')+`<path class="cell-rim" d="${blobPath(ring(1180,535,332,109,2),P)}"/>`+protein(1380,530,65,60,3)+molecule(1550,510,'H₂',1)+mover('bh-light','M220 235 Q360 290 470 410','photon',5)+mover('bh-electron','M480 470 Q720 395 880 500 Q1080 550 1380 530 Q1460 500 1550 510','electron',8)+label(500,710,'ZnIn₂S₄ 捕光材料','光生电子送入细胞')+label(1260,340,'Shewanella oneidensis','材料—细胞界面与代谢耦合')+label(1390,735,'有机底物参与','不能等同于全水分解')+note('2026 年半导体–微生物杂化研究 · 正电荷及底物的完整收支须计入','R3');
art.bioelectrode=`<path class="electrolyte" d="M210 400 L820 400 L820 730 Q515 790 210 730Z"/><path class="electrolyte" d="M1100 400 L1710 400 L1710 730 Q1405 790 1100 730Z"/><path class="chamber" d="M210 335 L210 730 Q515 790 820 730 L820 335 M1100 335 L1100 730 Q1405 790 1710 730 L1710 335"/><rect class="electrode" x="560" y="390" width="75" height="300" rx="9"/><rect class="electrode cathode" x="1330" y="390" width="55" height="300" rx="9"/>${Array.from({length:8},(_,i)=>`<g transform="translate(535 ${420+i*31}) rotate(-12)"><ellipse class="diatom" cx="0" cy="0" rx="47" ry="17"/>${line(-32,0,32,0,'bacterial-nucleoid')}</g>`).join('')}<path class="external-circuit" d="M597 390 L597 300 L1357 300 L1357 390"/>${mover('be-electron','M597 650 L597 300 L1357 300 L1357 650','electron',8)}${mover('be-light','M240 220 Q345 315 515 495','photon',5)}${molecule(1500,410,'H₂',1.1)}${molecule(1550,560,'H₂',.8)}${text(980,280,'外电路 · 电化学条件','micro')}${label(520,818,'活硅藻 / 导电支架光阳极')}${label(1430,818,'铂基阴极 · 析氢')}<path class="ion-bridge" d="M820 639 Q960 689 1100 639 L1100 661 Q960 711 820 661 Z"/>${mover('be-ion','M820 650 Q960 700 1100 650','proton',3)}${text(960,560,'离子通道（示意）','micro')}`+note('2026 年生物光电化学研究的功能拓扑 · 不声称无偏压、自供能或既定效率','R4');

function circuit(){
 let o='';const ys=[380,520,660],names=['q₀ / 光子编码','q₁ / 电子编码','q₂ / 质子编码'];
 for(let i=0;i<3;i++){
  o+=text(150,ys[i]+10,names[i],'label','start')+line(465,ys[i],1740,ys[i],'circuit-wire');
  o+=`<g class="gate" data-gate="0"><rect x="490" y="${ys[i]-36}" width="72" height="72" rx="8"/>${text(526,ys[i]+12,'H','gate-label')}</g>`;
 }
 for(const [x,title] of [[660,'R'],[830,'H']])o+=`<g class="gate"><rect x="${x}" y="344" width="72" height="72" rx="8"/>${text(x+36,392,title,'gate-label')}</g>`;
 for(const [x,from,to] of [[1030,380,520],[1200,520,660]])o+=line(x,from,x,to,'circuit-wire')+circle(x,from,13,'control')+circle(x,to,24,'target')+line(x-23,to,x+23,to,'circuit-wire')+line(x,to-23,x,to+23,'circuit-wire');
 o+=`<rect class="vqe-gate" x="1370" y="465" width="220" height="250" rx="18"/>${text(1480,565,'VQE','large')}${text(1480,615,'计算子线路','micro')}`;
 for(let i=0;i<3;i++)o+=`<g class="measure"><rect x="1650" y="${ys[i]-35}" width="75" height="70" rx="8"/><path d="M1665 ${ys[i]+10} Q1687 ${ys[i]-25} 1710 ${ys[i]+10} M1687 ${ys[i]+8} L1700 ${ys[i]-17}"/></g>`;
 o+=mover('qubit-progress','M460 380 L1730 380','photon',1);
 return o+text(960,814,'初始化 → 门操作 → 关联 → 变分计算 → 测量','label')+note('按参考技术文献权利要求整理的概念线路 · R 表示参考技术文献中的旋转操作','P · 图1—2');
}
art.circuit=circuit();
art.vqe=`<g id="vqe-loop">${box(215,345,510,170,'量子侧 · 制备与测量','参数态 |ψ(θ)⟩ → 能量期望值')}${box(1130,345,560,170,'经典侧 · 更新参数','优化 θ，返回下一轮线路')}${mover('vqe-return','M720 410 Q930 240 1130 410','photon',3)}${mover('vqe-return2','M1140 500 Q930 700 715 500','electron',3)}${text(960,734,'E(θ) = ⟨ψ(θ)| H |ψ(θ)⟩','equation')}${text(960,807,'P(111) 是模型测量概率，不是实物产氢率','label')}</g>`+note('本片未运行量子化学计算 · 不展示虚构能量、收敛曲线或产率','P');
art.ending=membrane({labels:false})+hydrogenase(1630,470,.58)+mover('final-electron','M1325 350 Q1460 350 1610 470','electron',3)+molecule(1650,700,'H₂',1.7)+text(960,790,'光能 → 电子传递 → 氢酶催化 → H₂','large')+note('生物通路示意 × 参考技术文献模拟概念 · 不构成实验结果或性能承诺','P · B1 · B2');

const parts=['cell-envelope','chloroplast-envelope','nucleus','thylakoid','PSII','PQ','Cyt-b6f','PC','PSI','Fd','HydA','H-cluster'];
// Schematic geometry: no biological scale is asserted. A nominal coordinate scale
// is used only by the topology checker; there are deliberately no measurements.
const audit=bioAudit({membranes:counters,parts,labels:parts.map(x=>({text:x,target:x})),unitsPerMicron:1,measurements:[]});
if(!audit.ok)throw new Error(audit.errors.join('\n'));
fs.writeFileSync(path.join(HERE,'bio-audit.json'),JSON.stringify({...audit,scope:'Schematic topology and declared label targets only; no physical dimensions validated.',parts},null,2));
console.log('bio audit passed');

const defs=`<defs><radialGradient id="ambient"><stop stop-color="var(--ambient)"/><stop offset="1" stop-color="var(--bg)"/></radialGradient><radialGradient id="orb"><stop stop-color="var(--orb-core)"/><stop offset=".6" stop-color="var(--cyan)"/><stop offset="1" stop-color="var(--orb-rim)"/></radialGradient><radialGradient id="gold"><stop stop-color="#fff6c9"/><stop offset="1" stop-color="var(--gold)" stop-opacity=".2"/></radialGradient><filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="5"/></filter></defs>`;
const svgFor=id=>`<svg class="iso-art" viewBox="0 0 1920 1080" role="img" aria-label="${esc(story.scenes.find(s=>s.id===id).title)}">${defs}<g class="world">${art[id]}</g></svg>`;
fs.writeFileSync(path.join(ROOT,'scenes.json'),JSON.stringify(Object.fromEntries(Object.keys(art).map(k=>[k,svgFor(k)]))));

const css=fs.readFileSync(path.join(HERE,'film.css'),'utf8');
const js=fs.readFileSync(path.join(HERE,'film.js'),'utf8');
const film=`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>${story.title} · Anima</title><style>${ISO_CSS}\n${BIO_CSS}\n${css}</style></head><body class="iso" data-theme="dark"><a id="standalone-home" href="../../../framework.html">← 返回主页 / Home</a><main id="stage" class="iso-plate" tabindex="0" aria-label="生物制氢动画，空格暂停，左右键切换章节"><div id="ambient"></div><video id="model-video" src="assets/microbial-world.mp4" muted playsinline preload="auto"></video><div id="video-wash"></div><header><span id="eyebrow"></span><h1 id="title"></h1></header><span id="figure-id"></span><span id="scale-note">结构及运动为教学示意 · 不按比例</span><div id="art"></div><div id="subtitle"></div><footer><span>ANIMA / QUANTUMBRIDGE</span><span id="readout" data-readout></span><span>生物光制氢 · 机制可视化</span></footer><div id="progress"></div></main><script>window.STORY=${JSON.stringify(story)};window.ART=${JSON.stringify(Object.fromEntries(Object.keys(art).map(k=>[k,svgFor(k)])))};</script><script>${js}</script></body></html>`;
fs.writeFileSync(path.join(ROOT,'film.html'),film);
fs.writeFileSync(path.join(ROOT,'film-light.html'),film.replace('data-theme="dark"','data-theme="light"'));
console.log(`Built ${Object.keys(art).length} Anima scenes · ${story.duration}s`);
