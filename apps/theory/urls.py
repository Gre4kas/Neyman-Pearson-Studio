from django.urls import path
from . import views

app_name = 'theory'

urlpatterns = [
    path('', views.article_list_view, name='list'),
    path('<slug:slug>/', views.article_detail_view, name='detail'),
    path('admin/preview/', views.admin_preview_view, name='admin_preview'),
    path('admin/upload-image/', views.upload_image_view, name='upload_image'),
]
