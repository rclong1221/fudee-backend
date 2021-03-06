from ast import Is
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

from fudee.relationships.api.serializers import \
    GetInviteSerializer, CreateInviteSerializer, \
    GetRelationshipSerializer, CreateRelationshipSerializer, \
    GetUserGroupSerializer, CreateUserGroupSerializer, \
    GetUserGroupUserSerializer, CreateUserGroupUserSerializer, \
    UserGroupImageSerializer

from fudee.relationships.models import \
    Invite, Relationship, UserGroup, UserGroupUser, UserGroupImage

from fudee.relationships.permissions import IsRelationshipUser, IsUserGroupUser

User = get_user_model()

class InviteViewSet(ListModelMixin, CreateModelMixin, GenericViewSet):
    # serializer = CreateInviteSerializer
    queryset = Invite.objects.all()
    lookup_field = "uuid"
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['email', 'phone']

    def get_serializer_class(self):
        if self.action == 'list':
            return GetInviteSerializer
        if self.action == 'create':
            return CreateInviteSerializer
    
    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.uuid, uuid_lib.UUID)
        try:
            return self.queryset.filter(user__id=self.request.user.uuid)
        except User.DoesNotExist:
            raise http.Http404
    
    def get_object(self, *args, **kwargs):
        assert isinstance(self.request.user.uuid, uuid_lib.UUID)
        try:
            return Invite.objects.get(user__uuid=self.request.user.uuid)
        except Invite.DoesNotExist:
            raise http.Http404
    
    def create(self, *args, **kwargs):
        # Check if user hasn't created a request this past 7 days
        try:
            q = None
            
            if self.request.data['email']:
                q = Invite.objects.filter(user__uuid=self.request.user.uuid, email=self.request.data['email'], date_created__gte=datetime.now()-timedelta(days=7))
                if len(q) > 0:
                    return Response(status=status.HTTP_409_CONFLICT)
            
            if self.request.data['phone']:
                q = Invite.objects.filter(user__uuid=self.request.user.uuid, phone=self.request.data['phone'], date_created__gte=datetime.now()-timedelta(days=7))
                if len(q) > 0:
                    return Response(status=status.HTTP_409_CONFLICT)
        except Invite.DoesNotExist:
            pass
        
        data = self.request.data.copy()
        data['user'] = self.request.user.uuid
        
        serializer = CreateInviteSerializer(data=data)
        
        if serializer.is_valid():
            # TODO: Shoot email
            # from django.core.mail import send_mail

            # send_mail(
            #     '{0} has invited you to join #TODO APP'.format(serializer.data.user.name),
            #     'Here is the message.',
            #     'from@example.com',
            #     ['to@example.com'],
            #     fail_silently=False,
            # )
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
    
    def list(self, *args, **kwargs):
        serializer = GetInviteSerializer(self.get_queryset(), many=True, context={'request': self.request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class RelationshipViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Relationship.objects.all()
    lookup_field = "uuid"
    permission_classes = [permissions.IsAuthenticated, IsRelationshipUser]
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['user1']
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return GetRelationshipSerializer
        if self.action == 'create' or self.action == 'update':
            return CreateRelationshipSerializer

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.uuid, uuid_lib.UUID)
        # user default
        user1 = self.request.user.uuid
        obj = None
        
        try:
            obj = self.queryset.filter(Q(user2__uuid=user1) | Q(user1__uuid=user1))
        except Relationship.DoesNotExist:
            raise http.Http404
        self.check_object_permissions(self.request, obj)
        return obj
    
    def get_object(self, *args, **kwargs):
        assert isinstance(self.request.user.uuid, uuid_lib.UUID)
        obj = None
        try:
            obj = Relationship.objects.get(uuid=self.kwargs['uuid'])
        except Relationship.DoesNotExist:
            raise http.Http404
        self.check_object_permissions(self.request, obj)
        return obj
    
    def create(self, *args, **kwargs):
        data = self.request.data
        user_uuid = str(self.request.user.uuid)
        if user_uuid != data['user1'] and user_uuid != data['user2']:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        data['updater'] = self.request.user.uuid
        serializer = CreateRelationshipSerializer(data=self.request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
    
    def update(self, *args, **kwargs):
        data = {key: self.request.data[key] for key in self.request.data.keys() & {'relationship'}}
        data['updater'] = self.request.user.uuid
        instance = None
        
        try:
            instance = self.get_object()
        except Relationship.DoesNotExist:
            Response(status=status.HTTP_400_BAD_REQUEST)
            
        data = self.request.data
        user_uuid = str(self.request.user.uuid)
        
        if user_uuid != data['user1'] and user_uuid != data['user2']:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = CreateRelationshipSerializer(instance=instance, data=data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
    
    def destroy(self, *args, **kwargs):
        instance = self.get_object()

        try:
            instance.delete()
            return Response(status=status.HTTP_202_ACCEPTED)
        except Relationship.DoesNotExist:
            Response(status=status.HTTP_400_BAD_REQUEST)

class UserGroupViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = UserGroup.objects.all()
    lookup_field = "uuid"
    permission_classes = [permissions.IsAuthenticated, IsUserGroupUser]

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return GetUserGroupSerializer
        if self.action == 'create' or self.action == 'update':
            return CreateUserGroupSerializer
    
    def get_object(self, *args, **kwargs):
        assert isinstance(self.request.user.uuid, uuid_lib.UUID)
        user = self.request.user
        ugu_obj = None
        
        try:
            ugu_obj = UserGroupUser.objects.get(Q(user=user) & Q(group__uuid=self.kwargs['uuid']))
        except UserGroupUser.DoesNotExist:
            raise http.Http404
        
        self.check_object_permissions(self.request, ugu_obj)
        ug_obj = None
        
        try:
            ug_obj = self.queryset.get(uuid=self.kwargs['uuid'])
        except UserGroup.DoesNotExist:
            raise http.Http404

        return ug_obj
    
    def create(self, *args, **kwargs):
        data = {key: self.request.data[key] for key in self.request.data.keys() & {'name'}}
        data['creator'] = self.request.user.uuid
        
        serializer = CreateUserGroupSerializer(data=data)

        if serializer.is_valid():
            ug_obj = serializer.save()
            # Create UserGroupUser entry for creator
            ug = UserGroup.objects.get(uuid=ug_obj.uuid)
            group_user = {
                'group': ug.uuid,
                'user': self.request.user.uuid,
                'access': 2,     #admin
                'is_active': True,
                'updater': self.request.user.uuid,
            }
            gs = CreateUserGroupUserSerializer(data=group_user)
            if gs.is_valid():
                print("\n\n2\n\n")
                gs.save()
                return Response(status=status.HTTP_201_CREATED)
            else:
                print("\n\n1\n\n")
                ug.delete()
                return Response(status=status.HTTP_409_CONFLICT)
        print("\n\n2\n\n")
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

    def update(self, *args, **kwargs):
        data = {key: self.request.data[key] for key in self.request.data.keys() & {'name'}}
        data['uuid'] = self.kwargs['uuid']
        data['updater'] = self.request.user.uuid
        instance = None
        
        try:
            instance = self.queryset.get(uuid=data['uuid'])
        except UserGroup.DoesNotExist:
            Response(status=status.HTTP_400_BAD_REQUEST)
        
        if self.request.user.uuid != instance.creator.uuid:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = CreateUserGroupSerializer(instance=instance, data=data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

class UserGroupUserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = UserGroupUser.objects.all()
    lookup_field = "uuid"
    permission_classes = [permissions.IsAuthenticated, IsUserGroupUser]

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return GetUserGroupUserSerializer
        if self.action == 'create' or self.action == 'update':
            return CreateUserGroupUserSerializer

    def get_object(self, *args, **kwargs):
        assert isinstance(self.request.user.uuid, uuid_lib.UUID)
        
        ug_obj = None
        
        try:
            ug_obj = self.queryset.get(uuid=self.kwargs['uuid'])
        except UserGroup.DoesNotExist:
            raise http.Http404
        
        user = self.request.user
        ugu_obj = None
        
        try:
            ugu_obj = self.queryset.get(Q(user=user) & Q(group=ug_obj.group))
        except UserGroupUser.DoesNotExist:
            raise http.Http404
        
        self.check_object_permissions(self.request, ugu_obj)

        return ug_obj
    
    def create(self, *args, **kwargs):
        # if user has R+W (1) or is admin (2)
        data = self.request.data
        data['updater'] = self.request.user.uuid
        max_access = -1
        try:
            instance = self.queryset.get(user__uuid=self.request.user.uuid, access__gte=1)
            max_access = instance.access
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if data['access'] > max_access:
            data['access'] = max_access
        
        data['is_active'] = True
        
        serializer = CreateUserGroupUserSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
    
    def update(self, *args, **kwargs):
        data = {key: self.request.data[key] for key in self.request.data.keys() & {'access', 'is_active'}}
        data['uuid'] = self.kwargs['uuid']
        data['updater'] = self.request.user.uuid
        instance = None

        try:
            instance = self.get_object()
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CreateUserGroupUserSerializer(instance=instance, data=data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

class UserGroupImageViewSet(DestroyModelMixin, GenericViewSet):
    serializer_class = UserGroupImageSerializer
    queryset = UserGroupImage.objects.all()
    parser_classes = (MultiPartParser, FileUploadParser)
    permission_classes = [permissions.IsAuthenticated, IsUserGroupUser]
    lookup_field = "uuid"
    
    def create(self, *args, **kwargs):
        data = self.request.data
        ugu = None
        
        try:
            ugu = UserGroupUser.objects.get(Q(group__uuid=data['user_group']) & Q(user=self.request.user))
        except UserGroupUser.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        print(ugu)
        self.check_object_permissions(self.request, ugu)
        
        serializer = UserGroupImageSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)