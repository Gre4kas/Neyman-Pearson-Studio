from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.forms import Textarea
from django.db import models
from django.utils.safestring import mark_safe
from .models import Article
import re

class MarkdownWidget(Textarea):
    """Кастомный виджет для Markdown редактора"""
    def __init__(self, attrs=None):
        default_attrs = {
            'rows': 25, 
            'cols': 100,
            'style': 'width: 100%; font-family: "Monaco", "Consolas", "Courier New", monospace; font-size: 14px; line-height: 1.5;'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    class Media:
        css = {
            'all': ('admin/css/theory_admin.css',)
        }
        js = ('admin/js/theory_admin.js',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'created_at', 'preview_link')
    search_fields = ('title', 'content_md')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('order',)
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'content_md':
            kwargs['widget'] = MarkdownWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'order'),
            'classes': ('wide',)
        }),
        ('Содержимое', {
            'fields': ('content_md', 'image_upload_help', 'markdown_help'),
            'description': 'Создайте содержимое статьи используя Markdown синтаксис',
            'classes': ('wide', 'collapse')
        }),
        ('Предпросмотр', {
            'fields': ('live_preview_area',),
            'classes': ('wide',)
        })
    )
    
    readonly_fields = ('content_html', 'preview_link', 'live_preview_area', 'markdown_help', 'image_upload_help')
    
    class Media:
        css = {
            'all': ('admin/css/theory_admin.css',)
        }
        js = ('admin/js/theory_admin.js',)
    
    def image_upload_help(self, obj):
        """Помощь по загрузке изображений с возможностью загрузки"""
        return format_html('''
        <div class="collapsible-section">
            <div class="collapsible-header" onclick="toggleCollapsible('image-help')">
                <span class="icon">📷</span>
                <span class="title">Управление изображениями</span>
                <span class="arrow">▼</span>
            </div>
            <div class="collapsible-content" id="image-help" aria-hidden="true" style="display:none;">
                
                <!-- Каталог загруженных изображений -->
                <div class="uploaded-images-section">
                    <div class="section-header">
                        <h4>📂 Загруженные изображения</h4>
                        <button type="button" onclick="loadUploadedImages()" class="refresh-btn">🔄 Обновить</button>
                    </div>
                    
                    <div class="images-grid" id="uploadedImagesList">
                        <div class="loading-message">🔄 Загрузка каталога изображений...</div>
                    </div>
                </div>
                
                <div class="section-divider"></div>
                
                <!-- Загрузка нового изображения -->
                <div class="upload-section">
                    <div class="section-header">
                        <h4>⬆️ Загрузить новое изображение</h4>
                    </div>
                    <div class="upload-zone">
                        <div class="upload-icon">📤</div>
                        <div class="upload-text">
                            <strong>Нажмите для загрузки изображения</strong>
                            <small>или перетащите файл сюда</small>
                        </div>
                        <input type="file" id="imageUpload" accept="image/*" class="visually-hidden">
                    </div>
                    
                    <div class="upload-progress" id="uploadProgress" style="display:none;">
                        <div class="progress-bar">
                            <div class="progress-fill"></div>
                        </div>
                        <span class="progress-text">Загрузка...</span>
                    </div>
                    
                    <div class="upload-result" id="uploadResult" style="display:none;">
                        <div class="result-text">✅ Изображение загружено!</div>
                        <div class="result-code">
                            <strong>Скопируйте код:</strong>
                            <input type="text" id="generatedCode" readonly>
                            <button type="button" onclick="copyToClipboard()" class="copy-btn">📋 Копировать</button>
                        </div>
                    </div>
                </div>
                
                <div class="section-divider"></div>
                
                <div class="help-methods">
                    <div class="method">
                        <h5>📤 Загрузка файла:</h5>
                        <code>Используйте форму выше для загрузки</code>
                        <p>Файлы сохраняются в <strong>/media/theory/images/</strong></p>
                    </div>
                    <div class="method">
                        <h5>🌐 Внешняя ссылка:</h5>
                        <code>![описание](https://example.com/image.jpg)</code>
                        <p>Используйте изображения из интернета</p>
                    </div>
                    <div class="method">
                        <h5>🎯 С центрированием:</h5>
                        <code>&lt;div align="center"&gt;<br>![описание](путь_к_изображению)<br>&lt;/div&gt;</code>
                        <p>Центрирование изображения на странице</p>
                    </div>
                    <div class="method">
                        <h5>📏 С размером:</h5>
                        <code>&lt;img src="путь" width="300" alt="описание"&gt;</code>
                        <p>Контроль размера изображения</p>
                    </div>
                </div>
            </div>
        </div>
        ''')
    
    image_upload_help.short_description = ""

    def markdown_help(self, obj):
        """Справка по Markdown"""
        return format_html('''
        <div class="collapsible-section">
            <div class="collapsible-header" onclick="toggleCollapsible('markdown-help')">
                <span class="icon">📚</span>
                <span class="title">Справка по Markdown</span>
                <span class="arrow">▼</span>
            </div>
            <div class="collapsible-content" id="markdown-help" aria-hidden="true" style="display:none;">
                <div class="help-grid">
                    <div class="help-column">
                        <div class="help-section">
                            <h5>📝 Заголовки</h5>
                            <div class="code-examples">
                                <code># Заголовок 1</code><br>
                                <code>## Заголовок 2</code><br>
                                <code>### Заголовок 3</code>
                            </div>
                        </div>
                        
                        <div class="help-section">
                            <h5>✏️ Форматирование текста</h5>
                            <div class="code-examples">
                                <code>**жирный текст**</code><br>
                                <code>*курсив*</code><br>
                                <code>`код`</code>
                            </div>
                        </div>
                        
                        <div class="help-section">
                            <h5>📝 Списки</h5>
                            <div class="code-examples">
                                <code>- Элемент списка</code><br>
                                <code>1. Нумерованный</code><br>
                                <code>2. Список</code>
                            </div>
                        </div>
                    </div>
                    
                    <div class="help-column">
                        <div class="help-section">
                            <h5>🔗 Ссылки</h5>
                            <div class="code-examples">
                                <code>[текст ссылки](URL)</code><br>
                                <code>[Google](https://google.com)</code>
                            </div>
                        </div>
                        
                        <div class="help-section">
                            <h5>🧮 Формулы LaTeX</h5>
                            <div class="code-examples">
                                <code>$E = mc^2$ - встроенная</code><br>
                                <code>$$x = \\frac{{a+b}}{{c}}$$ - блочная</code>
                            </div>
                        </div>
                        
                        <div class="help-section">
                            <h5>📊 Таблицы</h5>
                            <div class="code-examples">
                                <code>| Заголовок | Заголовок |</code><br>
                                <code>|-----------|-----------|</code><br>
                                <code>| Ячейка    | Ячейка    |</code>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        ''')
    
    markdown_help.short_description = ""
    
    def live_preview_area(self, obj):
        """Красивый предпросмотр статьи"""
        if obj and obj.content_html:
            # Подсчитываем статистику
            clean_content = re.sub('<[^<]+?>', ' ', obj.content_html)
            clean_content = re.sub(r'\s+', ' ', clean_content).strip()
            
            char_count = len(clean_content)
            word_count = len([w for w in clean_content.split() if w])
            
            # Подсчет LaTeX формул
            latex_inline = len(re.findall(r'\$[^$]+\$', obj.content_html))
            latex_block = len(re.findall(r'\$\$[^$]+\$\$', obj.content_html))
            latex_count = latex_inline + latex_block
            
            return format_html('''
                <div class="preview-container">
                    <div class="preview-header">
                        <span class="preview-icon">👁️</span>
                        <span class="preview-title">Предпросмотр</span>
                        <div class="preview-stats">
                            <span class="stat-item">📝 {} слов</span>
                            <span class="stat-item">✒️ {} символов</span>
                            <span class="stat-item">🧮 {} формул</span>
                        </div>
                    </div>
                    <div class="preview-content">
                        <article>
                            <h1>{}</h1>
                            <hr>
                            <div id="article-content">{}</div>
                        </article>
                    </div>
                </div>
                <script>
                    (function() {{
                        function renderMath() {{
                            if (window.MathJax && window.MathJax.typesetPromise) {{
                                const content = document.getElementById('article-content');
                                if (content) {{
                                    window.MathJax.typesetPromise([content]).catch(err => console.error('MathJax error (admin preview):', err));
                                }}
                            }}
                        }}
                        renderMath();
                        setTimeout(renderMath, 500);
                        setTimeout(renderMath, 1500);
                    }})();
                </script>
            ''', word_count, char_count, latex_count, mark_safe(obj.title), mark_safe(obj.content_html))
        else:
            return format_html('''
                <div class="preview-container empty">
                    <div class="preview-header">
                        <span class="preview-icon">👁️</span>
                        <span class="preview-title">Предпросмотр</span>
                    </div>
                    <div class="preview-content empty-content">
                        <p>📝 Содержимое появится после добавления текста и сохранения статьи</p>
                    </div>
                </div>
            ''')
    
    live_preview_area.short_description = ""
    
    def preview_link(self, obj):
        """Ссылка на просмотр статьи на сайте"""
        if obj.pk and obj.slug:
            url = reverse('theory:detail', args=[obj.slug])
            return format_html(
                '<a href="{}" target="_blank" class="button preview-link">'
                '🔗 Открыть на сайте'
                '</a>', 
                url
            )
        return format_html('<span style="color: #999; font-style: italic;">Сначала сохраните статью</span>')
    
    preview_link.short_description = "🌐 Просмотр"