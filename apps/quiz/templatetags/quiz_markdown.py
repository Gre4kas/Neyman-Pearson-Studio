from django import template
from django.utils.safestring import mark_safe
import markdown

register = template.Library()

# Настройки Markdown: включаем базовые расширения и поддерживаем простые конструкции.
# Формулы LaTeX не преобразуются markdown-пакетом, их рендерит MathJax на клиенте.
# Поэтому мы оставляем символы $ ... $ и $$ ... $$ нетронутыми.
MARKDOWN_EXTENSIONS = [
    'extra',        # Таблицы, списки и прочее
    'abbr',
    'attr_list',
    'def_list',
    'fenced_code',
    'footnotes',
    'tables'
]

@register.filter(name='markdownify')
def markdownify(value: str) -> str:
        """Преобразует Markdown в HTML.

        Особенности:
        - Формулы вида $...$ или $$...$$ не изменяются и будут отрендерены MathJax (конфигурация в base.html).
        - Безопасность: результат помечен как safe, предполагается что ввод контролируется (админ / подготовленные материалы).
            Если нужен ввод от пользователей — следует добавить санитайзинг (bleach и whitelist тегов).
        """
        if not value:
                return ''
        html = markdown.markdown(value, extensions=MARKDOWN_EXTENSIONS, output_format='html5')
        return mark_safe(html)
