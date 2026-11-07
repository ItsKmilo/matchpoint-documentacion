/* Tablero de los sprints 1 y 2 de MatchPoint.
   - Cualquiera lo ve en vivo (lee los issues públicos del repositorio).
   - El equipo, después de «Activar edición», arrastra las tarjetas entre columnas y registra
     seguimiento y sesiones desde esta misma página. Todo se guarda en GitHub con autor y hora.
   Sin librerías externas. */
(()=>{
  'use strict';
  const D=window.MATCHPOINT_TABLERO; if(!D)return;
  const REPO='ItsKmilo/matchpoint-documentacion', API=`https://api.github.com/repos/${REPO}`, GH=`https://github.com/${REPO}`;
  const ISSUE_SEG=21, ISSUE_SES=22, KEY='mp-tablero-token';
  const ESTADOS=['Por hacer','En progreso','En revisión','Terminado'];
  const $=s=>document.querySelector(s);
  const E=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const f=iso=>{const [y,m,d]=iso.slice(0,10).split('-');return `${d}/${m}/${y}`;};
  const fh=iso=>new Date(iso).toLocaleString('es-CO',{day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit',timeZone:'America/Bogota'});
  const store={get(){try{return localStorage.getItem(KEY)||'';}catch(e){return '';}},set(v){try{v?localStorage.setItem(KEY,v):localStorage.removeItem(KEY);}catch(e){}}};
  const menu=document.querySelector('.menu-toggle'),nav=document.querySelector('#site-nav');
  menu?.addEventListener('click',()=>{const o=nav.classList.toggle('open');menu.setAttribute('aria-expanded',String(o));});

  const S=D.sprint;
  const cab=k=>{const X=(D.sprints||{})[k]||S;$('#tb-objetivo').textContent=`${X.nombre}. Inicio: ${f(X.inicio)} · Entrega: ${f(X.entrega_avance)}. ${X.objetivo}`;};
  $('#tb-roles').innerHTML=Object.entries(S.roles).map(([r,n])=>`<div><small>${E(r.toUpperCase())}</small><strong>${E(n)}</strong></div>`).join('');

  const state={sprint:'Sprint 2',H:D.historias.map(h=>({...h})),seg:[],ses:[],live:false,token:store.get(),user:null,msg:''};
  const base=[...D.entradas].reverse().map(e=>({t:e.fecha,cuando:f(e.fecha),tipo:e.tipo,autor:'',texto:e.texto}));

  /* ---------------- GitHub ---------------- */
  function gh(path,opts={}){
    const h={Accept:'application/vnd.github+json'};
    if(state.token)h.Authorization=`Bearer ${state.token}`;
    if(opts.body)h['Content-Type']='application/json';
    return fetch(path.startsWith('http')?path:API+path,{...opts,headers:h,cache:'no-store'}).then(async r=>{
      if(!r.ok){const t=await r.json().catch(()=>({}));const err=new Error(t.message||r.status);err.status=r.status;throw err;}
      return r.status===204?null:r.json();});
  }
  const comment=(n,body)=>gh(`/issues/${n}/comments`,{method:'POST',body:JSON.stringify({body})});

  function load(){
    return Promise.all([gh('/issues?state=all&labels=Historia%20de%20usuario&per_page=100'),gh(`/issues/${ISSUE_SEG}/comments?per_page=100`),gh(`/issues/${ISSUE_SES}/comments?per_page=100`)])
    .then(([issues,seg,ses])=>{
      const byId=Object.fromEntries(D.historias.map(h=>[h.id,h]));
      const H=issues.map(i=>{const id=(i.title.match(/HU\d{3}/)||[''])[0],b=byId[id]||{},labels=i.labels.map(l=>l.name);
        return {...b,id,name:b.name||i.title,number:i.number,labels,url:i.html_url,sprint:labels.includes('Sprint 2')?'Sprint 2':(labels.includes('Sprint 1')?'Sprint 1':b.sprint),
          sp:+((i.title.match(/\((\d+) SP\)/)||[0,b.sp||0])[1]),
          priority:['Must','Should','Could'].find(p=>labels.includes(p))||b.priority,
          estado:i.state==='closed'?'Terminado':(ESTADOS.find(e=>labels.includes(e))||'Por hacer')};})
        .filter(h=>h.id).sort((a,b)=>a.id.localeCompare(b.id));
      if(H.length)state.H=H;
      state.seg=seg.map(c=>{const mov=/^Movimiento:/i.test(c.body),rol=(c.body.match(/^Rol:\s*(.+)$/mi)||[])[1];
        return {t:c.created_at,cuando:fh(c.created_at),tipo:mov?'Movimiento de tarea':(rol?`Seguimiento · ${rol.trim()}`:'Seguimiento'),autor:c.user.login,
          texto:c.body.replace(/^Rol:.*$/mi,'').replace(/^Movimiento:\s*/i,'').trim()};});
      state.ses=ses.map(c=>({t:c.created_at,cuando:fh(c.created_at),autor:c.user.login,texto:c.body}));
      state.live=true;
    }).catch(()=>{state.live=false;});
  }

  /* ---------------- Render ---------------- */
  function render(){
    cab(state.sprint);
    const H=state.H.filter(h=>h.sprint===state.sprint),total=H.reduce((a,h)=>a+h.sp,0)||1,sum=st=>H.filter(h=>st.includes(h.estado)).reduce((a,h)=>a+h.sp,0);
    const done=sum(['Terminado']),impl=sum(['En revisión','Terminado']),edit=!!state.user;
    $('#tb-kpis').innerHTML=[['HISTORIAS',H.length],['PUNTOS (SP)',total],['SP IMPLEMENTADOS',impl],['SP TERMINADOS',done],['PRUEBAS OK',H.reduce((a,h)=>a+h.pruebas,0)]].map(([a,b])=>`<div><span>${a}</span><strong>${b}</strong></div>`).join('');
    $('#tb-bar-done').style.width=(done/total*100)+'%';$('#tb-bar-impl').style.width=((impl-done)/total*100)+'%';
    $('#tb-source').innerHTML=state.live?`● En vivo · actualizado ${fh(new Date().toISOString())}`:'Mostrando la última copia guardada. Recarga en unos minutos para ver los cambios más recientes.';
    $('#tb-edit').innerHTML=edit
      ?`<div class="tb-editbar on"><span>✎ Edición activa como <b>@${E(state.user)}</b>. Arrastra las tarjetas entre columnas; los cambios se guardan solos.</span><button type="button" class="btn-link" id="tb-logout">Salir de edición</button></div>`
      :`<div class="tb-editbar"><span><b>¿Eres del equipo?</b> Activa la edición para mover tarjetas y registrar seguimiento y sesiones aquí mismo.</span><button type="button" class="btn btn-dark" id="tb-login-open">Activar edición</button></div>
        <form class="tb-login" id="tb-login" hidden><label>Token de GitHub (solo la primera vez en este navegador)<input name="token" type="password" autocomplete="off" required placeholder="ghp_…"></label><button class="btn btn-primary" type="submit">Entrar</button>
        <details><summary>¿Cómo obtengo el token? (1 minuto)</summary><ol><li>Entra a <a href="https://github.com/settings/tokens/new?scopes=public_repo&description=Tablero%20MatchPoint" target="_blank" rel="noopener">GitHub → Generate new token (classic)</a>.</li><li>Deja marcado solo <code>public_repo</code>, elige vencimiento de 30 días y pulsa <b>Generate token</b>.</li><li>Copia el token y pégalo aquí. Se guarda solo en este navegador.</li><li>Tu cuenta debe ser colaboradora del repositorio para mover tarjetas.</li></ol></details></form>`;
    $('#tb-msg')?.remove();
    if(state.msg){const m=document.createElement('p');m.id='tb-msg';m.className='tb-msg';m.textContent=state.msg;$('#tb-edit').append(m);}
    $('#tb-drag-hint').textContent=edit?'Arrastra una tarjeta a otra columna (en el celular, usa ◀ ▶). Al soltarla en «Terminado» queda aceptada por el Product Owner.':'';
    $('#tb-form-seg').hidden=!edit;$('#tb-form-ses').hidden=!edit;
    const idx=c=>ESTADOS.indexOf(c);
    $('#tb-kanban').innerHTML=ESTADOS.map(c=>{const list=H.filter(h=>h.estado===c);
      return `<div class="kcol" data-col="${c}"><div class="khead"><b>${c}</b><span>${list.length} HU · ${list.reduce((a,h)=>a+h.sp,0)} SP</span></div>${list.map(h=>`
      <article class="kcard${edit?' draggable':''}${h.saving?' saving':''}" ${edit&&h.number?`draggable="true" data-id="${h.id}"`:''}>
        <div class="ktop"><b>${E(h.id)}</b><span class="priority-tag priority-${E(h.priority)}">${E(h.priority)}</span></div>
        <strong>${E(h.name)}</strong><small>${E(h.owner)} · ${h.sp} SP</small>
        <div class="kfoot"><span>✓ ${h.pruebas} pruebas OK</span><a href="index.html#${E(h.id)}">Paso a paso ↗</a></div>
        ${edit&&h.number?`<div class="kmove"><button type="button" data-mv="${h.id}" data-to="${idx(c)-1}" ${idx(c)===0?'disabled':''} aria-label="Mover a la columna anterior">◀</button><button type="button" data-mv="${h.id}" data-to="${idx(c)+1}" ${idx(c)===3?'disabled':''} aria-label="Mover a la columna siguiente">▶</button></div>`:''}
      </article>`).join('')||'<p class="kempty">Sin historias</p>'}</div>`;}).join('');
    const ent=[...state.seg].sort((a,b)=>b.t.localeCompare(a.t)).concat(base);
    $('#tb-log').innerHTML=ent.map(e=>`<li><time>${E(e.cuando)}</time><div><span class="tag">${E(e.tipo)}</span> ${e.autor?`<span class="tag">@${E(e.autor)}</span>`:''}<p>${E(e.texto).replace(/\n/g,'<br>')}</p></div></li>`).join('');
    $('#tb-sessions').innerHTML=state.ses.length
      ?state.ses.map((s,i)=>`<article class="tb-session is-done"><div class="ktop"><b>Sesión ${i+1} · ${E(s.cuando)}</b><span class="tag tag-ok">Realizada</span></div><small>Registrada por @${E(s.autor)}</small><p class="tb-acta">${E(s.texto).replace(/\*\*/g,'').replace(/\n/g,'<br>')}</p></article>`).join('')
      :D.sesiones.map(s=>`<article class="tb-session"><div class="ktop"><b>Sesión ${s.n} · ${f(s.fecha)}</b><span class="tag tag-wait">${E(s.estado)}</span></div><h4>${E(s.tipo)}</h4><small>${E(s.duracion)}</small><div class="dialog-section-title">AGENDA</div><ol>${s.agenda.map(a=>`<li>${E(a)}</li>`).join('')}</ol><p class="tb-pending">Cuando se realice, regístrala con el formulario de arriba (activa la edición).</p></article>`).join('');
  }

  /* ---------------- Edición ---------------- */
  async function login(token){
    state.token=token.trim();
    try{const u=await gh('https://api.github.com/user');state.user=u.login;store.set(state.token);state.msg='';}
    catch(e){state.token='';state.user=null;store.set('');state.msg='El token no es válido o venció. Revisa los pasos y vuelve a intentarlo.';}
    render();
  }

  async function mover(id,to){
    const h=state.H.find(x=>x.id===id);const destino=ESTADOS[to];
    if(!h||!destino||h.estado===destino)return;
    const antes=h.estado;h.estado=destino;h.saving=true;state.msg='';render();
    const labels=(h.labels||[]).filter(l=>!ESTADOS.includes(l)).concat(destino);
    try{
      await gh(`/issues/${h.number}`,{method:'PATCH',body:JSON.stringify({labels,state:destino==='Terminado'?'closed':'open',state_reason:destino==='Terminado'?'completed':undefined})});
      h.labels=labels;
      const c=await comment(ISSUE_SEG,`Movimiento: ${h.id} · ${h.name} pasó de «${antes}» a «${destino}».`);
      state.seg.push({t:c.created_at,cuando:fh(c.created_at),tipo:'Movimiento de tarea',autor:state.user,texto:`${h.id} · ${h.name} pasó de «${antes}» a «${destino}».`});
    }catch(e){
      h.estado=antes;
      state.msg=e.status===403||e.status===404?`No se pudo mover ${h.id}: tu cuenta @${state.user} todavía no es colaboradora del repositorio. Pide al dueño que te agregue.`:`No se pudo mover ${h.id}. Revisa tu conexión e inténtalo de nuevo.`;
    }
    h.saving=false;render();
  }

  document.addEventListener('click',e=>{
    const sb=e.target.closest('.tb-sprints [data-sprint]');if(sb){state.sprint=sb.dataset.sprint;document.querySelectorAll('.tb-sprints button').forEach(b=>{const on=b===sb;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on));});render();}
    if(e.target.closest('#tb-login-open')){$('#tb-login').hidden=false;$('#tb-login input').focus();}
    if(e.target.closest('#tb-logout')){state.user=null;state.token='';store.set('');state.msg='';render();}
    const mv=e.target.closest('[data-mv]');if(mv)mover(mv.dataset.mv,+mv.dataset.to);
  });
  document.addEventListener('submit',async e=>{
    const form=e.target;e.preventDefault();const d=Object.fromEntries(new FormData(form));const btn=form.querySelector('button[type=submit]');
    if(form.id==='tb-login')return login(d.token||'');
    btn.disabled=true;
    try{
      if(form.id==='tb-form-seg'){
        const c=await comment(ISSUE_SEG,`Rol: ${d.rol}\n${d.texto.trim()}`);
        state.seg.push({t:c.created_at,cuando:fh(c.created_at),tipo:`Seguimiento · ${d.rol}`,autor:state.user,texto:d.texto.trim()});
      }
      if(form.id==='tb-form-ses'){
        const body=`Tipo: ${d.tipo}\nFecha y hora: ${d.fecha.replace('T',' ')}\nAsistentes: ${d.asistentes}\nRevisamos: ${d.revisamos}\nAcuerdos y estado de las HU: ${d.acuerdos}${d.evidencia?`\nEvidencia: ${d.evidencia}`:''}`;
        const c=await comment(ISSUE_SES,body);
        state.ses.push({t:c.created_at,cuando:fh(c.created_at),autor:state.user,texto:body});
      }
      form.reset();state.msg='Guardado.';
    }catch(err){state.msg='No se pudo guardar. Revisa tu conexión o el token e inténtalo de nuevo.';}
    btn.disabled=false;render();
  });

  /* Arrastrar y soltar */
  let dragId=null;
  document.addEventListener('dragstart',e=>{const c=e.target.closest('.kcard[draggable="true"]');if(!c)return;dragId=c.dataset.id;c.classList.add('dragging');e.dataTransfer.effectAllowed='move';e.dataTransfer.setData('text/plain',dragId);});
  document.addEventListener('dragend',()=>{document.querySelectorAll('.dragging,.drop-over').forEach(x=>x.classList.remove('dragging','drop-over'));});
  document.addEventListener('dragover',e=>{const col=e.target.closest('.kcol');if(!col||!dragId)return;e.preventDefault();document.querySelectorAll('.drop-over').forEach(x=>x!==col&&x.classList.remove('drop-over'));col.classList.add('drop-over');});
  document.addEventListener('drop',e=>{const col=e.target.closest('.kcol');if(!col||!dragId)return;e.preventDefault();const id=dragId;dragId=null;mover(id,ESTADOS.indexOf(col.dataset.col));});

  render();
  (state.token?gh('https://api.github.com/user').then(u=>{state.user=u.login;}).catch(()=>{state.token='';store.set('');}):Promise.resolve())
    .then(load).then(render);
})();
