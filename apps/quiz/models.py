from django.db import models
from django.conf import settings

class Quiz(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название теста")
    questions = models.ManyToManyField('Question', related_name='quizzes', verbose_name="Вопросы")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"

    def __str__(self):
        return self.title

class Question(models.Model):
    text = models.TextField(verbose_name="Текст вопроса")
    explanation = models.TextField(blank=True, help_text="Пояснение к правильному ответу.", verbose_name="Пояснение")

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return self.text[:50]

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE, verbose_name="Вопрос")
    text = models.CharField(max_length=255, verbose_name="Текст ответа")
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ")

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
        
    def __str__(self):
        return f"{'✓' if self.is_correct else '✗'}"

class QuizResult(models.Model):
    # Эта модель пока не используется, но оставим ее для будущего
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}%"
