// Refactored admin JS: single IIFE, debounced preview, AbortController, improved image handling.
(function() {
  console.log('Theory Admin JS loaded - v2.1 with enhanced debugging');
  
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

  window.toggleCollapsible = function(id){ 
    console.log('Toggling collapsible:', id);
    const el=document.getElementById(id); 
    if(!el) {
      console.error('Collapsible element not found:', id);
      return;
    }
    const show = el.style.display==='none'||getComputedStyle(el).display==='none'; 
    el.style.display= show?'block':'none'; 
    const arrow= el.parentElement.querySelector('.collapsible-header .arrow'); 
    if(arrow) arrow.textContent= show?'\u25b2':'\u25bc';
    console.log('Collapsible toggled:', id, 'visible:', show);
  };

  window.loadUploadedImages = function(){ 
    console.log('=== Starting loadUploadedImages ===');
    const grid=document.getElementById('uploadedImagesList'); 
    if(!grid) {
      console.error('ERROR: uploadedImagesList element not found in DOM');
      console.log('Available elements with id containing "upload":', 
        Array.from(document.querySelectorAll('[id*="upload"]')).map(el => ({id: el.id, tagName: el.tagName})));
      return;
    }
    console.log('Found uploadedImagesList element:', grid);
    grid.innerHTML='<div class="loading-message">\ud83d\udd04 Загрузка каталога изображений...</div>'; 
    
    console.log('Making fetch request to: /admin/theory/get-images/');
    fetch('/admin/theory/get-images/')
      .then(r=>{
        console.log('Fetch response received. Status:', r.status, 'OK:', r.ok);
        if (!r.ok) {
          throw new Error(`HTTP ${r.status}: ${r.statusText}`);
        }
        return r.json();
      })
      .then(data=>{ 
        console.log('=== Server Response Data ===');
        console.log('Full response object:', data);
        console.log('Success:', data.success);
        console.log('Count:', data.count);
        console.log('Images array length:', data.images ? data.images.length : 'N/A');
        
        if(!data.success){ 
          console.error('Server returned success=false. Error:', data.error);
          grid.innerHTML='<div class="error">Ошибка: '+(data.error||'Неизвестно')+'</div>'; 
          return;
        } 
        
        if(data.count===0){ 
          console.log('No images found (count=0)');
          grid.innerHTML='<div class="empty">Нет изображений</div>'; 
          return;
        } 
        
        console.log('=== Processing Images ===');
        const htmlParts = data.images.map((img, index) => {
          console.log(`Image ${index + 1}:`, {
            filename: img.filename,
            url: img.url,
            size: img.size,
            markdown: img.markdown
          });
          
          return '<div class="img-card">'+
            '<div class="img-thumb"><img src="'+img.url+'" alt="'+img.filename+'" onload="console.log(\'Image loaded: '+img.filename+'\')" onerror="console.error(\'Image failed to load: '+img.filename+'\');"></div>'+
            '<div class="img-meta" title="'+img.filename+'">'+img.filename+'</div>'+
            '<div class="img-size">'+img.size+'</div>'+
            '<input class="img-md" value="'+img.markdown+'" readonly />'+
            '<div class="img-actions">'+
              '<button type="button" class="btn-small" data-action="copy">\ud83d\udccb</button>'+ 
              '<button type="button" class="btn-small danger" data-action="delete" data-fn="'+img.filename+'">\ud83d\uddd1\ufe0f</button>'+
            '</div>'+
          '</div>';
        });
        
        const finalHTML = htmlParts.join('');
        console.log('Generated HTML length:', finalHTML.length);
        console.log('Setting grid innerHTML...');
        
        grid.innerHTML = finalHTML;
        
        console.log('=== Grid Update Complete ===');
        console.log('Grid children count:', grid.children.length);
        console.log('Grid innerHTML length:', grid.innerHTML.length);
        console.log('First few characters of innerHTML:', grid.innerHTML.substring(0, 200));
        
        // Verify images are actually in the DOM
        const imgCards = grid.querySelectorAll('.img-card');
        console.log('Found .img-card elements:', imgCards.length);
        imgCards.forEach((card, idx) => {
          const img = card.querySelector('img');
          const meta = card.querySelector('.img-meta');
          console.log(`Card ${idx}:`, {
            hasImg: !!img,
            imgSrc: img ? img.src : 'N/A',
            hasText: !!meta,
            text: meta ? meta.textContent : 'N/A'
          });
        });
      })
      .catch(err=>{ 
        console.error('=== Fetch Error ===');
        console.error('Error object:', err);
        console.error('Error message:', err.message);
        console.error('Error stack:', err.stack);
        grid.innerHTML='<div class="error">Fetch error: '+err.message+'</div>'; 
      }); 
      
    console.log('=== loadUploadedImages request sent ===');
  };

  document.addEventListener('click', function(e){ 
    const btn=e.target.closest('button'); 
    if(!btn) return; 
    
    if(btn.dataset.action==='copy'){ 
      console.log('Copy button clicked');
      const card=btn.closest('.img-card'); 
      if(!card) return; 
      const input=card.querySelector('.img-md'); 
      if(!input) return; 
      input.select(); 
      document.execCommand('copy'); 
      btn.textContent='\u2705'; 
      setTimeout(()=>{btn.textContent='\ud83d\udccb';},1100); 
    } else if(btn.dataset.action==='delete'){ 
      console.log('Delete button clicked');
      const fn=btn.dataset.fn; 
      if(!fn) return; 
      if(!confirm('Удалить изображение '+fn+'?')) return; 
      
      console.log('Deleting image:', fn);
      fetch('/admin/theory/delete-image/', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({filename:fn})})
        .then(r=>r.json())
        .then(data=>{ 
          console.log('Delete response:', data);
          if(data.success) {
            console.log('Delete successful, reloading images');
            loadUploadedImages(); 
          } else {
            alert('Ошибка удаления: '+(data.error||'Неизвестно')); 
          }
        })
        .catch(err=> {
          console.error('Delete error:', err);
          alert('Fetch error: '+err);
        }); 
    } 
  });

  (function initUpload(){ 
    console.log('=== Initializing Upload ===');
    const input=document.getElementById('imageUpload'); 
    const zone=document.querySelector('.upload-zone'); 
    
    console.log('Upload elements found:', {
      input: !!input,
      zone: !!zone,
      inputId: input ? input.id : 'N/A',
      zoneClass: zone ? zone.className : 'N/A'
    });
    
    if(!input||!zone) {
      console.error('Upload elements missing! Cannot initialize upload functionality.');
      return;
    }
    
    console.log('Setting up upload event listeners...');
    
    zone.addEventListener('dragover', e=>{ e.preventDefault(); zone.classList.add('drag'); }); 
    zone.addEventListener('dragleave', ()=> zone.classList.remove('drag')); 
    zone.addEventListener('drop', e=>{ 
      console.log('File dropped');
      e.preventDefault(); 
      zone.classList.remove('drag'); 
      if(e.dataTransfer.files && e.dataTransfer.files[0]){ 
        input.files=e.dataTransfer.files; 
        uploadFile(e.dataTransfer.files[0]); 
      } 
    }); 
    zone.addEventListener('click', ()=> {
      console.log('Upload zone clicked, opening file dialog');
      input.click();
    }); 
    input.addEventListener('change', ()=>{ 
      console.log('File input changed');
      if(input.files[0]) uploadFile(input.files[0]); 
    }); 
    
    console.log('Upload initialization complete');
  })();

  function uploadFile(file){ 
    console.log('=== Starting File Upload ===');
    console.log('File details:', {
      name: file.name,
      size: file.size,
      type: file.type,
      lastModified: file.lastModified
    });
    
    const progress=document.getElementById('uploadProgress'); 
    const fill= progress?progress.querySelector('.progress-fill'):null; 
    const result=document.getElementById('uploadResult'); 
    const codeInput=document.getElementById('generatedCode'); 
    
    console.log('Upload UI elements:', {
      progress: !!progress,
      fill: !!fill,
      result: !!result,
      codeInput: !!codeInput
    });
    
    if(!file) {
      console.error('No file provided to uploadFile function');
      return;
    }
    
    if(progress) progress.style.display='block'; 
    if(result) result.style.display='none'; 
    
    const formData=new FormData(); 
    formData.append('image', file); 
    
    console.log('Making POST request to /admin/theory/upload-image/');
    console.log('FormData created with image field');
    
    fetch('/admin/theory/upload-image/', {method:'POST', body:formData})
      .then(r=>{
        console.log('Upload response received:', {
          status: r.status,
          statusText: r.statusText,
          ok: r.ok,
          headers: Object.fromEntries(r.headers.entries())
        });
        
        if (!r.ok) {
          throw new Error(`HTTP ${r.status}: ${r.statusText}`);
        }
        return r.json();
      })
      .then(data=>{ 
        console.log('=== Upload Response Data ===');
        console.log('Full response:', data);
        
        if(data.success){ 
          console.log('Upload successful!');
          console.log('File URL:', data.url);
          console.log('Original name:', data.original_name);
          
          if(fill) {
            fill.style.width='100%';
            console.log('Progress bar updated to 100%');
          }
          if(progress) {
            progress.style.display='none';
            console.log('Progress bar hidden');
          }
          if(result) {
            result.style.display='block';
            console.log('Result section shown');
          }
          if(codeInput) {
            const markdownCode = '!['+(data.original_name||'Описание')+']('+data.url+')';
            codeInput.value=markdownCode;
            console.log('Generated markdown code:', markdownCode);
          }
          
          console.log('Calling loadUploadedImages to refresh the list...');
          loadUploadedImages(); 
        } else { 
          console.error('Upload failed - server returned success=false');
          console.error('Server error:', data.error);
          alert('Ошибка загрузки: '+(data.error||'Неизвестно')); 
          if(progress) progress.style.display='none'; 
        } 
      })
      .catch(err=>{ 
        console.error('=== Upload Fetch Error ===');
        console.error('Error object:', err);
        console.error('Error message:', err.message);
        console.error('Error stack:', err.stack);
        alert('Fetch error: '+err.message); 
        if(progress) progress.style.display='none'; 
      }); 
      
    console.log('=== Upload request sent ===');
  }

  window.copyToClipboard = function(){ 
    const input=document.getElementById('generatedCode'); 
    if(!input) return; 
    input.select(); 
    document.execCommand('copy');
    console.log('Markdown code copied to clipboard:', input.value);
  };

  document.addEventListener('DOMContentLoaded', function(){ 
    console.log('=== DOM Content Loaded ===');
    console.log('Document ready state:', document.readyState);
    
    ensureMathJax(function(){ 
      console.log('MathJax ready, setting up live preview...');
      setupLivePreview(); 
      
      setTimeout(function(){ 
        console.log('=== Delayed Initialization (500ms) ===');
        console.log('Looking for uploadedImagesList element...');
        
        const imagesList = document.getElementById('uploadedImagesList');
        if(imagesList) {
          console.log('Found uploadedImagesList element!');
          console.log('Element details:', {
            id: imagesList.id,
            tagName: imagesList.tagName,
            className: imagesList.className,
            innerHTML: imagesList.innerHTML.substring(0, 100) + '...'
          });
          console.log('Calling loadUploadedImages...');
          loadUploadedImages(); 
        } else {
          console.error('uploadedImagesList element not found!');
          console.log('All elements with id attribute:', 
            Array.from(document.querySelectorAll('[id]')).map(el => el.id));
          console.log('Elements containing "image" in class or id:', 
            Array.from(document.querySelectorAll('[id*="image"], [class*="image"]')).map(el => ({
              id: el.id,
              className: el.className,
              tagName: el.tagName
            })));
        }
      }, 500); 
    }); 
  });
  
  console.log('=== Theory Admin JS initialization complete ===');
})();