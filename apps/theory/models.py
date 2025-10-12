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
        # Сохраняем содержимое из визуального редактора
        if self.content_rich:
            self.content_html = self.content_rich
        super().save(*args, **kwargs)