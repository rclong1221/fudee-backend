from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from fudee.users.api.views import UserViewSet, UserImageViewSet, UserSearchViewSet
from fudee.relationships.api.views import InviteViewSet, RelationshipViewSet, UserGroupViewSet, UserGroupUserViewSet, UserGroupImageViewSet
from fudee.organizations.api.views import OrganizationViewSet, OrganizationUserViewSet, OrganizationImageViewSet
from fudee.events.api.views import EventViewSet, EventUserViewSet, EventImageViewSet
from fudee.shifts.api.views import ShiftViewSet, OrganizationEventViewSet, SwapViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("user_image", UserImageViewSet)
router.register("search", UserSearchViewSet)
router.register("invite", InviteViewSet)
router.register("relationship", RelationshipViewSet)
router.register("user_group", UserGroupViewSet)
router.register("user_group_image", UserGroupImageViewSet)
router.register("user_group_user", UserGroupUserViewSet)
router.register("organization", OrganizationViewSet)
router.register("organization_image", OrganizationImageViewSet)
router.register("organization_user", OrganizationUserViewSet)
router.register("event", EventViewSet)
router.register("event_user", EventUserViewSet)
router.register("event_image", EventImageViewSet)
router.register("shift", ShiftViewSet)
router.register("organization_event", OrganizationEventViewSet)
router.register("swap", SwapViewSet)

app_name = "api"
urlpatterns = router.urls