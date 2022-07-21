from django.contrib.auth import get_user_model
from rest_framework import serializers

from fudee.shifts.models import Shift
from fudee.organizations.models import Organization
from fudee.events.models import Event

from datetime import datetime

from fudee.organizations.api.serializers import GetOrganizationSerializer
from fudee.users.api.serializers import UserSerializer
from fudee.events.api.serializers import GetEventSerializer

User = get_user_model()

class GetShiftSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    date_updated = serializers.DateField(read_only=True)
    updater_id = serializers.IntegerField(read_only=True)
    employee = UserSerializer(read_only=True)
    event = GetEventSerializer(read_only=True)
    organization = GetOrganizationSerializer(read_only=True)
    
    class Meta:
        model = Shift
        fields =  ["uuid", "employee", "organization", "event", "date_updated", "updater_id"]

class CreateShiftSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    employee = serializers.UUIDField(format="hex_verbose", required=False)
    organization = serializers.UUIDField(format="hex_verbose", required=False)
    event = serializers.UUIDField(format="hex_verbose")
    date_updated = serializers.DateField(read_only=True)
    updater_id = serializers.IntegerField()
    
    def create(self, validated_data):
        """
        """
        # employee = User.objects.get(uuid=validated_data['employee'])
        # organization = Organization.objects.get(uuid=validated_data['organization'])
        event = Event.objects.get(uuid=validated_data['event'])
        data = Shift.objects.create(
            # employee=employee,
            # organization=organization,
            event=event,
            date_updated=datetime.now().strftime("%Y-%m-%d")
        )
        return data
    
    def update(self, instance, validated_data):
        employee = User.objects.get(uuid=validated_data['employee'])
        organization = Organization.objects.get(uuid=validated_data['organization'])
        instance.employee = employee
        instance.organization = organization
        instance.date_updated = datetime.now().strftime("%Y-%m-%d")
        instance.updater_id = validated_data.get('updater_id', instance.updater_id)
        instance.save()
        return instance
    
    class Meta:
        model = Shift
        fields =  ["uuid", "employee", "organization", "event", "date_updated", "updater_id"]