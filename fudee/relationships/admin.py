from django.contrib import admin
from fudee.relationships.models import Invite, Relationship, UserGroup, UserGroupUser, UserGroupImage

admin.site.register(Invite)
admin.site.register(Relationship)
admin.site.register(UserGroup)
admin.site.register(UserGroupUser)
admin.site.register(UserGroupImage)