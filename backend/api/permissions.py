from rest_framework import permissions


class IsAuthorStaffAdminOrReadOnly(permissions.BasePermission):
    """
    Просмотр разрешён любому пользователю.
    Создание, удаление, редактирование разрешено только автору,
    персоналу сервиса или администратору.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_staff
                or request.user.is_superuser)
