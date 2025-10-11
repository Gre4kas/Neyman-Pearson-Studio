from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.quiz_start_view, name='start'),
    path('question/<int:question_id>/', views.question_view, name='question'),
    path('check_answer/<int:question_id>/', views.check_answer_view, name='check_answer'),
    path('results/', views.quiz_results_view, name='results'),
]