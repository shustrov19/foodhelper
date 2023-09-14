import base64
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
# from rest_framework.exceptions import ValidationError
# from rest_framework.relations import SlugRelatedField
# from rest_framework_simplejwt.tokens import AccessToken

from recipes.models import (Favorite, Ingredient, IngredientRecipe,
                            Recipe, ShoppingList, Tag)
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


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для промежуточной модели Ингриденты для рецептов."""
    id = serializers.IntegerField(read_only=True, source='ingredient.id')
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id', 'name', 'measurement_unit', 'amount'
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
    tags = TagSerializer(read_only=True, many=True)
    author = UserReadSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(read_only=True, many=True,
                                             source='ingredient_recipe')
    image = Base64ImageField(read_only=True)

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


class IngredientRecipeCreateSerializer(serializers.ModelSerializer):
    """Ингредиент и количество для создания рецепта."""
    id = serializers.PrimaryKeyRelatedField(required=True,
                                            queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeСreateUpdateDeleteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания, обновления и удаления рецептов."""
    ingredients = IngredientRecipeCreateSerializer(many=True, required=True,
                                                   write_only=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, required=True,
                                              queryset=Tag.objects.all())
    author = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    image = Base64ImageField(required=True)
    name = serializers.CharField(required=True, max_length=200)
    text = serializers.CharField(required=True)
    cooking_time = serializers.IntegerField(required=True, min_value=1)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name',
            'image', 'text', 'cooking_time'
        )

    def create(self, validated_data):
        """Создание рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        recipe.tags.set(tags)
        IngredientRecipe.objects.bulk_create(
            [IngredientRecipe(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )
        return recipe

    def to_representation(self, instance):
        """
        Передача в Response подробных данных созданного или обновлённого
        рецепта через RecipeReadSerializer.
        """
        return RecipeReadSerializer(instance, context=self.context).data

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.set(tags)
        instance.ingredients.clear()
        IngredientRecipe.objects.bulk_create(
            [IngredientRecipe(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )
        instance.save()
        return instance


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления и удаления рецептов из избранного."""
    image = Base64ImageField(read_only=True)
    name = serializers.CharField(read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )
