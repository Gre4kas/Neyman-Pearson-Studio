from django.contrib import admin
from .models import Question, Answer, QuizResult

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1 # Количество пустых форм для добавления ответов

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text',)
    search_fields = ('text',)
    inlines = [AnswerInline]

@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'completed_at')
    list_filter = ('user',)
    readonly_fields = ('user', 'score', 'completed_at')