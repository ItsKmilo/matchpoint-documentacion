(()=>{
  'use strict';
  const d=window.MATCHPOINT_ENTREGA||{},box=document.getElementById('ent-video');if(!box)return;
  const E=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const u=(d.video||'').trim();
  const yt=u.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/|shorts\/))([\w-]{11})/);
  const dr=u.match(/drive\.google\.com\/file\/d\/([\w-]+)/);
  if(yt){box.innerHTML=`<div class="ent-frame"><iframe src="https://www.youtube-nocookie.com/embed/${yt[1]}" title="Review del Sprint 1" allow="encrypted-media; picture-in-picture" allowfullscreen loading="lazy"></iframe></div><p class="timeline-note"><a href="${E(u)}" target="_blank" rel="noopener">Abrir el video en YouTube ↗</a>${d.fecha?` · Grabado el ${E(d.fecha)}`:''}</p>`;}
  else if(dr){box.innerHTML=`<div class="ent-frame"><iframe src="https://drive.google.com/file/d/${dr[1]}/preview" title="Review del Sprint 1" allow="autoplay" loading="lazy"></iframe></div><p class="timeline-note"><a href="${E(u)}" target="_blank" rel="noopener">Abrir el video en Google Drive ↗</a>${d.fecha?` · Grabado el ${E(d.fecha)}`:''}</p>`;}
  else if(u){box.innerHTML=`<p><a class="btn btn-dark" href="${E(u)}" target="_blank" rel="noopener">Ver video de la review ↗</a></p>`;}
  else{box.innerHTML='<p class="tb-pending">El video de la review se publica aquí cuando el equipo lo grabe. Guion abajo.</p>';}
})();
