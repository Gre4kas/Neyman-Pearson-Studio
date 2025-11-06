// Admin JS для теории: MathJax, предпросмотр и загрузка изображений
(function () {

  // === Утилиты ===

  // Получение CSRF токена - улучшенная версия для Docker
  function getCSRFToken() {
    // Сначала пробуем получить из cookies
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='));
    
    if (cookieValue) {
      return cookieValue.split('=')[1];
    }
    
    // Если не найден в cookies, ищем в мета-теге
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta) {
      return csrfMeta.getAttribute('content');
    }
    
    // Если не найден в мета-теге, ищем в скрытом input
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (csrfInput) {
      return csrfInput.value;
    }
    
    console.warn('CSRF токен не найден');
    return null;
  }

  // Debounce функция
  function debounce(fn, wait) {
    let t;
    return function (...args) {
      clearTimeout(t);
      t = setTimeout(() => fn.apply(this, args), wait);
    };
  }

  // === MathJax настройка ===

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
    if (window.MathJax && window.MathJax.typesetPromise) {
      callback();
      return;
    }

    const existing = document.getElementById('mathjax-script');
    if (!existing) {
      const script = document.createElement('script');
      script.id = 'mathjax-script';
      script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js';
      script.async = true;
      script.onload = () => callback();
      script.onerror = () => console.error('MathJax load error');
      document.head.appendChild(script);
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

  // === Предпросмотр статей ===

  function setupLivePreview() {
    const textarea = document.querySelector('textarea[name="content_md"]');
    const previewContainer = document.querySelector('.preview-content');
    if (!textarea || !previewContainer) return;

    let controller = null;
    const loadingClass = 'is-loading';

    function setLoading(isLoading) {
      if (isLoading) {
        previewContainer.classList.add(loadingClass);
        if (!previewContainer.querySelector('.preview-loading')) {
          const loader = document.createElement('div');
          loader.className = 'preview-loading';
          loader.style.cssText = 'position:absolute; top:10px; right:14px; font-size:11px; color:#555;';
          loader.textContent = 'Обновление...';
          previewContainer.appendChild(loader);
        }
      } else {
        previewContainer.classList.remove(loadingClass);
        const loader = previewContainer.querySelector('.preview-loading');
        if (loader) loader.remove();
      }
    }

    function performPreview(content) {
      if (controller) controller.abort();
      controller = new AbortController();
      setLoading(true);

      const csrfToken = getCSRFToken();
      if (!csrfToken) {
        console.error('CSRF токен не найден');
        previewContainer.innerHTML = `<div class="error-message">❌ Ошибка: CSRF токен не найден</div>`;
        setLoading(false);
        return;
      }

      fetch(window.location.origin + '/theory/admin/preview/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ content }),
        signal: controller.signal
      })
        .then(response => {
          // Проверяем статус ответа
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }
          
          // Проверяем Content-Type
          const contentType = response.headers.get('content-type');
          if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Ответ сервера не является JSON');
          }
          
          return response.json();
        })
        .then(data => {
          if (data.success) {
            previewContainer.innerHTML = data.html;
            ensureMathJax(() => {
              const articleContent = document.getElementById('article-content');
              typesetTarget(articleContent);
              setTimeout(() => typesetTarget(articleContent), 400);
              setTimeout(() => typesetTarget(articleContent), 1200);
            });
          } else {
            console.error('Preview error:', data.error);
            previewContainer.innerHTML = `<div class="error-message">❌ Ошибка: ${data.error || 'Неизвестная ошибка'}</div>`;
          }
        })
        .catch(err => {
          if (err.name !== 'AbortError') {
            console.error('Preview fetch error:', err);
            previewContainer.innerHTML = `<div class="error-message">❌ Ошибка загрузки предпросмотра: ${err.message}</div>`;
          }
        })
        .finally(() => setLoading(false));
    }

    const debouncedPreview = debounce(() => performPreview(textarea.value), 450);
    textarea.addEventListener('input', debouncedPreview);

    // Начальный предпросмотр
    performPreview(textarea.value);
  }

  // === Функции интерфейса ===

  window.toggleCollapsible = function (id) {
    const element = document.getElementById(id);
    if (!element) return;

    const isHidden = element.style.display === 'none' || getComputedStyle(element).display === 'none';
    element.style.display = isHidden ? 'block' : 'none';

    const arrow = element.parentElement.querySelector('.collapsible-header .arrow');
    if (arrow) {
      arrow.textContent = isHidden ? '▲' : '▼';
    }
  };

  // === Управление изображениями ===

  window.loadUploadedImages = function () {
    const grid = document.getElementById('uploadedImagesList');
    if (!grid) return;

    grid.innerHTML = '<div class="loading-message">🔄 Загрузка каталога изображений...</div>';

    const csrfToken = getCSRFToken();
    if (!csrfToken) {
      grid.innerHTML = '<div class="error">❌ Ошибка: CSRF токен не найден</div>';
      return;
    }

    fetch('/theory/admin/get-images/', {
      method: 'GET',
      headers: {
        'X-CSRFToken': csrfToken
      }
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
          throw new Error('Ответ сервера не является JSON');
        }
        
        return response.json();
      })
      .then(data => {
        if (!data.success) {
          grid.innerHTML = `<div class="error">Ошибка: ${data.error || 'Неизвестная ошибка'}</div>`;
          return;
        }

        if (data.count === 0) {
          grid.innerHTML = '<div class="empty">📷 Нет загруженных изображений</div>';
          return;
        }

        grid.innerHTML = data.images.map(img => `
        <div class="img-card">
          <div class="img-thumb">
            <img src="${img.url}" alt="${img.filename}" loading="lazy">
          </div>
          <div class="img-meta" title="${img.filename}">
            <div class="filename">${img.filename}</div>
            <div class="created">${img.created}</div>
          </div>
          <div class="img-size">${img.size}</div>
          <input class="img-md" value="${img.markdown}" readonly />
          <div class="img-actions">
            <button type="button" class="btn-small btn-copy" data-action="copy" title="Копировать markdown">
              📋
            </button>
            <button type="button" class="btn-small btn-delete" data-action="delete" data-filename="${img.filename}" title="Удалить изображение">
              🗑️
            </button>
          </div>
        </div>
      `).join('');
      })
      .catch(error => {
        console.error('Ошибка загрузки изображений:', error);
        grid.innerHTML = `<div class="error">Ошибка загрузки: ${error.message}</div>`;
      });
  };

  // Обработчик кликов для кнопок изображений
  document.addEventListener('click', function (event) {
    const button = event.target.closest('button');
    if (!button) return;

    const action = button.dataset.action;

    if (action === 'copy') {
      handleCopyMarkdown(button);
    } else if (action === 'delete') {
      handleDeleteImage(button);
    }
  });

  function handleCopyMarkdown(button) {
    const card = button.closest('.img-card');
    if (!card) return;

    const input = card.querySelector('.img-md');
    if (!input) return;

    // Используем современный API если доступен
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(input.value)
        .then(() => {
          showButtonFeedback(button, '✅');
        })
        .catch(err => {
          console.error('Ошибка копирования:', err);
          fallbackCopyTextToClipboard(input, button);
        });
    } else {
      fallbackCopyTextToClipboard(input, button);
    }
  }

  function fallbackCopyTextToClipboard(input, button) {
    input.select();
    try {
      const successful = document.execCommand('copy');
      if (successful) {
        showButtonFeedback(button, '✅');
      } else {
        showButtonFeedback(button, '❌');
      }
    } catch (err) {
      console.error('Fallback копирование не удалось:', err);
      showButtonFeedback(button, '❌');
    }
  }

  function showButtonFeedback(button, icon) {
    const originalText = button.textContent;
    button.textContent = icon;
    button.disabled = true;

    setTimeout(() => {
      button.textContent = originalText;
      button.disabled = false;
    }, 1500);
  }

  function handleDeleteImage(button) {
    const filename = button.dataset.filename;
    if (!filename) return;

    if (!confirm(`Удалить изображение "${filename}"?\n\nЭто действие нельзя отменить.`)) {
      return;
    }

    const csrfToken = getCSRFToken();
    if (!csrfToken) {
      alert('❌ Ошибка: CSRF токен не найден. Попробуйте перезагрузить страницу.');
      return;
    }

    button.disabled = true;
    button.textContent = '⏳';

    fetch('/theory/admin/delete-image/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({ filename: filename })
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
          throw new Error('Ответ сервера не является JSON');
        }
        
        return response.json();
      })
      .then(data => {
        if (data.success) {
          // Перезагружаем список изображений
          loadUploadedImages();
        } else {
          alert(`Ошибка удаления: ${data.error || 'Неизвестная ошибка'}`);
          button.disabled = false;
          button.textContent = '🗑️';
        }
      })
      .catch(error => {
        console.error('Ошибка удаления изображения:', error);
        alert(`Ошибка удаления: ${error.message}`);
        button.disabled = false;
        button.textContent = '🗑️';
      });
  }

  // === Загрузка изображений ===

  let isUploading = false; // Флаг для предотвращения двойного срабатывания
  let isInitialized = false; // Флаг для предотвращения повторной инициализации

  function initializeImageUpload() {
    if (isInitialized) {
      console.log('Загрузка изображений уже инициализирована, пропускаем');
      return;
    }

    const fileInput = document.getElementById('imageUpload');
    const dropZone = document.querySelector('.upload-zone');

    if (!fileInput || !dropZone) {
      console.log('Элементы для загрузки изображений не найдены');
      return;
    }

    console.log('Инициализация загрузки изображений...');
    isInitialized = true;

    // Делаем файловый инпут более доступным для Docker
    fileInput.style.position = 'absolute';
    fileInput.style.opacity = '0';
    fileInput.style.width = '100%';
    fileInput.style.height = '100%';
    fileInput.style.cursor = 'pointer';
    fileInput.style.pointerEvents = 'auto';
    fileInput.style.zIndex = '1';

    // Делаем drop zone относительным для правильного позиционирования input
    dropZone.style.position = 'relative';

    // Drag & Drop обработчики
    dropZone.addEventListener('dragover', handleDragOver, false);
    dropZone.addEventListener('dragleave', handleDragLeave, false);
    dropZone.addEventListener('drop', handleDrop, false);

    // Click обработчик для drop zone
    dropZone.addEventListener('click', (event) => {
      console.log('Click на upload-zone, цель:', event.target.tagName, 'isUploading:', isUploading);
      
      // Если клик был на самом файловом input, не вмешиваемся
      if (event.target === fileInput) {
        console.log('Клик на файловом input, пропускаем');
        return;
      }
      
      // Предотвращаем всплытие для других элементов
      event.preventDefault();
      event.stopPropagation();
      
      if (!isUploading) {
        console.log('Открываем диалог выбора файла через клик');
        
        // Используем простой и надежный способ
        fileInput.click();
      } else {
        console.log('Загрузка уже в процессе, игнорируем клик');
      }
    });

    // File input change обработчик  
    fileInput.addEventListener('change', (event) => {
      console.log('File input change событие, файлов выбрано:', event.target.files.length);
      
      if (isUploading) {
        console.log('Загрузка уже в процессе, игнорируем изменение файла');
        return;
      }
      
      const file = event.target.files[0];
      if (file) {
        console.log('Файл выбран, начинаем загрузку:', file.name);
        uploadFile(file);
      } else {
        console.log('Файл не выбран');
      }
    });
  }

  function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    event.dataTransfer.dropEffect = 'copy';
    event.currentTarget.classList.add('drag');
  }

  function handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    // Проверяем, что мы действительно покинули зону, а не перешли на дочерний элемент
    if (!event.currentTarget.contains(event.relatedTarget)) {
      event.currentTarget.classList.remove('drag');
    }
  }

  function handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    event.currentTarget.classList.remove('drag');

    console.log('Drop событие произошло');
    
    const files = event.dataTransfer?.files;
    if (files && files.length > 0 && !isUploading) {
      console.log('Файл перетащен:', files[0].name);
      uploadFile(files[0]);
    } else if (isUploading) {
      console.log('Загрузка уже в процессе, игнорируем drop');
    } else {
      console.log('Файлы не найдены в drop событии');
    }
  }

  function uploadFile(file) {
    console.log('Начинаю загрузку файла:', file.name, 'Размер:', file.size, 'Тип:', file.type);

    // Проверяем, не идет ли уже загрузка
    if (isUploading) {
      console.warn('Загрузка уже в процессе, пропускаем повторный вызов');
      return;
    }

    // Устанавливаем флаг загрузки
    isUploading = true;
    console.log('Флаг isUploading установлен в true');

    // Валидация файла
    const validation = validateImageFile(file);
    if (!validation.valid) {
      alert(`Ошибка: ${validation.error}`);
      resetUploadState();
      return;
    }

    // Элементы UI
    const progressContainer = document.getElementById('uploadProgress');
    const progressFill = progressContainer ? progressContainer.querySelector('.progress-fill') : null;
    const resultContainer = document.getElementById('uploadResult');
    const codeInput = document.getElementById('generatedCode');

    // Показываем прогресс
    if (progressContainer) progressContainer.style.display = 'block';
    if (resultContainer) resultContainer.style.display = 'none';
    if (progressFill) progressFill.style.width = '0%';

    // Создаем FormData
    const formData = new FormData();
    formData.append('image', file);

    // Проверяем CSRF токен
    const csrfToken = getCSRFToken();
    if (!csrfToken) {
      console.error('CSRF токен не найден для загрузки');
      alert('❌ Ошибка: CSRF токен не найден. Попробуйте перезагрузить страницу.');
      resetUploadState();
      return;
    }

    // Отправляем запрос
    fetch('/theory/admin/upload-image/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken
      },
      body: formData
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
          throw new Error('Ответ сервера не является JSON');
        }
        
        return response.json();
      })
      .then(data => {
        console.log('Ответ сервера:', data);

        if (data.success) {
          // Анимируем прогресс до 100%
          if (progressFill) {
            progressFill.style.width = '100%';
          }

          setTimeout(() => {
            // Скрываем прогресс и показываем результат
            if (progressContainer) progressContainer.style.display = 'none';
            if (resultContainer) resultContainer.style.display = 'block';

            // Заполняем код для копирования
            if (codeInput && data.markdown) {
              codeInput.value = data.markdown;
            }

            // Перезагружаем список изображений
            loadUploadedImages();

            // Сбрасываем состояние загрузки
            resetUploadState();

          }, 500);

        } else {
          throw new Error(data.error || 'Неизвестная ошибка сервера');
        }
      })
      .catch(error => {
        console.error('Ошибка загрузки:', error);
        alert(`Ошибка загрузки: ${error.message}`);

        // Скрываем прогресс
        if (progressContainer) progressContainer.style.display = 'none';

        // Сбрасываем состояние при ошибке
        resetUploadState();
      });
  }

  function resetUploadState() {
    console.log('Сбрасываем состояние загрузки...');
    
    // Сбрасываем флаг загрузки
    isUploading = false;
    
    // Очищаем input асинхронно для предотвращения конфликтов
    setTimeout(() => {
      const fileInput = document.getElementById('imageUpload');
      if (fileInput) {
        fileInput.value = '';
        console.log('Input очищен');
      }
    }, 100);
    
    // Скрываем прогресс
    const progressContainer = document.getElementById('uploadProgress');
    if (progressContainer) {
      progressContainer.style.display = 'none';
    }
    
    console.log('Состояние загрузки успешно сброшено');
  }

  function validateImageFile(file) {
    // Проверяем, что файл выбран
    if (!file) {
      return { valid: false, error: 'Файл не выбран' };
    }

    // Проверяем размер (максимум 10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      return { valid: false, error: `Файл слишком большой (${(file.size / (1024 * 1024)).toFixed(1)} МБ). Максимум 10 МБ.` };
    }

    // Проверяем тип файла
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml'];
    if (!allowedTypes.includes(file.type)) {
      return { valid: false, error: 'Недопустимый тип файла. Разрешены: JPG, PNG, GIF, WebP, SVG' };
    }

    return { valid: true };
  }

  window.copyToClipboard = function () {
    const input = document.getElementById('generatedCode');
    if (!input) return;

    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(input.value)
        .then(() => {
          showCopyFeedback(true);
        })
        .catch(err => {
          console.error('Ошибка копирования:', err);
          fallbackCopy(input);
        });
    } else {
      fallbackCopy(input);
    }
  };

  function fallbackCopy(input) {
    input.select();
    try {
      const successful = document.execCommand('copy');
      showCopyFeedback(successful);
    } catch (err) {
      console.error('Fallback копирование не удалось:', err);
      showCopyFeedback(false);
    }
  }

  function showCopyFeedback(success) {
    const button = document.querySelector('.copy-btn');
    if (!button) return;

    const originalText = button.textContent;
    button.textContent = success ? '✅ Скопировано!' : '❌ Ошибка';

    setTimeout(() => {
      button.textContent = originalText;
    }, 2000);
  }

  // === Инициализация ===

  function tryInitializeUpload(attempt = 1, maxAttempts = 10) {
    console.log(`Попытка инициализации загрузки изображений: ${attempt}/${maxAttempts}`);
    
    const uploadZone = document.querySelector('.upload-zone');
    const fileInput = document.getElementById('imageUpload');
    
    if (uploadZone && fileInput) {
      console.log('Элементы найдены, инициализируем загрузку');
      initializeImageUpload();
      return true;
    } else {
      console.log(`Элементы не найдены (uploadZone: ${!!uploadZone}, fileInput: ${!!fileInput})`);
      if (attempt < maxAttempts) {
        setTimeout(() => tryInitializeUpload(attempt + 1, maxAttempts), 300);
      } else {
        console.error('Не удалось найти элементы загрузки после максимального количества попыток');
      }
      return false;
    }
  }

  function tryLoadImages(attempt = 1, maxAttempts = 5) {
    const imagesList = document.getElementById('uploadedImagesList');
    if (imagesList) {
      console.log('Загружаем список изображений');
      loadUploadedImages();
    } else if (attempt < maxAttempts) {
      setTimeout(() => tryLoadImages(attempt + 1, maxAttempts), 500);
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    console.log('Инициализация Theory Admin JS');

    ensureMathJax(function () {
      setupLivePreview();

      // Инициализируем загрузку с повторными попытками
      setTimeout(() => tryInitializeUpload(), 100);
      
      // Загружаем изображения с повторными попытками
      setTimeout(() => tryLoadImages(), 500);
    });
  });

  // Дополнительная инициализация для случаев, когда DOM уже загружен
  if (document.readyState === 'loading') {
    // DOM еще загружается, обработчик уже установлен выше
  } else {
    // DOM уже загружен, запускаем инициализацию сразу
    console.log('DOM уже готов, запускаем инициализацию немедленно');
    ensureMathJax(function () {
      setupLivePreview();
      setTimeout(() => tryInitializeUpload(), 50);
      setTimeout(() => tryLoadImages(), 300);
    });
  }

})();