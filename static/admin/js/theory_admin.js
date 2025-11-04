// Admin JS для теории: MathJax, предпросмотр и загрузка изображений
(function () {

  // === Утилиты ===

  // Получение CSRF токена
  function getCSRFToken() {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='));
    return cookieValue ? cookieValue.split('=')[1] : null;
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

      fetch(window.location.origin + '/theory/admin/preview/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ content }),
        signal: controller.signal
      })
        .then(response => response.json())
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
          }
        })
        .catch(err => {
          if (err.name !== 'AbortError') {
            console.error('Preview fetch error:', err);
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

    fetch('/theory/admin/get-images/', {
      method: 'GET',
      headers: {
        'X-CSRFToken': getCSRFToken()
      }
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
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

    button.disabled = true;
    button.textContent = '⏳';

    fetch('/theory/admin/delete-image/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify({ filename: filename })
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
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

    // Делаем файловый инпут более доступным
    fileInput.style.pointerEvents = 'auto';

    // Drag & Drop обработчики
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);

    // Click обработчик
    dropZone.addEventListener('click', (event) => {
      console.log('Click на upload-zone, isUploading:', isUploading);
      
      if (!isUploading) {
        console.log('Открываем диалог выбора файла');
        
        // Используем несколько способов для надежности
        try {
          // Способ 1: прямой клик
          fileInput.click();
        } catch (e) {
          console.warn('Прямой клик не сработал, пробуем альтернативный способ:', e);
          // Способ 2: создаем событие клика
          try {
            const clickEvent = new MouseEvent('click', {
              view: window,
              bubbles: true,
              cancelable: true
            });
            fileInput.dispatchEvent(clickEvent);
          } catch (e2) {
            console.error('Все способы вызова диалога не сработали:', e2);
          }
        }
      } else {
        console.log('Загрузка уже в процессе, игнорируем клик');
        event.preventDefault();
        event.stopPropagation();
      }
    });

    // File input change обработчик  
    fileInput.addEventListener('change', (event) => {
      console.log('File input change событие, файлов выбрано:', event.target.files.length);
      const file = event.target.files[0];
      if (file && !isUploading) {
        console.log('Файл выбран, начинаем загрузку:', file.name);
        uploadFile(file);
      } else if (file && isUploading) {
        console.log('Файл выбран, но загрузка уже в процессе');
      } else {
        console.log('Файл не выбран');
      }
    });
  }

  function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('drag');
  }

  function handleDragLeave(event) {
    event.currentTarget.classList.remove('drag');
  }

  function handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    event.currentTarget.classList.remove('drag');

    const files = event.dataTransfer.files;
    if (files && files[0] && !isUploading) {
      // Не устанавливаем fileInput.files, чтобы избежать двойного срабатывания
      // Сразу загружаем файл
      uploadFile(files[0]);
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
      isUploading = false; // Сбрасываем флаг при ошибке
      console.log('Ошибка валидации, флаг isUploading сброшен');
      
      // Очищаем input при ошибке валидации
      const fileInputEl = document.getElementById('imageUpload');
      if (fileInputEl) fileInputEl.value = '';
      
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

    // Отправляем запрос
    fetch('/theory/admin/upload-image/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCSRFToken()
      },
      body: formData
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
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

            // Сбрасываем флаг загрузки
            isUploading = false;
            console.log('Загрузка завершена, флаг isUploading сброшен');

            // Очищаем input после завершения операции
            const fileInput = document.getElementById('imageUpload');
            if (fileInput) fileInput.value = '';

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

        // Сбрасываем флаг загрузки при ошибке
        isUploading = false;
        console.log('Ошибка загрузки, флаг isUploading сброшен');

        // Очищаем input при ошибке
        const fileInput = document.getElementById('imageUpload');
        if (fileInput) fileInput.value = '';
      });
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

  document.addEventListener('DOMContentLoaded', function () {
    console.log('Инициализация Theory Admin JS');

    ensureMathJax(function () {
      setupLivePreview();

      // Проверяем с задержкой, что элементы загрузки появились в DOM
      setTimeout(function () {
        console.log('Поиск элементов для инициализации загрузки изображений...');
        const uploadZone = document.querySelector('.upload-zone');
        const fileInput = document.getElementById('imageUpload');
        console.log('Upload zone найден:', !!uploadZone);
        console.log('File input найден:', !!fileInput);

        initializeImageUpload();
      }, 200);

      // Загружаем изображения с небольшой задержкой
      setTimeout(function () {
        if (document.getElementById('uploadedImagesList')) {
          loadUploadedImages();
        }
      }, 700);
    });
  });

})();