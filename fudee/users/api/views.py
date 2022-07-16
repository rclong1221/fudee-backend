from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser

from fudee.users.api.serializers import UserSerializer, UserImageSerializer

from fudee.users.models import User_Image

User = get_user_model()

import uuid as uuid_lib

class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "uuid"

    # def get_queryset(self, *args, **kwargs):
    #     assert isinstance(self.request.user.uuid, uuid_lib.UUID)
    #     try:
    #         if self.request.method == 'GET':
    #             return self.queryset.filter(uuid=self.request.user.uuid)
    #     except User.DoesNotExist:
    #         raise http.Http404
    
    def get_object(self, *args, **kwargs):
        assert isinstance(self.request.user.uuid, uuid_lib.UUID)
        try:
            return User.objects.get(uuid=self.request.user.uuid)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
    def update(self, *args, **kwargs):
        user = self.get_object(self.request.user.uuid)
        serializer = UserSerializer(user, data=self.request.data, context={'request': self.request})
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, *args, **kwargs):
        user = self.get_object(self.request.user.uuid)
        data = dict(self.get_object(self.request.user.uuid))
        # data.is_active = False # TODO: move to serializer or something
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
    
    def get_object(self, *args, **kwargs):
        assert isinstance(self.request.user.uuid, uuid_lib.UUID)
        try:
            return User_Image.objects.get(uuid=self.request.user.uuid)
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, *args, **kwargs):
        ui = User_Image.objects.filter(user__uuid=self.request.user.uuid).latest('date_created')
        
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