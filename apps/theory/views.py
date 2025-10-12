from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage
from django.conf import settings
import json
import os
import uuid
from .models import Article

def article_list_view(request: HttpRequest) -> HttpResponse:
    articles = Article.objects.all()
    context = {
        'articles': articles
    }
    return render(request, 'theory/article_list.html', context)

def article_detail_view(request: HttpRequest, slug: str) -> HttpResponse:
    article = get_object_or_404(Article, slug=slug)
    context = {
        'article': article
    }
    return render(request, 'theory/article_detail.html', context)

@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def admin_preview_view(request: HttpRequest) -> JsonResponse:
    """AJAX эндпоинт для предпросмотра статей в админке - с MathJax рендерингом"""
    try:
        data = json.loads(request.body)
        content = data.get('content', '')
        
        if not content:
            return JsonResponse({
                'success': True,
                'html': '<div style="color: #666; font-style: italic; text-align: center; padding: 20px;">📝 Начните печатать в редакторе, чтобы увидеть предпросмотр...</div>'
            })
        
        # Обработка контента - убираем опасные теги и элементы CKEditor
        import re
        
        # Убираем опасные теги
        processed_content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
        processed_content = re.sub(r'<iframe[^>]*>.*?</iframe>', '', processed_content, flags=re.IGNORECASE | re.DOTALL)
        
        # Убираем все служебные элементы CKEditor
        processed_content = re.sub(r'<div[^>]*class="[^"]*ck-widget__type-around[^"]*"[^>]*>.*?</div>', '', processed_content, flags=re.IGNORECASE | re.DOTALL)
        processed_content = re.sub(r'<div[^>]*ck-widget__type-around[^>]*>.*?</div>', '', processed_content, flags=re.IGNORECASE | re.DOTALL)
        processed_content = re.sub(r'<div[^>]*ck-tooltip[^>]*>.*?</div>', '', processed_content, flags=re.IGNORECASE | re.DOTALL)
        processed_content = re.sub(r'<div[^>]*ck-balloon-panel[^>]*>.*?</div>', '', processed_content, flags=re.IGNORECASE | re.DOTALL)
        processed_content = re.sub(r'<button[^>]*ck-widget__type-around__button[^>]*>.*?</button>', '', processed_content, flags=re.IGNORECASE | re.DOTALL)
        
        # Убираем пустые параграфы
        processed_content = re.sub(r'<p[^>]*>&nbsp;</p>', '', processed_content)
        processed_content = re.sub(r'<p[^>]*>\s*</p>', '', processed_content)
        processed_content = re.sub(r'<p[^>]*>(\s|&nbsp;)*</p>', '', processed_content)
        
        # Нормализуем структуру изображений - сохраняем классы стилей
        processed_content = re.sub(
            r'<figure[^>]*class="([^"]*image[^"]*)"([^>]*)>', 
            lambda m: f'<figure class="{m.group(1).strip()}"{m.group(2)}>', 
            processed_content, 
            flags=re.IGNORECASE
        )
        
        # Нормализуем структуру таблиц - сохраняем классы стилей
        processed_content = re.sub(
            r'<figure[^>]*class="([^"]*table[^"]*)"([^>]*)>', 
            lambda m: f'<figure class="{m.group(1).strip()}"{m.group(2)}>', 
            processed_content, 
            flags=re.IGNORECASE
        )
        
        # Убираем лишние пробелы между тегами и нормализуем
        processed_content = re.sub(r'>\s+<', '><', processed_content)
        processed_content = re.sub(r'\n\s*\n\s*\n', '\n\n', processed_content)
        processed_content = processed_content.strip()
        
        # НЕ заменяем LaTeX формулы - оставляем их для MathJax
        # Формулы $...$ и $$...$$ остаются как есть, чтобы MathJax их обработал
        
        return JsonResponse({
            'success': True,
            'html': processed_content,
            'trigger_mathjax': True  # Сигнал для JavaScript что нужно запустить MathJax
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def upload_image_view(request: HttpRequest) -> JsonResponse:
    """Загрузка изображений для статей"""
    try:
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Файл не выбран'
            })
        
        image_file = request.FILES['image']
        
        # Проверяем тип файла
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml']
        if image_file.content_type not in allowed_types:
            return JsonResponse({
                'success': False,
                'error': 'Недопустимый тип файла. Разрешены: JPG, PNG, GIF, WebP, SVG'
            })
        
        # Проверяем размер файла (максимум 10MB)
        if image_file.size > 10 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': 'Файл слишком большой. Максимум 10MB'
            })
        
        # Генерируем уникальное имя файла
        file_ext = os.path.splitext(image_file.name)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        
        # Создаем путь в папке media/theory/images/
        file_path = f"theory/images/{unique_filename}"
        
        # Сохраняем файл
        saved_path = default_storage.save(file_path, image_file)
        
        # Создаем URL для доступа к файлу
        file_url = settings.MEDIA_URL + saved_path
        
        return JsonResponse({
            'success': True,
            'url': file_url,
            'filename': unique_filename,
            'original_name': image_file.name
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Ошибка сервера: {str(e)}'
        })