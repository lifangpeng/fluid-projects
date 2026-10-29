const select = document.querySelector('#scenario'), svg = document.querySelector('#graph'), details = document.querySelector('#details');
const controlBox = document.createElement('div');
select.parentElement.after(controlBox);
let live = false, controls = [], requestId = 0;
async function getJSON(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`请求失败 (${response.status})`);
  return response.json();
}
function element(tag, attrs, text) {
  const el = document.createElementNS('http://www.w3.org/2000/svg', tag);
  Object.entries(attrs).forEach(([k,v]) => el.setAttribute(k,v));
  if (text !== undefined) el.textContent = text;
  svg.append(el); return el;
}
async function render(overrides = {}) {
  const id = ++requestId;
  try {
    const sid = encodeURIComponent(select.value);
    const data = await getJSON(live ? `/api/scenarios/${sid}?${new URLSearchParams(overrides)}` : `data/${sid}.json`);
    if (id !== requestId) return;
    controlBox.querySelectorAll('select').forEach(el => el.value = data.state[el.name]);
    const sol = data.solution, nodes = Object.keys(sol.nodes), positions = {};
    nodes.forEach((name,i) => { const a=2*Math.PI*i/nodes.length; positions[name]=[400+260*Math.cos(a),210+145*Math.sin(a)]; });
    svg.replaceChildren(); details.replaceChildren();
    for (const [name,e] of Object.entries(sol.edges)) {
      const a=positions[e.from], b=positions[e.to];
      element('line', {x1:a[0],y1:a[1],x2:b[0],y2:b[1],class:e.enabled?'edge':'edge off'});
      element('text', {x:(a[0]+b[0])/2,y:(a[1]+b[1])/2}, name);
      const row=document.createElement('p');
      row.textContent=`${name}: Q=${e.flow_m3s.toExponential(3)} m³/s，v=${e.velocity_mps == null?'未提供管径':e.velocity_mps.toFixed(3)+' m/s'}（正方向 ${e.from} → ${e.to}）`;
      details.append(row);
    }
    for (const [name,p] of Object.entries(sol.nodes)) {
      const [x,y]=positions[name];
      element('circle',{cx:x,cy:y,r:30,class:'node'});
      element('text',{x:x-25,y:y},name);
      element('text',{x:x-35,y:y+48},`${p.toFixed(1)} Pa`);
    }
    const summary=document.createElement('p');
    summary.textContent=`${live?'实时计算':'静态结果'} · 功能通过率 ${(data.reliability*100).toFixed(1)}% · 收敛 ${sol.converged} · 质量残差 ${sol.residual}`;
    details.prepend(summary);
    for(const f of data.functions) {
      const row=document.createElement('p'); row.textContent=`${f.function}: ${f.functional?'正常':f.reason}；拓扑路径 ${(f.topology_path||[]).join(' → ') || '无'}`; details.append(row);
    }
    for(const warning of sol.warnings) {const row=document.createElement('p');row.textContent=warning;details.append(row);}
  } catch(error) {if(id===requestId) details.textContent=error.message;}
}
async function boot() {
  try {
    let index;
    try {index=await getJSON('/api/network');live=true;controls=index.controls;} catch {index=await getJSON('data/index.json');}
    index.scenarios.forEach(s=>select.add(new Option(s,s)));
    controls.forEach(c=>{const label=document.createElement('label');label.textContent=c.id+' ';const input=document.createElement('select');input.name=c.id;c.states.forEach(s=>input.add(new Option(s,s)));input.onchange=()=>render(Object.fromEntries([...controlBox.querySelectorAll('select')].map(el=>[el.name,el.value])));label.append(input);controlBox.append(label);});
    select.onchange=()=>render(); if(index.scenarios.length) await render();
  } catch(error) {details.textContent=error.message;}
}
boot();
