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

from fudee.organizations.api.serializers import \
    GetOrganizationSerializer, CreateOrganizationSerializer, \
    GetOrganizationUserSerializer, CreateOrganizationUserSerializer, OrganizationImageSerializer

from fudee.organizations.models import \
    Organization, OrganizationUser, OrganizationImage
    
from fudee.organizations.permissions import IsOrganizationUser

User = get_user_model()

class OrganizationViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Organization.objects.all()
    lookup_field = "uuid"
    permission_classes = [permissions.IsAuthenticated, IsOrganizationUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = []
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return GetOrganizationSerializer
        if self.action == 'create' or self.action == 'update':
            return CreateOrganizationSerializer

    def get_object(self, *args, **kwargs):
        assert isinstance(self.request.user.uuid, uuid_lib.UUID)
        user = self.request.user
        org_user_obj = None
        
        try:
            org_user_obj = OrganizationUser.objects.get(Q(user=user) & Q(organization__uuid=self.kwargs['uuid']))
        except OrganizationUser.DoesNotExist:
            raise http.Http404
        
        self.check_object_permissions(self.request, org_user_obj)
        org_obj = None
        
        try:
            org_obj = self.queryset.get(uuid=self.kwargs['uuid'])
        except Organization.DoesNotExist:
            raise http.Http404

        return org_obj
    
    def list(self, *args, **kwargs):
        serializer = GetOrganizationSerializer(self.get_queryset(), many=True, context={'request': self.request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, *args, **kwargs):
        data = self.request.data
        data['updater'] = self.request.user
        serializer = CreateOrganizationSerializer(data=data)
        
        if serializer.is_valid():
            org_obj = serializer.save()
            # Create Organization entry for creator
            org = Organization.objects.get(uuid=org_obj.uuid)
            # Create OrganizationUser entry
            org_user = {
                'organization': org.uuid,
                'user': self.request.user.uuid,
                'access': 2,     #admin
                'is_active': True,
                'updater': self.request.user,
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
        data = self.request.data
        data['uuid'] = self.kwargs['uuid']
        data['updater'] = self.request.user
        instance = None
        
        try:
            instance = self.get_object()
        except Organization.DoesNotExist:
            Response(status=status.HTTP_400_BAD_REQUEST)
        
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
    filterset_fields = []

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return GetOrganizationUserSerializer
        if self.action == 'create' or self.action == 'update':
            return CreateOrganizationUserSerializer

    def get_object(self, *args, **kwargs):
        assert isinstance(self.request.user.uuid, uuid_lib.UUID)
        org_obj = None
        
        try:
            org_obj = self.queryset.get(uuid=self.kwargs['uuid'])
        except Organization.DoesNotExist:
            raise http.Http404
        
        user = self.request.user
        org_user_obj = None
        
        try:
            org_user_obj = self.queryset.get(Q(user=user) & Q(organization=org_obj.organization))
        except OrganizationUser.DoesNotExist:
            raise http.Http404
        
        self.check_object_permissions(self.request, org_user_obj)
        
        return org_obj
    
    def create(self, *args, **kwargs):
        # if user has R+W (1) or is admin (2)
        data = self.request.data
        data['updater'] = self.request.user
        max_access = -1
        
        try:
            instance = self.queryset.get(user__uuid=self.request.user.uuid, access__gte=1)
            max_access = instance.access
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if data['access'] > max_access:
            data['access'] = max_access
        
        data['is_active'] = True
        
        serializer = CreateOrganizationUserSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
    
    def update(self, *args, **kwargs):
        data = self.request.data
        
        try:
            data.pop('organization')
        except:
            pass
        try:
            data.pop('user')
        except:
            pass
        
        data['uuid'] = self.kwargs['uuid']
        data['updater'] = self.request.user
        instance = None

        try:
            instance = self.get_object()
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CreateOrganizationUserSerializer(instance=instance, data=data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

class OrganizationImageViewSet(UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = OrganizationImageSerializer
    queryset = OrganizationImage.objects.all()
    parser_classes = (MultiPartParser, FileUploadParser)
    lookup_field = "uuid"
    
    def create(self, *args, **kwargs):
        data = self.request.data
        org = None
        org_user = None
        print(data['organization'])
        try:
            org = Organization.objects.filter(uuid=data['organization'])[0]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        try:
            org_user = OrganizationUser.objects.filter(Q(organization__uuid=org.uuid) & Q(user__uuid=self.request.user.uuid))[0]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if org_user.access != 2:
            return Response(status.HTTP_404_NOT_FOUND)
        
        serializer = OrganizationImageSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)