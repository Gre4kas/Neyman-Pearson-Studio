// Refactored admin JS: single IIFE, debounced preview, AbortController, improved image handling.
(function() {
  console.log('Theory Admin JS loaded - v2.0 with fixed URLs');
  
  // === MathJax bootstrap (idempotent) ===
  window.MathJax = window.MathJax || {
    tex: {
      inlineMath: [['$', '$'], ['\\(', '\\)']],
      displayMath: [['$$', '$$'], ['\\[', '\\]']],
      processEscapes: true,
      processEnvironments: true
    },
    options: { renderActions: { addMenu: [] } }
  };

  function ensureMathJax(callback, attempt = 0) {
    if (window.MathJax && window.MathJax.typesetPromise) { callback(); return; }
    const existing = document.getElementById('mathjax-script');
    if (!existing) {
      const s = document.createElement('script');
      s.id = 'mathjax-script';
      s.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js';
      s.async = true;
      s.onload = () => callback();
      s.onerror = () => console.error('MathJax load error');
      document.head.appendChild(s);
    } else if (attempt < 15) {
      setTimeout(() => ensureMathJax(callback, attempt + 1), 300);
    }
  }

  function typesetTarget(target) {
    if (!target) return;
    if (window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.typesetPromise([target]).catch(err => console.error('MathJax render error:', err));
    }
  }

  function debounce(fn, wait) { let t; return function(...args){ clearTimeout(t); t = setTimeout(() => fn.apply(this,args), wait); }; }

  function setupLivePreview() {
    const textarea = document.querySelector('textarea[name="content_md"]');
    const previewContainer = document.querySelector('.preview-content');
    if (!textarea || !previewContainer) return;
    let controller = null; const loadingClass = 'is-loading';
    function setLoading(is){
      if(is){
        previewContainer.classList.add(loadingClass);
        if(!previewContainer.querySelector('.preview-loading')){
          const loader=document.createElement('div'); loader.className='preview-loading';
          loader.style.cssText='position:absolute; top:10px; right:14px; font-size:11px; color:#555;';
          loader.textContent='Обновление...'; previewContainer.appendChild(loader);
        }
      } else {
        previewContainer.classList.remove(loadingClass);
        const l=previewContainer.querySelector('.preview-loading'); if(l) l.remove();
      }
    }
    function performPreview(content){
      if(controller) controller.abort(); controller=new AbortController(); setLoading(true);
      fetch(window.location.origin + '/theory/admin/preview/', {
        method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({content}), signal:controller.signal
      })
        .then(r=>r.json())
        .then(data=>{ if(!data.success) return; previewContainer.innerHTML=data.html; ensureMathJax(()=>{
          const articleContent=document.getElementById('article-content'); typesetTarget(articleContent);
          setTimeout(()=>typesetTarget(articleContent),400); setTimeout(()=>typesetTarget(articleContent),1200);
        }); })
        .catch(err=>{ if(err.name!=='AbortError') console.error('Preview error:',err); })
        .finally(()=> setLoading(false));
    }
    const debounced = debounce(()=> performPreview(textarea.value),450);
    textarea.addEventListener('input', debounced);
    performPreview(textarea.value);
  }

  window.toggleCollapsible = function(id){ const el=document.getElementById(id); if(!el) return; const show = el.style.display==='none'||getComputedStyle(el).display==='none'; el.style.display= show?'block':'none'; const arrow= el.parentElement.querySelector('.collapsible-header .arrow'); if(arrow) arrow.textContent= show?'\u25b2':'\u25bc'; };

  window.loadUploadedImages = function(){ 
    console.log('Loading uploaded images...');
    const grid=document.getElementById('uploadedImagesList'); 
    if(!grid) {
      console.error('uploadedImagesList element not found');
      return;
    }
    grid.innerHTML='<div class="loading-message">\ud83d\udd04 Загрузка каталога изображений...</div>'; 
    
    console.log('Making request to /admin/theory/get-images/');
    fetch('/admin/theory/get-images/')
      .then(r=>{
        console.log('Response status:', r.status);
        return r.json();
      })
      .then(data=>{ 
        console.log('Images data received:', data);
        if(!data.success){ 
          grid.innerHTML='<div class="error">Ошибка: '+(data.error||'Неизвестно')+'</div>'; 
          return;
        } 
        if(data.count===0){ 
          grid.innerHTML='<div class="empty">Нет изображений</div>'; 
          return;
        } 
        grid.innerHTML = data.images.map(img=>'<div class="img-card">'+
          '<div class="img-thumb"><img src="'+img.url+'" alt="'+img.filename+'"></div>'+
          '<div class="img-meta" title="'+img.filename+'">'+img.filename+'</div>'+
          '<div class="img-size">'+img.size+'</div>'+
          '<input class="img-md" value="'+img.markdown+'" readonly />'+
          '<div class="img-actions">'+
            '<button type="button" class="btn-small" data-action="copy">\ud83d\udccb</button>'+ 
            '<button type="button" class="btn-small danger" data-action="delete" data-fn="'+img.filename+'">\ud83d\uddd1\ufe0f</button>'+
          '</div>'+
        '</div>').join(''); 
        console.log('Images grid updated with', data.count, 'images');
      })
      .catch(err=>{ 
        console.error('Fetch error:', err);
        grid.innerHTML='<div class="error">Fetch error: '+err+'</div>'; 
      }); 
  };

  document.addEventListener('click', function(e){ const btn=e.target.closest('button'); if(!btn) return; if(btn.dataset.action==='copy'){ const card=btn.closest('.img-card'); if(!card) return; const input=card.querySelector('.img-md'); if(!input) return; input.select(); document.execCommand('copy'); btn.textContent='\u2705'; setTimeout(()=>{btn.textContent='\ud83d\udccb';},1100); } else if(btn.dataset.action==='delete'){ const fn=btn.dataset.fn; if(!fn) return; if(!confirm('Удалить изображение '+fn+'?')) return; fetch('/admin/theory/delete-image/', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({filename:fn})})
      .then(r=>r.json())
      .then(data=>{ if(data.success) loadUploadedImages(); else alert('Ошибка удаления: '+(data.error||'Неизвестно')); })
      .catch(err=> alert('Fetch error: '+err)); } });

  (function initUpload(){ 
    const input=document.getElementById('imageUpload'); 
    const zone=document.querySelector('.upload-zone'); 
    if(!input||!zone) {
      console.error('Upload elements not found:', {input: !!input, zone: !!zone});
      return;
    }
    console.log('Upload zone initialized');
    
    zone.addEventListener('dragover', e=>{ e.preventDefault(); zone.classList.add('drag'); }); 
    zone.addEventListener('dragleave', ()=> zone.classList.remove('drag')); 
    zone.addEventListener('drop', e=>{ e.preventDefault(); zone.classList.remove('drag'); if(e.dataTransfer.files && e.dataTransfer.files[0]){ input.files=e.dataTransfer.files; uploadFile(input.files[0]); } }); 
    zone.addEventListener('click', ()=> input.click()); 
    input.addEventListener('change', ()=>{ if(input.files[0]) uploadFile(input.files[0]); }); 
  })();

  function uploadFile(file){ 
    console.log('Starting file upload:', file.name);
    const progress=document.getElementById('uploadProgress'); 
    const fill= progress?progress.querySelector('.progress-fill'):null; 
    const result=document.getElementById('uploadResult'); 
    const codeInput=document.getElementById('generatedCode'); 
    if(!file) return; 
    if(progress) progress.style.display='block'; 
    if(result) result.style.display='none'; 
    const formData=new FormData(); 
    formData.append('image', file); 
    
    console.log('Making upload request to /admin/theory/upload-image/');
    fetch('/admin/theory/upload-image/', {method:'POST', body:formData})
      .then(r=>{
        console.log('Upload response status:', r.status);
        return r.json();
      })
      .then(data=>{ 
        console.log('Upload response data:', data);
        if(data.success){ 
          if(fill) fill.style.width='100%'; 
          if(progress) progress.style.display='none'; 
          if(result) result.style.display='block'; 
          if(codeInput) codeInput.value='!['+(data.original_name||'Описание')+']('+data.url+')'; 
          loadUploadedImages(); 
          console.log('Upload successful!');
        } else { 
          console.error('Upload failed:', data.error);
          alert('Ошибка загрузки: '+(data.error||'Неизвестно')); 
          if(progress) progress.style.display='none'; 
        } 
      })
      .catch(err=>{ 
        console.error('Upload fetch error:', err);
        alert('Fetch error: '+err); 
        if(progress) progress.style.display='none'; 
      }); 
  }

  window.copyToClipboard = function(){ const input=document.getElementById('generatedCode'); if(!input) return; input.select(); document.execCommand('copy'); };

  document.addEventListener('DOMContentLoaded', function(){ 
    console.log('DOM Content Loaded - initializing...');
    ensureMathJax(function(){ 
      setupLivePreview(); 
      setTimeout(function(){ 
        console.log('Checking for uploadedImagesList element...');
        if(document.getElementById('uploadedImagesList')) {
          console.log('Found uploadedImagesList, loading images...');
          loadUploadedImages(); 
        } else {
          console.log('uploadedImagesList not found');
        }
      }, 500); 
    }); 
  });
})();