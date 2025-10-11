from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='theory_index'),
]
