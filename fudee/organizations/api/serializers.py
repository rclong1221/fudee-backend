import uuid
from django.contrib.auth import get_user_model
from rest_framework import serializers
from fudee.organizations.models import Organization
    
from phonenumber_field.modelfields import PhoneNumberField
from datetime import datetime

User = get_user_model()

class GetOrganizationSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    name = serializers.CharField(max_length=254, blank=False, null=False, read_only=True)
    image = serializers.FileField(read_only=True)
    date_created = serializers.DateField(read_only=True)
    date_updated = serializers.DateField(read_only=True)
    updater_id = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Organization
        fields = ["uuid", "name", "image", "date_created", "date_updated", "updater_id"]

class CreateOrganizationSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    name = serializers.CharField(max_length=254, blank=False, null=False)
    image = serializers.IntegerField()
    date_created = serializers.DateField(read_only=True)
    date_updated = serializers.DateField(read_only=True)
    updater_id = serializers.IntegerField()
    
    def create(self, validated_data):
        """
        """
        updater = User.objects.get(id=validated_data['updater_id'])
        data = Organization.objects.create(
            updater_id=updater.id,
            name=validated_data['name'],
        )
        return data
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.date_updated = datetime.now().strftime("%Y-%m-%d")
        instance.updater_id = validated_data.get('updater_id', instance.updater_id)
        instance.save()
        return instance
    
    class Meta:
        model = Organization
        fields = ["uuid", "name", "image", "date_created", "date_updated", "updater_id"]

# TODO: class UpdateOrganizationImageSerializer(serializers.ModelSerializer):