from rest_framework.routers import DefaultRouter

from .views import CreatureViewSet, DungeonViewSet, LevelViewSet, WaveViewSet

app_name = 'bestiary'

router = DefaultRouter()
router.register('creatures', CreatureViewSet)
router.register('dungeons', DungeonViewSet)
router.register('levels', LevelViewSet)
router.register('waves', WaveViewSet)
