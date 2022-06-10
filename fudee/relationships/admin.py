from django.contrib import admin
from fudee.relationships.models import Invite, Relationship, User_Group
admin.site.register(Invite)
admin.site.register(Relationship)
admin.site.register(User_Group)