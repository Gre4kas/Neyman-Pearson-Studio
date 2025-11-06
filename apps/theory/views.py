from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage
from django.conf import settings
import json
import os
import uuid
from datetime import datetime
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

@require_http_methods(["POST"])
def admin_preview_view(request: HttpRequest) -> JsonResponse:
    """AJAX эндпоинт для предпросмотра статей в админке - с MathJax рендерингом"""
    try:
        print(f"Preview request from {request.META.get('REMOTE_ADDR', 'unknown')}")
        print(f"Request headers: {dict(request.META)}")
        print(f"Content type: {request.content_type}")
        print(f"CSRF token in request: {request.META.get('HTTP_X_CSRFTOKEN', 'Not found')}")
        
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
        
        # Конвертируем Markdown в HTML (с сохранением LaTeX формул)
        import markdown as md_mod
        md_converter = md_mod.Markdown(
            extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
                'markdown.extensions.toc',
                'markdown.extensions.nl2br',
            ]
        )
        # processed_content сейчас всё ещё сырой HTML/Markdown перемешанный
        # Мы ожидаем Markdown во входе, поэтому используем исходный content
        converted_html = ''
        try:
            converted_html = md_converter.convert(content)
        except Exception:
            converted_html = processed_content  # fallback

        # Восстанавливаем формулы (markdown могли экранировать) - простой проход не трогаем, оставляем как есть

        wrapped_html = f"""
        <article>
            <h1>Предпросмотр статьи</h1>
            <hr>
            <div id=\"article-content\">{converted_html}</div>
        </article>
        """.strip()

        return JsonResponse({
            'success': True,
            'html': wrapped_html,
            'trigger_mathjax': True  # Сигнал для JavaScript что нужно запустить MathJax
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@require_http_methods(["POST"])
def upload_image_view(request: HttpRequest) -> JsonResponse:
    """Загрузка изображений для статей"""
    try:
        print(f"Upload request from {request.META.get('REMOTE_ADDR', 'unknown')}")
        print(f"CSRF token: {request.META.get('HTTP_X_CSRFTOKEN', 'Not found')}")
        print(f"Files in request: {list(request.FILES.keys())}")
        
        # Проверяем наличие файла
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Файл не выбран'
            })
        
        image_file = request.FILES['image']
        
        # Проверяем, что файл не пустой
        if not image_file or image_file.size == 0:
            return JsonResponse({
                'success': False,
                'error': 'Выбранный файл пустой'
            })
        
        # Проверяем тип файла по расширению и MIME типу
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
        allowed_mime_types = [
            'image/jpeg', 
            'image/jpg', 
            'image/png', 
            'image/gif', 
            'image/webp', 
            'image/svg+xml'
        ]
        
        file_ext = os.path.splitext(image_file.name)[1].lower()
        if file_ext not in allowed_extensions:
            return JsonResponse({
                'success': False,
                'error': f'Недопустимое расширение файла. Разрешены: {", ".join(allowed_extensions)}'
            })
        
        if image_file.content_type not in allowed_mime_types:
            return JsonResponse({
                'success': False,
                'error': 'Недопустимый тип файла. Разрешены только изображения.'
            })
        
        # Проверяем размер файла (максимум 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if image_file.size > max_size:
            return JsonResponse({
                'success': False,
                'error': f'Файл слишком большой ({image_file.size / (1024*1024):.1f} МБ). Максимум 10 МБ.'
            })
        
        # Генерируем уникальное имя файла
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        
        # Создаем путь в папке media/theory/images/
        file_path = f"theory/images/{unique_filename}"
        
        # Убеждаемся, что директория существует
        images_dir = os.path.join(settings.MEDIA_ROOT, 'theory', 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        # Сохраняем файл
        try:
            saved_path = default_storage.save(file_path, image_file)
        except Exception as save_error:
            return JsonResponse({
                'success': False,
                'error': f'Ошибка при сохранении файла: {str(save_error)}'
            })
        
        # Создаем URL для доступа к файлу
        file_url = request.build_absolute_uri(settings.MEDIA_URL + saved_path)
        
        return JsonResponse({
            'success': True,
            'url': file_url,
            'filename': unique_filename,
            'original_name': image_file.name,
            'size': image_file.size,
            'markdown': f"![{image_file.name}]({file_url})"
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Ошибка сервера: {str(e)}'
        })


@require_http_methods(["GET"])
def get_uploaded_images_view(request: HttpRequest) -> JsonResponse:
    """Получение списка загруженных изображений"""
    try:
        images_dir = "theory/images"
        images = []
        
        # Проверяем, существует ли директория
        if not default_storage.exists(images_dir):
            # Создаем директорию если её нет
            images_full_dir = os.path.join(settings.MEDIA_ROOT, 'theory', 'images')
            os.makedirs(images_full_dir, exist_ok=True)
            
            return JsonResponse({
                'success': True,
                'images': [],
                'count': 0,
                'message': 'Директория создана, но изображений пока нет'
            })
        
        try:
            # Получаем список файлов
            directories, files = default_storage.listdir(images_dir)
            
            # Фильтруем только изображения
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
            
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext not in image_extensions:
                    continue  # Пропускаем не изображения
                
                file_path = f"{images_dir}/{file}"
                
                try:
                    # Получаем информацию о файле
                    file_url = request.build_absolute_uri(settings.MEDIA_URL + file_path)
                    file_size = default_storage.size(file_path)
                    
                    # Пытаемся получить дату создания
                    created_date = "Неизвестно"
                    try:
                        full_path = default_storage.path(file_path)
                        created_time = os.path.getctime(full_path)
                        created_date = datetime.fromtimestamp(created_time).strftime('%d.%m.%Y %H:%M')
                    except:
                        pass
                    
                    # Определяем размер в удобном формате
                    if file_size < 1024:
                        size_str = f"{file_size} Б"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size // 1024} КБ"
                    else:
                        size_str = f"{file_size / (1024 * 1024):.1f} МБ"
                    
                    # Получаем оригинальное имя из имени файла (если возможно)
                    original_name = file
                    
                    images.append({
                        'filename': file,
                        'url': file_url,
                        'size': size_str,
                        'created': created_date,
                        'original_name': original_name,
                        'markdown': f"![{original_name}]({file_url})"
                    })
                    
                except Exception as file_error:
                    # Логируем ошибку, но продолжаем обработку других файлов
                    print(f"Ошибка обработки файла {file}: {file_error}")
                    continue
        
        except Exception as listdir_error:
            return JsonResponse({
                'success': False,
                'error': f'Ошибка чтения директории: {str(listdir_error)}'
            })
        
        # Сортируем по дате создания (новые сверху)
        try:
            images.sort(key=lambda x: datetime.strptime(x['created'], '%d.%m.%Y %H:%M') if x['created'] != "Неизвестно" else datetime.min, reverse=True)
        except:
            # Если сортировка по дате не удалась, сортируем по имени файла
            images.sort(key=lambda x: x['filename'], reverse=True)
        
        return JsonResponse({
            'success': True,
            'images': images,
            'count': len(images)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Ошибка получения изображений: {str(e)}'
        })


@require_http_methods(["POST"])
def delete_image_view(request: HttpRequest) -> JsonResponse:
    """Удаление загруженного изображения"""
    try:
        # Парсим JSON данные
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Некорректный JSON в запросе'
            })
        
        filename = data.get('filename', '').strip()
        
        if not filename:
            return JsonResponse({
                'success': False,
                'error': 'Имя файла не указано'
            })
        
        # Проверяем, что имя файла безопасно (без путей вверх)
        if '..' in filename or '/' in filename or '\\' in filename:
            return JsonResponse({
                'success': False,
                'error': 'Недопустимое имя файла'
            })
        
        file_path = f"theory/images/{filename}"
        
        if default_storage.exists(file_path):
            try:
                default_storage.delete(file_path)
                return JsonResponse({
                    'success': True,
                    'message': f'Изображение {filename} успешно удалено'
                })
            except Exception as delete_error:
                return JsonResponse({
                    'success': False,
                    'error': f'Ошибка при удалении файла: {str(delete_error)}'
                })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Файл не найден или уже был удален'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Ошибка удаления: {str(e)}'
        })