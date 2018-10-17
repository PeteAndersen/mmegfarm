from rest_framework.routers import SimpleRouter

from .views import CreatureViewSet, DungeonViewSet, LevelViewSet, WaveViewSet

app_name = 'bestiary'

router = SimpleRouter()
router.register('creatures', CreatureViewSet)
router.register('dungeons', DungeonViewSet)
router.register('levels', LevelViewSet)
router.register('waves', WaveViewSet)
