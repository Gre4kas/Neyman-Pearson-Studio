from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from apps.theory.views import upload_image_view

urlpatterns = [
    path('admin/theory/upload-image/', upload_image_view, name='admin_upload_image'),
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('users/', include('apps.users.urls')),
    path('calculator/', include('apps.calculator.urls')),
    path('theory/', include('apps.theory.urls')),
    path('quiz/', include('apps.quiz.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
