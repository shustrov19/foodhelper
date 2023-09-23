from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingList, Tag, TagRecipe)

admin.site.site_title = 'Админ-панель сайта Foodgram'
admin.site.site_header = 'Админ-панель сайта Foodgram'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


class IngredientAdmin(admin.ModelAdmin):
    """Отображение ингредиентов."""
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)


class IngredientRecipeAdmin(admin.ModelAdmin):
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


class RecipeAdmin(admin.ModelAdmin):
    """Отображение рецептов."""
    list_display = ('id', 'name', 'author', 'in_favorite_count')
    list_filter = ('author', 'name', 'tags')
    inlines = (IngredientsInline, TagsInline)

    def in_favorite_count(self, obj):
        """Подсчёт количества добавлений в избранное рецепта."""
        return obj.favorite.all().count()

    in_favorite_count.short_description = 'Количество добавлений избранное'


class TagAdmin(admin.ModelAdmin):
    """Отображение тегов"""
    list_display = ('id', 'name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'recipe')


admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(TagRecipe, TagRecipeAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
