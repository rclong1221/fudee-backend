import uuid
from django.contrib.auth import get_user_model
from rest_framework import serializers
from fudee.events.models import Event

from datetime import datetime

User = get_user_model()

class GetEventSerializer(serializers.ModelSerializer):
    recurrences = serializers.CharField()
    
    class Meta:
        model = Event
        fields = ["uuid", "title", "description", "location", "recurrences", "primary_image", "date_start", "date_end", "user", "date_created", "date_updated", "updater_id"]

# class GetOrganizationSerializer(serializers.ModelSerializer):
#     uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
#     name = serializers.CharField(read_only=True)
#     image = serializers.FileField(read_only=True)
#     date_created = serializers.DateField(read_only=True)
#     date_updated = serializers.DateField(read_only=True)
#     updater_id = serializers.IntegerField(read_only=True)
    
#     class Meta:
#         model = Organization
#         fields = ["uuid", "name", "image", "date_created", "date_updated", "updater_id", "primary_image"]

# class CreateOrganizationSerializer(serializers.ModelSerializer):
#     uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
#     name = serializers.CharField(max_length=254, allow_blank=False)
#     date_created = serializers.DateField(read_only=True)
#     date_updated = serializers.DateField(read_only=True)
#     updater_id = serializers.IntegerField()
    
#     def create(self, validated_data):
#         """
#         """
#         updater = User.objects.get(id=validated_data['updater_id'])
#         data = Organization.objects.create(
#             updater_id=updater.id,
#             name=validated_data['name'],
#         )
#         return data
    
#     def update(self, instance, validated_data):
#         instance.name = validated_data.get('name', instance.name)
#         instance.date_updated = datetime.now().strftime("%Y-%m-%d")
#         instance.updater_id = validated_data.get('updater_id', instance.updater_id)
#         instance.save()
#         return instance
    
#     class Meta:
#         model = Organization
#         fields = ["uuid", "name", "date_created", "date_updated", "updater_id"]

# # TODO: class UpdateOrganizationImageSerializer(serializers.ModelSerializer):

# class GetOrganizationUserSerializer(serializers.ModelSerializer):
#     uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
#     organization = serializers.IntegerField(read_only=True)
#     user = serializers.IntegerField(read_only=True)
#     access = serializers.IntegerField(read_only=True)
#     is_active = serializers.BooleanField(read_only=True)
#     date_accepted = serializers.DateField(read_only=True)
#     date_updated = serializers.DateField(read_only=True)
#     updater_id = serializers.IntegerField(read_only=True)
    
#     class Meta:
#         model = OrganizationUser
#         fields = ["uuid", "organization", "user", "access", "is_active", "date_created", "date_accepted", "date_updated", "updater_id"]

# class CreateOrganizationUserSerializer(serializers.ModelSerializer):
#     uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
#     organization = serializers.IntegerField()
#     user = serializers.IntegerField()
#     access = serializers.IntegerField()
#     is_active = serializers.BooleanField()
#     date_accepted = serializers.DateField(read_only=True)
#     date_updated = serializers.DateField(read_only=True)
#     updater_id = serializers.IntegerField()
    
#     def create(self, validated_data):
#         """
#         """
#         user = User.objects.get(id=validated_data['user'])
#         organization = Organization.objects.get(id=validated_data['group'])
#         data = OrganizationUser.objects.create(
#             organization=organization,
#             user=user,
#             access=validated_data['access'],
#             is_active=validated_data['is_active'],
#             date_updated=datetime.now().strftime("%Y-%m-%d"),
#             updater_id=validated_data['updater_id'],
#         )
#         return data

#     def update(self, instance, validated_data):
#         # instance.access = validated_data.get('access', instance.access)
#         instance.is_active = validated_data.get('is_active', instance.is_active)
#         instance.date_updated = datetime.now().strftime("%Y-%m-%d")
#         instance.updater_id = validated_data.get('updater_id', instance.updater_id)
#         instance.save()
#         return instance
    
#     class Meta:
#         model = OrganizationUser
#         fields = ["uuid", "organization", "user", "access", "is_active", "date_created", "date_accepted", "date_updated", "updater_id"]

# class OrganizationImageSerializer(serializers.ModelSerializer):
#     uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
#     image = serializers.ImageField()
#     organization = serializers.IntegerField()
#     date_created = serializers.DateTimeField(read_only=True)

#     def create(self, validated_data):
#         """
#         """
#         organization = Organization.objects.get(id=validated_data['organization'])
#         data = Organization_Image.objects.create(
#             image=validated_data['image'],
#             organization=organization
#         )
#         return data
    
#     class Meta:
#         model = Organization
#         fields = ["uuid", "image", "organization", "date_created"]