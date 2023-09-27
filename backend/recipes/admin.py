from django.contrib import admin

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingList, Tag, TagRecipe)

admin.site.site_title = 'Админ-панель сайта Foodgram'
admin.site.site_header = 'Админ-панель сайта Foodgram'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Отображение избранных рецептов."""
    list_display = ('id', 'user', 'recipe')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Отображение списка покупок."""
    list_display = ('id', 'user', 'recipe')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Отображение ингредиентов."""
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    """Отображение модели связи ингредиентов и рецептов."""
    list_display = ('id', 'ingredient', 'recipe', 'amount')


class IngredientsInline(admin.TabularInline):
    """
    Функционал для добавления ингридиентов в рецепты сразу из пункта 'Рецепты'.
    """
    model = IngredientRecipe


class TagsInline(admin.TabularInline):
    """
    Функционал для добавления тегов в рецепты сразу из пункта 'Рецепты'.
    """
    model = TagRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Отображение рецептов."""
    list_display = ('id', 'name', 'author', 'in_favorite_count')
    list_filter = ('author', 'name', 'tags')
    inlines = (IngredientsInline, TagsInline)

    def in_favorite_count(self, obj):
        """Подсчёт количества добавлений в избранное рецепта."""
        return obj.favorite.all().count()

    in_favorite_count.short_description = 'Количество добавлений избранное'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Отображение тегов."""
    list_display = ('id', 'name', 'color', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    """Отображение модели связи тегов и рецептов."""
    list_display = ('id', 'tag', 'recipe')
