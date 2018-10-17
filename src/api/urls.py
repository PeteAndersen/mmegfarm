from django.urls import path, include

from rest_framework import routers

from bestiary.urls import router as bestaryRouter

app_name = 'api'

router = routers.DefaultRouter()
router.registry.extend(bestaryRouter.registry)

urlpatterns = [
    path('', include(router.urls)),
]
