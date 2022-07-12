from django.contrib import admin
from fudee.organizations.models import Organization, OrganizationUser, Organization_Image

admin.site.register(Organization)
admin.site.register(OrganizationUser)
admin.site.register(Organization_Image)