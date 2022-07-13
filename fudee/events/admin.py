from django.contrib import admin
from fudee.events.models import Event, EventUser, EventImage

admin.site.register(Event)
admin.site.register(EventUser)
admin.site.register(EventImage)