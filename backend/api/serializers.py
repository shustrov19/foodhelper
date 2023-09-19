import base64

from django.core.files.base import ContentFile
from djoser import serializers as djoser_serializers
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingList, Tag)
from users.models import Follow, User


class UserReadSerializer(djoser_serializers.UserSerializer):
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


class UserCreateSerializer(djoser_serializers.UserCreateSerializer):
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

    def validate(self, data):
        if User.objects.filter(username=data['username']):
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует'
            )
        return data


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
    """Сериализатор для отображения ингридиентов в рецепте."""
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


class RecipeReadMinSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра краткой информации о рецептах."""
    name = serializers.CharField(read_only=True)
    image = Base64ImageField(read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )


class RecipeReadMaxSerializer(RecipeReadMinSerializer,
                              serializers.ModelSerializer):
    """Сериализатор только для просмотра рецептов."""
    tags = TagSerializer(read_only=True, many=True)
    author = UserReadSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(read_only=True, many=True,
                                             source='ingredient_recipe')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Проверка, есть ли рецепт в избранном пользователя."""
        user = self.context['request'].user
        return (user.is_authenticated and
                Favorite.objects.filter(user=user, recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        """Проверка, есть ли рецепт в списке покупок пользователя."""
        user = self.context['request'].user
        return (user.is_authenticated and
                ShoppingList.objects.filter(user=user, recipe=obj).exists())


class IngredientRecipeCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для указания только id игредиента и его количества
    при создания рецепта.
    """
    id = serializers.IntegerField(required=True)
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeСreateUpdateDeleteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания, обновления и удаления рецептов."""
    ingredients = IngredientRecipeCreateSerializer(many=True, required=True)
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
            'id', 'tags', 'author', 'ingredients', 'name', 'image', 'text',
            'cooking_time'
        )

    def validate(self, data):
        ingredients = data['ingredients']
        for ingredient in ingredients:
            try:
                Ingredient.objects.get(pk=ingredient['id'])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    f'Ингредиента с id = {ingredient["id"]} не существует!'
                )
        return data

    def create(self, validated_data):
        """Создание рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients:
            recipe.ingredients.add(
                ingredient['id'],
                through_defaults={
                    'amount': ingredient['amount']}
            )
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        for tag in tags:
            instance.tags.add(tag)
        instance.ingredients.clear()
        for ingredient in ingredients:
            instance.ingredients.add(
                ingredient['id'],
                through_defaults={
                    'amount': ingredient['amount']}
            )
        instance.save()
        return instance

    def to_representation(self, instance):
        """
        Передача в Response подробных данных созданного или обновлённого
        рецепта через RecipeReadMaxSerializer.
        """
        return RecipeReadMaxSerializer(instance, context=self.context).data


class UserSubscriptionsSerializer(UserReadSerializer):
    """Сериализатор для просмотра, создания, удаления подписок."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )
        read_only_fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        """Получение рецептов избранного автора."""
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = RecipeReadMinSerializer(recipes, read_only=True,
                                             many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Подсчёт количества рецептов избранного автора."""
        return Recipe.objects.filter(author=obj).count()
