const byId = id => document.getElementById(id);
const html = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const agenda = {group:'proximos',page:0,revision:0,busy:false,running:0,next:null,teamsLoaded:false};
const selectedId = new URLSearchParams(location.search).get('simulacion');
function openMatch(id){location.assign(`/directo?simulacion=${encodeURIComponent(id)}`);}
function updateNextButton(){
  byId('next-match').disabled=agenda.busy||agenda.running>0||!agenda.next;
  byId('next-match').textContent=agenda.running>0?'Hay un partido en curso':'Jugar siguiente partido';
}
async function api(path, options={}){
  const response=await fetch(path,{...options,cache:'no-store',signal:AbortSignal.timeout(12000),headers:{'Content-Type':'application/json'}});
  const data=await response.json();
  if(!response.ok)throw new Error(data.mensaje || data.detail || `No se pudo completar (${response.status})`);
  return data;
}
async function refreshMatches(){
  const revision=++agenda.revision,group=agenda.group,page=agenda.page;
  try{
    const [data,upcoming]=await Promise.all([
      api(`/api/v1/directo/partidos?grupo=${group}&pagina=${page}`),
      group==='proximos'&&page===0?Promise.resolve(null):api('/api/v1/directo/partidos?grupo=proximos&pagina=0')
    ]);
    if(revision!==agenda.revision)return;
    agenda.running=data.enCurso;agenda.next=(upcoming||data).items[0]?.simulacionId||null;
    updateNextButton();
    byId('matches-status').textContent=agenda.running?'Hay un partido en curso. Podés verlo en la pestaña En curso; los próximos quedan esperando.':'';
    const labels={LISTA:'POR JUGAR',EJECUTANDO:'EN VIVO',PAUSADA:'EN PAUSA',ERROR:'INTERRUMPIDO',FINALIZADA:'FINALIZADO'};
    const empty={proximos:'Todavía no hay próximos cruces. Agregá un partido eligiendo los equipos abajo.','en-curso':'No hay partidos en curso.',finalizados:'Todavía no hay partidos finalizados.'};
    byId('matches-list').innerHTML=data.items.length?data.items.map(item=>{
      const [home,away]=item.equipos,canStart=['LISTA','PAUSADA','ERROR'].includes(item.estado);
      return `<article class="match-card ${item.simulacionId===selectedId?'current':''}"><div class="match-card-heading"><span>${html(item.partidoId)}</span><span>${labels[item.estado]||html(item.estado)}</span></div><h3>${html(home.nombre)} <span>vs.</span> ${html(away.nombre)}</h3><p>${item.estado==='LISTA'?'Listo para jugar':`${html(item.marcador.local)} : ${html(item.marcador.visitante)} · ${Math.floor(item.segundoPartido/60)} min`}${item.simulacionId===selectedId?' · Estás viendo este partido':''}</p><div class="match-card-actions">${canStart?`<button class="match-button primary" type="button" data-play="${html(item.simulacionId)}" data-state="${html(item.estado)}" ${agenda.running||agenda.busy?'disabled':''}>${item.estado==='LISTA'?'Jugar y ver':'Continuar y ver'}</button>`:''}<button class="match-button" type="button" data-open="${html(item.simulacionId)}">${item.estado==='LISTA'?'Ver previa':item.estado==='FINALIZADA'?'Ver resultado':'Ver partido'}</button></div></article>`;
    }).join(''):`<p class="empty">${empty[group]}</p>`;
    byId('matches-page').textContent=`Página ${page+1}`;
    byId('matches-prev').disabled=page===0;byId('matches-next').disabled=!data.hayMas;
  }catch(error){
    if(revision!==agenda.revision)return;
    agenda.next=null;updateNextButton();
    byId('matches-status').textContent=`No se pudo actualizar la lista. ${error.message}`;
  }
}
async function loadTeams(){
  if(agenda.teamsLoaded)return;
  try{
    const data=await api('/api/v1/directo/equipos');
    const options='<option value="">Elegí un equipo</option>'+data.items.map(team=>`<option value="${html(team.equipoId)}">${html(team.nombre)}</option>`).join('');
    byId('new-home').innerHTML=options;byId('new-away').innerHTML=options;
    byId('new-home').disabled=false;byId('new-away').disabled=false;byId('prepare-match').disabled=data.items.length<2;
    agenda.teamsLoaded=true;
  }catch(error){byId('prepare-status').textContent=`No se pudieron cargar los equipos. Usá Actualizar lista para reintentar. ${error.message}`;}
}
async function playMatch(id,status='LISTA'){
  if(agenda.busy)return;
  agenda.busy=true;updateNextButton();
  document.querySelectorAll('[data-play]').forEach(button=>button.disabled=true);
  try{
    await api(`/api/v1/simulaciones/${encodeURIComponent(id)}/${status==='LISTA'?'iniciar':'reanudar'}`,{method:'POST'});
    openMatch(id);
  }catch(error){
    // Un timeout puede ocurrir después de confirmar el inicio: no crear otro partido.
    try{const current=await api(`/api/v1/simulaciones/${encodeURIComponent(id)}`);if(current.estado==='EJECUTANDO'){openMatch(id);return;}}catch{}
    agenda.busy=false;await refreshMatches();
    byId('matches-status').textContent=error.message;
  }
}
byId('matches-list').addEventListener('click',event=>{
  const button=event.target.closest('button');if(!button||button.disabled)return;
  if(button.dataset.open)openMatch(button.dataset.open);
  if(button.dataset.play)playMatch(button.dataset.play,button.dataset.state);
});
byId('next-match').addEventListener('click',()=>{if(agenda.next)playMatch(agenda.next);});
function selectGroup(group){
  agenda.group=group;agenda.page=0;
  document.querySelectorAll('[data-group]').forEach(button=>{button.classList.toggle('active',button.dataset.group===group);button.setAttribute('aria-pressed',String(button.dataset.group===group));});
  refreshMatches();
}
document.querySelectorAll('[data-group]').forEach(button=>button.addEventListener('click',()=>selectGroup(button.dataset.group)));
byId('matches-prev').addEventListener('click',()=>{if(agenda.page>0){agenda.page--;refreshMatches();}});
byId('matches-next').addEventListener('click',()=>{agenda.page++;refreshMatches();});
byId('refresh-matches').addEventListener('click',()=>{refreshMatches();loadTeams();});
byId('prepare-match-form').addEventListener('submit',async event=>{
  event.preventDefault();
  const home=byId('new-home').value,away=byId('new-away').value;
  if(!home||!away||home===away){byId('prepare-status').textContent='Elegí dos equipos distintos.';return;}
  const button=byId('prepare-match');if(button.disabled)return;
  button.disabled=true;byId('prepare-status').textContent='Guardando el próximo cruce…';
  try{
    const created=await api('/api/v1/simulaciones',{method:'POST',body:JSON.stringify({localId:home,visitanteId:away,semilla:Date.now()%2147483647,velocidad:Number(byId('new-speed').value)})});
    byId('prepare-status').textContent=`${created.partidoId} agregado. Elegí Jugar y ver cuando quieras comenzar.`;
    selectGroup('proximos');
  }catch(error){byId('prepare-status').textContent=`No se pudo confirmar el cruce. Revisá Actualizar lista antes de reintentar. ${error.message}`;}
  finally{button.disabled=false;}
});
async function pollMatches(){if(!document.hidden)await refreshMatches();setTimeout(pollMatches,5000);}
loadTeams();pollMatches();
