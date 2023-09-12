from rest_framework.permissions import BasePermission, SAFE_METHODS
from .exceptions import Unauthorized401, NotEnoughRights403


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated


class IsAuthor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class RecipePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise Unauthorized401()
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in ['PATCH', 'DELETE']:
            if obj.author == request.user:
                return True
            else:
                raise NotEnoughRights403()
        return True
