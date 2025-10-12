from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'created_at', 'preview_link')
    search_fields = ('title', 'content_rich')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('order',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'order')
        }),
        ('Содержимое статьи', {
            'fields': ('content_rich',),
        }),
        ('Предпросмотр статьи', {
            'fields': ('live_preview_area',),
            'description': 'Живой предпросмотр статьи - обновляется автоматически при редактировании'
        })
    )
    
    readonly_fields = ('content_html', 'preview_link', 'live_preview_area')
    

    
    def live_preview_area(self, obj):
        """Единая область для предпросмотра статьи - как на реальной странице"""
        # Подготавливаем статистику для уже сохраненного контента
        stats_html = ""
        
        if obj and obj.content_html:
            import re
            
            # Подсчитываем статистику
            content = obj.content_html
            
            # Убираем HTML теги для подсчета чистого текста
            clean_content = re.sub('<[^<]+?>', ' ', content)
            clean_content = re.sub(r'\s+', ' ', clean_content).strip()
            clean_content = clean_content.replace('&nbsp;', ' ').replace('&amp;', '&')
            
            # Статистика
            char_count = len(clean_content)
            word_count = len([w for w in clean_content.split() if w])
            # Подсчет LaTeX формул
            latex_inline = len(re.findall(r'\$[^$]+\$', content))
            latex_block = len(re.findall(r'\$\$[^$]+\$\$', content))
            latex_count = latex_inline + latex_block
            
            stats_html = format_html(
                '<div style="background: #e8f4f8; border: 1px solid #bee5eb; padding: 8px 12px; margin-bottom: 10px; border-radius: 4px; font-size: 12px; color: #0c5460;">'
                '<strong>📊 Статистика:</strong> {0} символов • {1} слов • {2} формул (встроенных: {3}, блочных: {4})'
                '</div>',
                char_count, word_count, latex_count, latex_inline, latex_block
            )
        
        # Подготавливаем сохраненную версию
        saved_preview_html = ""
        if obj and obj.content_html:
            # Очищаем сохраненный контент от лишних элементов CKEditor
            import re
            clean_saved_content = obj.content_html
            
            # Убираем пустые параграфы с &nbsp;
            clean_saved_content = re.sub(r'<p>&nbsp;</p>', '', clean_saved_content)
            clean_saved_content = re.sub(r'<p>\s*</p>', '', clean_saved_content)
            
            # Убираем лишние пустые строки и пробелы
            clean_saved_content = re.sub(r'\n\s*\n\s*\n', '\n\n', clean_saved_content)
            
            saved_preview_html = format_html(
                '<div style="background: #f8f9fa; border-left: 4px solid #6c757d; padding: 12px; margin-bottom: 15px; border-radius: 4px;">'
                '<div style="font-weight: bold; color: #495057; margin-bottom: 8px;">💾 Сохраненная версия:</div>'
                '<div id="saved-content" style="overflow-wrap: break-word; word-wrap: break-word; max-width: 100%; overflow-x: auto;">{0}</div>'
                '</div>',
                clean_saved_content
            )
        else:
            saved_preview_html = format_html(
                '<div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; margin-bottom: 15px; border-radius: 4px;">'
                '<div style="color: #856404;"><em>💾 Сохраненного контента пока нет - сохраните статью</em></div>'
                '</div>'
            )

        return format_html(
            '<style>'
            '.preview-content-area {{ overflow-wrap: break-word; word-wrap: break-word; max-width: 100%; }}'
            '.preview-content-area img {{ max-width: 100% !important; height: auto !important; }}'
            '.preview-content-area figure {{ margin: 10px 0 !important; max-width: 100% !important; }}'
            '.preview-content-area .ck-widget__type-around {{ display: none !important; }}'
            '.preview-content-area .ck-widget__type-around__button {{ display: none !important; }}'
            '.preview-content-area .ck-tooltip {{ display: none !important; }}'
            '</style>'
            '<div id="live-preview-container" style="border: 2px solid #007cba; border-radius: 8px; overflow: hidden; min-height: 300px; max-width: 100%;">'
            '<div style="background: linear-gradient(90deg, #007cba, #0056b3); color: white; padding: 12px 16px; font-weight: bold; display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">'
            '<span style="font-size: 18px;">👁️</span>'
            '<span>Предпросмотр статьи (как на сайте)</span>'
            '<div style="margin-left: auto; display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">'
            '<button type="button" id="refresh-preview-btn" style="background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.3); color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; cursor: pointer; transition: all 0.2s;" title="Принудительно обновить предпросмотр">🔄 Обновить</button>'
            '<div style="font-size: 12px; opacity: 0.9;" id="preview-status">Готов к работе</div>'
            '</div>'
            '</div>'
            '<div style="padding: 15px; background: white; max-width: 100%; overflow: hidden;">'
            '{0}'  # stats_html
            '{1}'  # saved_preview_html
            # Живой предпросмотр (тоже с MathJax)
            '<div style="border: 2px dashed #28a745; border-radius: 4px; padding: 15px; background: #f8fff8; max-width: 100%; overflow: hidden;">'
            '<div style="font-weight: bold; color: #155724; margin-bottom: 10px; font-size: 14px;">🔥 Живой предпросмотр:</div>'
            '<div id="live-preview-content" class="preview-content-area" style="min-height: 150px; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif; line-height: 1.6; color: #333; overflow-wrap: break-word; word-wrap: break-word; max-width: 100%;">'
            '<div style="color: #666; font-style: italic; text-align: center; padding: 20px;">'
            '📝 Начните печатать в редакторе, чтобы увидеть предпросмотр...'
            '</div>'
            '</div>'
            '</div>'
            '</div>'
            '</div>'
            # MathJax скрипты и стили - как на реальной странице
            '<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" async></script>'
            '<script>'
            'if (!window.MathJax) {{'
            '  window.MathJax = {{'
            '    tex: {{'
            '      inlineMath: [["$", "$"]],'
            '      displayMath: [["$$", "$$"]],'
            '      processEscapes: true,'
            '      processEnvironments: true'
            '    }},'
            '    options: {{'
            '      skipHtmlTags: ["script", "noscript", "style", "textarea", "pre", "code", "a"]'
            '    }},'
            '    startup: {{'
            '      ready() {{'
            '        console.log("MathJax загружен в админке");'
            '        MathJax.startup.defaultReady();'
            '      }}'
            '    }}'
            '  }};'
            '}}'
            '</script>',
            stats_html,
            saved_preview_html
        )
    
    live_preview_area.short_description = "👁️ Предпросмотр"
    

    
    def preview_link(self, obj):
        """Ссылка на просмотр статьи на сайте"""
        if obj.pk and obj.slug:
            url = reverse('theory:detail', args=[obj.slug])
            return format_html(
                '<a href="{}" target="_blank" class="button" style="background: #28a745; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; font-size: 12px;">'
                '🔗 Открыть на сайте'
                '</a>', 
                url
            )
        return format_html('<span style="color: #999; font-style: italic;">Сначала сохраните статью</span>')
    
    preview_link.short_description = "🌐 Просмотр"
    
    class Media:
        css = {
            'all': ('admin/css/theory_admin.css', 'admin/css/ckeditor_math.css', 'admin/css/latex_support.css')
        }
        js = ('admin/js/theory_admin.js', 'admin/js/ckeditor_math.js', 'admin/js/latex_examples.js')