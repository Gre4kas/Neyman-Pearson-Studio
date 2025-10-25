# Generated manually for markdown conversion

from django.db import migrations, models
from django.db import connection


def add_content_md_field(apps, schema_editor):
    """Добавляет поле content_md только если его нет"""
    with connection.cursor() as cursor:
        # Проверяем, существует ли поле content_md
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='theory_article' AND column_name='content_md';
        """)
        if not cursor.fetchone():
            # Поле не существует, создаем его
            cursor.execute("""
                ALTER TABLE theory_article 
                ADD COLUMN content_md text DEFAULT '# Новая статья

Введите содержимое статьи в формате Markdown здесь.' NOT NULL;
            """)


def remove_content_md_field(apps, schema_editor):
    """Удаляет поле content_md при откате миграции"""
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE theory_article DROP COLUMN IF EXISTS content_md;")


class Migration(migrations.Migration):

    dependencies = [
        ("theory", "0002_alter_article_options_remove_article_content_and_more"),
    ]

    operations = [
        migrations.RunPython(add_content_md_field, remove_content_md_field),
    ]