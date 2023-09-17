from rest_framework.permissions import SAFE_METHODS, BasePermission


class ReadOnly(BasePermission):
    # Не нащел этот пермишен в базовых, поэтому решил оставить
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsAuthor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
