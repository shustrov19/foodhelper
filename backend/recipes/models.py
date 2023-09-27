from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    """Ингредиенты."""
    name = models.CharField('Название ингредиента', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Теги."""
    COLOR_PALETTE = (
        ('#C76161', 'Красный'),
        ('#63F059', 'Зелёный'),
        ('#3C99F0', 'Синий'),
    )
    name = models.CharField('Название тега', max_length=200, unique=True)
    color = ColorField('Цвет в HEX', max_length=7, unique=True,
                       samples=COLOR_PALETTE)
    slug = models.SlugField('Slug', max_length=200, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


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
        validators=(
            MinValueValidator(1, 'Минимальное время приготовления - '
                              '1 минута'),
            MaxValueValidator(1440, 'Максимальное время приготовления - '
                              '1440 минут(1 день)')
        )
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Модель для связи ингредиетов и рецептов."""
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='ingredient_recipe',
                                   verbose_name='Ингредиент')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='ingredient_recipe',
                               verbose_name='Рецепт')
    amount = models.PositiveSmallIntegerField(
        'Количество ингредиента',
        validators=(MinValueValidator(1, 'Ингредиент должен быть в количестве '
                                      '1 и больше'),
                    MaxValueValidator(32000, 'Ингредиент должен быть в '
                                      'количестве не более 32000'))
    )

    class Meta:
        verbose_name = 'Игредиент для рецепта'
        verbose_name_plural = 'Игредиенты для рецептов'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='Уникальный ингредиент для рецепта',
            ),
        )

    def __str__(self):
        return (f'{self.ingredient.name} в количестве {self.amount} '
                f'{self.ingredient.measurement_unit}  для {self.recipe.name}')


class TagRecipe(models.Model):
    """Модель для связи тегов и рецептов."""
    tag = models.ForeignKey(Tag,
                            on_delete=models.CASCADE,
                            verbose_name='Тег',
                            related_name='tag_recipe')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='tag_recipe')

    class Meta:
        verbose_name = 'Тег для рецепта'
        verbose_name_plural = 'Теги для рецептов'
        constraints = (
            models.UniqueConstraint(
                fields=('tag', 'recipe'),
                name='Уникальный тег для рецепта',
            ),
        )

    def __str__(self):
        return f'Тег - {self.tag} для {self.recipe}'


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

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='Уникальный рецепт в списке покупок',
            ),
        )

    def __str__(self):
        return f'У {self.user} в списке покупок {self.recipe}'


class Favorite(models.Model):
    """Избранные рецепты."""
    user = models.ForeignKey(User,
                             verbose_name='Пользователь',
                             on_delete=models.CASCADE,
                             related_name='favorite')
    recipe = models.ForeignKey(Recipe,
                               verbose_name='Избранный рецепт',
                               on_delete=models.CASCADE,
                               related_name='favorite')

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='Уникальный избранный рецепт',
            ),
        )

    def __str__(self):
        return f'У {self.user} в избранном {self.recipe}'
