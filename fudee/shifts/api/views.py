from cgitb import lookup
from datetime import datetime, timedelta
from math import perm
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

from fudee.events.permissions import IsEventUser
from fudee.shifts.permissions import IsShiftUser

User = get_user_model()

class OrganizationEventViewSet(RetrieveModelMixin, ListModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Event.objects.all()
    lookup_field = "uuid"
    permission_classes = [permissions.IsAuthenticated, IsEventUser]
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = "__all__"
        
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return GetEventSerializer
        if self.action == 'create' or self.action == 'update':
            return CreateEventSerializer
    
    def get_object(self, *args, **kwargs):
        assert isinstance(self.request.user.uuid, uuid_lib.UUID)
        user = self.request.user
        event_user_obj = None
        
        try:
            event_user_obj = EventUser.objects.get(Q(user=user) & Q(event__uuid=self.kwargs['uuid']))
        except EventUser.DoesNotExist:
            raise http.Http404
        
        self.check_object_permissions(self.request, event_user_obj)
        event_obj = None
        
        try:
            event_obj = self.queryset.get(uuid=self.kwargs['uuid'])
        except Event.DoesNotExist:
            raise http.Http404

        return event_obj
        
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
        try:
            data.pop('user')
        except:
            pass
        data['updater_id'] = self.request.user.id
        instance = None
        
        try:
            instance = self.get_object()
        except Event.DoesNotExist:
            Response(status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CreateEventSerializer(instance=instance, data=data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)


class ShiftViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Shift.objects.all()
    lookup_field = "uuid"
    permission_classes = [permissions.IsAuthenticated, IsEventUser]
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return GetShiftSerializer
        if self.action == 'create' or self.action == 'update':
            return CreateShiftSerializer
    
    def get_object(self, *args, **kwargs):
        assert isinstance(self.request.user.uuid, uuid_lib.UUID)
        user = self.request.user
        
        shift_obj = None
        
        try:
            shift_obj = self.queryset.get(uuid=self.kwargs['uuid'])
        except Event.DoesNotExist:
            raise http.Http404
        
        # event_user_obj = None
        # try:
        #     event_user_obj = EventUser.objects.get(Q(user=user) & Q(event=shift_obj.event))
        # except EventUser.DoesNotExist:
        #     raise http.Http404
        # self.check_object_permissions(self.request, event_user_obj)
        
        # if self.request.method == 'PUT' or self.request.method == 'PATCH' or self.request.method == 'DELETE':
        #     try:
        #         OrganizationUser.objects.filter(Q(organization__uuid=self.request.data['organization']) & Q(user__uuid=self.request.data['employee'])).first()
        #     except OrganizationUser.DoesNotExist:
        #         return http.Http404
        #     try:
        #         event_user_obj = EventUser.objects.get(Q(user=self.request.data['employee']) & Q(event=shift_obj.event))
        #     except EventUser.DoesNotExist:
        #         raise http.Http404
        #     self.check_object_permissions(self.request, event_user_obj)

        return shift_obj
    
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
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user is OrganizationAdmin
        try:
            org_user = OrganizationUser.objects.filter(Q(organization__uuid=data['organization']) & Q(user__uuid=self.request.user.uuid)).first()
        except OrganizationUser.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if org_user.access < 2:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = self.get_object()
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CreateShiftSerializer(instance=instance, data=data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)