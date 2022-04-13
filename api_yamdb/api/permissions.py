from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, BasePermission

MODERATOR = ['admin', 'moderator']


class CustomIsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (
                request.user.is_superuser
                or request.user.role == 'admin'
                or request.user.is_staff
            )

    
class OwnerOrAdmins(permissions.BasePermission):

    def has_permission(self, request, view):
        if (
            request.user.is_anonymous
            or not (
                request.user.role == 'admin'
                or request.user.is_superuser)):
            return False
        else:
            return True

    def has_object_permission(self, request, view, obj):
        return (
            obj.username == request.user
            or request.user.role == 'admin'
            or request.user.is_superuser)


class ReadOnlyOrAdmins(permissions.BasePermission):

    def has_permission(self, request, view):
        if (request.user.is_anonymous
                and request.method not in permissions.SAFE_METHODS):
            return False
        else:
            return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_superuser
                or request.user.role in ('admin'))


class ReadOnlyOrOwnerOrAllAdmins(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.user
                and request.method in permissions.SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_superuser
            or request.user.role in MODERATOR
            or obj.author == request.user)


class IsAdminOrReadOnly(BasePermission):
    """Разрешение на уровне админ."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.role == 'admin'
        else:
            False


class CustomIsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == 'admin'
        else:
            False


class ModeratorOrReadOnly(BasePermission):
    """Разрешение на уровне модератор."""
    def has_permission(self, request, view):
        """Безопасный метод или роль пользователя выше чем user."""
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            if request.user.role in MODERATOR:
                return True
        else:
            return False


class AuthorAndStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            if (request.user.role in MODERATOR):
                return True
        return obj.author == request.user
