from django.contrib.auth import get_user_model
from rest_framework import serializers

from fudee.shifts.models import Shift, Swap
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
    updater = UserSerializer(read_only=True)
    employee = UserSerializer(read_only=True)
    event = GetEventSerializer(read_only=True)
    organization = GetOrganizationSerializer(read_only=True)
    
    class Meta:
        model = Shift
        fields =  ["uuid", "employee", "organization", "event", "date_updated", "updater"]

class CreateShiftSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    employee = serializers.UUIDField(format="hex_verbose", required=False)
    organization = serializers.UUIDField(format="hex_verbose", required=False)
    event = serializers.UUIDField(format="hex_verbose")
    date_updated = serializers.DateField(read_only=True)
    updater = serializers.UUIDField(format="hex_verbose", required=False)
    
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
        updater = User.objects.get(uuid=validated_data.get('updater', instance.updater))
        employee = User.objects.get(uuid=validated_data['employee'])
        organization = Organization.objects.get(uuid=validated_data['organization'])
        instance.employee = employee
        instance.organization = organization
        instance.date_updated = datetime.now().strftime("%Y-%m-%d")
        instance.updater = updater
        instance.save()
        return instance
    
    class Meta:
        model = Shift
        fields =  ["uuid", "employee", "organization", "event", "date_updated", "updater"]
    
class GetSwapSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    old_employee = UserSerializer(read_only=True)
    new_employee = UserSerializer(read_only=True)
    shift = GetShiftSerializer(read_only=True)
    is_approved = serializers.BooleanField(read_only=True)
    date_created = serializers.DateField(read_only=True)
    date_updated = serializers.DateField(read_only=True)
    manager = UserSerializer(read_only=True)
    
    class Meta:
        model = Shift
        fields =  ["uuid", "old_employee", "new_employee", "shift", "is_approved", "date_created", "date_updated", "manager"]

class CreateSwapSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    old_employee = serializers.UUIDField(format="hex_verbose")
    new_employee = serializers.UUIDField(format="hex_verbose", required=False)
    shift = serializers.UUIDField(format="hex_verbose")
    is_approved = serializers.BooleanField(required=False)
    date_updated = serializers.DateField(read_only=True)
    manager = serializers.UUIDField(format="hex_verbose", required=False)
    
    def create(self, validated_data):
        """
        """
        old_employee = User.objects.get(uuid=validated_data['old_employee'])
        shift = Shift.objects.get(uuid=validated_data['shift'])
        data = Swap.objects.create(
            old_employee=old_employee,
            shift=shift,
            is_approved=False,
            date_updated=datetime.now().strftime("%Y-%m-%d")
        )
        return data
    
    def update(self, instance, validated_data):
        new_employee = User.objects.get(uuid=validated_data['new_employee'])
        manager = User.objects.get(uuid=validated_data['manager'])
        instance.new_employee = new_employee
        instance.is_approved = True
        instance.date_updated = datetime.now().strftime("%Y-%m-%d")
        instance.manager = manager
        instance.save()
        return instance
    
    class Meta:
        model = Shift
        fields =  ["uuid", "old_employee", "new_employee", "shift", "is_approved", "date_updated", "manager"]