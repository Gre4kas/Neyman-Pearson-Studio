from django.db import models
import markdown

class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content_md = models.TextField(help_text="Содержимое в формате Markdown", verbose_name="Содержимое (Markdown)")
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
        self.content_html = markdown.markdown(self.content_md, extensions=['fenced_code', 'tables'])
        super().save(*args, **kwargs)