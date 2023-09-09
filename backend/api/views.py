from djoser.serializers import SetPasswordSerializer
# from django.shortcuts import get_object_or_404
# from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
# from rest_framework.filters import SearchFilter
# from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

# from .filters import TitlesFilter
# from .permissions import (IsAdmin, IsAdminOrReadOnly,
#                           IsAuthorModerAdminOrReadOnly)
from .pagination import CustomPagination
# from .permissions import IsCurrentUserOrAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeReadSerializer,
                          TagSerializer,
                          UserCreateSerializer, UserReadSerializer)

from recipes.models import Ingredient, Recipe, Tag
from users.models import User


class UserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                  mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Вьюсет для отображения и создания пользователей."""
    queryset = User.objects.all()
    pagination_class = CustomPagination
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от вида действия."""
        if self.action in ('list', 'retrieve'):
            return UserReadSerializer
        return UserCreateSerializer

    @action(detail=False, methods=['get'],
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        """Дополнительный URL 'users/me' для текущего пользователя."""
        serializer = UserReadSerializer(
            instance=self.request.user, context={'request': request}
        )
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],
            permission_classes=(permissions.IsAuthenticated,))
    def set_password(self, request):
        """
        Дополнительный URL эндпоинт 'users/set_password' для смены пароля,
        реализованный на основе сериализатора из библиотеки Djoser.
        """
        serializer = SetPasswordSerializer(data=request.data,
                                           context={'request': request})
        if serializer.is_valid(raise_exception=True):
            self.request.user.set_password(serializer.data["new_password"])
            self.request.user.save()
        return Response('Пароль успешно изменен.',
                        status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для отображения тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для отображения и создания рецептов."""
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от вида действия."""
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return UserCreateSerializer
