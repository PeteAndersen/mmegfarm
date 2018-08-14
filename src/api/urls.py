from django.urls import path, include

from rest_framework import routers

from .views import CreatureViewSet, DungeonViewSet, LevelViewSet, WaveViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register('creatures', CreatureViewSet)
router.register('dungeons', DungeonViewSet)
router.register('levels', LevelViewSet)
router.register('waves', WaveViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
