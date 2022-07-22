from rest_framework import permissions
from collections.abc import Iterable

class IsShiftUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj.user != request.user:
            return False
        if request.method == 'PUT' or request.method == 'PATCH' or request.method == 'DELETE':
            if obj.access < 2:
                return False
        if obj.access < 1:
            return False
        return True