from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json


class AdminPreviewTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='pass12345')
		self.client = Client()
		self.client.login(username='admin', password='pass12345')

	def test_admin_preview_structure(self):
		url = reverse('theory:admin_preview')
		markdown_content = "# Заголовок\n\nТестовая формула: $E=mc^2$"  # простое содержимое
		response = self.client.post(url, data=json.dumps({'content': markdown_content}), content_type='application/json')
		self.assertEqual(response.status_code, 200)
		data = response.json()
		self.assertTrue(data.get('success'))
		html = data.get('html', '')
		# Проверяем структуру 1:1
		self.assertIn('<article>', html)
		self.assertIn('<h1>Предпросмотр статьи</h1>', html)
		self.assertIn('<hr>', html)
		self.assertIn('id="article-content"', html)
		# ЛаТеХ не должен быть преобразован здесь (оставляем для MathJax)
		self.assertIn('$E=mc^2$', html)
		# Сигнал для MathJax
		self.assertTrue(data.get('trigger_mathjax'))
