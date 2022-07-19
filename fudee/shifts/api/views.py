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
    
from fudee.shifts.models import Shift

from fudee.shifts.api.serializers import GetShiftSerializer, CreateShiftSerializer

from fudee.organizations.models import Organization, OrganizationUser

User = get_user_model()

class OrganizationEventViewSet(RetrieveModelMixin, ListModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
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
        
        # Create Event entry
        serializer = CreateEventSerializer(data=data)
        
        if serializer.is_valid():
            event_obj = serializer.save()
        
            # Create EventUser entry
            event_user = {
                'event': event_obj.uuid,
                'user': self.request.user.uuid,
                'access': 2,     #admin
                'is_active': True,
                'updater_id': self.request.user.id,
            }
            eu_serializer = CreateEventUserSerializer(data=event_user)
            if eu_serializer.is_valid():
                eu_obj = eu_serializer.save()
                
                # Create Shift entry
                shift = {
                    # 'employee': None,
                    # 'organization': None,
                    'event': event_obj.uuid,
                    'updater_id': self.request.user.id
                }
                
                shift_serializer = CreateShiftSerializer(data=shift)
                if shift_serializer.is_valid():
                    shift_serializer.save()
                    
                    return Response(status=status.HTTP_201_CREATED)
                else:
                    eu = EventUser.objects.get(uuid=eu_obj.uuid)
                    eu.delete()
                    
                    event = Event.objects.get(uuid=event_obj.uuid)
                    event.delete()
                    return Response(status=status.HTTP_409_CONFLICT)
            else:
                event = Event.objects.get(uuid=event_obj.uuid)
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


class ShiftViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Shift.objects.all()
    lookup_field = "uuid"
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return GetShiftSerializer
        if self.action == 'create' or self.action == 'update':
            return CreateShiftSerializer
        
    def update(self, *args, **kwargs):
        data = self.request.data
        data['uuid'] = self.kwargs['uuid']
        data['updater_id'] = self.request.user.id
        instance = None
        
        org_user = None
        
        # Check if employee is in OrganizationUser
        try:
            org_user = OrganizationUser.objects.filter(Q(organization__uuid=data['organization']) & Q(user__uuid=data['employee'])).first()
        except OrganizationUser.DoesNotExist:
            print("\n\n\nhere1")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user is OrganizationAdmin
        try:
            org_user = OrganizationUser.objects.filter(Q(organization__uuid=data['organization']) & Q(user__uuid=self.request.user.uuid)).first()
        except OrganizationUser.DoesNotExist:
            print("\n\n\nhere2")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if org_user.access < 2:
            print("\n\n\nhere3")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            print(data['uuid'])
            instance = self.queryset.get(uuid=data['uuid'])
        except:
            print("\n\n\nhere4")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        # if self.request.user.uuid != instance.user.uuid:
        #     return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = CreateShiftSerializer(instance=instance, data=data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)