from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path('bestiary/', include('bestiary.urls')),
    path('', TemplateView.as_view(template_name='base.html'))
]
