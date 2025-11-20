from django.urls import path
from . import views

app_name = 'calculator'

urlpatterns = [
    path('', views.calculator_page_view, name='page'),
    path('calculate/', views.calculate_view, name='calculate'),
    path('history/', views.calculation_history_view, name='history'),
    path('matrix/', views.matrix_calculator_page_view, name='matrix_page'),
    path('matrix-calculate/', views.matrix_calculate_view, name='matrix_calculate'),
]
