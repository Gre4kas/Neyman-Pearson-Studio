from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    
    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.html',
        redirect_authenticated_user=True # Не пускать залогиненных на страницу входа
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(
        next_page='home' # Куда перенаправить после выхода
    ), name='logout'),
]
