from django.contrib.auth import get_user_model
from rest_framework import serializers
from fudee.events.models import Event

from datetime import datetime

User = get_user_model()

class GetEventSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    recurrences = serializers.CharField()
    
    class Meta:
        model = Event
        fields = ["uuid", "title", "description", "location", "recurrences", "primary_image", "date_start", "date_end", "user", "date_created", "date_updated", "updater_id"]

class CreateEventSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    user = serializers.IntegerField()
    recurrences = serializers.CharField(allow_blank=True)
    date_updated = serializers.DateField(read_only=True)
    updater_id = serializers.IntegerField(read_only=True)
    
    ["uuid", "title", "description", "location", "recurrences", "date_start", "date_end", "user", "date_updated", "updater_id"]
    
    def create(self, validated_data):
        """
        """
        user = User.objects.get(id=validated_data['user'])
        data = Event.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            location=validated_data['location'],
            recurrences=validated_data['recurrences'],
            date_start=validated_data['date_start'],
            date_end=validated_data['date_end'],
            user=user,
            date_updated=datetime.now().strftime("%Y-%m-%d"),
            updater_id=user.id,
        )
        return data

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.location = validated_data.get('location', instance.location)
        instance.recurrences = validated_data.get('recurrences', instance.recurrences)
        instance.date_start = validated_data.get('date_start', instance.date_start)
        instance.date_end = validated_data.get('date_end', instance.date_end)
        instance.date_updated = datetime.now().strftime("%Y-%m-%d")
        instance.updater_id = validated_data.get('updater_id', instance.updater_id)
        instance.save()
        return instance
    
    class Meta:
        model = Event
        fields = ["uuid", "title", "description", "location", "recurrences", "date_start", "date_end", "user", "date_updated", "updater_id"]
