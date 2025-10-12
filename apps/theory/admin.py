from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.forms import Textarea
from django.db import models
from .models import Article
import re

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'created_at', 'preview_link')
    search_fields = ('title', 'content_md')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('order',)
    
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 20, 'cols': 80})},
    }
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'order')
        }),
        ('Содержимое статьи (Markdown)', {
            'fields': ('content_md', 'markdown_help'),
            'description': 'Используйте Markdown для форматирования текста. Поддерживаются заголовки, списки, ссылки, изображения, таблицы и формулы LaTeX.'
        }),
        ('Предпросмотр статьи', {
            'fields': ('live_preview_area',),
            'description': 'Живой предпросмотр статьи - обновляется автоматически при редактировании'
        })
    )
    
    readonly_fields = ('content_html', 'preview_link', 'live_preview_area', 'markdown_help')
    

    def markdown_help(self, obj):
        """Справка по Markdown"""
        return format_html('''
        <div style="background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
            <h4 style="margin-top: 0; color: #495057;">Справка по Markdown:</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; font-size: 12px;">
                <div>
                    <strong>Заголовки:</strong><br>
                    # Заголовок 1<br>
                    ## Заголовок 2<br>
                    ### Заголовок 3<br><br>
                    
                    <strong>Текст:</strong><br>
                    **жирный**<br>
                    *курсив*<br>
                    `код`<br><br>
                    
                    <strong>Списки:</strong><br>
                    - Элемент списка<br>
                    1. Нумерованный список<br>
                </div>
                <div>
                    <strong>Ссылки и изображения:</strong><br>
                    [текст ссылки](URL)<br>
                    ![alt текст](URL изображения)<br><br>
                    
                    <strong>Формулы LaTeX:</strong><br>
                    $E = mc^2$ - встроенная<br>
                    $$x = \\frac{{-b \\pm \\sqrt{{b^2-4ac}}}}{{2a}}$$ - блочная<br><br>
                    
                    <strong>Таблицы:</strong><br>
                    | Заголовок | Заголовок |<br>
                    |-----------|-----------|<br>
                    | Ячейка    | Ячейка    |<br>
                </div>
            </div>
        </div>
        ''')
    
    markdown_help.short_description = "📚 Справка"
    
    def live_preview_area(self, obj):
        """Предпросмотр статьи в формате HTML"""
        stats_html = ""
        content_html = ""
        
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
            
            stats_html = format_html(
                '<div style="background: #e8f4f8; border: 1px solid #bee5eb; padding: 8px 12px; margin-bottom: 10px; border-radius: 4px; font-size: 12px; color: #0c5460;">'
                '<strong>📊 Статистика:</strong> {} символов • {} слов • {} формул LaTeX'
                '</div>',
                char_count, word_count, latex_count
            )
            
            content_html = obj.content_html
        else:
            content_html = '<p style="text-align: center; color: #666; font-style: italic;">Содержимое появится после сохранения статьи</p>'

        return format_html('''
            <div style="border: 2px solid #007cba; border-radius: 8px; overflow: hidden;">
                <div style="background: linear-gradient(90deg, #007cba, #0056b3); color: white; padding: 12px 16px; font-weight: bold;">
                    <span style="font-size: 18px;">👁️</span> Предпросмотр статьи (HTML)
                </div>
                <div style="padding: 15px; background: white;">
                    {}
                    <div style="border: 2px dashed #28a745; border-radius: 4px; padding: 15px; background: #f8fff8; max-height: 500px; overflow-y: auto;">
                        {}
                    </div>
                </div>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            <script>
                if (window.MathJax) {{
                    MathJax.typesetPromise().catch(err => console.log('MathJax error:', err));
                }}
            </script>
        ''', stats_html, content_html)
    
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