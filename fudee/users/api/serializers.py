from django.contrib.auth import get_user_model
from rest_framework import serializers

from fudee.users.models import User_Image

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    date_updated = serializers.DateTimeField(read_only=True)
    url = serializers.CharField(read_only=True)
    primary_image = serializers.UUIDField(format="hex_verbose", read_only=True)
    
    class Meta:
        model = User
        fields = ["uuid", "username", "name", "first_name", "last_name", "middle_name", "is_active", "date_updated", "primary_image", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "uuid"}
        }

class UserImageSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex_verbose", read_only=True)
    image = serializers.ImageField()
    user = serializers.UUIDField(format="hex_verbose")
    date_created = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        """
        """
        user = User.objects.get(uuid=validated_data['user'])
        data = User_Image.objects.create(
            image=validated_data['image'],
            user=user
        )
        return data
    
    class Meta:
        model = User_Image
        fields = ["uuid", "image", "user", "date_created"]