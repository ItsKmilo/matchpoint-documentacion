/* Sitio estático MatchPoint: sin librerías externas ni servicios remotos. */
(()=>{
  'use strict';
  const $=(s,r=document)=>r.querySelector(s);
  const $$=(s,r=document)=>Array.from(r.querySelectorAll(s));
  const escapeHTML=(s)=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const reduceMotion=()=>window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const menu=$('.menu-toggle'),nav=$('#site-nav');
  menu?.addEventListener('click',()=>{const open=nav.classList.toggle('open');menu.setAttribute('aria-expanded',String(open));menu.setAttribute('aria-label',open?'Cerrar menú':'Abrir menú');});
  $$('#site-nav a').forEach(a=>a.addEventListener('click',()=>{nav.classList.remove('open');menu?.setAttribute('aria-expanded','false');}));
  window.addEventListener('keydown',e=>{if(e.key==='Escape' && nav?.classList.contains('open')){nav.classList.remove('open');menu.setAttribute('aria-expanded','false');menu.focus();}});

  /* ---------- Mapa de historias ---------- */
  const mapList={
    full:{src:'descargas/Mapa_Historias_MatchPoint_Editable.svg',alt:'Mapa completo de historias de MatchPoint: 6 épicas, 20 historias y 2 sprints'},
    config:{src:'descargas/MatchPoint_Detalle_01_Configuracion_EDITABLE.svg',alt:'Mapa detallado: acceso, participantes, torneos y eventos'},
    participacion:{src:'descargas/MatchPoint_Detalle_02_Participacion_EDITABLE.svg',alt:'Mapa detallado: consulta de eventos y pronósticos'},
    creditos:{src:'descargas/MatchPoint_Detalle_03_Creditos_y_Transacciones_EDITABLE.svg',alt:'Mapa detallado: créditos iniciales, saldo, movimientos y ajustes'},
    resultados:{src:'descargas/MatchPoint_Detalle_04_Resultados_y_Control_EDITABLE.svg',alt:'Mapa detallado: cierre, resultados, liquidación y auditoría'}
  };
  const mapViewport=$('#map-viewport'),mapImage=$('#map-image'),mapOpen=$('#map-open'),mapDownload=$('#map-download');
  function switchMap(key){const entry=mapList[key];if(!entry)return;mapImage.src=entry.src;mapImage.alt=entry.alt;mapImage.classList.toggle('detail',key!=='full');mapOpen.href=entry.src;mapDownload.href=entry.src;mapViewport.scrollLeft=0;mapViewport.scrollTop=0;$$('.map-tabs button').forEach(btn=>{const yes=btn.dataset.map===key;btn.classList.toggle('active',yes);btn.setAttribute('aria-selected',String(yes));btn.tabIndex=yes?0:-1;});}
  $$('.map-tabs button').forEach((b,i,all)=>{b.addEventListener('click',()=>switchMap(b.dataset.map));b.addEventListener('keydown',e=>{let next;if(e.key==='ArrowRight')next=(i+1)%all.length;else if(e.key==='ArrowLeft')next=(i-1+all.length)%all.length;else if(e.key==='Home')next=0;else if(e.key==='End')next=all.length-1;else return;e.preventDefault();all[next].focus();switchMap(all[next].dataset.map);});});

  /* ---------- Product Backlog ---------- */
  const records=Array.isArray(window.MATCHPOINT_BACKLOG)?window.MATCHPOINT_BACKLOG:[];
  const search=$('#search-stories'),priority=$('#filter-priority'),sprint=$('#filter-sprint'),epic=$('#filter-epic'),tbody=$('#story-rows'),counter=$('#results-count');
  const PAGE=10;let visibleLimit=PAGE,shown=[];
  const epicNames=[...new Set(records.map(x=>x.epic))];epicNames.forEach(name=>{let opt=document.createElement('option');opt.value=name;opt.textContent=name;epic.append(opt);});
  const safeLower=s=>String(s??'').normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();
  function filters(){let term=safeLower(search.value.trim());return records.filter(x=>(!term||safeLower([x.id,x.name,x.epic,x.story,x.stage,x.owner,x.activity,x.actor].join(' ')).includes(term))&&(!priority.value||x.priority===priority.value)&&(!sprint.value||x.sprint===sprint.value)&&(!epic.value||x.epic===epic.value));}
  const controls=document.createElement('div');controls.className='paging-controls';controls.innerHTML=`<button type="button" id="next-stories">Mostrar ${PAGE} más ↓</button><button type="button" id="all-stories">Ver todas las historias</button>`;$('.backlog-app').insertBefore(controls,$('.backlog-footnote'));
  function render(){shown=filters();counter.textContent=`Mostrando ${Math.min(visibleLimit,shown.length)} de ${shown.length} historias${shown.length!==records.length?' filtradas':''}`;
    if(!shown.length){tbody.innerHTML='<tr><td class="empty-row" colspan="7">No se encontraron historias. Prueba con otros filtros.</td></tr>';}
    else {tbody.innerHTML=shown.slice(0,visibleLimit).map(x=>`<tr><td>${escapeHTML(x.id)}</td><td>${escapeHTML(x.name)}</td><td>${escapeHTML(x.epic)}</td><td><span class="priority-tag priority-${escapeHTML(x.priority)}">${escapeHTML(x.priority)}</span></td><td><span class="sprint-pill sprint-${x.sprint.slice(-1)}">${escapeHTML(x.sprint)}</span></td><td>${x.sp}</td><td><button class="detail-link" type="button" data-detail="${escapeHTML(x.id)}" aria-label="Ver paso a paso y mockup de ${escapeHTML(x.id)}">Paso a paso ↗</button></td></tr>`).join('');}
    $('#next-stories').disabled=visibleLimit>=shown.length;$('#next-stories').hidden=visibleLimit>=shown.length;$('#all-stories').hidden=visibleLimit>=shown.length;
  }
  for(let el of [search,priority,sprint,epic])el.addEventListener(el===search?'input':'change',()=>{visibleLimit=PAGE;render();});
  $('#clear-filters').addEventListener('click',()=>{search.value='';priority.value='';sprint.value='';epic.value='';visibleLimit=PAGE;render();search.focus();});
  $('#next-stories').addEventListener('click',()=>{visibleLimit+=PAGE;render();});
  $('#all-stories').addEventListener('click',()=>{visibleLimit=records.length;render();});
  $$('.sprint-filter').forEach(btn=>btn.addEventListener('click',()=>{search.value='';priority.value='';epic.value='';sprint.value=btn.dataset.sprint;visibleLimit=PAGE;render();$('#backlog').scrollIntoView({behavior:reduceMotion()?'auto':'smooth'});setTimeout(()=>sprint.focus({preventScroll:true}),250);}));

  /* ---------- Galería de HU con mockups ---------- */
  const gallery=$('#hu-gallery');
  function renderGallery(filter){if(!gallery)return;const list=records.filter(x=>!filter||x.sprint===filter);
    gallery.innerHTML=list.map(x=>`<button type="button" class="hu-card" data-detail="${escapeHTML(x.id)}" aria-label="Abrir ${escapeHTML(x.id)} ${escapeHTML(x.name)}: paso a paso y mockup"><span class="hu-thumb"><img src="${escapeHTML(x.mockup)}" alt="" loading="lazy" width="1920" height="1200"></span><span class="hu-card-body"><span class="hu-card-top"><b>${escapeHTML(x.id)}</b><span class="sprint-pill sprint-${x.sprint.slice(-1)}">${escapeHTML(x.sprint)}</span></span><strong>${escapeHTML(x.name)}</strong><small>${escapeHTML(x.epic)} · ${x.steps.length} pasos · ${x.sp} SP</small></span></button>`).join('');}
  $$('.hu-tabs button').forEach(b=>b.addEventListener('click',()=>{$$('.hu-tabs button').forEach(o=>{const on=o===b;o.classList.toggle('active',on);o.setAttribute('aria-pressed',String(on));});renderGallery(b.dataset.sprint);}));
  gallery?.addEventListener('click',e=>{const c=e.target.closest('[data-detail]');if(c)openStory(c.dataset.detail);});
  $$('.hu-open').forEach(b=>b.addEventListener('click',()=>openStory(b.dataset.open)));
  renderGallery('');

  /* ---------- Detalle: formato tabla de HU + mockup ---------- */
  const dialog=$('#story-dialog'),dContent=$('#dialog-content'),close=$('#dialog-close');
  function openStory(id){let x=records.find(r=>r.id===id);if(!x||!dialog)return;
    const steps=x.steps.map((s,i)=>`<tr><td class="hu-label">${i===0?'Criterios de aceptación<br><small>paso a paso</small>':''}</td><td><span class="step-n">${i+1}</span>${escapeHTML(s)}</td></tr>`).join('');
    dContent.innerHTML=`<div class="dialog-id">${escapeHTML(x.id)} · ${escapeHTML(x.epic)} · ${escapeHTML(x.sprint)}</div><h3 class="dialog-title" id="dialog-title">${escapeHTML(x.name)}</h3><div class="dialog-tags"><span class="priority-tag priority-${escapeHTML(x.priority)}">${escapeHTML(x.priority)}</span><span class="tag">${escapeHTML(x.sprint)}</span><span class="tag">${escapeHTML(x.type)}</span><span class="tag">Riesgo ${escapeHTML(x.risk.toLowerCase())}</span><span class="tag">${x.sp} SP</span></div>
    <div class="hu-table-wrap"><table class="hu-table"><tbody><tr class="hu-head"><th>Identificador</th><th>${escapeHTML(x.id)}</th></tr><tr><td class="hu-label">Nombre</td><td>${escapeHTML(x.name)}</td></tr><tr><td class="hu-label">Descripción</td><td>${escapeHTML(x.story)}</td></tr>${steps}</tbody></table></div>
    <div class="dialog-section-title">MOCKUP · LOS NÚMEROS ROJOS CORRESPONDEN A CADA PASO</div><figure class="dialog-mockup"><a href="${escapeHTML(x.mockup)}" target="_blank" rel="noopener"><img src="${escapeHTML(x.mockup)}" alt="Mockup de ${escapeHTML(x.id)}: ${escapeHTML(x.mockupDesc)}" width="1920" height="1200"></a><figcaption>${escapeHTML(x.mockupDesc)} <a href="${escapeHTML(x.mockupSvg)}" download>SVG editable ↧</a></figcaption></figure>
    <div class="dialog-metadata"><div><small>ACTOR</small><strong>${escapeHTML(x.actor)}</strong></div><div><small>RESPONSABLE PROPUESTO</small><strong>${escapeHTML(x.owner)}</strong></div><div><small>DEPENDENCIAS</small><strong>${escapeHTML(x.dependencies)}</strong></div><div><small>ESTADO</small><strong>${escapeHTML(x.status)}</strong></div></div>${x.notes?`<div class="dialog-section-title">NOTAS DE PLANIFICACIÓN</div><p class="dialog-notes">${escapeHTML(x.notes)}</p>`:''}`;
    dialog.showModal();close.focus();}
  tbody.addEventListener('click',e=>{let button=e.target.closest('[data-detail]');if(button)openStory(button.dataset.detail);});
  close.addEventListener('click',()=>dialog.close());dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});
  render();
  if(location.hash && /^#HU\d{3}$/.test(location.hash)){openStory(location.hash.slice(1));}
  if('IntersectionObserver' in window){const links=$$('#site-nav a[href^="#"]');const io=new IntersectionObserver(items=>{items.forEach(entry=>{if(entry.isIntersecting){links.forEach(a=>a.classList.toggle('active',a.getAttribute('href')==='#'+entry.target.id));}})},{rootMargin:'-25% 0px -62% 0px'});$$('main section[id]').forEach(section=>io.observe(section));}
})();
