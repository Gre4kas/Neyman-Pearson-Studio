from django.urls import path
from . import views

app_name = 'calculator'

urlpatterns = [
    path('', views.calculator_page_view, name='page'),
    path('calculate/', views.calculate_view, name='calculate'),
]