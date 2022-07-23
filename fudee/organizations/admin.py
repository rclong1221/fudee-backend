from django.contrib import admin
from fudee.organizations.models import Organization, OrganizationUser, OrganizationImage

admin.site.register(Organization)
admin.site.register(OrganizationUser)
admin.site.register(OrganizationImage)