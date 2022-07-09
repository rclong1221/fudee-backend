from django.contrib import admin
from fudee.organizations.models import Organization, OrganizationUser

admin.site.register(Organization)
admin.site.register(OrganizationUser)