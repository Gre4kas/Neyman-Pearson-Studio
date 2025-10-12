from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
import json
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
