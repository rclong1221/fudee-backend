import uuid
from django.contrib.auth import get_user_model
from rest_framework import serializers
from fudee.relationships.models import Invite, \
    Relationship, UserGroup, UserGroupUser, UserGroupImage
from fudee.users.api.serializers import UserSerializer
    
from phonenumber_field.modelfields import PhoneNumberField
from datetime import datetime

User = get_user_model()

class GetInviteSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    phone = PhoneNumberField()
    
    class Meta:
        model = Invite
        fields = ["uuid", "user", "email", "phone", "accepted", "date_created"]

class CreateInviteSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    user = serializers.UUIDField(format="hex_verbose")
    email = serializers.EmailField(max_length=254, write_only=True)
    phone = PhoneNumberField()
    accepted = serializers.BooleanField(read_only=True)
    date_created = serializers.DateField(read_only=True)
    
    def create(self, validated_data):
        """
        """
        user = User.objects.get(uuid=validated_data['user'])
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
    updater = UserSerializer()
    
    class Meta:
        model = Relationship
        fields = ["uuid", "user1", "user2", "relationship", "date_created", "date_accepted", "date_updated", "updater"]

class CreateRelationshipSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    user1 = serializers.UUIDField(format="hex_verbose")
    user2 = serializers.UUIDField(format="hex_verbose")
    date_created = serializers.DateField(read_only=True)
    date_accepted = serializers.DateField(read_only=True)
    date_updated = serializers.DateField(read_only=True)
    updater = serializers.UUIDField(format="hex_verbose", required=False)
    
    def create(self, validated_data):
        """
        """
        user1 = User.objects.get(uuid=validated_data['user1'])
        user2 = User.objects.get(uuid=validated_data['user2'])
        data = Relationship.objects.create(
            user1=user1,
            user2=user2,
            relationship=validated_data['relationship'],
            date_updated=datetime.now().strftime("%Y-%m-%d"),
            updater=validated_data['updater'],
        )
        return data
    
    def update(self, instance, validated_data):
        instance.relationship = validated_data.get('relationship', instance.relationship)
        instance.date_updated = datetime.now().strftime("%Y-%m-%d")
        instance.updater = validated_data.get('updater', instance.updater)
        instance.save()
        return instance
    
    class Meta:
        model = Relationship
        fields = ["uuid", "user1", "user2", "relationship", "date_created", "date_accepted", "date_updated", "updater"]

class GetUserGroupSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    
    class Meta:
        model = UserGroup
        fields = ["uuid", "name", "creator", "date_created", "primary_image"]

class CreateUserGroupSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    name = serializers.CharField()
    creator = serializers.UUIDField(format="hex_verbose")
    date_created = serializers.DateField(read_only=True)
    
    def create(self, validated_data):
        """
        """
        user = User.objects.get(uuid=validated_data['creator'])
        data = UserGroup.objects.create(
            name=validated_data['name'],
            creator=user,
        )
        return data
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance
    
    class Meta:
        model = UserGroup
        fields = ["uuid", "name", "creator", "date_created"]

class GetUserGroupUserSerializer(serializers.ModelSerializer):
    group = GetUserGroupSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    updater = UserSerializer()
    
    class Meta:
        model = UserGroupUser
        fields = ["uuid", "group", "user", "access", "is_active", "date_created", "date_accepted", "date_updated", "updater"]

class CreateUserGroupUserSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    group = serializers.UUIDField(format="hex_verbose")
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
        group = UserGroup.objects.get(uuid=validated_data['group'])
        data = UserGroupUser.objects.create(
            group=group,
            user=user,
            access=validated_data['access'],
            is_active=validated_data['is_active'],
            date_updated=datetime.now().strftime("%Y-%m-%d"),
            updater=validated_data['updater'],
        )
        return data

    def update(self, instance, validated_data):
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.date_updated = datetime.now().strftime("%Y-%m-%d")
        instance.updater = validated_data.get('updater', instance.updater)
        instance.save()
        return instance
    
    class Meta:
        model = UserGroupUser
        fields = ["uuid", "group", "user", "access", "is_active", "date_created", "date_accepted", "date_updated", "updater"]
        
class UserGroupImageSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    image = serializers.ImageField()
    user_group = serializers.UUIDField(format="hex_verbose")
    date_created = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        """
        """
        user_group = UserGroup.objects.get(uuid=validated_data['user_group'])
        data = UserGroupImage.objects.create(
            image=validated_data['image'],
            user_group=user_group
        )
        return data
    
    class Meta:
        model = UserGroupImage
        fields = ["uuid", "image", "user_group", "date_created"]