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
            
            # Убираем все служебные элементы CKEditor
            processed_content = re.sub(r'<div[^>]*class="[^"]*ck-widget__type-around[^"]*"[^>]*>.*?</div>', '', processed_content, flags=re.IGNORECASE | re.DOTALL)
            processed_content = re.sub(r'<button[^>]*ck-widget__type-around__button[^>]*>.*?</button>', '', processed_content, flags=re.IGNORECASE | re.DOTALL)
            processed_content = re.sub(r'<div[^>]*ck-tooltip[^>]*>.*?</div>', '', processed_content, flags=re.IGNORECASE | re.DOTALL)
            processed_content = re.sub(r'<div[^>]*ck-balloon-panel[^>]*>.*?</div>', '', processed_content, flags=re.IGNORECASE | re.DOTALL)
            
            # Нормализуем структуру изображений - сохраняем все классы стилей
            processed_content = re.sub(
                r'<figure[^>]*class="([^"]*image[^"]*)"([^>]*)>', 
                lambda m: f'<figure class="{m.group(1).strip()}"{m.group(2)}>', 
                processed_content, 
                flags=re.IGNORECASE
            )
            
            # Нормализуем структуру таблиц - сохраняем все классы стилей  
            processed_content = re.sub(
                r'<figure[^>]*class="([^"]*table[^"]*)"([^>]*)>', 
                lambda m: f'<figure class="{m.group(1).strip()}"{m.group(2)}>', 
                processed_content, 
                flags=re.IGNORECASE
            )
            
            # Исправляем классы выравнивания изображений
            processed_content = re.sub(r'image-style-align-left', 'image-style-align-left', processed_content)
            processed_content = re.sub(r'image-style-align-right', 'image-style-align-right', processed_content)
            processed_content = re.sub(r'image-style-align-center', 'image-style-align-center', processed_content)
            processed_content = re.sub(r'image-style-side', 'image-style-side', processed_content)
            
            # Убираем пустые параграфы и лишние символы
            processed_content = re.sub(r'<p[^>]*>&nbsp;</p>', '', processed_content)
            processed_content = re.sub(r'<p[^>]*>\s*</p>', '', processed_content)
            processed_content = re.sub(r'<p[^>]*>(\s|&nbsp;)*</p>', '', processed_content)
            
            # Убираем лишние пустые строки и нормализуем отступы
            processed_content = re.sub(r'\n\s*\n\s*\n', '\n\n', processed_content)
            processed_content = re.sub(r'>\s+<', '><', processed_content)
            processed_content = processed_content.strip()
            
            self.content_html = processed_content
        super().save(*args, **kwargs)