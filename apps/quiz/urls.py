from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.quiz_list_view, name='list'),
    path('history/', views.quiz_history_view, name='history'),
    path('start/<int:quiz_id>/', views.quiz_start_view, name='start'),
    path('<int:quiz_id>/question/<int:question_id>/', views.question_view, name='question'),
    path('<int:quiz_id>/check_answer/<int:question_id>/', views.check_answer_view, name='check_answer'),
    path('<int:quiz_id>/results/', views.quiz_results_view, name='results'),
]
