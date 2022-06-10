import uuid
from django.contrib.auth import get_user_model
from rest_framework import serializers
from fudee.relationships.models import Invite, \
    Relationship
from fudee.users.api.serializers import UserSerializer

from phonenumber_field.modelfields import PhoneNumberField
from datetime import datetime

class GetInviteSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    phone = PhoneNumberField()
    
    class Meta:
        model = Invite
        fields = ["uuid", "user", "email", "phone", "accepted", "date_created"]

class CreateInviteSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    user = serializers.IntegerField()
    email = serializers.EmailField(max_length=254, write_only=True)
    phone = PhoneNumberField()
    accepted = serializers.BooleanField(read_only=True)
    date_created = serializers.DateField(read_only=True)
    
    def create(self, validated_data):
        """
        """
        user = User.objects.get(id=validated_data['user'])
        data = Invite.objects.create(
            user=user,
            email=validated_data['email'],
            phone=validated_data['phone'],
        )
        return data
    
    class Meta:
        model = Invite
        fields = ["uuid", "user", "email", "phone", "accepted", "date_created"]


class GetRelationshipSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    user1 = UserSerializer()
    user2 = UserSerializer()
    relationship = serializers.IntegerField()
    date_created = serializers.DateField(read_only=True)
    
    class Meta:
        model = Relationship
        fields = ["uuid", "user1", "user2", "relationship", "date_created", "date_accepted", "date_updated", "updater_id"]

class CreateRelationshipSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose")
    user1 = serializers.IntegerField()
    user2 = serializers.IntegerField()
    relationship = serializers.IntegerField()
    date_created = serializers.DateField(read_only=True)
    date_accepted = serializers.DateField(read_only=True)
    date_updated = serializers.DateField(read_only=True)
    updater_id = serializers.IntegerField()
    
    def create(self, validated_data):
        """
        """
        user1 = User.objects.get(id=validated_data['user1'])
        user2 = User.objects.get(id=validated_data['user2'])
        data = Relationship.objects.create(
            user1=user1,
            user2=user2,
            relationship=validated_data['relationship'],
            updater_id=user1.id,
        )
        return data
    
    def update(self, instance, validated_data):
        instance.relationship = validated_data.get('relationship', instance.relationship)
        instance.date_updated = datetime.now().strftime("%Y-%m-%d")
        instance.updater_id = validated_data.get('updater_id', instance.updater_id)
        instance.save()
        return instance
    
    class Meta:
        model = Relationship
        fields = ["uuid", "user1", "user2", "relationship", "date_created", "date_accepted", "date_updated", "updater_id"]
