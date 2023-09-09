import base64
# from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
# from rest_framework.exceptions import ValidationError
# from rest_framework.relations import SlugRelatedField
# from rest_framework_simplejwt.tokens import AccessToken

from recipes.models import Favorite, Ingredient, Recipe, ShoppingList, Tag
from users.models import Follow, User


class UserReadSerializer(UserSerializer):
    """Сериализатор только для просмотра пользователей."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """
        Проверка, является ли автор запроса подписчиком
        полученного пользователя.
        """
        user = self.context['request'].user
        if not user.is_authenticated or user == obj:
            return False
        return Follow.objects.filter(user=user, following=obj).exists()


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователей."""
    username = serializers.RegexField(regex=r'^[\w.@+-]+\Z', max_length=150,
                                      required=True)
    email = serializers.EmailField(max_length=254, required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(max_length=150, required=True,
                                     write_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра тегов."""
    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра ингредиентов."""
    class Meta:
        model = Ingredient
        fields = (
            'id', 'name', 'measurement_unit'
        )


class Base64ImageField(serializers.ImageField):
    """Сериализатор для декодирования текста в картинку."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор только для просмотра рецептов."""
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Проверка, есть ли рецепт в избранном автора запроса."""
        user = self.context['request'].user
        return (user.is_authenticated and
                Favorite.objects.filter(user=user, recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        """Проверка, есть ли рецепт в списке покупок автора запроса."""
        user = self.context['request'].user
        return (user.is_authenticated and
                ShoppingList.objects.filter(user=user, recipe=obj).exists())
