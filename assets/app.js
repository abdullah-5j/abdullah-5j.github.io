(() => {
  const root = document.documentElement;
  const stored = (()=>{try{return localStorage.getItem('verox-theme')||'dark'}catch{return 'dark'}})();
  function applyTheme(value){root.dataset.theme = value === 'system' ? (matchMedia('(prefers-color-scheme: light)').matches?'light':'dark') : value;}
  applyTheme(stored);
  const toggle = document.getElementById('theme-toggle');
  const menu = document.getElementById('theme-menu');
  toggle?.addEventListener('click',()=>{const isOpen=menu?.classList.toggle('open');toggle.setAttribute('aria-expanded', String(!!isOpen));});
  menu?.querySelectorAll('[data-theme-choice]').forEach(btn=>btn.addEventListener('click',()=>{
    const value=btn.dataset.themeChoice;try{localStorage.setItem('verox-theme',value)}catch{}applyTheme(value);menu.classList.remove('open');toggle.setAttribute('aria-expanded','false');
  }));
  if (window.matchMedia) {matchMedia('(prefers-color-scheme: light)').addEventListener?.('change',()=>{try{if(localStorage.getItem('verox-theme')==='system')applyTheme('system')}catch{}})}
  document.getElementById('discord-copy')?.addEventListener('click', async e=>{try{await navigator.clipboard.writeText('notabdu11ah');e.currentTarget.title='Copied: notabdu11ah';}catch{prompt('My Discord username:', 'notabdu11ah');}});
  const sidebar = document.getElementById('sidebar');
  document.getElementById('mobile-trigger')?.addEventListener('click',()=>sidebar?.classList.toggle('show'));
  document.addEventListener('click',(event)=>{if(sidebar?.classList.contains('show')&&!sidebar.contains(event.target)&&!event.target.closest('#mobile-trigger'))sidebar.classList.remove('show');if(menu?.classList.contains('open')&&!event.target.closest('#theme-control-container'))menu.classList.remove('open');});
  const overlay = document.getElementById('search-backdrop');
  const input = document.getElementById('search-input');
  const results = document.getElementById('search-results');
  let items = null;
  const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  async function loadPosts(){if(items!==null)return items;try{const r=await fetch('/site.json');items=r.ok?await r.json():[];}catch{items=[]}return items;}
  function searchSnippet(post, term){const source=post.search_text||post.summary||'';if(!term)return post.summary||source.slice(0,180);const at=source.toLowerCase().indexOf(term);const start=Math.max(0,at<0?0:at-70);const end=Math.min(source.length,start+190);return `${start?'…':''}${source.slice(start,end)}${end<source.length?'…':''}`;}
  async function search(q){if(!results)return;const all=await loadPosts();const text=q.trim().toLowerCase();const hits=text?all.filter(p=>[p.title,p.summary,p.section,p.search_text,...(p.tags||[])].join(' ').toLowerCase().includes(text)).slice(0,20):all.slice(0,8);results.innerHTML=hits.length?hits.map(p=>`<a class="search-hit" href="${esc(p.url)}"><strong>${esc(p.title)}</strong><span>${esc(searchSnippet(p,text))}</span><small>${esc(p.section)}${p.date?' · '+esc(p.date):''}</small></a>`).join(''):`<div class="search-empty">${text?'No matching writeups found.':'No published articles yet.'}</div>`;}
  function openSearch(){overlay?.classList.add('open');document.body.style.overflow='hidden';input?.focus();search(input?.value||'')}
  function closeSearch(){overlay?.classList.remove('open');document.body.style.overflow='';}
  document.getElementById('open-search')?.addEventListener('click',openSearch);
  document.getElementById('close-search')?.addEventListener('click',closeSearch);
  overlay?.addEventListener('click',e=>{if(e.target===overlay)closeSearch()});
  input?.addEventListener('input',()=>search(input.value));
  document.addEventListener('keydown',event=>{if((event.key==='/'&&!['INPUT','TEXTAREA'].includes(document.activeElement?.tagName))||(event.ctrlKey&&event.key==='k')){event.preventDefault();openSearch();}if(event.key==='Escape')closeSearch();});

  document.querySelectorAll('.code-copy').forEach(button=>button.addEventListener('click',async()=>{const code=button.closest('.code-block')?.querySelector('code');if(!code)return;try{await navigator.clipboard.writeText(code.innerText);button.textContent='Copied';setTimeout(()=>button.textContent='Copy',1400)}catch{button.textContent='Select & copy'}}));
  document.querySelectorAll('.copy-link').forEach(button=>button.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(button.dataset.url||location.href);button.textContent='Copied';setTimeout(()=>button.textContent='Copy link',1400)}catch{prompt('Copy this link:',button.dataset.url||location.href)}}));

  const lightbox=document.getElementById('image-lightbox');
  document.querySelectorAll('.article-body img').forEach(img=>{img.tabIndex=0;img.setAttribute('role','button');img.setAttribute('aria-label',`Open image: ${img.alt||'article image'}`);const open=()=>{const target=lightbox?.querySelector('img');const caption=lightbox?.querySelector('p');if(!target||!lightbox)return;target.src=img.currentSrc||img.src;target.alt=img.alt||'';if(caption)caption.textContent=img.alt||'';lightbox.showModal()};img.addEventListener('click',open);img.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();open()}})});
  lightbox?.querySelector('.lightbox-close')?.addEventListener('click',()=>lightbox.close());
  lightbox?.addEventListener('click',event=>{if(event.target===lightbox)lightbox.close()});

  const topButton=document.getElementById('back-to-top');
  const setTopVisibility=()=>topButton?.classList.toggle('show',scrollY>500);
  addEventListener('scroll',setTopVisibility,{passive:true});setTopVisibility();
  topButton?.addEventListener('click',()=>scrollTo({top:0,behavior:'smooth'}));

  const tocLinks=[...document.querySelectorAll('.toc-list a')];
  if(tocLinks.length&&'IntersectionObserver'in window){const map=new Map(tocLinks.map(link=>[decodeURIComponent(link.hash.slice(1)),link]));const observer=new IntersectionObserver(entries=>{entries.filter(entry=>entry.isIntersecting).forEach(entry=>{tocLinks.forEach(link=>link.classList.remove('active'));map.get(entry.target.id)?.classList.add('active')})},{rootMargin:'-15% 0px -70%'});map.forEach((_,id)=>{const heading=document.getElementById(id);if(heading)observer.observe(heading)})}

  if('serviceWorker'in navigator){let registration;navigator.serviceWorker.addEventListener('controllerchange',()=>location.reload());addEventListener('load',async()=>{try{registration=await navigator.serviceWorker.register('/sw.js');const toast=document.getElementById('update-toast');const show=()=>toast?.classList.add('show');if(registration.waiting)show();registration.addEventListener('updatefound',()=>{const worker=registration.installing;worker?.addEventListener('statechange',()=>{if(worker.state==='installed'&&navigator.serviceWorker.controller)show()})});document.getElementById('apply-update')?.addEventListener('click',()=>registration?.waiting?.postMessage('SKIP_WAITING'));document.getElementById('dismiss-update')?.addEventListener('click',()=>toast?.classList.remove('show'))}catch{}})}
})();
