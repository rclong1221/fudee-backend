from django.contrib import admin
from fudee.events.models import Event, EventUser

admin.site.register(Event)
admin.site.register(EventUser)