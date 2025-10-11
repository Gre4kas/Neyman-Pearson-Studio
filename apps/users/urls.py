from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'users'

def users_redirect(request):
    return redirect('home')

urlpatterns = [
    path('', users_redirect, name='index'),  # Редирект с /users/ на главную
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
