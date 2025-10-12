from django.db import models
import markdown
from django_ckeditor_5.fields import CKEditor5Field

class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content_md = models.TextField(help_text="Содержимое в формате Markdown", verbose_name="Содержимое (Markdown)", blank=True)
    content_rich = CKEditor5Field(help_text="Богатый текстовый редактор", verbose_name="Содержимое (Визуальный редактор)", blank=True, config_name='theory_editor')
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
        # Приоритет отдаем визуальному редактору, если он заполнен
        if self.content_rich:
            self.content_html = self.content_rich
        elif self.content_md:
            self.content_html = markdown.markdown(self.content_md, extensions=['fenced_code', 'tables'])
        super().save(*args, **kwargs)