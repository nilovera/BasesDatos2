const $ = id => document.getElementById(id);
const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const clock = value => `${String(Math.floor(value / 60)).padStart(2,'0')}:${String(Math.floor(value % 60)).padStart(2,'0')}`;
const state = {id:new URLSearchParams(location.search).get('simulacion'), snapshot:null, pitch:null, mode:'positions', subject:'all', selection:0, eventSignature:'', commentSignature:'', messages:new Map()};
let speedBusy = false;

async function api(path, options = {}) {
  const response = await fetch(path, {...options, cache:'no-store', signal:AbortSignal.timeout(12000), headers:{'Content-Type':'application/json', ...options.headers}});
  const data = await response.json();
  if (!response.ok) throw new Error(data.mensaje || data.message || data.error?.message || (typeof data.detail==='string'?data.detail:null) || `No se pudo actualizar (${response.status})`);
  return data;
}
function message(scope, text) {
  if (text) state.messages.set(scope,text); else state.messages.delete(scope);
  $('notice').textContent = [...state.messages.values()].join(' · ');
  $('notice').hidden = state.messages.size === 0;
}
function player(id) {return state.snapshot?.jugadores.find(row=>row.jugadorId===id)?.nombre || id || '';}
function team(id) {return state.snapshot?.equipos.find(row=>row.equipoId===id)?.nombre || id || '';}
function eventPresentation(event) {
  const d=event.datos || {};
  const minute=d.minuto ?? (event.tipo==='FIN_PARTIDO'?90:0);
  switch(event.tipo) {
    case 'INICIO_PARTIDO': return {minute:0, icon:'↗', title:'¡Se juega!', detail:'Comienza el partido.', kind:''};
    case 'GOL': return {minute,icon:'✦',title:`Gol de ${player(d.jugadorId)}`,detail:`${team(d.equipoId)}${d.asistenteJugadorId?` · Asistencia de ${player(d.asistenteJugadorId)}`:''}`,kind:'goal'};
    case 'GOL_ANULADO_VAR': return {minute,icon:'VAR',title:'Gol anulado por el VAR',detail:`${player(d.jugadorId)} · ${({OFFSIDE:'Fuera de juego',FALTA_PREVIA:'Falta previa',MANO:'Mano'})[d.motivo] || d.motivo || 'Revisión arbitral'}`,kind:'var'};
    case 'TARJETA': return {minute,icon:d.color==='ROJA'?'🟥':'🟨',title:`Tarjeta ${d.color==='ROJA'?'roja':'amarilla'}`,detail:`${player(d.jugadorId)} · ${team(d.equipoId)}`,kind:''};
    case 'SUSTITUCION': return {minute,icon:'⇄',title:'Cambio',detail:`Entra ${player(d.entraJugadorId)} · Sale ${player(d.saleJugadorId)}`,kind:''};
    case 'FIN_PARTIDO': return {minute:90,icon:'⚑',title:'Final del partido',detail:'Se cerraron los 90 minutos.',kind:''};
    case 'CORRECCION_EVENTO': return {minute,icon:'↺',title:'Corrección oficial',detail:d.motivo || 'Actualización del acta del partido',kind:'var'};
    default:return {minute,icon:'•',title:event.tipo,detail:'Evento confirmado',kind:''};
  }
}
function selectionOptions(snapshot) {
  const select=$('subject');
  const fingerprint=snapshot.equipos.map(x=>x.equipoId).join(',');
  if(select.dataset.teams===fingerprint) return;
  select.dataset.teams=fingerprint;
  select.innerHTML='<option value="all">Todos los jugadores</option>'+snapshot.equipos.map(t=>`<optgroup label="${escape(t.nombre)}"><option value="team:${escape(t.equipoId)}">${escape(t.nombre)} · Equipo completo</option>${snapshot.jugadores.filter(p=>p.equipoId===t.equipoId).map(p=>`<option value="player:${escape(p.jugadorId)}">${escape(p.nombre)} · ${escape(p.posicion.toLowerCase())}</option>`).join('')}</optgroup>`).join('');
  select.value=state.subject;
}
function renderSnapshot(snapshot) {
  state.snapshot=snapshot;
  const s=snapshot.simulacion;
  state.id=s.simulacionId;
  const [home,away]=snapshot.equipos;
  $('home-name').textContent=home.nombre; $('away-name').textContent=away.nombre;
  $('legend-home').textContent=home.nombre; $('legend-away').textContent=away.nombre;
  $('home-crest').textContent=(home.codigoExterno || home.nombre).slice(0,3).toUpperCase();
  $('away-crest').textContent=(away.codigoExterno || away.nombre).slice(0,3).toUpperCase();
  $('home-score').textContent=snapshot.marcador.local; $('away-score').textContent=snapshot.marcador.visitante;
  $('clock').textContent=clock(s.segundoPartido);
  $('period').textContent=s.estado==='FINALIZADA'?'FINAL DEL PARTIDO':s.estado==='PAUSADA'?'PARTIDO EN PAUSA':s.estado==='ERROR'?'TRANSMISIÓN INTERRUMPIDA':s.estado==='LISTA'?'POR COMENZAR':s.segundoPartido<2700?'PRIMER TIEMPO':'SEGUNDO TIEMPO';
  $('live-badge').textContent=({FINALIZADA:'FINALIZADO',PAUSADA:'EN PAUSA',LISTA:'POR COMENZAR',ERROR:'INTERRUMPIDO'})[s.estado] || 'EN VIVO';
  $('live-badge').classList.toggle('running',s.estado==='EJECUTANDO');
  $('match-id').textContent=s.partidoId;
  $('match-description').textContent=`${s.estado==='FINALIZADA'?'Resultado final':'Partido simulado'} · ${new Date(snapshot.actualizadoEn).toLocaleTimeString('es-AR',{hour:'2-digit',minute:'2-digit',second:'2-digit'})}`;
  $('seed').textContent=`Semilla ${s.semilla}`;
  $('progress').style.width=`${s.progresoPct}%`;
  const select=$('speed');
  if(![...select.options].some(o=>Number(o.value)===s.velocidad)) select.add(new Option(`${s.velocidad}×`,s.velocidad));
  if(!speedBusy) select.value=String(s.velocidad);
  select.disabled=speedBusy || ['FINALIZADA','ERROR'].includes(s.estado);
  selectionOptions(snapshot);
  const signature=snapshot.eventos.map(e=>e.eventoId).join(',');
  if(signature!==state.eventSignature) {
    state.eventSignature=signature;
    const container=$('events'), scroll=container.scrollTop;
    container.innerHTML=snapshot.eventos.length?[...snapshot.eventos].reverse().map(e=>{const p=eventPresentation(e);return `<article class="event-row ${p.kind}"><time class="event-minute">${escape(p.minute)}′</time><span class="event-icon" style="${p.icon==='VAR'?'font-size:8px':''}">${escape(p.icon)}</span><div><h3>${escape(p.title)}</h3><p>${escape(p.detail)}</p></div></article>`;}).join(''):'<p class="empty">El primer silbatazo está por llegar.</p>';
    container.scrollTop=scroll>30?scroll:0;
  }
  const goals=snapshot.eventos.filter(e=>e.tipo==='GOL');
  $('events-count').textContent=snapshot.eventos.length;
  $('event-counter').textContent=snapshot.eventos.length;
  $('goals-count').textContent=goals.length;
  message('simulation',s.error?`El partido se interrumpió: ${s.error}`:null);
  renderPitch();
}
function selected(row) {
  if(state.subject==='all') return true;
  const [kind,id]=state.subject.split(':');
  return kind==='team'?row.equipo_id===id:row.jugador_id===id;
}
function renderPitch() {
  if(!state.snapshot) return;
  const points=state.pitch?.posiciones || [];
  const home=state.snapshot.equipos[0].equipoId;
  const x=value=>40+Math.max(0,Math.min(100,Number(value)))*9.2;
  const y=value=>30+Math.max(0,Math.min(100,Number(value)))*5.4;
  $('player-layer').innerHTML=points.map(p=>`<g class="player ${state.subject.startsWith('player:')&&selected(p)?'selected':''}" transform="translate(${x(p.x)} ${y(p.y)})" opacity="${selected(p)?(state.mode==='heatmap'?'.55':'1'):'.2'}"><title>${escape(player(p.jugador_id))}</title><circle r="13" fill="${p.equipo_id===home?'#caf288':'#80c9eb'}"/><text y=".3">${Number(p.jugador_id.slice(-2))}</text></g>`).join('');
  const ball=state.pitch?.pelota;
  $('ball-layer').innerHTML=ball?`<g transform="translate(${x(ball.x)} ${y(ball.y)})"><title>Pelota · ${clock(ball.segundo_partido)}</title><circle r="7" fill="#fff" stroke="#183329" stroke-width="2"/><path d="M-2 -3L3 -1L2 3L-3 3L-4 -1Z" fill="#183329"/></g>`:'';
  $('goal-layer').innerHTML=state.snapshot.eventos.filter(e=>e.tipo==='GOL' && Number.isFinite(e.datos?.x) && Number.isFinite(e.datos?.y) && (state.subject==='all'||(state.subject.startsWith('team:')?e.datos.equipoId===state.subject.split(':')[1]:e.datos.jugadorId===state.subject.split(':')[1]))).map(e=>`<g transform="translate(${x(e.datos.x)} ${y(e.datos.y)})"><title>${escape(eventPresentation(e).title)} · ${escape(e.datos.minuto)}′</title><circle r="17" fill="#14291fdc" stroke="#d5ee8c"/><text y="6" text-anchor="middle" font-size="23" fill="#e6f6b1">✦</text></g>`).join('');
  const cells=state.pitch?.celdas || [], max=Math.max(1,...cells.map(c=>Number(c.muestras)));
  $('heat-layer').innerHTML=state.mode==='heatmap'?cells.map(c=>{const intensity=Number(c.muestras)/max;return `<rect x="${40+Number(c.cx)*46}" y="${30+Number(c.cy)*45}" width="46" height="45" fill="hsl(${Math.round(65-intensity*45)} 90% 62%)" opacity="${.1+intensity*.65}"/>`;}).join(''):'';
  $('heat-scale').hidden=state.mode!=='heatmap';
  const sample=points.length?Math.max(...points.map(p=>Number(p.segundo_partido))):null;
  $('sample-time').textContent=sample!==null?`Última muestra · ${clock(sample)}`:'Sin muestras todavía';
  $('pitch-summary').textContent=state.mode==='heatmap'?`${cells.reduce((n,c)=>n+Number(c.muestras),0).toLocaleString('es-AR')} posiciones acumuladas · ${$('subject').selectedOptions[0]?.textContent || ''}`:points.length?`${points.length} jugadores en cancha · Coordenadas registradas durante el partido`:'Las posiciones aparecerán cuando el partido genere telemetría.';
}
async function pollSnapshot() {
  if(document.hidden) {setTimeout(pollSnapshot,2000);return;}
  try {
    renderSnapshot(await api(`/api/v1/directo${state.id?'?simulacionId='+encodeURIComponent(state.id):''}`));
    message('snapshot',null);
  } catch(error) {
    message('snapshot',`No se pudo actualizar la transmisión. ${error.message}`);
    $('live-badge').textContent='SIN SEÑAL'; $('live-badge').classList.remove('running');
  }
  setTimeout(pollSnapshot,2000);
}
async function pollPitch() {
  const requestSelection=state.selection, id=state.id;
  if(id&&!document.hidden) {
    const params=new URLSearchParams({simulacionId:id});
    const [kind,subject]=state.subject.split(':');
    if(kind==='team') params.set('equipoId',subject);
    if(kind==='player') params.set('jugadorId',subject);
    try {
      const result=await api(`/api/v1/directo/cancha?${params}`);
      if(requestSelection===state.selection && id===state.id) {state.pitch=result;renderPitch();message('pitch',null);}
    }catch(error){message('pitch','La cancha no pudo actualizarse; se conserva la última muestra.');}
  }
  setTimeout(pollPitch,4000);
}
async function pollComments() {
  if(state.id&&!document.hidden) {
    try {
      const data=await api(`/api/v1/directo/comentarios?simulacionId=${encodeURIComponent(state.id)}`);
      const signature=data.items.map(c=>c.comentarioId).join(',');
      if(signature!==state.commentSignature){
        state.commentSignature=signature;
        const container=$('comments'),scroll=container.scrollTop;
        container.innerHTML=data.items.length?data.items.map(c=>`<article class="comment-row"><span class="avatar">${escape(c.usuarioId.slice(-2))}</span><div><div class="comment-meta"><strong>Hincha ${escape(c.usuarioId.slice(-4))}</strong><time>${new Date(c.creadoEn).toLocaleTimeString('es-AR',{hour:'2-digit',minute:'2-digit',timeZoneName:undefined})}</time></div><p>${escape(c.contenido)}</p></div></article>`).join(''):'<p class="empty">Los comentarios de la tribuna aparecerán acá.</p>';
        container.scrollTop=scroll>30?scroll:0;
      }
      message('comments',null);
    }catch(error){message('comments','Los comentarios están demorados. Reintentando…');}
  }
  setTimeout(pollComments,5000);
}
$('speed').addEventListener('change',async event=>{
  if(!state.id||speedBusy)return;
  speedBusy=true;event.target.disabled=true;
  try{
    const simulation=await api(`/api/v1/simulaciones/${encodeURIComponent(state.id)}/velocidad`,{method:'PATCH',body:JSON.stringify({velocidad:Number(event.target.value)})});
    state.snapshot.simulacion=simulation;message('speed',null);
  }catch(error){message('speed',`No se pudo cambiar la velocidad. ${error.message}`);}
  finally{speedBusy=false;renderSnapshot(state.snapshot);}
});
$('subject').addEventListener('change',event=>{state.subject=event.target.value;state.selection++;if(state.pitch)state.pitch.celdas=[];renderPitch();});
document.querySelectorAll('[data-mode]').forEach(button=>button.addEventListener('click',()=>{
  state.mode=button.dataset.mode;
  document.querySelectorAll('[data-mode]').forEach(b=>{b.classList.toggle('active',b===button);b.setAttribute('aria-pressed',String(b===button));});
  renderPitch();
}));
pollSnapshot();pollPitch();pollComments();
