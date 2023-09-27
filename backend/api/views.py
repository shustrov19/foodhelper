from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import FoodgramPagination
from .permissions import IsAuthorAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeReadMaxSerializer,
                          RecipeReadMinSerializer,
                          RecipeСreateUpdateDeleteSerializer, ShoppingList,
                          TagSerializer, UserCreateSerializer,
                          UserReadSerializer, UserSubscriptionsSerializer)
from .utils import download_shop_cart
from recipes.models import Favorite, Ingredient, Recipe, Tag
from users.models import Follow, User


class UserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                  mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Вьюсет для отображения и создания пользователей."""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    pagination_class = FoodgramPagination
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от вида запроса."""
        if self.request.method == 'GET':
            return UserReadSerializer
        return self.serializer_class

    @action(detail=False, methods=['get'],
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        """Дополнительный URL эндпоинт 'users/me' для текущего пользователя."""
        serializer = UserReadSerializer(instance=self.request.user,
                                        context={'request': request})
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
            self.request.user.set_password(serializer.data['new_password'])
            self.request.user.save()
        return Response('Пароль успешно изменён',
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            pagination_class=FoodgramPagination,
            permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        """
        Дополнительный URL эндпоинт 'users/subscriptions' для просмотра
        подписок пользователя.
        """
        followings = User.objects.filter(following__user=self.request.user)
        paginated_followings = self.paginate_queryset(followings)
        serializer = UserSubscriptionsSerializer(paginated_followings,
                                                 many=True,
                                                 context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, *args, **kwargs):
        """
        Дополнительный URL эндпоинт 'users/{id}/subscribe' для оформления
        и удаления подписки на автора.
        """
        author = get_object_or_404(User, pk=kwargs.get('pk'))
        following_author = Follow.objects.filter(following=author,
                                                 user=self.request.user)
        if request.method == 'POST':
            if author == self.request.user:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if following_author:
                return Response(
                    {'errors': 'Уже есть подписка на данного автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = UserSubscriptionsSerializer(
                author,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(following=author, user=self.request.user)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if not following_author:
            return Response(
                {'errors': 'На данного автора подписка не оформлена'},
                status=status.HTTP_400_BAD_REQUEST
            )
        following_author.delete()
        return Response(
            {'detail': 'Отписка от данного автора прошла успешно'},
            status=status.HTTP_204_NO_CONTENT
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name', )


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeСreateUpdateDeleteSerializer
    pagination_class = FoodgramPagination
    permission_classes = (IsAuthorAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от вида запроса."""
        if self.request.method == 'GET':
            return RecipeReadMaxSerializer
        return self.serializer_class

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, *args, **kwargs):
        """
        Дополнительный URL 'recipes/{id}/favorite'
        для добавления и удаления рецепта из избранного.
        """
        recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        favorite_recipe = Favorite.objects.filter(user=self.request.user,
                                                  recipe=recipe)
        if request.method == 'POST':
            if favorite_recipe:
                return Response({'errors': 'Рецепт есть в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeReadMinSerializer(recipe, data=request.data)
            serializer.is_valid(raise_exception=True)
            Favorite.objects.create(user=self.request.user, recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if not favorite_recipe:
            return Response({'errors': 'Рецепта нет в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)
        favorite_recipe.delete()
        return Response({'detail': 'Рецепт успешно удален из избранного'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, *args, **kwargs):
        """
        Дополнительный URL эндпоинт 'recipes/{id}/shopping_cart'
        для добавления и удаления рецепта из списка покупок.
        """
        recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        shopping_recipe = ShoppingList.objects.filter(user=self.request.user,
                                                      recipe=recipe)
        if request.method == 'POST':
            if shopping_recipe:
                return Response({'errors': 'Рецепт уже в списке покупок'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeReadMinSerializer(recipe, data=request.data)
            serializer.is_valid(raise_exception=True)
            ShoppingList.objects.create(user=self.request.user, recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if not shopping_recipe:
            return Response({'errors': 'Рецепта нет в списке покупок'},
                            status=status.HTTP_400_BAD_REQUEST)
        shopping_recipe.delete()
        return Response({'detail': 'Рецепт успешно удален из списка покупок'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        """
        Дополнительный URL эндпоинт 'recipes/download_shopping_cart'
        для скачивания списка ингредиентов из списка покупок.
        """
        user = get_object_or_404(User, pk=self.request.user.pk)
        return download_shop_cart(user)
