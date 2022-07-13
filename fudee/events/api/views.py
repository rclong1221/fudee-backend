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
    GetEventSerializer, CreateEventSerializer

from fudee.events.models import \
    Event

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
        data['user'] = self.request.user.id
        data['updater_id'] = self.request.user.id
        
        print("\n\n\n")
        print(data)
        print("\n\n\n")
        serializer = CreateEventSerializer(data=data)
        
        if serializer.is_valid():
            event_obj = serializer.save()
            
            return Response(status=status.HTTP_201_CREATED)
        
            # # Create Event entry for creator
            # event = Event.objects.get(id=event_obj.id)
            # # Create EventUser entry
            # event_user = {
            #     'event': event.id,
            #     'user': self.request.user.id,
            #     'access': 2,     #admin
            #     'is_active': True,
            #     'updater_id': self.request.user.id,
            # }
            # gs = CreateEventUserSerializer(data=event_user)
            # if gs.is_valid():
            #     eu = gs.save()
            #     return Response(status=status.HTTP_201_CREATED)
            # else:
            #     event.delete()
            #     return Response(status=status.HTTP_409_CONFLICT)
        
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)