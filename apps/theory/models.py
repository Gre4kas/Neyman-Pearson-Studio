from django.db import models
import markdown

class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content_md = models.TextField(help_text="Содержимое статьи в формате Markdown", verbose_name="Содержимое (Markdown)")
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
        # Конвертируем Markdown в HTML
        if self.content_md:
            md = markdown.Markdown(
                extensions=[
                    'markdown.extensions.extra',      # Поддержка таблиц, определений, и др.
                    'markdown.extensions.codehilite', # Подсветка синтаксиса кода
                    'markdown.extensions.toc',        # Генерация оглавления
                    'markdown.extensions.nl2br',      # Поддержка переносов строк
                ]
            )
            self.content_html = md.convert(self.content_md)
        else:
            self.content_html = ''
        super().save(*args, **kwargs)