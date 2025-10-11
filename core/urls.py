from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('calculator/', include('apps.calculator.urls')),
    path('theory/', include('apps.theory.urls')),
    # path('quiz/', include('apps.quiz.urls')),
]