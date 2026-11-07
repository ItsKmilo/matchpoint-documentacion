/* Tablero de retrospectiva (Starfish en el Sprint 1, Velero en el Sprint 2).
   Las notas y acciones son comentarios del issue con la etiqueta «Retrospectiva» del repositorio:
   quedan con autor, fecha y hora. Cualquiera lo ve; el equipo escribe tras «Activar edición»
   (el mismo token del tablero del sprint). Sin librerías externas. */
(()=>{
  'use strict';
  const REPO='ItsKmilo/matchpoint-documentacion',API=`https://api.github.com/repos/${REPO}`,KEY='mp-tablero-token';
  const CFG=window.MP_RETRO||{sprint:'Sprint 1',tecnica:'starfish'};
  const TECNICAS={
    starfish:[
      {k:'Empezar a hacer',d:'Lo que no hacemos y deberíamos empezar.',c:'#2563eb'},
      {k:'Dejar de hacer',d:'Lo que no aporta o nos frena.',c:'#dc2626'},
      {k:'Seguir haciendo',d:'Lo que funcionó y se mantiene.',c:'#16a34a'},
      {k:'Hacer más',d:'Lo que funcionó y conviene aumentar.',c:'#7c3aed'},
      {k:'Hacer menos',d:'Lo que aporta poco para lo que cuesta.',c:'#d97706'}],
    velero:[
      {k:'Viento',d:'Lo que nos impulsó durante el sprint.',c:'#16a34a'},
      {k:'Anclas',d:'Lo que nos frenó o retrasó.',c:'#dc2626'},
      {k:'Rocas',d:'Riesgos que vemos por delante.',c:'#d97706'},
      {k:'Isla',d:'La meta: cómo se ve el proyecto terminado.',c:'#2563eb'}]};
  const PUNTAS=TECNICAS[CFG.tecnica]||TECNICAS.starfish;
  const $=s=>document.querySelector(s);
  const E=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fh=iso=>new Date(iso).toLocaleString('es-CO',{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit',timeZone:'America/Bogota'});
  const store={get(){try{return localStorage.getItem(KEY)||'';}catch(e){return '';}},set(v){try{v?localStorage.setItem(KEY,v):localStorage.removeItem(KEY);}catch(e){}}};
  const st={token:store.get(),user:null,issue:null,notas:[],acciones:[],live:false,msg:''};

  function gh(path,opts={}){
    const h={Accept:'application/vnd.github+json'};
    if(st.token)h.Authorization=`Bearer ${st.token}`;
    if(opts.body)h['Content-Type']='application/json';
    return fetch(path.startsWith('http')?path:API+path,{...opts,headers:h,cache:'no-store'}).then(async r=>{
      if(!r.ok){const t=await r.json().catch(()=>({}));const e=new Error(t.message||r.status);e.status=r.status;throw e;}
      return r.status===204?null:r.json();});
  }
  function parse(c){
    const b=c.body||'';const col=(b.match(/^Punta:\s*(.+)$/mi)||[])[1];const acc=(b.match(/^Acción:\s*(.+)$/mi)||[])[1];
    if(col){st.notas.push({punta:col.trim(),texto:b.replace(/^Punta:.*$/mi,'').trim(),autor:c.user.login,t:c.created_at});}
    else if(acc){st.acciones.push({accion:acc.trim(),resp:((b.match(/^Responsable:\s*(.+)$/mi)||[])[1]||'').trim(),fecha:((b.match(/^Para:\s*(.+)$/mi)||[])[1]||'').trim(),autor:c.user.login,t:c.created_at});}
  }
  async function load(){
    try{
      const issues=await gh('/issues?state=all&labels=Retrospectiva&per_page=10');
      st.issue=issues.find(i=>i.title.toLowerCase().includes(CFG.sprint.toLowerCase()))||null;
      st.notas=[];st.acciones=[];
      if(st.issue){(await gh(`/issues/${st.issue.number}/comments?per_page=100`)).forEach(parse);}
      st.live=true;
    }catch(e){st.live=false;}
  }
  function render(){
    const edit=!!st.user&&!!st.issue;
    $('#rt-source').innerHTML=st.live?(st.issue?`● En vivo · ${st.notas.length} notas · ${st.acciones.length} acciones`:'El tablero se activa cuando exista el issue de la retrospectiva.'):'No se pudo leer GitHub. Recarga en unos minutos.';
    $('#rt-edit').innerHTML=st.user
      ?`<div class="tb-editbar on"><span>✎ Edición activa como <b>@${E(st.user)}</b>. Escribe tus notas en cada punta.</span><button type="button" class="btn-link" id="rt-logout">Salir de edición</button></div>`
      :`<div class="tb-editbar"><span><b>¿Eres del equipo?</b> Activa la edición para escribir notas (usa el mismo token del tablero del sprint).</span><button type="button" class="btn btn-dark" id="rt-login-open">Activar edición</button></div>
        <form class="tb-login" id="rt-login" hidden><label>Token de GitHub<input name="token" type="password" autocomplete="off" required placeholder="ghp_…"></label><button class="btn btn-primary" type="submit">Entrar</button>
        <details><summary>¿Cómo obtengo el token?</summary><ol><li>Entra a <a href="https://github.com/settings/tokens/new?scopes=public_repo&description=Tablero%20MatchPoint" target="_blank" rel="noopener">GitHub → Generate new token (classic)</a>.</li><li>Deja marcado solo <code>public_repo</code> y pulsa <b>Generate token</b>.</li><li>Pégalo aquí. Se guarda solo en este navegador.</li></ol></details></form>`;
    if(st.msg){const m=document.createElement('p');m.className='tb-msg';m.textContent=st.msg;$('#rt-edit').append(m);}
    $('#rt-board').className='starfish'+(PUNTAS.length===4?' four':'');$('#rt-board').innerHTML=PUNTAS.map((p,i)=>{const ns=st.notas.filter(n=>n.punta.toLowerCase()===p.k.toLowerCase());
      return `<div class="sf-col" style="--c:${p.c}"><div class="sf-head"><span class="sf-n">${i+1}</span><div><b>${p.k}</b><small>${p.d}</small></div><em>${ns.length}</em></div>
      ${ns.map(n=>`<div class="sf-note"><p>${E(n.texto).replace(/\n/g,'<br>')}</p><small>@${E(n.autor)} · ${fh(n.t)}</small></div>`).join('')||'<p class="kempty">Sin notas todavía</p>'}
      ${edit?`<form class="sf-add" data-punta="${p.k}"><textarea name="texto" rows="2" required placeholder="Nueva nota…"></textarea><button class="btn btn-dark" type="submit">Agregar</button></form>`:''}</div>`;}).join('');
    $('#rt-form-accion').hidden=!edit;
    $('#rt-acciones').innerHTML=st.acciones.length?st.acciones.map(a=>`<tr><td>${E(a.accion)}</td><td>${E(a.resp)}</td><td>${E(a.fecha)}</td><td>@${E(a.autor)} · ${fh(a.t)}</td></tr>`).join(''):'<tr><td colspan="4" class="empty-row">Las acciones se acuerdan al final de la sesión.</td></tr>';
  }
  async function login(t){
    st.token=t.trim();
    try{st.user=(await gh('https://api.github.com/user')).login;store.set(st.token);st.msg='';}
    catch(e){st.token='';st.user=null;store.set('');st.msg='El token no es válido o venció.';}
    render();
  }
  document.addEventListener('click',e=>{
    if(e.target.closest('#rt-login-open')){$('#rt-login').hidden=false;$('#rt-login input').focus();}
    if(e.target.closest('#rt-logout')){st.user=null;st.token='';store.set('');render();}
  });
  document.addEventListener('submit',async e=>{
    const f=e.target;e.preventDefault();const d=Object.fromEntries(new FormData(f));
    if(f.id==='rt-login')return login(d.token||'');
    const btn=f.querySelector('button[type=submit]');btn.disabled=true;
    try{
      let body;
      if(f.classList.contains('sf-add'))body=`Punta: ${f.dataset.punta}\n${d.texto.trim()}`;
      if(f.id==='rt-form-accion')body=`Acción: ${d.accion.trim()}\nResponsable: ${d.resp.trim()}\nPara: ${d.fecha}`;
      if(!body)return;
      const c=await gh(`/issues/${st.issue.number}/comments`,{method:'POST',body:JSON.stringify({body})});
      parse({...c,body,user:{login:st.user}});st.msg='';f.reset();
    }catch(err){st.msg='No se pudo guardar. Revisa tu conexión o el token.';}
    btn.disabled=false;render();
  });
  render();
  (st.token?gh('https://api.github.com/user').then(u=>{st.user=u.login;}).catch(()=>{st.token='';store.set('');}):Promise.resolve()).then(load).then(render);
})();
