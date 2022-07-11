from django.contrib import admin
from fudee.relationships.models import Invite, Relationship, User_Group, User_Group_User, User_Group_Image

admin.site.register(Invite)
admin.site.register(Relationship)
admin.site.register(User_Group)
admin.site.register(User_Group_User)
admin.site.register(User_Group_Image)