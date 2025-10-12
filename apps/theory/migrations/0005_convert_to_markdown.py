# Generated manually for markdown conversion

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("theory", "0004_remove_markdown_field"),
    ]

    operations = [
        # Удаляем поле content_rich (CKEditor)
        migrations.RemoveField(
            model_name="article",
            name="content_rich",
        ),
        # Добавляем поле content_md (Markdown)
        migrations.AddField(
            model_name="article", 
            name="content_md",
            field=models.TextField(
                help_text="Содержимое статьи в формате Markdown",
                verbose_name="Содержимое (Markdown)",
                default="# Новая статья\n\nВведите содержимое статьи в формате Markdown здесь."
            ),
        ),
    ]