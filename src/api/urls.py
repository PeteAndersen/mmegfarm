from django.urls import path, include

from rest_framework import routers

from .views import CreatureViewSet, DungeonViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register('creatures', CreatureViewSet)
router.register('dungeons', DungeonViewSet)

urlpatterns = [
    path('', include(router.urls)),
]