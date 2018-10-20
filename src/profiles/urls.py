from rest_framework.routers import DefaultRouter

from .views import ProfileViewSet, CreatureInstanceViewSet, GlyphInstanceViewSet, TeamViewSet

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet)
router.register(r'creature-instances', CreatureInstanceViewSet)
router.register(r'glyphs', GlyphInstanceViewSet)
router.register(r'teams', TeamViewSet)
