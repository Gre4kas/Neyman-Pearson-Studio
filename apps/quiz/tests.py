from django.test import TestCase
from django.template import Context, Template


class MarkdownFilterTests(TestCase):
	def render(self, md_text: str):
		tpl = Template("""{% load quiz_markdown %}{{ text|markdownify }}""")
		return tpl.render(Context({'text': md_text})).strip()

	def test_bold_rendering(self):
		html = self.render("**Жирный текст**")
		self.assertIn('<strong>Жирный текст</strong>', html)

	def test_list_rendering(self):
		md = "- один\n- два\n- три"
		html = self.render(md)
		# Должен появиться ul и три li
		self.assertIn('<ul>', html)
		self.assertEqual(html.count('<li>'), 3)

	def test_latex_preserved(self):
		src = "Формула: $E=mc^2$ и $$P(\\text{ошибка}) = \\alpha$$"
		html = self.render(src)
		# Markdown не должен удалять символы доллара
		self.assertIn('$E=mc^2$', html)
		self.assertIn('$$P(\\text{ошибка}) = \\alpha$$', html)
		# Текст до формулы сохраняется
		self.assertIn('Формула:', html)
