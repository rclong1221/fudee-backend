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

from fudee.relationships.api.serializers import \
    GetInviteSerializer, CreateInviteSerializer, \
    GetRelationshipSerializer, CreateRelationshipSerializer

from fudee.relationships.models import \
    Invite, Relationship

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
        assert isinstance(self.request.user.id, int)
        try:
            return self.queryset.filter(user=self.request.user.id)
        except User.DoesNotExist:
            raise http.Http404
    
    # def get_object(self, *args, **kwargs):
    #     assert isinstance(self.request.user.id, int)
    #     try:
    #         return Invite.objects.get(id=self.request.user.id)
    #     except Invite.DoesNotExist:
    #         raise http.Http404
    
    def create(self, *args, **kwargs):
        # Check if user hasn't created a request this past 7 days
        try:
            q = None
            
            if self.request.data['email']:
                q = Invite.objects.filter(user=self.request.user.id, email=self.request.data['email'], date_created__gte=datetime.now()-timedelta(days=7))
                if len(q) > 0:
                    return Response(status=status.HTTP_409_CONFLICT)
            
            if self.request.data['phone']:
                q = Invite.objects.filter(user=self.request.user.id, phone=self.request.data['phone'], date_created__gte=datetime.now()-timedelta(days=7))
                if len(q) > 0:
                    return Response(status=status.HTTP_409_CONFLICT)
        except Invite.DoesNotExist:
            pass
        
        data = self.request.data
        
        # Check if user isn't faking ID
        if self.request.user.id != data['user']:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user1']
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return GetRelationshipSerializer
        if self.action == 'create' or self.action == 'update':
            return CreateRelationshipSerializer

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        # user default
        user1 = self.request.user.id
        
        # if self.request.data['user1'] is not None:
        #     user = self.request.data['user1']
        # if self.request.data['user2'] is not None:
        #     req_user2 = self.request.data['user2']
            
        if self.request.user.id != user1:
            return self.queryset.none()
        
        # if self.request.data['user1'] is not None and self.request.data['user2'] is not None:
        #     return self.queryset.filter(Q(user2=req_user2) | Q(user=req_user))
        # elif self.request.data['user1'] is  None and self.request.data['user2'] is not None:
        #     return None
        return self.queryset.filter(Q(user2=user1) | Q(user1=user1))
    
    # def get_object(self, *args, **kwargs):
    #     assert isinstance(self.request.user, User)
    #     try:
    #         return Relationship.objects.filter(Q(user1=self.request.kwargs['uuid']) | Q(user2=self.request.kwargs['uuid'])).first()
    #     except Relationship.DoesNotExist:
    #         raise http.Http404
    
    def list(self, *args, **kwargs):
        serializer = GetRelationshipSerializer(self.get_queryset(), many=True, context={'request': self.request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, *args, **kwargs):
        if self.request.user.id != self.request.data['user1'] and self.request.user.id != self.request.data['user2']:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = CreateRelationshipSerializer(data=self.request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
    
    def update(self, *args, **kwargs):
        data = {key: self.request.data[key] for key in self.request.data.keys() & {'relationship'}}
        data['uuid'] = self.kwargs['uuid']
        data['updater_id'] = self.request.user.id
        instance = None
        
        try:
            instance = self.queryset.get(uuid=data['uuid'])
        except self.queryset.DoesNotExist:
            Response(status=status.HTTP_400_BAD_REQUEST)
        
        if self.request.user.id != instance.user1.id and self.request.user.id != instance.user2.id:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = CreateRelationshipSerializer(instance=instance, data=data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

    # @action(detail=False)
    # def me(self, request):
    #     serializer = RelationshipSerializer(request.user, context={"request": request})
    #     return Response(status=status.HTTP_200_OK, data=serializer.data)