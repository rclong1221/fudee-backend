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

import uuid as uuid_lib

from fudee.organizations.api.serializers import \
    GetOrganizationSerializer, CreateOrganizationSerializer, \
    GetOrganizationUserSerializer, CreateOrganizationUserSerializer

from fudee.organizations.models import \
    Organization, OrganizationUser

User = get_user_model()

class OrganizationViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Organization.objects.all()
    lookup_field = "uuid"
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = []
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return GetOrganizationSerializer
        if self.action == 'create' or self.action == 'update':
            return CreateOrganizationSerializer
    
    def list(self, *args, **kwargs):
        serializer = GetOrganizationSerializer(self.get_queryset(), many=True, context={'request': self.request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, *args, **kwargs):
        data = self.request.data
        data['updater_id'] = self.request.user.id
        serializer = CreateOrganizationSerializer(data=data)
        
        if serializer.is_valid():
            org_obj = serializer.save()
            # Create Organization entry for creator
            org = Organization.objects.get(id=org_obj.id)
            # Create OrganizationUser entry
            org_user = {
                'organization': org.id,
                'user': self.request.user.id,
                'access': 2,     #admin
                'is_active': True,
                'updater_id': self.request.user.id,
            }
            gs = CreateOrganizationUserSerializer(data=org_user)
            if gs.is_valid():
                gs.save()
                return Response(status=status.HTTP_201_CREATED)
            else:
                org.delete()
                return Response(status=status.HTTP_409_CONFLICT)
        
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
    
    def update(self, *args, **kwargs):
        data = {key: self.request.data[key] for key in self.request.data.keys() & {'organization'}}
        data['uuid'] = self.kwargs['uuid']
        data['updater_id'] = self.request.user.id
        instance = None
        
        try:
            instance = self.queryset.get(uuid=data['uuid'])
        except self.queryset.DoesNotExist:
            Response(status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: Check if user is authorized to edit Organization through OrganizationUsers table
        # if self.request.user.id != instance.user1.id and self.request.user.id != instance.user2.id:
        #     return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = CreateOrganizationSerializer(instance=instance, data=data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

class OrganizationUserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = OrganizationUser.objects.all()
    lookup_field = "uuid"
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'organization']

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return GetOrganizationUserSerializer
        if self.action == 'create' or self.action == 'update':
            return CreateOrganizationUserSerializer

    # def get_queryset(self, *args, **kwargs):
    #     assert isinstance(self.request.user.id, int)
    #     return self.queryset.filter(id=self.request.user.id)
    
    def create(self, *args, **kwargs):
        # if user has R+W (1) or is admin (2)
        data = self.request.data
        data['updater_id'] = self.request.user.id
        max_access = -1
        try:
            instance = self.queryset.get(user=self.request.user.id, access__gte=1)
            max_access = instance.access
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if data['access'] > max_access:
            data['access'] = max_access
        
        data['is_active'] = False
        
        serializer = CreateOrganizationUserSerializer(data=data)

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
        
        if self.request.user.id != instance.user.id:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = CreateOrganizationUserSerializer(instance=instance, data=data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

    @action(detail=False)
    def me(self, request):
        serializer = GetOrganizationUserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)