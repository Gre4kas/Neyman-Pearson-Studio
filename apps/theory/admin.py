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
        ('Предпросмотр и отладка', {
            'fields': ('preview_content', 'content_html'),
            'classes': ('collapse',),
            'description': 'Эти поля генерируются автоматически и предназначены для просмотра результата.'
        })
    )
    
    readonly_fields = ('content_html', 'preview_content', 'preview_link')
    
    def preview_content(self, obj):
        """Показывает превью контента в админке"""
        if obj.content_html:
            # Очищаем HTML теги для превью
            import re
            clean_content = re.sub('<[^<]+?>', '', obj.content_html)
            preview = clean_content[:300]
            if len(clean_content) > 300:
                preview += '...'
            
            # Также показываем количество символов
            char_count = len(clean_content)
            word_count = len(clean_content.split())
            
            return format_html(
                '<div style="max-height: 150px; overflow-y: auto; border: 1px solid #ddd; padding: 12px; background: #f8f9fa; border-radius: 4px; font-size: 13px; line-height: 1.4;">'
                '<div style="margin-bottom: 8px; color: #666; font-size: 11px;"><strong>📊 Статистика:</strong> {0} символов, {1} слов</div>'
                '<div style="color: #333;">{2}</div>'
                '</div>',
                char_count,
                word_count, 
                preview
            )
        return format_html('<div style="color: #999; font-style: italic;">Контент не добавлен</div>')
    
    preview_content.short_description = "📄 Превью и статистика"
    
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