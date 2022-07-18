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
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser

import uuid as uuid_lib

from fudee.relationships.api.serializers import \
    GetInviteSerializer, CreateInviteSerializer, \
    GetRelationshipSerializer, CreateRelationshipSerializer, \
    GetUserGroupSerializer, CreateUserGroupSerializer, \
    GetUserGroupUserSerializer, CreateUserGroupUserSerializer, \
    UserGroupImageSerializer

from fudee.relationships.models import \
    Invite, Relationship, User_Group, User_Group_User, User_Group_Image

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
    permission_classes = [permissions.IsAuthenticated]
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
        
        return self.queryset.filter(Q(user2__uuid=user1) | Q(user1__uuid=user1))
    
    def get_object(self, *args, **kwargs):
        assert isinstance(self.request.kwargs['uuid'], uuid_lib.UUID)
        try:
            return Relationship.objects.filter(Q(user1__uuid=self.request.kwargs['uuid']) | Q(user2__uuid=self.request.kwargs['uuid'])).first()
        except Relationship.DoesNotExist:
            raise http.Http404
    
    # def list(self, *args, **kwargs):
    #     serializer = GetRelationshipSerializer(self.get_queryset(), many=True, context={'request': self.request})
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, *args, **kwargs):
        data = self.request.data
        user_uuid = str(self.request.user.uuid)
        if user_uuid != data['user1'] and user_uuid != data['user2']:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        data['updater_id'] = self.request.user.id
        serializer = CreateRelationshipSerializer(data=self.request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
    
    def update(self, *args, **kwargs):
        data = {key: self.request.data[key] for key in self.request.data.keys() & {'relationship'}}
        data['updater_id'] = self.request.user.id
        instance = None
        
        try:
            instance = self.queryset.get(uuid=self.kwargs['uuid'])
        except self.queryset.DoesNotExist:
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
        user1 = self.request.user.uuid
        instance = Relationship.objects.filter(Q(user1__uuid=user1) | Q(user2__uuid=user1) & Q(uuid=self.kwargs['uuid'])).first()

        try:
            instance.delete()
            return Response(status=status.HTTP_202_ACCEPTED)
        except self.queryset.DoesNotExist:
            Response(status=status.HTTP_400_BAD_REQUEST)

    # @action(detail=False)
    # def me(self, request):
    #     serializer = RelationshipSerializer(request.user, context={"request": request})
    #     return Response(status=status.HTTP_200_OK, data=serializer.data)


class UserGroupViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = User_Group.objects.all()
    lookup_field = "uuid"
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return GetUserGroupSerializer
        if self.action == 'create' or self.action == 'update':
            return CreateUserGroupSerializer

    # def get_queryset(self, *args, **kwargs):
    #     assert isinstance(self.request.user.id, int)
    #     return self.queryset.filter(id=self.request.user.id)
    
    def create(self, *args, **kwargs):
        data = {key: self.request.data[key] for key in self.request.data.keys() & {'name'}}
        data['creator'] = self.request.user.uuid
        
        serializer = CreateUserGroupSerializer(data=data)

        if serializer.is_valid():
            ug_obj = serializer.save()
            # Create User_Group_User entry for creator
            ug = User_Group.objects.get(uuid=ug_obj.uuid)
            group_user = {
                'group': ug.uuid,
                'user': self.request.user.uuid,
                'access': 2,     #admin
                'is_active': True,
                'updater_id': self.request.user.id,
            }
            gs = CreateUserGroupUserSerializer(data=group_user)
            if gs.is_valid():
                gs.save()
                return Response(status=status.HTTP_201_CREATED)
            else:
                ug.delete()
                return Response(status=status.HTTP_409_CONFLICT)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

    def update(self, *args, **kwargs):
        data = {key: self.request.data[key] for key in self.request.data.keys() & {'name'}}
        data['uuid'] = self.kwargs['uuid']
        data['updater_id'] = self.request.user.id
        instance = None
        
        try:
            instance = self.queryset.get(uuid=data['uuid'])
        except self.queryset.DoesNotExist:
            Response(status=status.HTTP_400_BAD_REQUEST)
        
        if self.request.user.id != instance.creator.id:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = CreateUserGroupSerializer(instance=instance, data=data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

    # @action(detail=False)
    # def me(self, request):
    #     serializer = GetUserGroupSerializer(request.user, context={"request": request})
    #     return Response(status=status.HTTP_200_OK, data=serializer.data)

class UserGroupUserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = User_Group_User.objects.all()
    lookup_field = "uuid"
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'group']

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return GetUserGroupUserSerializer
        if self.action == 'create' or self.action == 'update':
            return CreateUserGroupUserSerializer

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
        
        serializer = CreateUserGroupUserSerializer(data=data)

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
        
        serializer = CreateUserGroupUserSerializer(instance=instance, data=data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

    @action(detail=False)
    def me(self, request):
        serializer = GetUserGroupUserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

class UserGroupImageViewSet(UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = UserGroupImageSerializer
    queryset = User_Group_Image.objects.all()
    parser_classes = (MultiPartParser, FileUploadParser)
    lookup_field = "uuid"
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user_group']
    
    # def get_object(self, *args, **kwargs):
    #     try:
    #         return User_Group_Image.objects.get(user=self.request.user)
    #     except User.DoesNotExist:
    #         return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # def retrieve(self, *args, **kwargs):
    #     # get requested User Group Image
    #     ugi = User_Group_Image.objects.filter(group=self.request.data['user_group']).latest('date_created')
        
    #     # get user's user group credentials
        
        
    #     # if user doesnt have credentials 404
        
        
    #     # else create/update user group image
        
        
    #     user_group_image = {
    #         'uuid': ugi.uuid,
    #         'user_group': ugi.user_group.id,
    #         'image': ugi.image,
    #         'date_created': ugi.date_created
    #     }

    #     serializer = UserGroupImageSerializer(data=user_group_image)
    #     if serializer.is_valid():
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
    
    def create(self, *args, **kwargs):
        data = self.request.data
        ug = None
        ugu = None
        
        try:
            ug = User_Group.objects.filter(id=data['user_group'])[0]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        try:
            ugu = User_Group_User.objects.filter(Q(group=ug) & Q(user=self.request.user))[0]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if ugu.access != 2:
            return Response(status.HTTP_404_NOT_FOUND)
        
        serializer = UserGroupImageSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)