from rest_framework import permissions


class IsCurrentUserOrAdminOrReadOnly(permissions.BasePermission):
    """
    Доступ для неавторизованных пользователей только чтение.
    Другие методы доступны только для авторизованного пользователя и
    администратора.
    """
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS or
                (obj.user == request.user or request.user.is_superuser))
