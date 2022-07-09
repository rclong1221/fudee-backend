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
    GetOrganizationSerializer, CreateOrganizationSerializer

from fudee.organizations.models import \
    Organization

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
        print("\n\n\n")
        print(data)
        print("\n\n\n")
        serializer = CreateOrganizationSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            # TODO: Create OrganizationUser entry
            return Response(status=status.HTTP_201_CREATED)
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