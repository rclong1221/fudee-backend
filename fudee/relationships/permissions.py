from rest_framework import permissions
from collections.abc import Iterable

class IsRelationshipUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Iterable):
            for o in obj:
                if o.user1 != request.user and o.user2 != request.user:
                    return False
        elif obj != request.user:
            return False
        return True

class IsUserGroupAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj.user != request.user:
            return False
        if obj.access != 2:
            return False
        return True

class IsUserGroupUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj.user != request.user:
            return False
        if obj.access < 1:
            return False
        return True