from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    """Ингредиенты."""
    name = models.CharField('Название ингредиента', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Tag(models.Model):
    """Теги."""
    RED = '#ff0400'
    YELLOW = '#fff700'
    GREEN = '#07a824'
    TAGS_COLORS = (
        (RED, 'Красный'),
        (GREEN, 'Зелёный'),
        (YELLOW, 'Жёлтый'),
    )
    name = models.CharField('Название тега', max_length=200, unique=True)
    color = models.CharField('Цвет в HEX', max_length=7, blank=True,
                             choices=TAGS_COLORS, default=GREEN, unique=True)
    slug = models.SlugField('Slug', max_length=200, blank=True, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Recipe(models.Model):
    """Рецепты."""
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientRecipe',
                                         related_name='recipes',
                                         verbose_name='Ингредиенты')
    tags = models.ManyToManyField(Tag,
                                  through='TagRecipe',
                                  related_name='recipes',
                                  verbose_name='Теги')
    image = models.ImageField('Изображение блюда',
                              upload_to='recipes/images/')
    name = models.CharField('Название блюда',
                            max_length=200)
    text = models.TextField('Описание блюда')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        validators=(MinValueValidator(1, 'Минимальное время приготовления - '
                                         '1 минута'),)
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientRecipe(models.Model):
    """Модель для связи ингредиетов и рецептов."""
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   verbose_name='Ингредиент')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    amount = models.PositiveSmallIntegerField('Количество ингредиента')

    def __str__(self):
        return (f'Ингредиент - {self.ingredient.name} '
                f'для рецепта - {self.recipe.name}')

    class Meta:
        verbose_name = 'Игредиент и рецепт'
        verbose_name_plural = 'Игредиенты и рецепты'


class TagRecipe(models.Model):
    """Модель для связи тегов и рецептов."""
    tag = models.ForeignKey(Tag,
                            on_delete=models.CASCADE,
                            verbose_name='Тег')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт')

    def __str__(self):
        return f'Тег - {self.tag} для рецепта - {self.recipe}'

    class Meta:
        verbose_name = 'Тег и рецепт'
        verbose_name_plural = 'Теги и рецепты'


class ShoppingList(models.Model):
    """Список покупок."""
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='shoplist',
                               verbose_name='Рецепт в списке покупок')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='shoplist',
                             verbose_name='Пользователь, собравший список')

    def __str__(self):
        return (f'У пользователя {self.user.get_full_name()} в списке покупок '
                f'рецепт - {self.recipe}')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='Уникальный рецепт в списке',
            ),
        )


class Favorite(models.Model):
    """Избранные рецепты."""
    user = models.ForeignKey(User,
                             verbose_name='Пользователь',
                             on_delete=models.CASCADE,
                             related_name='favoriter')
    recipe = models.ForeignKey(Recipe,
                               verbose_name='Избранный рецепт',
                               on_delete=models.CASCADE,
                               related_name='favorite_recipes')

    def __str__(self):
        return (f'У пользователя {self.user.get_full_name()} в избранном '
                f'рецепт - {self.recipe}')

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='Уникальный избранный рецепт',
            ),
        )
