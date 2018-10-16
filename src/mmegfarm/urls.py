from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include

from allauth.account.views import confirm_email

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls', namespace='api')),
    re_path(r'^auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$', confirm_email, name="account_confirm_email"),
    path('auth/', include('rest_auth.urls')),
    path('auth/registration/', include('rest_auth.registration.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
