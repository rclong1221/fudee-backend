from django.contrib.auth import get_user_model
from rest_framework import serializers

from fudee.shifts.models import Shift
from fudee.events.api.serializers import CreateEventSerializer

from datetime import datetime

User = get_user_model()

class GetShiftSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    date_updated = serializers.DateField(read_only=True)
    updater_id = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Shift
        fields =  ["uuid", "employee", "organization", "event", "date_updated", "updater_id"]

class CreateShiftSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    employee = serializers.IntegerField()
    organization = serializers.IntegerField()
    event = CreateEventSerializer()
    date_updated = serializers.DateField(read_only=True)
    updater_id = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Shift
        fields =  ["uuid", "employee", "organization", "event", "date_updated", "updater_id"]