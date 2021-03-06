from django.contrib.auth import get_user_model
from rest_framework import serializers
from fudee.events.models import Event, EventUser, EventImage

from fudee.users.api.serializers import UserSerializer

from datetime import datetime

User = get_user_model()

class GetEventSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    recurrences = serializers.CharField()
    
    class Meta:
        model = Event
        fields = ["uuid", "title", "description", "location", "recurrences", "primary_image", "date_start", "date_end", "user", "date_created", "date_updated", "updater"]

class CreateEventSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    user = serializers.UUIDField(format="hex_verbose")
    recurrences = serializers.CharField(allow_blank=True)
    date_updated = serializers.DateField(read_only=True)
    updater = serializers.UUIDField(format="hex_verbose", required=False)
    
    ["uuid", "title", "description", "location", "recurrences", "date_start", "date_end", "user", "date_updated", "updater"]
    
    def create(self, validated_data):
        """
        """
        user = User.objects.get(uuid=validated_data['user'])
        data = Event.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            location=validated_data['location'],
            recurrences=validated_data['recurrences'],
            date_start=validated_data['date_start'],
            date_end=validated_data['date_end'],
            user=user,
            date_updated=datetime.now().strftime("%Y-%m-%d"),
            updater=user,
        )
        return data

    def update(self, instance, validated_data):
        updater = User.objects.get(uuid=validated_data.get('updater', instance.updater))
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.location = validated_data.get('location', instance.location)
        instance.recurrences = validated_data.get('recurrences', instance.recurrences)
        instance.date_start = validated_data.get('date_start', instance.date_start)
        instance.date_end = validated_data.get('date_end', instance.date_end)
        instance.date_updated = datetime.now().strftime("%Y-%m-%d")
        instance.updater = updater
        instance.save()
        return instance
    
    class Meta:
        model = Event
        fields = ["uuid", "title", "description", "location", "recurrences", "date_start", "date_end", "user", "date_updated", "updater"]

class GetEventUserSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    access = serializers.IntegerField(read_only=True)
    event = GetEventSerializer(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    date_accepted = serializers.DateField(read_only=True)
    date_updated = serializers.DateField(read_only=True)
    updater = UserSerializer()
    
    class Meta:
        model = EventUser
        fields = ["uuid", "event", "user", "access", "is_active", "date_created", "date_accepted", "date_updated", "updater"]

class CreateEventUserSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    event = serializers.UUIDField(format="hex_verbose")
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
        event = Event.objects.get(uuid=validated_data['event'])
        updater = User.objects.get(uuid=validated_data['updater'])
        data = EventUser.objects.create(
            event=event,
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
        model = EventUser
        fields = ["uuid", "event", "user", "access", "is_active", "date_created", "date_accepted", "date_updated", "updater"]
        
class EventImageSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    image = serializers.ImageField()
    event = serializers.UUIDField(format="hex_verbose")
    date_created = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        """
        """
        event = Event.objects.get(uuid=validated_data['event'])
        data = EventImage.objects.create(
            image=validated_data['image'],
            event=event
        )
        return data
    
    class Meta:
        model = EventImage
        fields = ["uuid", "image", "event", "date_created"]