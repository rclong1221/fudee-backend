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

from fudee.relationships.serializers import \
    GetInviteSerializer, CreateInviteSerializer

from fudee.relationships.models import \
    Invite

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