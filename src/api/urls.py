from rest_framework import routers

from bestiary.urls import router as bestiary_router
from profiles.urls import router as profile_router

app_name = 'api'

router = routers.DefaultRouter()
router.registry.extend(bestiary_router.registry)
router.registry.extend(profile_router.registry)

urlpatterns = router.urls
