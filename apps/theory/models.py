from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content_rich = CKEditor5Field(help_text="Содержимое статьи", verbose_name="Содержимое", config_name='theory_editor')
    content_html = models.TextField(editable=False, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Обрабатываем и сохраняем содержимое из визуального редактора
        if self.content_rich:
            import re
            
            # Очищаем и обрабатываем контент
            processed_content = self.content_rich
            
            # Убираем элементы CKEditor для вставки параграфов
            processed_content = re.sub(r'<div[^>]*class="[^"]*ck-widget__type-around[^"]*"[^>]*>.*?</div>', '', processed_content, flags=re.IGNORECASE | re.DOTALL)
            processed_content = re.sub(r'<button[^>]*ck-widget__type-around__button[^>]*>.*?</button>', '', processed_content, flags=re.IGNORECASE | re.DOTALL)
            
            # Убираем другие служебные элементы CKEditor
            processed_content = re.sub(r'<div[^>]*ck-tooltip[^>]*>.*?</div>', '', processed_content, flags=re.IGNORECASE | re.DOTALL)
            
            # Исправляем структуру изображений
            processed_content = re.sub(r'<figure[^>]*class="[^"]*image[^"]*"([^>]*)>', r'<figure class="image"\1>', processed_content, flags=re.IGNORECASE)
            
            # Исправляем структуру таблиц
            processed_content = re.sub(r'<figure[^>]*class="[^"]*table[^"]*"([^>]*)>', r'<figure class="table"\1>', processed_content, flags=re.IGNORECASE)
            
            # Убираем пустые параграфы
            processed_content = re.sub(r'<p[^>]*>&nbsp;</p>', '', processed_content)
            processed_content = re.sub(r'<p[^>]*>\s*</p>', '', processed_content)
            
            # Убираем лишние пустые строки
            processed_content = re.sub(r'\n\s*\n\s*\n', '\n\n', processed_content)
            processed_content = processed_content.strip()
            
            self.content_html = processed_content
        super().save(*args, **kwargs)