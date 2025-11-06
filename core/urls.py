from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from apps.theory.views import upload_image_view, get_uploaded_images_view, delete_image_view

urlpatterns = [
    path('admin/theory/upload-image/', upload_image_view, name='admin_upload_image'),
    path('admin/theory/get-images/', get_uploaded_images_view, name='admin_get_images'),
    path('admin/theory/delete-image/', delete_image_view, name='admin_delete_image'),
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('users/', include('apps.users.urls')),
    path('calculator/', include('apps.calculator.urls')),
    path('theory/', include('apps.theory.urls')),
    path('quiz/', include('apps.quiz.urls')),
]

# Serve media files during development and for admin uploads
# В production Nginx будет обслуживать /media/, но Django admin нужен доступ для загрузки
from django.views.static import serve
from django.urls import re_path

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # В production добавляем только для admin загрузок
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
