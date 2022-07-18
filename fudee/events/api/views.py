from cgitb import lookup
from datetime import datetime, timedelta
from multiprocessing import context
from operator import le
from django import http
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.parsers import MultiPartParser, FileUploadParser

import uuid as uuid_lib
    
from fudee.events.api.serializers import \
    GetEventSerializer, CreateEventSerializer, \
    GetEventUserSerializer, CreateEventUserSerializer, EventImageSerializer

from fudee.events.models import \
    Event, EventUser, EventImage

User = get_user_model()

class EventViewSet(RetrieveModelMixin, ListModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Event.objects.all()
    lookup_field = "uuid"
    permission_classes = [permissions.IsAuthenticated]
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = "__all__"
        
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return GetEventSerializer
        if self.action == 'create' or self.action == 'update':
            return CreateEventSerializer
        
    def create(self, *args, **kwargs):
        data = self.request.data.copy()
        data['user'] = self.request.user.uuid
        data['updater_id'] = self.request.user.id
        
        serializer = CreateEventSerializer(data=data)
        
        if serializer.is_valid():
            event_obj = serializer.save()
        
            # Create Event entry for creator
            event = Event.objects.get(uuid=event_obj.uuid)
            # Create EventUser entry
            event_user = {
                'event': event.uuid,
                'user': self.request.user.uuid,
                'access': 2,     #admin
                'is_active': True,
                'updater_id': self.request.user.id,
            }
            gs = CreateEventUserSerializer(data=event_user)
            if gs.is_valid():
                gs.save()
                return Response(status=status.HTTP_201_CREATED)
            else:
                event.delete()
                return Response(status=status.HTTP_409_CONFLICT)
        
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
    
    def update(self, *args, **kwargs):
        data = self.request.data.copy()
        data['uuid'] = self.kwargs['uuid']
        data.pop('user')
        data['updater_id'] = self.request.user.id
        instance = None
        
        try:
            instance = self.queryset.get(uuid=data['uuid'])
        except self.queryset.DoesNotExist:
            Response(status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: Check if user is authorized to edit Event through EventUsers table
        # if self.request.user.id != instance.user.id
        #     return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = CreateEventSerializer(instance=instance, data=data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

class EventUserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = EventUser.objects.all()
    lookup_field = "uuid"
    permission_classes = [permissions.IsAuthenticated]
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['user', 'event']

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return GetEventUserSerializer
        if self.action == 'create' or self.action == 'update':
            return CreateEventUserSerializer

    # def get_queryset(self, *args, **kwargs):
    #     assert isinstance(self.request.user.id, int)
    #     return self.queryset.filter(id=self.request.user.id)
    
    def create(self, *args, **kwargs):
        # if user has R+W (1) or is admin (2)
        data = self.request.data
        data['updater_id'] = self.request.user.id
        max_access = -1
        try:
            instance = self.queryset.get(user__uuid=self.request.user.uuid, access__gte=1)
            max_access = instance.access
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if data['access'] > max_access:
            data['access'] = max_access
        
        data['is_active'] = True
        
        serializer = CreateEventUserSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
    
    def update(self, *args, **kwargs):
        data = {key: self.request.data[key] for key in self.request.data.keys() & {'access', 'is_active'}}
        data['uuid'] = self.kwargs['uuid']
        data['updater_id'] = self.request.user.id
        instance = None

        try:
            instance = self.queryset.get(uuid=data['uuid'])
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if self.request.user.uuid != instance.user.uuid:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = CreateEventUserSerializer(instance=instance, data=data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

    @action(detail=False)
    def me(self, request):
        serializer = GetEventUserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

class EventImageViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = EventImageSerializer
    queryset = EventImage.objects.all()
    parser_classes = (MultiPartParser, FileUploadParser)
    lookup_field = "uuid"
    
    def create(self, *args, **kwargs):
        data = self.request.data
        event = None
        event_user = None
        
        try:
            event = Event.objects.filter(uuid=data['event'])[0]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        try:
            event_user = EventUser.objects.filter(Q(event__uuid=event.uuid) & Q(user__uuid=self.request.user.uuid))[0]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if event_user.access != 2:
            return Response(status.HTTP_404_NOT_FOUND)
        
        serializer = EventImageSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)