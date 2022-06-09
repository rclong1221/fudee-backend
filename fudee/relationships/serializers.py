import uuid
from django.contrib.auth import get_user_model
from rest_framework import serializers
from fudee.users.models import Invite
from fudee.users.serializers import UserSerializer

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

