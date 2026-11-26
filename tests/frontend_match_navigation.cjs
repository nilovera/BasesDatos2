// Verificación sin navegador ni dependencias externas: node tests/frontend_match_navigation.cjs
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const elements=new Map();
function element(id){
  if(!elements.has(id))elements.set(id,{id,innerHTML:'',textContent:'',value:'',disabled:false,dataset:{},handlers:{},classList:{toggle(){}},setAttribute(){},addEventListener(event,handler){this.handlers[event]=handler;}});
  return elements.get(id);
}
const groups=['proximos','en-curso','finalizados'].map(group=>Object.assign(element(group),{dataset:{group}}));
const prepared={simulacionId:'SIM-next',partidoId:'PAR-1008',estado:'LISTA',equipos:[{nombre:'Brasil'},{nombre:'Uruguay'}],marcador:{local:0,visitante:0},segundoPartido:0};
const final={...prepared,simulacionId:'SIM-final',estado:'FINALIZADA',equipos:[{nombre:'Argentina'},{nombre:'México'}],marcador:{local:2,visitante:1},segundoPartido:5400};
const upcoming=[prepared];let running=0,navigated=null,calls=[];
const context=vm.createContext({
  document:{getElementById:element,hidden:false,querySelectorAll:selector=>selector==='[data-group]'?groups:[]},
  location:{search:'?simulacion=SIM-final',assign:url=>{navigated=url;}},
  URLSearchParams,AbortSignal,Date,setTimeout(){},
  fetch:async(url,options={})=>{
    calls.push({url,options});let result;
    if(url.endsWith('/equipos'))result={items:[{equipoId:'EQ-03',nombre:'Brasil'},{equipoId:'EQ-04',nombre:'Uruguay'}]};
    else if(url==='/api/v1/simulaciones'){
      const payload=JSON.parse(options.body);assert.equal(payload.localId,'EQ-03');assert.equal(payload.visitanteId,'EQ-04');
      upcoming.push({...prepared,simulacionId:'SIM-added',partidoId:'PAR-1009'});result=upcoming.at(-1);
    }else if(url.endsWith('/iniciar')){running++;result={estado:'EJECUTANDO'};}
    else{const group=new URL(url,'http://test').searchParams.get('grupo');result={items:group==='finalizados'?[final]:group==='proximos'?upcoming:[],pagina:0,hayMas:false,enCurso:running};}
    return {ok:true,json:async()=>result};
  },
});
const flush=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
  vm.runInContext(fs.readFileSync(path.join(__dirname,'../frontend/assets/matches.js'),'utf8'),context);
  await flush();
  assert.match(element('matches-list').innerHTML,/Brasil/);
  assert.equal(element('next-match').disabled,false);
  await vm.runInContext("selectGroup('finalizados')",context);await flush();
  assert.match(element('matches-list').innerHTML,/Argentina/);
  assert.match(element('matches-list').innerHTML,/2 : 1/);
  assert.doesNotMatch(element('matches-list').innerHTML,/data-play/);
  element('new-home').value='EQ-03';element('new-away').value='EQ-03';
  await element('prepare-match-form').handlers.submit({preventDefault(){}});
  assert.match(element('prepare-status').textContent,/dos equipos distintos/);
  assert.equal(calls.filter(call=>call.url==='/api/v1/simulaciones').length,0);
  element('new-away').value='EQ-04';element('new-speed').value='25';
  await element('prepare-match-form').handlers.submit({preventDefault(){}});await flush();
  assert.match(element('matches-list').innerHTML,/PAR-1009/);
  assert.match(element('prepare-status').textContent,/agregado/);
  await vm.runInContext("playMatch('SIM-next')",context);
  assert.equal(navigated,'/directo?simulacion=SIM-next');
  await vm.runInContext('refreshMatches()',context);
  assert.equal(element('next-match').disabled,true);
  assert.match(element('matches-status').textContent,/partido en curso/);
  console.log('OK: catálogo, próximos, resultados, validación de rivales, guardado, inicio y navegación al partido correcto.');
})().catch(error=>{console.error(error);process.exitCode=1;});
