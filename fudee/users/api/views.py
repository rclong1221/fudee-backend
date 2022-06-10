from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .serializers import UserSerializer

User = get_user_model()



class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "uuid"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.uuid, uuid_lib.UUID)
        try:
            if self.request.method == 'GET':
                return self.queryset.filter(uuid=self.request.user.uuid)
        except User.DoesNotExist:
            raise http.Http404
    
    def get_object(self, *args, **kwargs):
        assert isinstance(self.request.user.uuid, uuid_lib.UUID)
        try:
            return User.objects.get(uuid=self.request.user.uuid)
        except User.DoesNotExist:
            raise http.Http404
    
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
