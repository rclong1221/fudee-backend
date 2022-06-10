from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from fudee.users.api.views import UserViewSet
from fudee.relationships.api.views import InviteViewSet, RelationshipViewSet, UserGroupViewSet, UserGroupUserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("invite", InviteViewSet)
router.register("relationship", RelationshipViewSet)
router.register("user_group", UserGroupViewSet)
router.register("user_group_user", UserGroupUserViewSet)

app_name = "api"
urlpatterns = router.urls