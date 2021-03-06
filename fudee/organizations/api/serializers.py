import uuid
from django.contrib.auth import get_user_model
from rest_framework import serializers
from fudee.organizations.models import Organization, OrganizationUser, OrganizationImage

from fudee.users.api.serializers import UserSerializer
    
from phonenumber_field.modelfields import PhoneNumberField
from datetime import datetime

User = get_user_model()

class GetOrganizationSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    name = serializers.CharField(read_only=True)
    image = serializers.FileField(read_only=True)
    date_created = serializers.DateField(read_only=True)
    date_updated = serializers.DateField(read_only=True)
    updater = UserSerializer(read_only=True)
    
    class Meta:
        model = Organization
        fields = ["uuid", "name", "image", "date_created", "date_updated", "updater", "primary_image"]

class CreateOrganizationSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    name = serializers.CharField(max_length=254, allow_blank=False)
    date_created = serializers.DateField(read_only=True)
    date_updated = serializers.DateField(read_only=True)
    updater = serializers.UUIDField(format="hex_verbose", required=False)
    
    def create(self, validated_data):
        """
        """
        updater = User.objects.get(uuid=validated_data['updater'])
        data = Organization.objects.create(
            updater=updater,
            name=validated_data['name'],
        )
        return data
    
    def update(self, instance, validated_data):
        updater = User.objects.get(uuid=validated_data.get('updater', instance.updater))
        instance.name = validated_data.get('name', instance.name)
        instance.date_updated = datetime.now().strftime("%Y-%m-%d")
        instance.updater = updater
        instance.save()
        return instance
    
    class Meta:
        model = Organization
        fields = ["uuid", "name", "date_created", "date_updated", "updater"]

class GetOrganizationUserSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    organization = GetOrganizationSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    access = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    date_accepted = serializers.DateField(read_only=True)
    date_updated = serializers.DateField(read_only=True)
    updater = UserSerializer(read_only=True)
    
    class Meta:
        model = OrganizationUser
        fields = ["uuid", "organization", "user", "access", "is_active", "date_created", "date_accepted", "date_updated", "updater"]

class CreateOrganizationUserSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    organization = serializers.UUIDField(format="hex_verbose")
    user = serializers.UUIDField(format="hex_verbose")
    access = serializers.IntegerField()
    is_active = serializers.BooleanField()
    date_accepted = serializers.DateField(read_only=True)
    date_updated = serializers.DateField(read_only=True)
    updater = serializers.UUIDField(format="hex_verbose", required=False)
    
    def create(self, validated_data):
        """
        """
        user = User.objects.get(uuid=validated_data['user'])
        organization = Organization.objects.get(uuid=validated_data['organization'])
        updater = User.objects.get(uuid=validated_data['updater'])
        data = OrganizationUser.objects.create(
            organization=organization,
            user=user,
            access=validated_data['access'],
            is_active=validated_data['is_active'],
            date_updated=datetime.now().strftime("%Y-%m-%d"),
            updater=updater,
        )
        return data

    def update(self, instance, validated_data):
        updater = User.objects.get(uuid=validated_data.get('updater', instance.updater))
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.date_updated = datetime.now().strftime("%Y-%m-%d")
        instance.updater = updater
        instance.save()
        return instance
    
    class Meta:
        model = OrganizationUser
        fields = ["uuid", "organization", "user", "access", "is_active", "date_created", "date_accepted", "date_updated", "updater"]

class OrganizationImageSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    image = serializers.ImageField()
    organization = serializers.UUIDField(format="hex_verbose")
    date_created = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        """
        """
        organization = Organization.objects.get(uuid=validated_data['organization'])
        data = OrganizationImage.objects.create(
            image=validated_data['image'],
            organization=organization
        )
        return data
    
    class Meta:
        model = OrganizationImage
        fields = ["uuid", "image", "organization", "date_created"]