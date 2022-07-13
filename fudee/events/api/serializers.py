from django.contrib.auth import get_user_model
from rest_framework import serializers
from fudee.events.models import Event

from datetime import datetime

User = get_user_model()

class GetEventSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    recurrences = serializers.CharField()
    
    class Meta:
        model = Event
        fields = ["uuid", "title", "description", "location", "recurrences", "primary_image", "date_start", "date_end", "user", "date_created", "date_updated", "updater_id"]