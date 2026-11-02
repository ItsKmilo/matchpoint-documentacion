/* Tablero del Sprint 1 de MatchPoint (sin librerías externas). */
(()=>{
  'use strict';
  const D=window.MATCHPOINT_TABLERO; if(!D)return;
  const $=s=>document.querySelector(s);
  const E=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const f=iso=>{const [y,m,d]=iso.split('-');return `${d}/${m}/${y}`;};
  const menu=document.querySelector('.menu-toggle'),nav=document.querySelector('#site-nav');
  menu?.addEventListener('click',()=>{const o=nav.classList.toggle('open');menu.setAttribute('aria-expanded',String(o));});

  const H=D.historias, S=D.sprint;
  const total=H.reduce((a,h)=>a+h.sp,0);
  const done=H.filter(h=>h.estado==='Terminado').reduce((a,h)=>a+h.sp,0);
  const impl=H.filter(h=>h.estado==='En revisión'||h.estado==='Terminado').reduce((a,h)=>a+h.sp,0);
  const tests=H.reduce((a,h)=>a+h.pruebas,0);
  $('#tb-objetivo').textContent=`${S.nombre}. Inicio: ${f(S.inicio)} · Entrega de avance: ${f(S.entrega_avance)}. ${S.objetivo}`;
  $('#tb-roles').innerHTML=Object.entries(S.roles).map(([r,n])=>`<div><small>${E(r.toUpperCase())}</small><strong>${E(n)}</strong></div>`).join('');
  $('#tb-kpis').innerHTML=[['HISTORIAS',H.length],['PUNTOS (SP)',total],['SP IMPLEMENTADOS',impl],['SP TERMINADOS',done],['PRUEBAS OK',tests]].map(([a,b])=>`<div><span>${a}</span><strong>${b}</strong></div>`).join('');
  $('#tb-bar-done').style.width=(done/total*100)+'%';
  $('#tb-bar-impl').style.width=((impl-done)/total*100)+'%';

  const cols=['Por hacer','En progreso','En revisión','Terminado'];
  $('#tb-kanban').innerHTML=cols.map(c=>{const list=H.filter(h=>h.estado===c);
    return `<div class="kcol"><div class="khead"><b>${c}</b><span>${list.length} HU · ${list.reduce((a,h)=>a+h.sp,0)} SP</span></div>${list.map(h=>`
    <article class="kcard"><div class="ktop"><b>${E(h.id)}</b><span class="priority-tag priority-${E(h.priority)}">${E(h.priority)}</span></div>
    <strong>${E(h.name)}</strong><small>${E(h.owner)} · ${h.sp} SP</small>
    <div class="kfoot"><span title="Pruebas automáticas aprobadas">✓ ${h.pruebas} pruebas OK · ${h.pasos} pasos</span><a href="index.html#${E(h.id)}">Paso a paso ↗</a></div></article>`).join('')||'<p class="kempty">Sin historias</p>'}</div>`;}).join('');

  $('#tb-log').innerHTML=[...D.entradas].reverse().map(e=>`<li><time>${f(e.fecha)}</time><div><span class="tag">${E(e.tipo)}</span> <span class="tag">${E(e.rol)}</span><p>${E(e.texto)}</p></div></li>`).join('');

  $('#tb-sessions').innerHTML=D.sesiones.map(s=>{const real=s.estado==='Realizada';
    return `<article class="tb-session ${real?'is-done':''}"><div class="ktop"><b>Sesión ${s.n} · ${f(s.fecha)}</b><span class="tag ${real?'tag-ok':'tag-wait'}">${E(s.estado)}</span></div>
    <h4>${E(s.tipo)}</h4><small>${E(s.duracion)}</small>
    <div class="dialog-section-title">AGENDA</div><ol>${s.agenda.map(a=>`<li>${E(a)}</li>`).join('')}</ol>
    ${real?`<div class="dialog-section-title">ASISTENTES</div><p>${E(s.asistentes.join(', '))}</p><div class="dialog-section-title">ACUERDOS Y SEGUIMIENTO</div><ul>${s.acuerdos.map(a=>`<li>${E(a)}</li>`).join('')}</ul>${s.evidencia?`<p><a href="${E(s.evidencia)}" target="_blank" rel="noopener">Ver evidencia ↗</a></p>`:''}`
    :'<p class="tb-pending">El acta se completa cuando la sesión se realice: asistentes, acuerdos y estado de cada HU.</p>'}</article>`;}).join('');
})();
