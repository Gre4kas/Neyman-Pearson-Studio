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
        ('Содержимое', {
            'fields': ('content_rich',),
            'description': 'Используйте визуальный редактор для создания содержимого. '
                          'Редактор поддерживает жирный текст, курсив, списки, ссылки, изображения, '
                          'таблицы, код и математические формулы LaTeX.'
        }),
        ('Автоматически генерируемые поля', {
            'fields': ('content_html', 'preview_content'),
            'classes': ('collapse',),
        })
    )
    
    readonly_fields = ('content_html', 'preview_content', 'preview_link')
    
    def preview_content(self, obj):
        """Показывает превью контента в админке"""
        if obj.content_html:
            # Ограничиваем длину превью
            preview = obj.content_html[:500]
            if len(obj.content_html) > 500:
                preview += '...'
            return format_html('<div style="max-height: 200px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; background: #f9f9f9;">{}</div>', preview)
        return "Нет контента"
    
    preview_content.short_description = "Превью контента"
    
    def preview_link(self, obj):
        """Ссылка на просмотр статьи на сайте"""
        if obj.pk:
            url = reverse('theory:detail', args=[obj.slug])
            return format_html('<a href="{}" target="_blank" class="button">Просмотр на сайте</a>', url)
        return "Сохраните статью для предпросмотра"
    
    preview_link.short_description = "Предпросмотр"
    
    class Media:
        css = {
            'all': ('admin/css/theory_admin.css', 'admin/css/ckeditor_math.css')
        }
        js = ('admin/js/theory_admin.js', 'admin/js/ckeditor_math.js')