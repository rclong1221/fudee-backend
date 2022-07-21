from django.contrib.auth import get_user_model
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.parsers import MultiPartParser, FileUploadParser
from django.db.models import Q

from fudee.users.api.serializers import UserSerializer, UserImageSerializer

from fudee.users.models import User_Image

from fudee.users.permissions import IsUserOwner, IsUserImageOwner

User = get_user_model()

import uuid as uuid_lib

class UserViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "uuid"
    permission_classes = [permissions.IsAuthenticated, IsUserOwner]
    
    def get_object(self, *args, **kwargs):
        assert isinstance(self.request.user.uuid, uuid_lib.UUID)
        obj = None
        try:
            obj =  User.objects.get(uuid=self.kwargs['uuid'])
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(self.request, obj)
        return obj
    
    def update(self, *args, **kwargs):
        user = self.get_object()
        serializer = UserSerializer(user, data=self.request.data, context={'request': self.request})
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, *args, **kwargs):
        user = self.get_object()
        try:
            user.soft_delete()
            return Response(status=status.HTTP_202_ACCEPTED)
        except self.queryset.DoesNotExist:
            Response(status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserSerializer(user, data=data, context={'request': self.request})
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT, data=serializer.data)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

class UserImageViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = UserImageSerializer
    queryset = User_Image.objects.all()
    lookup_field = "uuid"
    parser_classes = (MultiPartParser, FileUploadParser)
    permission_classes = [permissions.IsAuthenticated, IsUserImageOwner]
    
    def get_object(self, *args, **kwargs):
        assert isinstance(self.request.user.uuid, uuid_lib.UUID)
        obj = None
        try:
            obj = self.queryset.get(uuid=self.kwargs['uuid'])
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        self.check_object_permissions(self.request, obj)
        return obj
    
    def retrieve(self, *args, **kwargs):
        try:
            ui = self.get_object()
        except User_Image.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        user_image = {
            'uuid': ui.uuid,
            'user': ui.user.uuid,
            'image': ui.image,
            'date_created': ui.date_created
        }

        serializer = UserImageSerializer(data=user_image)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
    
    def create(self, *args, **kwargs):
        # if user has R+W (1) or is admin (2)
        data = self.request.data.copy()
        data['user'] = self.request.user.uuid
        
        serializer = UserImageSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)