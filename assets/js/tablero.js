/* Tablero del Sprint 1 de MatchPoint.
   Lee en vivo los issues del repositorio (estado de cada HU, seguimiento del SM/PO y sesiones).
   Si GitHub no responde, muestra la última copia guardada en tablero-data.js. */
(()=>{
  'use strict';
  const D=window.MATCHPOINT_TABLERO; if(!D)return;
  const REPO='ItsKmilo/matchpoint-documentacion', API=`https://api.github.com/repos/${REPO}`, GH=`https://github.com/${REPO}`;
  const ISSUE_SEG=21, ISSUE_SES=22;
  const ESTADOS=['Por hacer','En progreso','En revisión','Terminado'];
  const $=s=>document.querySelector(s);
  const E=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const f=iso=>{const [y,m,d]=iso.slice(0,10).split('-');return `${d}/${m}/${y}`;};
  const fh=iso=>{const d=new Date(iso);return d.toLocaleString('es-CO',{day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit',timeZone:'America/Bogota'});};
  const menu=document.querySelector('.menu-toggle'),nav=document.querySelector('#site-nav');
  menu?.addEventListener('click',()=>{const o=nav.classList.toggle('open');menu.setAttribute('aria-expanded',String(o));});
  const S=D.sprint;
  $('#tb-objetivo').textContent=`${S.nombre}. Inicio: ${f(S.inicio)} · Entrega de avance: ${f(S.entrega_avance)}. ${S.objetivo}`;
  $('#tb-roles').innerHTML=Object.entries(S.roles).map(([r,n])=>`<div><small>${E(r.toUpperCase())}</small><strong>${E(n)}</strong></div>`).join('');

  function render(H, entradas, sesiones, live){
    const total=H.reduce((a,h)=>a+h.sp,0)||1;
    const sum=st=>H.filter(h=>st.includes(h.estado)).reduce((a,h)=>a+h.sp,0);
    const done=sum(['Terminado']), impl=sum(['En revisión','Terminado']);
    $('#tb-kpis').innerHTML=[['HISTORIAS',H.length],['PUNTOS (SP)',total],['SP IMPLEMENTADOS',impl],['SP TERMINADOS',done],['PRUEBAS OK',D.historias.reduce((a,h)=>a+h.pruebas,0)]].map(([a,b])=>`<div><span>${a}</span><strong>${b}</strong></div>`).join('');
    $('#tb-bar-done').style.width=(done/total*100)+'%';
    $('#tb-bar-impl').style.width=((impl-done)/total*100)+'%';
    $('#tb-source').innerHTML=live?`● En vivo desde <a href="${GH}/issues?q=is%3Aissue+milestone%3A%22Sprint+1%22" target="_blank" rel="noopener">GitHub Issues</a> · actualizado ${fh(new Date().toISOString())}`:'Copia guardada (GitHub no respondió). Recarga en unos minutos para ver los cambios más recientes.';
    $('#tb-kanban').innerHTML=ESTADOS.map(c=>{const list=H.filter(h=>h.estado===c);
      return `<div class="kcol"><div class="khead"><b>${c}</b><span>${list.length} HU · ${list.reduce((a,h)=>a+h.sp,0)} SP</span></div>${list.map(h=>`
      <article class="kcard"><div class="ktop"><b>${E(h.id)}</b><span class="priority-tag priority-${E(h.priority)}">${E(h.priority)}</span></div>
      <strong>${E(h.name)}</strong><small>${E(h.owner)} · ${h.sp} SP</small>
      <div class="kfoot"><span title="Pruebas automáticas aprobadas">✓ ${h.pruebas} pruebas OK</span><span><a href="index.html#${E(h.id)}">Paso a paso</a>${h.url?` · <a href="${E(h.url)}" target="_blank" rel="noopener">Mover ↗</a>`:''}</span></div></article>`).join('')||'<p class="kempty">Sin historias</p>'}</div>`;}).join('');
    $('#tb-log').innerHTML=entradas.length?entradas.map(e=>`<li><time>${E(e.cuando)}</time><div><span class="tag">${E(e.tipo)}</span> ${e.autor?`<span class="tag">${E(e.autor)}</span>`:''}<p>${E(e.texto).replace(/\n/g,'<br>')}</p></div></li>`).join(''):'<li><time>—</time><div><p>Sin entradas todavía.</p></div></li>';
    $('#tb-sessions').innerHTML=(sesiones.length?sesiones.map(s=>`<article class="tb-session is-done"><div class="ktop"><b>${E(s.cuando)}</b><span class="tag tag-ok">Realizada</span></div><h4>Registrada por ${E(s.autor)}</h4><p class="tb-acta">${E(s.texto).replace(/\n/g,'<br>')}</p></article>`).join('')
      :D.sesiones.map(s=>`<article class="tb-session"><div class="ktop"><b>Sesión ${s.n} · ${f(s.fecha)}</b><span class="tag tag-wait">${E(s.estado)}</span></div><h4>${E(s.tipo)}</h4><small>${E(s.duracion)}</small><div class="dialog-section-title">AGENDA</div><ol>${s.agenda.map(a=>`<li>${E(a)}</li>`).join('')}</ol><p class="tb-pending">Se registra como comentario en el <a href="${GH}/issues/${ISSUE_SES}" target="_blank" rel="noopener">reporte de sesiones</a> cuando se realice.</p></article>`).join(''));
  }

  const local=D.historias.map(h=>({...h}));
  const baseEntradas=[...D.entradas].reverse().map(e=>({cuando:f(e.fecha),tipo:e.tipo,autor:'',texto:e.texto}));
  render(local, baseEntradas, [], false);

  const get=u=>fetch(u,{headers:{Accept:'application/vnd.github+json'}}).then(r=>{if(!r.ok)throw new Error(r.status);return r.json();});
  Promise.all([get(`${API}/issues?state=all&labels=Sprint%201,Historia%20de%20usuario&per_page=100`),get(`${API}/issues/${ISSUE_SEG}/comments?per_page=100`),get(`${API}/issues/${ISSUE_SES}/comments?per_page=100`)])
  .then(([issues,seg,ses])=>{
    const byId=Object.fromEntries(local.map(h=>[h.id,h]));
    const H=issues.map(i=>{const id=(i.title.match(/HU\d{3}/)||[''])[0];const base=byId[id]||{};const labels=i.labels.map(l=>l.name);
      const estado=i.state==='closed'?'Terminado':(ESTADOS.find(e=>labels.includes(e))||'Por hacer');
      const sp=+((i.title.match(/\((\d+) SP\)/)||[0,base.sp||0])[1]);
      return {...base,id,name:base.name||i.title,sp,priority:['Must','Should','Could'].find(p=>labels.includes(p))||base.priority,estado,url:i.html_url};}).filter(h=>h.id).sort((a,b)=>a.id.localeCompare(b.id));
    const ent=[...seg.map(c=>({t:c.created_at,cuando:fh(c.created_at),tipo:'Seguimiento SM / PO',autor:c.user.login,texto:c.body}))].sort((a,b)=>b.t.localeCompare(a.t));
    const sesiones=ses.map(c=>({cuando:fh(c.created_at),autor:c.user.login,texto:c.body}));
    render(H.length?H:local,[...ent,...baseEntradas],sesiones,true);
  }).catch(()=>{});
})();
